"""Synthetic rig/causality fixtures. No image model, real art approval or weak-model claim."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m
import topic_output as out
import perform_core as pc
from test_topic_outputs import fixture


def performance_fixture(root, kit=0):
    d=fixture(root);d.update(width=960,height=540,fps=30,duration=12,poster_frame=330)
    # Everything below is a regression fixture, never a production art receipt.
    d['layers']=[]; d['assets']=[]; d['concept']['entities']=[]
    names=['vessel','token','copy','door','front','probe']
    for name in names:
        d['concept']['entities'].append(dict(id=name,meaning='regression geometry',subject='SYNTHETIC '+name,
           operation='store/retrieve',consequence='test deterministic contact',invariant='same logical identity'))
    for i,name in enumerate(['empty','full','checking','pass','fail','token','copy','door','front','probe']):
        entity='vessel' if name in ('empty','full','checking','pass','fail') else name
        image=Image.new('RGBA',(320,320),(0,0,0,0));p=ImageDraw.Draw(image)
        if name=='front':
            p.rectangle((8,190,312,235),fill=(90,40+kit*20,110,255));p.rectangle((8,190,30,308),fill=(90,80,110,255))
        elif name=='door':
            p.rounded_rectangle((15,30,306,200),20,fill=(160+kit*10,115,80,255),outline=(35,40,70,255),width=9)
            p.ellipse((150,95,180,125),fill=(240,230,170,255))
        elif name=='probe':
            p.ellipse((25,25,295,295),fill=(40,130,170,255));p.ellipse((65,65,255,255),fill=(200,230,170,255))
        else:
            p.rounded_rectangle((8,8,312,312),30+kit*20,fill=(50+30*kit,80+i*11,120,255),outline=(30,30,40,255),width=8)
            p.polygon([(40,245),(160,45+kit*20),(285,245)],fill=(210,110+i*9,80,255))
            if name=='full':p.ellipse((150,175,240,265),fill=(255,230,40,255))
        f=root/(name+'.png');image.save(f)
        d['assets'].append(dict(id=name,entity=entity,path=f.name,sha256=m.sha(f),role='subject' if entity=='vessel' else 'prop',
             generation=dict(project_id=d['project_id'],tool='synthetic-unit-test',model='NOT A MODEL',run_reference='regression-only',prompt='Synthetic geometry '+name)))
    common={'start':0,'end':360}
    d['layers']=[dict(id='vessel-body',asset='empty',box=[.40,.24,.54,.65],**common),
       dict(id='token-body',asset='token',box=[.07,.31,.24,.30],**common),
       dict(id='copy-body',asset='copy',box=[.07,.31,.24,.30],opacity=0,**common),
       dict(id='vessel-door',asset='door',box=[.40,.24,.54,.65],**common),
       dict(id='vessel-front',asset='front',box=[.40,.24,.54,.65],**common),
       dict(id='vessel-probe',asset='probe',box=[.55,.35,.20,.25],opacity=0,**common)]
    entry=[[.15,.60],[.50,.17],[.85,.67]][kit]
    d['performance']={'version':1,'rigs':[
      dict(id='vessel',layer='vessel-body',artboard=[320,320],anchors={'entry':entry,'inside':[.60,.65],'output':entry},
         states={'empty':'empty','full':'full','checking':'checking','pass':'pass','fail':'fail'},initial_state='empty',
         gate={'layer':'vessel-door','pivot':[.1,.65],'open_degrees':-35},front='vessel-front',probe='vessel-probe'),
      dict(id='token',layer='token-body',artboard=[320,320],anchors={'contact':[.5,.5]}),
      dict(id='copy',layer='copy-body',artboard=[320,320],anchors={'contact':[.5,.5]})],
      'cues':[], 'actions':[
       dict(id='save',kind='store',object='token',target='vessel',duration=4,caption='Store a token.',consequence='The token enters; the vessel becomes occupied.'),
       dict(id='recall',kind='retrieve',object='copy',target='vessel',derived_from='token',after=['save'],duration=4,
            caption='Retrieve a copy.',consequence='A matching copy exits while the stored item remains.') ]}
    if kit==1:d['performance']['rigs'][0]['gate']={'layer':'vessel-door','open_offset':[0,-.18]}
    if kit==2:d['performance']['rigs'][0]['gate']={'layer':'vessel-door','open_offset':[.28,0]}
    return d

class PerformanceTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.d=performance_fixture(self.root)
    def tearDown(self): self.t.cleanup()
    def scene(self,d=None): return pc.compile_performance(d or self.d)
    def test_resolves_five_supported_actions(self):
        self.assertEqual(set(pc.ACTIONS),{'store','retrieve','transfer','verify','replace'})
    def test_no_input_mutation(self):
        saved=copy.deepcopy(self.d);self.scene();self.assertEqual(saved,self.d)
    def test_validate_existing_pipeline(self): m.validate(self.d,self.root)
    def test_no_canned_art_in_compiler(self):
        a=self.scene();self.assertEqual(a['assets'],self.d['assets'])
    def test_store_switches_at_commit_not_contact(self):
        s=self.scene();e=s['compiled_actions'][0]
        self.assertEqual(pc.semantic_state(s,e['commit']-1)['states']['vessel'],'empty')
        self.assertEqual(pc.semantic_state(s,e['commit'])['states']['vessel'],'full')
    def test_retrieval_preserves_original(self):
        s=self.scene();state=pc.semantic_state(s,359)
        self.assertEqual(state['contents']['vessel'],'token');self.assertEqual(state['copies']['copy'],'token')
    def test_contact_anchor_exact_for_three_shapes(self):
        for kit in range(3):
            d=performance_fixture(self.root,kit);s=pc.compile_performance(d);e=s['compiled_actions'][0]
            obj=next(l for l in s['layers'] if l['id']=='token-body');p=m.layer_state(obj,e['contact'],s)
            target=pc.port(s,'vessel','entry',e['contact']);self.assertAlmostEqual(p['x'],target[0],places=6);self.assertAlmostEqual(p['y'],target[1],places=6)
    def test_missing_port_blocks(self):
        del self.d['performance']['rigs'][0]['anchors']['entry']
        with self.assertRaisesRegex(m.Problem,'E_PORT'):self.scene()
    def test_missing_gate_blocks_store(self):
        del self.d['performance']['rigs'][0]['gate']
        with self.assertRaisesRegex(m.Problem,'E_RIG_PART'):self.scene()
    def test_missing_front_mask_blocks(self):
        del self.d['performance']['rigs'][0]['front']
        with self.assertRaisesRegex(m.Problem,'E_RIG_PART'):self.scene()
    def test_invalid_initial_occupancy(self):
        self.d['performance']['actions']=self.d['performance']['actions'][1:];self.d['performance']['actions'][0].pop('after')
        with self.assertRaisesRegex(m.Problem,'E_CAUSAL_STATE'):self.scene()
    def test_wrong_copy_identity(self):
        self.d['performance']['actions'][1]['derived_from']='unrelated'
        with self.assertRaisesRegex(m.Problem,'E_CAUSAL_STATE'):self.scene()
    def test_states_same_asset_rejected(self):
        self.d['performance']['rigs'][0]['states']['full']='empty'
        with self.assertRaisesRegex(m.Problem,'E_STATE_ART'):self.scene()
    def test_unknown_operation_rejected(self):
        self.d['performance']['actions'][0]['kind']='wiggle'
        with self.assertRaisesRegex(m.Problem,'E_OPERATION'):self.scene()
    def test_future_dependency_rejected(self):
        self.d['performance']['actions'][0]['after']=['recall']
        with self.assertRaisesRegex(m.Problem,'E_DEPENDENCY'):self.scene()
    def test_timing_too_short_blocks(self):
        self.d['performance']['actions'][0]['duration']=.15
        with self.assertRaisesRegex(m.Problem,'E_PACING'):self.scene()
    def test_cue_resizes_local_action_without_global_speedup(self):
        p=self.d['performance'];p['cues']=[dict(id='line1',start=1,end=6,text='store')];p['actions'][0]['cue']='line1'
        s=self.scene();self.assertEqual((s['compiled_actions'][0]['start'],s['compiled_actions'][0]['end']),(30,180))
        self.assertEqual(s['compiled_actions'][1]['start'],180);self.assertEqual(s['compiled_actions'][1]['end'],300)
    def test_overlapping_fixed_cues_block(self):
        p=self.d['performance'];p['cues']=[dict(id='line1',start=1,end=5),dict(id='line2',start=3,end=8)]
        p['actions'][0]['cue']='line1';p['actions'][1]['cue']='line2'
        with self.assertRaisesRegex(m.Problem,'E_CUE_CONFLICT'):self.scene()
    def test_unknown_cue_blocks(self):
        self.d['performance']['actions'][0]['cue']='unknown'
        with self.assertRaisesRegex(m.Problem,'E_CUE'):self.scene()
    def test_overrun_does_not_truncate(self):
        self.d['performance']['actions'][1]['duration']=12
        with self.assertRaisesRegex(m.Problem,'E_PACING'):self.scene()
    def test_manual_conflicting_tracks_rejected(self):
        self.d['layers'][1]['keys']=[{'frame':0,'slot':'left'},{'frame':80,'slot':'right'}]
        with self.assertRaisesRegex(m.Problem,'E_TRACK_CONFLICT'):self.scene()
    def test_registration_mismatch_blocks(self):
        self.d['performance']['rigs'][0]['artboard']=[800,800]
        with self.assertRaisesRegex(m.Problem,'E_REGISTRATION'):m.validate(self.d,self.root)
    def test_generated_identity_preserved_in_variants(self):
        self.d['assets'][1]['entity']='copy'
        with self.assertRaisesRegex(m.Problem,'E_STATE_ART'):self.scene()
    def test_occluder_renders_after_object(self):
        s=self.scene();ids=[l['id'] for l in s['layers']]
        self.assertGreater(ids.index('vessel-front'),ids.index('token-body'))
    def test_svg_contains_independent_variants(self):
        xml=out.svg(self.d,self.root,110)
        self.assertIn('data-variant="full"',xml);self.assertIn('data-variant="empty"',xml)
    def test_end_is_static_and_seek_deterministic(self):
        s=self.scene();a=pc.semantic_state(s,300);pc.semantic_state(s,12);self.assertEqual(a,pc.semantic_state(s,300))
        self.assertTrue(a['stopped'])
    def test_verify_displays_checking_then_result(self):
        p=self.d['performance'];p['actions']=[dict(id='check',kind='verify',object='token',target='vessel',result='fail',duration=4,caption='Verify first.',consequence='The test reports failure, not repair.')]
        s=self.scene();e=s['compiled_actions'][0]
        self.assertEqual(pc.semantic_state(s,e['contact']+1)['states']['vessel'],'checking')
        self.assertEqual(pc.semantic_state(s,e['commit'])['states']['vessel'],'fail')
    def test_replace_requires_different_states(self):
        self.d['performance']['actions']=[dict(id='edit',kind='replace',object='token',target='vessel',state='empty',duration=4,caption='Change.',consequence='A different artifact is required.')]
        with self.assertRaisesRegex(m.Problem,'E_STATE_CHANGE'):self.scene()
    def test_transfer_arrives_before_commit(self):
        self.d['performance']['actions']=[dict(id='send',kind='transfer',object='token',target='vessel',duration=4,caption='Transfer.',consequence='The packet reaches the receiver.')]
        e=self.scene()['compiled_actions'][0];self.assertLess(e['contact'],e['commit'])
    def test_explicit_state_change_on_replace(self):
        self.d['performance']['actions']=[dict(id='edit',kind='replace',object='token',target='vessel',state='full',duration=4,caption='Change.',consequence='Replacement artwork becomes visible after delivery.')]
        s=self.scene();e=s['compiled_actions'][0]
        self.assertEqual(pc.semantic_state(s,e['commit'])['states']['vessel'],'full')
    def test_unknown_rig_fields_block(self):
        self.d['performance']['rigs'][0]['script']='whatever'
        with self.assertRaisesRegex(m.Problem,'E_FIELD'):self.scene()

    def test_bad_model_field_types_return_structured_errors(self):
        edits=[('kind',['store']),('object',['token']),('cue',['line1'])]
        for field,value in edits:
            d=copy.deepcopy(self.d);d['performance']['actions'][0][field]=value
            with self.assertRaises(m.Problem):pc.compile_performance(d)
        d=copy.deepcopy(self.d);d['performance']['rigs'][0]['states']['full']=['full']
        with self.assertRaises(m.Problem):pc.compile_performance(d)
    def test_sliding_gate_translates_without_hinge_rotation(self):
        self.d['performance']['rigs'][0]['gate']={'layer':'vessel-door','open_offset':[0,-.18]}
        s=self.scene();gate=next(l for l in s['layers'] if l['id']=='vessel-door')
        a=m.layer_state(gate,0,s);b=m.layer_state(gate,30,s)
        self.assertEqual(a['rotate'],b['rotate']);self.assertLess(b['y'],a['y']-20)
        m.validate(self.d,self.root)
    def test_all_actions_work_through_public_validation(self):
        for kind in ('store','transfer','verify','replace'):
            d=copy.deepcopy(self.d)
            a=dict(id='operation',kind=kind,object='token',target='vessel',duration=4,caption='Operation test.',consequence='A visible state change follows the operation.')
            if kind=='verify':a['result']='pass'
            if kind=='replace':a['state']='full'
            d['performance']['actions']=[a]
            m.validate(d,self.root)
    def test_open_gate_cannot_be_clipped_outside_frame(self):
        self.d['performance']['rigs'][0]['gate'].update(pivot=[.1,.1],open_degrees=-60)
        with self.assertRaisesRegex(m.Problem,'E_STAGE_BOUNDS'):m.validate(self.d,self.root)
    def test_off_center_contact_is_aligned(self):
        self.d['performance']['rigs'][1]['anchors']['contact']=[.2,.7]
        s=self.scene();e=s['compiled_actions'][0]
        self.assertEqual([round(x,6) for x in pc.port(s,'token','contact',e['contact'])],
                         [round(x,6) for x in pc.port(s,'vessel','entry',e['contact'])])

if __name__=='__main__':unittest.main()
