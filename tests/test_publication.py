"""No-network regression tests for publication guards."""
from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'scripts' / 'publish_github.py'

class PublicationTests(unittest.TestCase):
    def load(self):
        self.assertTrue(MODULE.exists(), 'Publication helper has not been implemented')
        spec = importlib.util.spec_from_file_location('publish_github', MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_valid_slug(self):
        m = self.load()
        self.assertEqual(m.validate_target('wz20', 'explain-motion'), 'wz20/explain-motion')

    def test_unsafe_slug_rejected(self):
        m = self.load()
        for owner, repo in [('..', 'x'), ('user', '../x'), ('--help', 'x'), ('user', 'a b'), ('user', 'a/b')]:
            with self.subTest(owner=owner, repo=repo), self.assertRaises(m.PublishError):
                m.validate_target(owner, repo)

    def test_public_consent_required(self):
        m = self.load()
        with self.assertRaises(m.PublishError):
            m.require_public(False)

    def test_identity_mismatch(self):
        m = self.load()
        with self.assertRaises(m.PublishError):
            m.check_identity({'login': 'someone-else', 'id': 1}, 'wz20')

    def test_noreply_email(self):
        m = self.load()
        self.assertEqual(m.check_identity({'login': 'wz20', 'id': 72806779}, 'wz20'),
                         '72806779+wz20@users.noreply.github.com')

    def test_existing_repo_not_overwritten(self):
        m = self.load()
        with self.assertRaises(m.PublishError):
            m.check_missing_repo(subprocess.CompletedProcess([], 0, '{"private":false}', ''))

    def test_only_explicit_404_means_missing(self):
        m = self.load()
        m.check_missing_repo(subprocess.CompletedProcess([], 1, '', 'gh: Not Found (HTTP 404)'))
        for error in ['HTTP 403 forbidden', 'network unavailable', 'HTTP 401']:
            with self.subTest(error=error), self.assertRaises(m.PublishError):
                m.check_missing_repo(subprocess.CompletedProcess([], 1, '', error))

    def test_secret_file_rejected(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.env').write_text('secret')
            with self.assertRaises(m.PublishError): m.scan_public_files(p)

    def test_font_file_rejected(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'font.woff2').write_bytes(b'font')
            with self.assertRaises(m.PublishError): m.scan_public_files(p)

    def test_symlink_rejected(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'escape').symlink_to('/tmp')
            with self.assertRaises(m.PublishError): m.scan_public_files(p)

    def test_source_tree_is_preserved(self):
        self.load()
        root=MODULE.parents[1]
        self.assertEqual((root/'docs/index.html').read_bytes(),
                         (root/'technical-animation/examples/agent-loop/preview.html').read_bytes())

if __name__ == '__main__': unittest.main()
