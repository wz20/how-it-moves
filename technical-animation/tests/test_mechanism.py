"""Contract/mutation tests. Images are synthetic fixtures, not image-generation evidence."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m
import mechanism_core as mc
import action_requirements as ar
from test_performance import performance_fixture
from test_topic_outputs import fixture


def mechanism_fixture(root, kit=0):
    return with_mechanism(performance_fixture(root,kit))

def with_mechanism(d):
    d=copy.deepcopy(d)
    d['presentation']='animated'
    d['mechanism']={
      'version':1, 'kind':'discrete',
      'variables':{
        'occupancy':{'type':'enum','values':['empty','full'],'initial':'empty','binding':{'rig':'vessel','channel':'state'}},
        'stored':{'type':'set','values':['token'],'initial':[],'binding':{'rig':'vessel','channel':'contents'}},
        'copy_origin':{'type':'enum','values':[None,'token'],'initial':None,'binding':{'rig':'copy','channel':'copy'}}},
      'events':[
        {'id':'save','action':'save','after':[],'requires':[{'ref':'occupancy','op':'eq','value':'empty'}],
         'effects':[{'ref':'occupancy','op':'set','value':'full'},{'ref':'stored','op':'add','value':'token'}],
         'observation':'See the same token enter; the interior changes from empty to full.'},
        {'id':'recall','action':'recall','after':['save.commit'],
         'requires':[{'ref':'stored','op':'contains','value':'token'}],
         'effects':[{'ref':'copy_origin','op':'set','value':'token'}],
         'observation':'Watch a distinct copy emerge; the original remains stored.'}],
      'invariants':[]}
    return d

class MechanismTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.d=mechanism_fixture(self.root)
    def tearDown(self):self.t.cleanup()
    def test_preflight_without_assets(self):
        self.d['assets']=[];self.d['layers']=[];self.d['performance']['rigs']=[]
        p=mc.plan(self.d);self.assertEqual(p['final']['stored'],['token'])
    def test_original_not_mutated(self):
        old=copy.deepcopy(self.d);mc.resolve(self.d);self.assertEqual(old,self.d)
    def test_real_compiler_agrees(self):
        s=mc.resolve(self.d);self.assertEqual(s['mechanism_trace'][-1]['after']['copy_origin'],'token')
    def test_dependencies_are_milestones(self):
        s=mc.resolve(self.d);a,b=s['mechanism_trace'];self.assertGreaterEqual(b['start'],a['commit'])
    def test_forward_dependency_rejected(self):
        self.d['mechanism']['events'][0]['after']=['recall.commit']
        with self.assertRaisesRegex(m.Problem,'E_EVENT_DEPENDENCY'):mc.plan(self.d)
    def test_unknown_milestone_rejected(self):
        self.d['mechanism']['events'][1]['after']=['save.wiggle']
        with self.assertRaisesRegex(m.Problem,'E_EVENT_DEPENDENCY'):mc.plan(self.d)
    def test_false_precondition_rejected(self):
        self.d['mechanism']['events'][0]['requires'][0]['value']='full'
        with self.assertRaisesRegex(m.Problem,'E_PRECONDITION'):mc.plan(self.d)
    def test_unbound_effect_rejected(self):
        self.d['mechanism']['variables']['stored'].pop('binding')
        with self.assertRaisesRegex(m.Problem,'E_BINDING'):mc.plan(self.d)
    def test_unknown_variable_rejected(self):
        self.d['mechanism']['events'][0]['effects'][0]['ref']='unknown'
        with self.assertRaisesRegex(m.Problem,'E_VARIABLE'):mc.plan(self.d)
    def test_state_type_enforced(self):
        self.d['mechanism']['events'][0]['effects'][0]['value']=17
        with self.assertRaisesRegex(m.Problem,'E_STATE_TYPE'):mc.plan(self.d)
    def test_unsupported_expression_rejected(self):
        self.d['mechanism']['events'][0]['requires'][0]['op']='eval'
        with self.assertRaisesRegex(m.Problem,'E_PREDICATE'):mc.plan(self.d)
    def test_false_effect_not_just_prose(self):
        self.d['mechanism']['variables']['occupancy']['values'].append('broken')
        self.d['mechanism']['events'][0]['effects'][0]['value']='broken'
        with self.assertRaisesRegex(m.Problem,'E_MECHANISM_DIVERGENCE'):mc.resolve(self.d)
    def test_same_effect_not_mechanism(self):
        self.d['mechanism']['events'][0]['effects'][0]['value']='empty'
        with self.assertRaisesRegex(m.Problem,'E_NO_CHANGE'):mc.plan(self.d)
    def test_invariant_checked(self):
        self.d['mechanism']['invariants']=[{'ref':'occupancy','op':'eq','value':'empty'}]
        with self.assertRaisesRegex(m.Problem,'E_INVARIANT'):mc.plan(self.d)
    def test_undeclared_action_rejected(self):
        self.d['mechanism']['events'].pop()
        with self.assertRaisesRegex(m.Problem,'E_EVENT_COVERAGE'):mc.plan(self.d)
    def test_conditional_branch_skips_choreography(self):
        self.d['mechanism']['variables']['should_recall']={'type':'bool','initial':False}
        self.d['mechanism']['events'][1]['when']=[{'ref':'should_recall','op':'eq','value':True}]
        s=mc.resolve(self.d);self.assertEqual(len(s['compiled_actions']),1)
        self.assertEqual(s['mechanism_skipped'],['recall'])
    def test_dependency_on_skipped_event_blocks(self):
        self.d['mechanism']['variables']['save_allowed']={'type':'bool','initial':False}
        self.d['mechanism']['events'][0]['when']=[{'ref':'save_allowed','op':'eq','value':True}]
        with self.assertRaisesRegex(m.Problem,'E_EVENT_DEPENDENCY'):mc.plan(self.d)
    def test_no_geometry_only_final(self):
        d=fixture(self.root)
        with self.assertRaisesRegex(m.Problem,'E_MECHANISM_REQUIRED'):mc.production_gate(d)
    def test_svg_not_required_to_move(self):
        d=fixture(self.root);d['formats']=['svg'];d['presentation']='static'
        d['mechanism']={'version':1,'kind':'static','relations':[{'from':'source','to':'tool','relation':'inspection','observation':'The lens faces the actual object surface.'}]}
        mc.production_gate(d)
    def test_interaction_is_not_playback(self):
        self.d['presentation']='interactive'
        with self.assertRaisesRegex(m.Problem,'E_INTERACTION_ADAPTER'):mc.production_gate(self.d)
    def test_fps_does_not_change_terminal_state(self):
        x=mc.resolve(self.d);self.d['fps']=60
        for l in self.d['layers']:l['end']=720
        y=mc.resolve(self.d);self.assertEqual(x['mechanism_trace'][-1]['after'],y['mechanism_trace'][-1]['after'])
    def test_requirements_without_rigs(self):
        self.d['performance']['rigs']=[];self.d['assets']=[];self.d['layers']=[]
        p=ar.derive(self.d);v=p['objects']['vessel']
        self.assertIn('front',v['parts']);self.assertIn('inside',v['ports']);self.assertEqual(set(v['events']),{'save','recall'})
    def test_not_every_object_has_a_gate(self):
        p=ar.derive(self.d);self.assertNotIn('gate',p['objects']['token']['parts'])
    def test_asset_plan_has_no_guessed_coordinates(self):
        p=ar.derive(self.d);self.assertNotIn('pivot',p['objects']['vessel']);self.assertIn('measurement',p)
    def test_motion_specific_generation_brief(self):
        t=m.prompts(self.d);self.assertIn('Required by event',t);self.assertIn('front',t)
    def test_positive_and_negative_fixture_gate(self):mc.production_gate(self.d)

if __name__=='__main__':unittest.main()
