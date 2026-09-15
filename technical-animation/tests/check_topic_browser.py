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
    r['quality_layers']={k:'approved' for k in ('technical','event','visual')}
    for e in r.get('events',[]):
        e['verdict']='approved';e['transition_inspected']=True
        e['findings']={k:'Synthetic integration harness only; actual production requires visual inspection.' for k in e['findings']}
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
        # Compatibility preserves draft geometry, NOT a final-delivery bypass.
        try:out.prepare_review(data,root,root/'review')
        except m.Problem as e:assert e.code=='E_MECHANISM_REQUIRED'
        else:raise AssertionError('legacy geometry accepted as current production review')
        checked.append('legacy draft playback does not qualify as mechanism production')
        try:out.export(data,root,root/'final',['html'],root/'fake-review.json')
        except m.Problem as e:assert e.code=='E_MECHANISM_REQUIRED'
        else:raise AssertionError('legacy geometry bypassed final mechanism gate')
        checked.append('legacy geometry cannot bypass new final export even with a review filename')
    return checked

if __name__=='__main__':
    checks=run();print(json.dumps({'passed':len(checks),'checks':checks,'assets':'SYNTHETIC TEST ONLY','art_review':'not performed'},indent=2))
