#!/usr/bin/env python3
"""Integration with SYNTHETIC images only; not an artwork-quality evaluation."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from test_topic_outputs import fixture
import topic_model as m
import topic_output as out


def approve_fixture(path):
    # Deliberately explicit unit-test fixture, NEVER a production approval command.
    r=json.loads(path.read_text());r['verdict']='approved';r['method']='vision-agent';r['reviewer']='SYNTHETIC TEST HARNESS — NOT ART REVIEW'
    for s in r['shots']:
        s['verdict']='approved'
        for k in s['findings']:s['findings'][k]='Synthetic integration fixture assertion only; no artwork quality is claimed.'
    path.write_text(json.dumps(r))


def run():
    checked=[]
    with tempfile.TemporaryDirectory(prefix='how-it-moves-synthetic-') as tmp:
        root=Path(tmp);data=fixture(root);m.validate(data,root)
        pw,b=out.browser()
        try:
            page=b.new_page(viewport={'width':1920,'height':1180});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(out.html(data,root));page.wait_for_function('window.ready===true')
            for frame in (0,11,29,59,20,45,0):
                state=page.evaluate('(f)=>window.renderFrame(f)',frame)
                for layer in data['layers']:
                    expected=m.layer_state(layer,frame,data)
                    for k in ('x','y','rotate','scale','opacity'):
                        assert abs(state['layers'][layer['id']][k]-expected[k])<1e-7,(frame,k)
            checked.append('Python / browser interpolation parity at 7 frames')
            page.evaluate('window.renderFrame(10)');first=page.locator('#stage').screenshot()
            page.evaluate('window.renderFrame(58)');page.evaluate('window.renderFrame(10)')
            assert first==page.locator('#stage').screenshot();checked.append('random-seek identical pixels')
            page.evaluate('window.renderFrame(0)');page.click('#toggle');page.wait_for_timeout(150)
            assert page.evaluate('window.semanticState.frame')>0
            page.click('#toggle');f=page.evaluate('window.semanticState.frame');page.wait_for_timeout(100)
            assert f==page.evaluate('window.semanticState.frame');checked.append('play / pause')
            page.locator('#seek').evaluate('(e)=>{e.value=40;e.dispatchEvent(new Event("input"))}')
            assert page.evaluate('window.semanticState.frame')==40;checked.append('seek slider')
            assert not errors;checked.append('zero browser errors')
        finally:b.close();pw.stop()
        rp=out.prepare_review(data,root,root/'review')
        assert json.loads(rp.read_text())['verdict']=='pending';checked.append('review never auto-approves')
        approve_fixture(rp)
        # Route checks: unrequested formats must not be generated.
        for selected in (['svg'],['html'],['video'],['html','video','svg']):
            dest=root/('-'.join(selected))
            report=out.export(data,root,dest,selected,rp)
            expected={'html':'animation.html','svg':'illustration.svg','video':'video.mp4'}
            assert set(report['files'])=={expected[s] for s in selected}
            assert set(p.name for p in dest.iterdir())==set(report['files'])|{'delivery.json','asset-history-entry.json'}
            if 'video' in selected:
                v=report['video'];assert v['streams'][0]['nb_read_frames']=='60';assert len(v['streams'])==1
            checked.append('export only '+','.join(selected))
        changed=json.loads(json.dumps(data));changed['style']+=' Changed.'
        try:out.export(changed,root,root/'stale',['svg'],rp)
        except m.Problem as e:assert e.code=='E_REVIEW_STALE'
        else:raise AssertionError('stale approval accepted')
        checked.append('source changes invalidate review')
        # No review can be re-used with altered capture bytes.
        r=json.loads(rp.read_text());(root/r['evidence'][0]['path']).write_bytes(b'changed')
        try:out.export(data,root,root/'altered',['html'],rp)
        except m.Problem:pass
        else:raise AssertionError('edited evidence accepted')
        checked.append('evidence tampering blocks export')
    return checked

if __name__=='__main__':
    checks=run();print(json.dumps({'passed':len(checks),'checks':checks,'assets':'SYNTHETIC TEST ONLY','art_review':'not performed'},indent=2))
