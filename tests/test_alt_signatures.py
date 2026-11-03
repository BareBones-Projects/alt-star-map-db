import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('alt_signatures', Path(__file__).resolve().parents[1] / 'tools/alt_signatures.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Signatures(unittest.TestCase):
    def test_syntax_and_idempotence(self):
        c = {'holder': 'Example', 'bare_id': 'ABC'}
        for style, text in [('# ', '#!/usr/bin/python3\n# coding: utf-8\nprint(1)\n'), ('html', '<!doctype html>\n<html></html>\n'), ('// ', 'int x;\n'), ('block', 'body {}\n'), ('-- ', 'SELECT 1;\n')]:
            out = m.annotated(text, c, style)
            self.assertEqual(out, m.annotated(out, c, style))
            self.assertEqual(out.count('@ALT_HEADER_SIGNED'), 1)
            if text.startswith('#!') or text.startswith('<!doctype'):
                self.assertEqual(out.splitlines()[0], text.splitlines()[0])
        compile(m.annotated('print(1)\n', c, '# '), 'example.py', 'exec')

    def test_escape_and_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError):
                m.safe_path(root, '../outside')
            (root / 'x').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                m.safe_path(root, 'x/file')
            (root / '.alt-signatures.json').write_text(json.dumps({'files': [], 'holder': '-->', 'bare_id': 'X'}))
            with self.assertRaises(ValueError):
                m.config(root)

    @unittest.skipUnless(shutil.which('openssl'), 'OpenSSL required')
    def test_signature_and_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.alt-signatures.json').write_text(json.dumps({'files': ['example.py'], 'holder': 'Example', 'bare_id': 'ABC'}))
            (root / 'example.py').write_text('print(1)\n')
            key, pub = root / 'key.pem', root / 'public.pem'
            subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048', '-out', str(key)], check=True, capture_output=True)
            subprocess.run(['openssl', 'pkey', '-in', str(key), '-pubout', '-out', str(pub)], check=True, capture_output=True)
            script = str(Path(m.__file__).resolve())
            def run(*args):
                return subprocess.run(['python3', script, *args, '--root', d], capture_output=True)
            self.assertEqual(run('apply').returncode, 0)
            self.assertEqual(run('sign', '--key', str(key)).returncode, 0)
            self.assertEqual(run('verify', '--key', str(pub)).returncode, 0)
            (root / 'example.py').write_text('print(2)\n')
            self.assertNotEqual(run('verify', '--key', str(pub)).returncode, 0)
            self.assertNotEqual(run('render', '--tag', '@HEX_ABC_UNKNOWN').returncode, 0)
            rendered = run('render', '--tag', '@HEX_ABC_BODY', '--shroud')
            self.assertIn(b'@BAREMARK_SHROUD_START', rendered.stdout)

if __name__ == '__main__':
    unittest.main()
