#!/usr/bin/env python3
"""Real browser/media checks with three synthetic rigs; not a visual-quality or model benchmark."""
from __future__ import annotations
import argparse, json, math, struct, subprocess, sys, tempfile, wave
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m, topic_output as out, perform_core as pc
from test_mechanism import mechanism_fixture as performance_fixture
from test_production_tools import tone
from check_topic_browser import approve_fixture


def run(destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True);checks=[];snapshots=[]
    with tempfile.TemporaryDirectory(prefix='performance-test-') as tmp:
        root=Path(tmp);pw,b=out.browser()
        try:
            for kit in range(3):
                folder=root/str(kit);folder.mkdir();d=performance_fixture(folder,kit);scene=pc.compile_performance(d)
                m.validate(d,folder)
                page=b.new_page(viewport={'width':960,'height':640},device_scale_factor=1);errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(out.html(d,folder));page.wait_for_function('window.ready===true')
                indices=list(range(0,360,3))+[359]
                js=page.evaluate('(fs)=>fs.map(f=>window.renderFrame(f))',indices)
                for frame,state in zip(indices,js):
                    selfstate=pc.semantic_state(scene,frame);assert state['performance']==selfstate,(kit,frame,state['performance'],selfstate)
                    for layer in scene['layers']:
                        expect=m.layer_state(layer,frame,scene)
                        actual=state['layers'][layer['id']]
                        for key in ('x','y','scale','rotate','opacity','pivot_x','pivot_y'):assert abs(expect[key]-actual[key])<1e-7,(kit,frame,key,expect[key],actual[key])
                        assert expect['asset']==actual.get('asset')
                checks.append(f'kit {kit}: 121 frames Python/JS poses, pivots, variants and causal state agree')
                for frame in [0,20,38,62,81,119,151,187,220,359]:
                    page.evaluate('(f)=>window.renderFrame(f)',frame);path=destination/f'kit{kit}-{frame:03d}.png';page.locator('#stage').screenshot(path=str(path));snapshots.append(path.name)
                frame=62;page.evaluate('(f)=>window.renderFrame(f)',frame);a=page.locator('#stage').screenshot()
                page.evaluate("document.getElementById('vessel-front').style.display='none'");without=page.locator('#stage').screenshot()
                assert a!=without,'registered front layer did not affect pixels'
                page.evaluate("document.getElementById('vessel-front').style.display=''")
                page.evaluate('window.renderFrame(359)');page.evaluate('(f)=>window.renderFrame(f)',frame)
                assert a==page.locator('#stage').screenshot();checks.append(f'kit {kit}: visible foreground mask and history-independent pixels')
                page.evaluate('window.renderFrame(0)');page.click('#toggle');page.wait_for_timeout(200);assert page.evaluate('window.semanticState.frame')>0
                page.click('#toggle');stopped=page.evaluate('window.semanticState.frame');page.wait_for_timeout(150);assert stopped==page.evaluate('window.semanticState.frame')
                page.locator('#seek').evaluate('(e)=>{e.value=62;e.dispatchEvent(new Event("input"))}');assert page.evaluate('window.semanticState.frame')==62
                assert not errors;checks.append(f'kit {kit}: playback, pause, seek, zero browser errors')
                page.close()
            # Local audio playback uses the same explicit trim and offset as the video export.
            folder=root/'audio';folder.mkdir();d=performance_fixture(folder)
            d['performance']['cues']=[dict(id='line1',start=1,end=5,text='Store then preserve the source.')];d['performance']['actions'][0]['cue']='line1'
            tonepath=tone(folder);d['soundtrack']=[dict(role='narration',path=tonepath.name,sha256=m.sha(tonepath),start=1,trim_in=0,trim_out=2,gain=.8)]
            page=b.new_page(viewport={'width':960,'height':640});page.set_content(out.html(d,folder));page.wait_for_function('window.ready===true')
            page.evaluate('window.renderFrame(29)');assert not page.evaluate('window.semanticState.performance.active.length')
            page.evaluate('window.renderFrame(30)');assert page.evaluate('window.semanticState.performance.active[0]')=='save'
            page.evaluate('window.renderFrame(45)');audio=page.evaluate('window.audioStatus');assert abs(audio[0]['time']-.5)<.03;assert audio[0]['paused']
            page.click('#toggle');page.wait_for_timeout(300);assert not page.evaluate('window.audioStatus[0].paused');assert not page.evaluate('window.audioError||null')
            page.click('#toggle');assert page.evaluate('window.audioStatus[0].paused');checks.append('embedded local audio seeks to trim+offset, plays and pauses with scene')
            page.close()
        finally:b.close();pw.stop()
        review=out.prepare_review(d,folder,folder/'review')
        r=json.loads(review.read_text());assert r['verdict']=='pending';assert 'audio_timing' in r['shots'][0]['findings'];checks.append('per-action/hold review is pending and includes audio timing + mix inspection')
        approve_fixture(review)  # explicitly labeled synthetic harness; not a user-facing approval command
        report=out.export(d,folder,folder/'delivery',['html','video','svg'],review)
        metadata=report['video'];vs=[s for s in metadata['streams'] if s['codec_type']=='video'];as_=[s for s in metadata['streams'] if s['codec_type']=='audio']
        assert len(vs)==len(as_)==1 and int(vs[0]['nb_read_frames'])==360
        checks.append('all three formats exported; MP4 has 360 frames and a real AAC track, complete decode passed')
        # Check that delayed audio is silent before t=1 and has a signal after t=1, not merely an empty track.
        pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(folder/'delivery/video.mp4'),'-map','0:a:0','-ac','1','-ar','16000','-f','s16le','-'])
        values=struct.unpack('<'+'h'*(len(pcm)//2),pcm)
        def rms(a,b):v=values[round(a*16000):round(b*16000)];return math.sqrt(sum(n*n for n in v)/len(v))
        assert rms(.15,.7)<30 and rms(1.25,2.5)>500 and rms(3.5,4.0)<30
        checks.append('decoded audio signal obeys the 1-second start and explicit 2-second source trim')
        # Static SVG and HTML share variant/pivot selection, not a whole-scene screenshot.
        svg=(folder/'delivery/illustration.svg').read_text();assert 'data-variant="full"' in svg and '<text' in svg and '<script' not in svg
        checks.append('SVG keeps independent raster state layers and editable vector text without scripts')
        changed=json.loads(json.dumps(d));changed['performance']['rigs'][0]['anchors']['entry'][0]=.17
        try:out.export(changed,folder,folder/'stale',['svg'],review)
        except m.Problem as e:assert e.code=='E_REVIEW_STALE'
        else:raise AssertionError('rig change did not invalidate visual approval')
        checks.append('changed rig ports invalidate all prior review evidence')
        # The media is a test fixture and remains in the verification folder, not a marketing demo.
        (destination/'synthetic-contract-test.mp4').write_bytes((folder/'delivery/video.mp4').read_bytes())
    return {'passed':len(checks),'checks':checks,'sampled_browser_frames':363,'screenshots':snapshots,
            'artwork':'SYNTHETIC REGRESSION FIXTURES ONLY','real_model_eval':'not run','art_quality_eval':'not performed','cross_engine_benchmark':'not run'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    report=run(args.out);(args.out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
