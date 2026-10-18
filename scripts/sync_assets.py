"""Embed shared assets and hash-based CSP. Run after editing CSS/JS; --check detects drift."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import re
from structured_data import build_schema

ROOT = Path(__file__).resolve().parents[1]

def digest(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode() + "'"

def sync(check=False):
    stale = []
    for page in ROOT.rglob('*.html'):
        original = page.read_text(encoding='utf-8')
        if '<header id="image">' not in original:
            continue
        text = re.sub(r'    <!-- generated:head:start -->.*?    <!-- generated:head:end -->\n', '', original, flags=re.S)
        text = re.sub(r'<script data-navigation>.*?</script>', '<script src="/script.js"></script>', text, flags=re.S)
        text = re.sub(r'    <script data-contact>.*?</script>\n', '', text, flags=re.S)
        text = re.sub(r'    <link rel="stylesheet" href="/(?:style.css|aboutus/style.css)" />\n', '', text)
        css = (ROOT / 'style.css').read_text().strip()
        if page.relative_to(ROOT).as_posix() in ('aboutus/index.html', 'aboutus/levi-bryan/index.html', 'codesmith95/index.html'):
            css += '\n' + (ROOT / 'aboutus/style.css').read_text().strip()
        script = (ROOT / 'script.js').read_text().strip()
        analytics = (ROOT / 'analytics.js').read_text().strip()
        clarity = (ROOT / 'clarity.js').read_text().strip()
        analytics_tag = ('    <!-- Google tag (gtag.js) -->\n'
                         '    <script async src="https://www.googletagmanager.com/gtag/js?id=G-YHRY359L0X"></script>\n'
                         f'    <script data-analytics>{analytics}</script>\n')
        analytics_tag += f'    <script type="text/javascript" data-clarity>{clarity}</script>\n'
        # Escape HTML-sensitive characters so future copy cannot close the script.
        data = json.dumps(build_schema(text), separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        schemas = f'    <script type="application/ld+json">{data}</script>\n'
        hashes = [digest(script), digest(analytics), digest(clarity), digest(data)]
        if page.relative_to(ROOT).as_posix() == 'contact/index.html':
            contact = (ROOT / 'contact.js').read_text().strip()
            hashes.append(digest(contact))
            text = text.replace('  </body>', f'    <script data-contact>{contact}</script>\n  </body>')
        # Analytics endpoints; keep inline hashing and Trusted Types enforcement.
        policy = ("default-src 'none'; base-uri 'none'; object-src 'none'; form-action 'none'; "
                  "img-src 'self' https://lh3.googleusercontent.com https://www.googletagmanager.com https://*.google-analytics.com https://*.clarity.ms https://c.bing.com; "
                  "connect-src https://www.googletagmanager.com https://*.google-analytics.com https://*.google.com https://*.clarity.ms; "
                  'script-src https://www.googletagmanager.com https://www.clarity.ms https://scripts.clarity.ms ' + ' '.join(hashes) +
                  '; style-src ' + digest(css) +
                  "; require-trusted-types-for 'script'; trusted-types goog#html default")
        generated = f'    <!-- generated:head:start -->\n    <meta http-equiv="Content-Security-Policy" content="{policy}" />\n    <meta name="referrer" content="strict-origin-when-cross-origin" />\n{analytics_tag}    <style>{css}</style>\n{schemas}    <!-- generated:head:end -->\n'
        text = text.replace('    <meta name="viewport"', generated + '    <meta name="viewport"', 1)
        text = text.replace('<script src="/script.js"></script>', '<script data-navigation>' + script + '</script>')
        if text != original:
            stale.append(page.relative_to(ROOT).as_posix())
            if not check:
                page.write_text(text, encoding='utf-8')
    if check and stale:
        raise SystemExit('Run python scripts/sync_assets.py: ' + ', '.join(stale))
    print('PASS: embedded styles, navigation, CSP hashes, and structured data are synchronized.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    sync(parser.parse_args().check)
