"""Publication contract: GitHub Pages serves only docs/, not sibling source paths."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

class DirectedPublicationTests(unittest.TestCase):
    def test_module_dependencies_stay_inside_docs(self):
        pending = [DOCS / 'directed-search.html']
        seen = set()
        while pending:
            file = pending.pop().resolve()
            if file in seen:
                continue
            self.assertTrue(file.is_relative_to(DOCS.resolve()), str(file))
            self.assertTrue(file.is_file(), str(file))
            seen.add(file)
            for rel in re.findall(r"from\s+['\"]([^'\"]+\.mjs)['\"]", file.read_text(encoding='utf-8')):
                self.assertTrue(rel.startswith('.'), rel)
                pending.append(file.parent / rel)
        self.assertGreaterEqual(len(seen), 4)

    def test_published_runtime_matches_skill(self):
        for name in ('motion.mjs', 'editorial.mjs', 'partition-search.mjs'):
            self.assertEqual((DOCS/'directed-runtime'/name).read_bytes(),
                             (ROOT/'technical-animation/runtime'/name).read_bytes())

if __name__ == '__main__':
    unittest.main()
