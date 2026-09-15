"""No providers invoked. Test local audio, rig registration and targeted repair utilities."""
import copy, json, math, struct, sys, tempfile, unittest, wave
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m
import soundtrack
import asset_pack
import repair_plan
from test_mechanism import mechanism_fixture as performance_fixture


def tone(root,seconds=2):
    p=root/'tone.wav'
    with wave.open(str(p),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000)
        w.writeframes(b''.join(struct.pack('<h',round(2400*math.sin(2*math.pi*440*t/16000))) for t in range(round(seconds*16000))))
    return p

class ProductionToolsTests(unittest.TestCase):
    def setUp(self):self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.d=performance_fixture(self.root)
    def tearDown(self):self.t.cleanup()
    def audio(self):
        p=tone(self.root)
        self.d['soundtrack']=[dict(role='narration',path=p.name,sha256=m.sha(p),start=1,trim_in=0,trim_out=2,gain=.8)]
    def test_audio_optional(self):self.assertEqual(soundtrack.validate(self.d,self.root),[])
    def test_real_local_audio_metadata(self):
        self.audio();meta=soundtrack.validate(self.d,self.root);self.assertEqual(len(meta),1);self.assertAlmostEqual(meta[0]['duration'],2)
    def test_audio_hash_changes_block(self):
        self.audio();self.d['soundtrack'][0]['sha256']='0'*64
        with self.assertRaisesRegex(m.Problem,'E_AUDIO_HASH'):soundtrack.validate(self.d,self.root)
    def test_audio_outside_project_blocks(self):
        self.audio();self.d['soundtrack'][0]['path']='../tone.wav'
        with self.assertRaisesRegex(m.Problem,'E_PATH'):soundtrack.validate(self.d,self.root)
    def test_audio_overrun_not_silently_trimmed(self):
        self.audio();self.d['soundtrack'][0]['start']=11
        with self.assertRaisesRegex(m.Problem,'E_AUDIO_RANGE'):soundtrack.validate(self.d,self.root)
    def test_audio_source_trim_outside_file_rejected(self):
        self.audio();self.d['soundtrack'][0]['trim_out']=3
        with self.assertRaisesRegex(m.Problem,'E_AUDIO_RANGE'):soundtrack.validate(self.d,self.root)
    def test_svg_only_does_not_silently_discard_audio(self):
        self.audio();self.d['formats']=['svg']
        with self.assertRaisesRegex(m.Problem,'E_AUDIO_FORMAT'):soundtrack.validate(self.d,self.root)
    def test_excessive_combined_gain_blocks(self):
        self.audio();s=copy.deepcopy(self.d['soundtrack'][0]);s['role']='music';self.d['soundtrack'].append(s)
        with self.assertRaisesRegex(m.Problem,'E_AUDIO_GAIN'):soundtrack.validate(self.d,self.root)
    def test_parse_srt_preserves_timestamps(self):
        s='1\n00:00:01,200 --> 00:00:03,600\n收到反馈\n再决策\n\n2\n00:00:04,000 --> 00:00:06,000\n重新验证\n'
        cues=soundtrack.parse_srt(s);self.assertEqual(cues[0]['start'],1.2);self.assertEqual(cues[0]['text'],'收到反馈 再决策')
    def test_parse_srt_bad_times_reject(self):
        with self.assertRaisesRegex(m.Problem,'E_CUE'):soundtrack.parse_srt('1\n00:00:08,000 --> 00:00:01,000\nx')
    def test_registered_normalization_keeps_shared_transform(self):
        report=asset_pack.normalize([self.root/'empty.png',self.root/'door.png',self.root/'front.png'],self.root/'normalized',512)
        self.assertEqual(report['canvas'],[512,512]);self.assertEqual(len(report['files']),3)
        for f in report['files']:
            with Image.open(self.root/'normalized'/f['name']) as im:self.assertEqual(list(im.size),[512,512])
        self.assertEqual(report['status'],'processed-not-generated')
    def test_independent_crops_not_guessed_into_alignment(self):
        Image.new('RGBA',(400,320),(100,20,40,255)).save(self.root/'bad.png')
        with self.assertRaisesRegex(m.Problem,'E_REGISTRATION'):asset_pack.normalize([self.root/'empty.png',self.root/'bad.png'],self.root/'n',512)
    def test_normalize_never_overwrites(self):
        dest=self.root/'n';dest.mkdir()
        with self.assertRaisesRegex(m.Problem,'E_EXISTS'):asset_pack.normalize([self.root/'empty.png'],dest,512)
    def test_repair_targets_missing_mask_not_entire_project(self):
        del self.d['performance']['rigs'][0]['front']
        report=repair_plan.diagnose(self.d,self.root)
        self.assertEqual(report['status'],'blocked');self.assertEqual(report['issues'][0]['stage'],'asset-rig')
        self.assertIn('front',report['issues'][0]['message']);self.assertFalse(report['auto_approved'])
    def test_good_source_is_not_visual_approval(self):
        report=repair_plan.diagnose(self.d,self.root);self.assertEqual(report['status'],'awaiting-visual-review');self.assertFalse(report['auto_approved'])
    def test_runtime_fingerprint_changes_after_audio_mutation(self):
        import topic_output as out
        self.audio();a=out.fingerprint(self.d,self.root);self.d['soundtrack'][0]['start']=2
        self.assertNotEqual(a,out.fingerprint(self.d,self.root))

if __name__=='__main__':unittest.main()
