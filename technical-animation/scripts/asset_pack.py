"""Registration-preserving artwork preparation; does not generate or segment images."""
from __future__ import annotations
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from PIL import Image
import topic_model as m


def normalize(paths, destination, canvas=1024):
    """Crop the shared union, use one scale/offset for ALL related layers.

Independently cropped or differently sized poses are rejected, never guessed into alignment.
The coordinate affine transform is returned for port/pivot conversion.
"""
    dest=Path(destination)
    m.require(not dest.exists(),'E_EXISTS','use a new asset-pack directory')
    m.require(type(canvas) is int and 256<=canvas<=4096,'E_SIZE','canvas 256..4096')
    m.require(1<=len(paths)<=30,'E_ASSET','1..30 registered layers required')
    images=[];bounds=[];size=None;names=set()
    for raw in paths:
        p=Path(raw).resolve();m.require(p.is_file(),'E_PATH','missing '+str(raw))
        m.require(p.name not in names,'E_ASSET','duplicate basename');names.add(p.name)
        with Image.open(p) as im:
            m.require(im.format in ('PNG','WEBP') and im.width*im.height<=40_000_000,'E_ASSET','registered PNG/WebP layers required')
            m.require(size is None or size==im.size,'E_REGISTRATION','layers have different source canvases; provide aligned layers instead of independent crops')
            size=im.size;rgba=im.convert('RGBA');box=rgba.getchannel('A').getbbox()
            m.require(box is not None,'E_ART','empty layer '+p.name)
            images.append((p,rgba));bounds.append(box)
    union=[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)]
    w,h=union[2]-union[0],union[3]-union[1]
    scale=(canvas*.90)/max(w,h);nw=max(1,round(w*scale));nh=max(1,round(h*scale));ox=(canvas-nw)//2;oy=(canvas-nh)//2
    # Rounded target dimensions yield a <=1 pixel difference between axes; record exact affine.
    sx=nw/w;sy=nh/h
    dest.parent.mkdir(parents=True,exist_ok=True);tmp=Path(tempfile.mkdtemp(prefix='.registered-',dir=dest.parent))
    try:
        report={'status':'processed-not-generated','source_canvas':list(size),'canvas':[canvas,canvas],
          'transform_pixels':{'sx':sx,'sy':sy,'tx':ox-union[0]*sx,'ty':oy-union[1]*sy},
          'port_conversion':'output_normalized = (source_normalized * source_canvas * scale + translation) / output_canvas',
          'files':[], 'approval':'pending; inspect registration and transparency; retain original generation receipts'}
        for p,im in images:
            out=Image.new('RGBA',(canvas,canvas),(0,0,0,0));cropped=im.crop(tuple(union)).resize((nw,nh),Image.Resampling.LANCZOS)
            out.alpha_composite(cropped,(ox,oy));name=p.stem+'.png'
            m.require(not (tmp/name).exists(),'E_ASSET','output name collision')
            out.save(tmp/name)
            report['files'].append({'name':name,'source_sha256':m.sha(p),'sha256':m.sha(tmp/name)})
        (tmp/'registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        dest.mkdir()
        for p in tmp.iterdir():p.rename(dest/p.name)
        return report
    finally:shutil.rmtree(tmp,ignore_errors=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('images',type=Path,nargs='+');p.add_argument('--out',type=Path,required=True);p.add_argument('--canvas',type=int,default=1024)
    a=p.parse_args()
    try:print(json.dumps(normalize(a.images,a.out,a.canvas),ensure_ascii=False,indent=2))
    except (m.Problem,OSError,ValueError) as e:raise SystemExit(str(e))
if __name__=='__main__':main()
