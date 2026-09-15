"""Local audio and explicit narration cue spans. No voice cloning, TTS or ASR.

FFmpeg's atrim/asetpts/adelay/amix/apad are used only during video encoding.
Files and command arguments are local and explicit; nothing is fetched or executed from JSON.
"""
from __future__ import annotations
import base64
import json
import re
import shutil
import subprocess
from pathlib import Path
import topic_model as m

MIME={'.wav':'audio/wav','.mp3':'audio/mpeg','.m4a':'audio/mp4','.ogg':'audio/ogg','.flac':'audio/flac'}


def validate(data,root):
    tracks=data.get('soundtrack',[])
    m.require(isinstance(tracks,list) and len(tracks)<=2,'E_AUDIO','at most one narration and one music track')
    if not tracks:return []
    m.require(any(f in data.get('formats',[]) for f in ('html','video')),'E_AUDIO_FORMAT','static SVG has no audio; explicitly choose an audiovisual output')
    probe=shutil.which('ffprobe');m.require(probe,'E_AUDIO_DEP','ffprobe is required to validate audio duration')
    result=[];roles=set();gain=0
    for i,t in enumerate(tracks):
        m.require(isinstance(t,dict) and not set(t)-{'role','path','sha256','start','trim_in','trim_out','gain'},'E_AUDIO','invalid soundtrack fields')
        role=t.get('role');m.require(role in ('narration','music') and role not in roles,'E_AUDIO','one track per role');roles.add(role)
        path=m.local(root,t.get('path'))
        m.require(path.suffix.lower() in MIME and path.stat().st_size<=80_000_000,'E_AUDIO','unsupported/oversized audio')
        m.require(m.sha(path)==t.get('sha256'),'E_AUDIO_HASH',t['path'])
        a=m.number(t.get('start',0),'audio.start',0,180)
        lo=m.number(t.get('trim_in',0),'audio.trim_in',0,3600)
        hi=m.number(t.get('trim_out'),'audio.trim_out',0,3600)
        level=m.number(t.get('gain',1),'audio.gain',0,1);gain+=level
        meta=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(path)],text=True,timeout=20))
        aud=[s for s in meta.get('streams',[]) if s['codec_type']=='audio']
        m.require(len(aud)==1 and not any(s['codec_type']=='video' for s in meta.get('streams',[])),'E_AUDIO','use an audio-only file')
        duration=float(meta['format'].get('duration',aud[0].get('duration',0)))
        m.require(0<=lo<hi<=duration+.001 and a+(hi-lo)<=data['duration']+.001,'E_AUDIO_RANGE','track exceeds source or scene duration; revise the explicit trim/cues')
        result.append({'role':role,'duration':duration,'start':a,'trim_in':lo,'trim_out':hi,'gain':level,'mime':MIME[path.suffix.lower()]})
    m.require(gain<=1.000001,'E_AUDIO_GAIN','combined track gain must be <=1; reduce music instead of clipping')
    return result


def html_tracks(data,root):
    # Export only audio bytes/timing, not private paths or generation receipts.
    result=[]
    for track,meta in zip(data.get('soundtrack',[]),validate(data,root)):
        p=m.local(root,track['path'])
        result.append({**meta,'src':'data:'+meta['mime']+';base64,'+base64.b64encode(p.read_bytes()).decode()})
    return result


def ffmpeg_audio(data,root,start_index=1):
    """Return explicit input args, filtergraph and output-map args; no shell interpolation."""
    meta=validate(data,root)
    if not meta:return [],[],['-an']
    inputs=[];filters=[];labels=[]
    for i,(track,t) in enumerate(zip(data['soundtrack'],meta)):
        inputs+=['-i',str(m.local(root,track['path']))]
        label='sound'+str(i);labels.append('['+label+']')
        # Delays use integer sample counts at a fixed 48 kHz rate for consistent placement.
        filters.append(f'[{i+start_index}:a:0]atrim=start={t["trim_in"]}:end={t["trim_out"]},asetpts=PTS-STARTPTS,aresample=48000,volume={t["gain"]},adelay=delays={round(t["start"]*48000)}S:all=1[{label}]')
    filters.append(''.join(labels)+f'amix=inputs={len(meta)}:duration=longest:normalize=0,apad=whole_dur={data["duration"]},atrim=duration={data["duration"]}[mix]')
    return inputs,['-filter_complex',';'.join(filters)],['-map','0:v:0','-map','[mix]','-c:a','aac','-b:a','192k','-ar','48000']


def parse_srt(text):
    """Import supplied SRT as cue IDs line-1, line-2. Not forced alignment or transcription."""
    blocks=re.split(r'\n\s*\n',text.replace('\r\n','\n').strip().lstrip('\ufeff'))
    def timecode(t):
        matched=re.fullmatch(r'(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})',t)
        m.require(matched is not None,'E_CUE','invalid SRT timestamp')
        h,mi,se,ms=map(int,matched.groups());m.require(mi<60 and se<60,'E_CUE','invalid SRT time')
        return h*3600+mi*60+se+ms/1000
    result=[]
    for i,block in enumerate(blocks,1):
        lines=block.splitlines()
        if lines and lines[0].strip().isdigit():lines=lines[1:]
        m.require(len(lines)>=2 and '-->' in lines[0],'E_CUE','invalid SRT block '+str(i))
        ends=lines[0].split('-->');a=timecode(ends[0].strip());b=timecode(ends[1].strip())
        m.require(a<b,'E_CUE','cue end precedes start')
        words=' '.join(l.strip() for l in lines[1:]);m.string(words,'cue.text',400)
        result.append(dict(id='line-'+str(i),start=a,end=b,text=words))
    m.require(result,'E_CUE','no subtitle cues found')
    return result
