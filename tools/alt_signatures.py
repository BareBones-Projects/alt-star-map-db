#!/usr/bin/env python3
"""ALT source notices, HEX snippet selection, and detached content signatures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

KINDS = 'SIDEBAR BODY FRAME HEADER FOOTER SQUARE RECTANGLE VERTICAL BANNER ICON_01 ICON_02 ICON_03 ICON_04 ICON_05 ICON_06 ICON_07'.split()
NOTICE = '''========================================================================
Copyright (c) 2026 [Your Name or Company Name]. All rights reserved.
Portions of this project may utilize open-source components or assets
licensed under separate terms. See LICENSE or NOTICE files for details.
========================================================================'''
STYLES = {'.py': '# ', '.js': '// ', '.ts': '// ', '.cpp': '// ', '.h': '// ', '.cs': '// ', '.sql': '-- ', '.css': 'block', '.html': 'html', '.md': 'html'}

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()

def safe_path(root, name):
    p = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Unsafe path: ' + name)
    return p

def config(root):
    c = json.loads((root / '.alt-signatures.json').read_text())
    if not re.fullmatch(r'[A-Za-z0-9_-]+', c['bare_id']):
        raise ValueError('bare_id must contain letters, digits, underscores or hyphens')
    if not c['holder'] or any(x in c['holder'] for x in ['\n', '\r', '*/', '-->', '\x00']):
        raise ValueError('Invalid copyright holder')
    if len(c['files']) != len(set(c['files'])):
        raise ValueError('Duplicate files')
    for f in c['files']:
        safe_path(root, f)
        if Path(f).suffix not in STYLES:
            raise ValueError('Unsupported comment syntax: ' + f)
    return c

def block(tag, c, style):
    body = '@' + tag + '\n' + NOTICE.replace('[Your Name or Company Name]', c['holder']) + '\n@BAREMARK_VERIFIED_PENDING\n'
    if style == 'html':
        return '<!-- ALT-SIGNATURE-BEGIN:' + tag + '\n' + body + 'ALT-SIGNATURE-END:' + tag + ' -->\n'
    if style == 'block':
        return '/* ALT-SIGNATURE-BEGIN:' + tag + '\n' + body + 'ALT-SIGNATURE-END:' + tag + ' */\n'
    return ''.join(style + line + '\n' for line in ('ALT-SIGNATURE-BEGIN:' + tag + '\n' + body + 'ALT-SIGNATURE-END:' + tag).splitlines())

def annotated(text, c, style):
    for tag in ['ALT_HEADER_SIGNED', 'ALT_FOOT_SIGNED']:
        if style == 'html':
            pattern = r'<!-- ALT-SIGNATURE-BEGIN:' + tag + r'\n.*?ALT-SIGNATURE-END:' + tag + r' -->\n?'
        elif style == 'block':
            pattern = r'/\* ALT-SIGNATURE-BEGIN:' + tag + r'\n.*?ALT-SIGNATURE-END:' + tag + r' \*/\n?'
        else:
            pattern = re.escape(style) + 'ALT-SIGNATURE-BEGIN:' + tag + r'\n.*?' + re.escape(style) + 'ALT-SIGNATURE-END:' + tag + r'\n?'
        text = re.sub(pattern, '', text, flags=re.S)
    # Preserve shebang, Python encoding declaration and HTML doctype positions.
    lines = text.splitlines(keepends=True)
    n = 0
    if lines and lines[0].startswith('#!'):
        n = 1
    if style == '# ':
        for i, line in enumerate(lines[:2]):
            if re.match(r'^#.*coding[:=]\s*[-\w.]+', line):
                n = i + 1
    if style == 'html' and lines and lines[0].lower().startswith('<!doctype'):
        n = 1
    prefix, rest = ''.join(lines[:n]), ''.join(lines[n:])
    return prefix + block('ALT_HEADER_SIGNED', c, style) + rest.rstrip('\n') + '\n' + block('ALT_FOOT_SIGNED', c, style)

def apply(root):
    c = config(root)
    for name in c['files']:
        p = safe_path(root, name)
        text = p.read_bytes().decode('utf-8')
        p.write_bytes(annotated(text, c, STYLES[p.suffix]).encode())

def manifest(root):
    c = config(root)
    names = sorted(c['files'] + ['.alt-signatures.json'])
    return canonical({'version': 1, 'files': {f: hashlib.sha256(safe_path(root, f).read_bytes()).hexdigest() for f in names}})

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['apply', 'check', 'sign', 'verify', 'render', 'inject'])
    p.add_argument('--root', type=Path, default=Path('.'))
    p.add_argument('--key', type=Path)
    p.add_argument('--tag')
    p.add_argument('--target')
    p.add_argument('--snippet', type=Path)
    p.add_argument('--shroud', action='store_true')
    a = p.parse_args()
    root = a.root.resolve()
    c = config(root)
    if a.command == 'apply':
        apply(root)
    elif a.command == 'check':
        for f in c['files']:
            text = safe_path(root, f).read_bytes().decode('utf-8')
            if annotated(text, c, STYLES[Path(f).suffix]) != text:
                raise ValueError('Missing or stale ALT notices: ' + f)
    elif a.command in ['render', 'inject']:
        tags = ['@ALT_HEADER_SIGNED', '@ALT_FOOT_SIGNED'] + ['@HEX_' + c['bare_id'] + '_' + k for k in KINDS]
        if a.tag not in tags:
            raise ValueError('Unknown tag; choose one of: ' + ', '.join(tags))
        if a.tag.startswith('@ALT_'):
            if a.command == 'inject':
                raise ValueError('Use apply to insert ALT notices; inject accepts HEX tags only')
            print(block(a.tag[1:], c, 'html'), end='')
        else:
            payload = a.snippet.read_text() if a.snippet else ''
            if a.shroud:
                payload = '<!-- @BAREMARK_SHROUD_START -->\n' + payload + '\n<!-- @BAREMARK_SHROUD_END -->'
            start, end = '<!-- ' + a.tag + ':START -->', '<!-- ' + a.tag + ':END -->'
            if start in payload or end in payload:
                raise ValueError('Snippet contains reserved slot boundaries')
            rendered = start + '\n' + payload + '\n' + end
            if a.command == 'render':
                print(rendered)
            else:
                if a.target not in c['files'] or Path(a.target).suffix != '.html':
                    raise ValueError('--target must be a configured HTML file')
                target = safe_path(root, a.target)
                text = target.read_text()
                if text.count(start) != 1 or text.count(end) != 1 or text.index(start) >= text.index(end):
                    raise ValueError('Target must contain exactly one ordered START/END slot pair; render an empty slot first')
                left = text.index(start)
                right = text.index(end) + len(end)
                target.write_text(text[:left] + rendered + text[right:])
    else:
        if not a.key:
            raise ValueError('--key is required (private for sign, trusted public for verify)')
        m, s = root / '.alt-signature-manifest.json', root / '.alt-signature-manifest.sig'
        if a.command == 'sign':
            if c['holder'] == '[Your Name or Company Name]' or c['bare_id'] == 'bareID_INPUT_HERE':
                raise ValueError('Set the copyright holder and bare_id before signing')
            m.write_bytes(manifest(root))
            subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(a.key.resolve()), '-out', str(s), str(m)], check=True)
        else:
            if m.read_bytes() != manifest(root):
                raise ValueError('Signed manifest does not match current files/configuration')
            subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(a.key.resolve()), '-signature', str(s), str(m)], check=True)
        # This authenticates content under the supplied key, not BareMark certification.

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        sys.exit(str(e))
