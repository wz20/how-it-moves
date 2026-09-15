#!/usr/bin/env python3
"""End-to-end tests using SYNTHETIC assets; never a production art/teaching benchmark."""
import argparse, copy, json, sys, tempfile, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m, topic_output as out, mechanism_core as mc, visual_evidence as ve
from test_mechanism import mechanism_fixture
from test_topic_outputs import fixture


def approve_synthetic_only(path):
    # Test-only helper. Production CLI never exposes auto-approval.
    d=json.loads(path.read_text());d['verdict']='approved';d['reviewer']='SYNTHETIC TEST HARNESS; NOT A HUMAN ART REVIEW';d['method']='vision-agent'
    for s in d['shots']:
        s['verdict']='approved'
        for k in s['findings']:s['findings'][k]='Synthetic regression approval solely to exercise mechanics; not client quality evidence.'
    d['quality_layers']={k:'approved' for k in ('technical','event','visual')}
    for e in d['events']:
        e['verdict']='approved';e['transition_inspected']=True
        e['findings']={k:'Synthetic integration harness; the actual production reviewer must inspect this event.' for k in e['findings']}
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2))


def run(dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True);checks=[]
    with tempfile.TemporaryDirectory(prefix='mechanism-test-') as tmp:
        root=Path(tmp);d=mechanism_fixture(root);scene=m.resolved(d)
        # Add explicit explanatory text and decoration to exercise actual ablation views.
        d['layers'].append(dict(id='explain',type='text',slot='title',text='TEST ONLY',size=32,purpose='narration'))
        d['layers'].append(dict(id='necessary',type='text',slot='subtitle',text='M1',size=28,purpose='label'))
        d['layers'].append(dict(id='decor',type='path',points=[[.05,.18],[.3,.18]],purpose='decoration'))
        pw,b=out.browser()
        try:
            for kit in (0,1,2):
                folder=root/str(kit);folder.mkdir();q=mechanism_fixture(folder,kit)
                page=b.new_page(viewport={'width':960,'height':660});page.set_content(out.html(q,folder,True));page.wait_for_function('window.ready===true')
                actual=out.ve.observe_page(page,m.resolved(q));assert actual
                print('CHECK',len(checks)+1,flush=True);checks.append(f'kit {kit}: real DOM image variants and pixel-contribution witnesses pass')
                page.close()
            page=b.new_page(viewport={'width':960,'height':660});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(out.html(d,root,True));page.wait_for_function('window.ready===true')
            e=m.resolved(d)['mechanism_trace'][0]
            page.evaluate('(f)=>window.renderFrame(f)',e['commit']);state=page.evaluate('window.semanticState.performance')
            full=page.locator('#stage').screenshot(path=str(dest/'synthetic-full.png'))
            page.evaluate('window.setReviewView("labels-only")')
            assert page.locator('#explain').get_attribute('opacity')=='0'
            assert page.locator('#necessary').get_attribute('opacity')=='1'
            assert state==page.evaluate('window.semanticState.performance')
            labels=page.locator('#stage').screenshot(path=str(dest/'synthetic-labels-only.png'));assert full!=labels
            page.evaluate('window.setReviewView("mechanism-only")')
            assert page.locator('#decor').get_attribute('opacity')=='0'
            assert state==page.evaluate('window.semanticState.performance')
            page.locator('#stage').screenshot(path=str(dest/'synthetic-mechanism-only.png'))
            print('CHECK',len(checks)+1,flush=True);checks.append('ablation removes explanatory text/decor, retains labels and mechanism states')
            page.evaluate('window.setReviewView("full")');page.evaluate('(f)=>window.renderFrame(f)',e['commit']);a=page.locator('#stage').screenshot()
            page.evaluate('window.renderFrame(0)');page.evaluate('(f)=>window.renderFrame(f)',e['commit']);assert a==page.locator('#stage').screenshot()
            print('CHECK',len(checks)+1,flush=True);checks.append('arbitrary seeking restores bit-identical actual pixels')
            page.evaluate('window.playEvent("save")');page.wait_for_timeout(180);assert page.evaluate('window.semanticState.frame')>0
            page.click('#toggle');f=page.evaluate('window.semanticState.frame');page.wait_for_timeout(140);assert f==page.evaluate('window.semanticState.frame')
            print('CHECK',len(checks)+1,flush=True);checks.append('event playback, pause and deterministic controls operate')
            # Hide the witness with real CSS: typed event state still passes, actual output fails.
            page.evaluate('document.getElementById("vessel-body").style.display="none"')
            try:ve.observe_page(page,m.resolved(d))
            except m.Problem as err:assert err.code=='E_VISUAL_OCCLUDED'
            else:raise AssertionError('hidden witness passed actual-pixel check')
            print('CHECK',len(checks)+1,flush=True);checks.append('state-correct but visually hidden outcome is rejected')
            assert not errors;page.close()
        finally:b.close();pw.stop()
        print('PREPARE REVIEW',flush=True)
        review=out.prepare_review(d,root,root/'review')
        r=json.loads(review.read_text());assert r['verdict']=='pending' and len(r['events'])==2 and r['ablation_evidence']
        print('CHECK',len(checks)+1,flush=True);checks.append('review creates pending three-layer/event/ablation evidence, not approval')
        try:out.export(d,root,root/'not-approved',['html'],review)
        except m.Problem as err:assert err.code=='E_REVIEW'
        else:raise AssertionError('pending review exported')
        print('CHECK',len(checks)+1,flush=True);checks.append('unreviewed final export fails closed')
        approve_synthetic_only(review)
        print('EXPORT ALL',flush=True)
        report=out.export(d,root,root/'delivery',['html','video','svg'],review)
        assert set(report['files'])=={'animation.html','video.mp4','illustration.svg'}
        assert report['video']['streams'][0]['nb_read_frames']=='360'
        print('CHECK',len(checks)+1,flush=True);checks.append('one reviewed source exports HTML, 360-frame MP4 and independent-layer SVG; full decode passes')
        changed=copy.deepcopy(d);changed['performance']['rigs'][0]['anchors']['entry'][0]=.16
        try:out.export(changed,root,root/'stale',['html'],review)
        except m.Problem as err:assert err.code=='E_REVIEW_STALE'
        else:raise AssertionError('changed source kept approval')
        print('CHECK',len(checks)+1,flush=True);checks.append('source/anchor mutation invalidates review and export')
        # Static SVG has an actual relation contract, not a motion quota.
        folder=root/'static';folder.mkdir();q=fixture(folder);q['formats']=['svg'];q['presentation']='static';q['layers'][0]['keys']=[]
        q['mechanism']={'version':1,'kind':'static','relations':[{'from':'source','to':'tool','relation':'inspects','observation':'The lens faces the vessel surface.'}]}
        rv=out.prepare_review(q,folder,folder/'review');approve_synthetic_only(rv)
        rp=out.export(q,folder,folder/'delivery',['svg'],rv);assert set(rp['files'])=={'illustration.svg'}
        print('CHECK',len(checks)+1,flush=True);checks.append('static SVG exports after relation/visual review without unnecessary motion')
        (dest/'synthetic-contract-test.mp4').write_bytes((root/'delivery/video.mp4').read_bytes())
    return {'passed':len(checks),'checks':checks,'asset_kind':'synthetic-test-only','visual_quality':'not_evaluated','learning_outcome':'not_tested','weak_model_benchmark':'not_run'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    report=run(args.out);(args.out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
