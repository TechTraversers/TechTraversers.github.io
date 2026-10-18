"""Check local links, page semantics, metadata, shared navigation, and sitemap.

No third-party dependencies. --inventory accepts an optional JSON list of files
verified in the source revision when reviewing through a text-only connector.
"""
from argparse import ArgumentParser
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import xml.etree.ElementTree as ET
from sync_assets import digest

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.techtraversers.com'
IMAGE_ASSETS = json.loads((ROOT / 'image-assets.json').read_text(encoding='utf-8'))['files']
PUBLIC_IMAGE_URLS = {image[key] for image in IMAGE_ASSETS.values() for key in ('url', 'mobile_url') if key in image}
HOSTS = {'www.techtraversers.com', 'techtraversers.com'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.errors = []
        self.stack = []
        self.feed(text)
        if self.stack:
            self.errors.append(f'unclosed tags: {self.stack}')

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.nodes.append((tag, attrs))
        if tag in {'a', 'button'} and any(t in {'a', 'button'} for t in self.stack):
            self.errors.append('nested interactive elements')
        if tag in {'div', 'ol', 'ul', 'section', 'h1', 'h2'} and 'p' in self.stack:
            self.errors.append(f'{tag} nested in a paragraph')
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'unmatched closing tag: {tag}')
        else:
            self.stack.pop()


def check(inventory=()):
    failures = []
    known = set(inventory) | {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
    pages = {str(p.relative_to(ROOT)): Page(p.read_text(encoding='utf-8')) for p in ROOT.rglob('*.html')}

    def require(condition, message):
        if not condition:
            failures.append(message)

    def local_target(url, source):
        parsed = urlsplit(url)
        if parsed.scheme and parsed.scheme not in {'http', 'https'}:
            return None
        if parsed.netloc and parsed.hostname not in HOSTS:
            return None
        path = unquote(parsed.path)
        if not path:
            return source
        target = (ROOT / path.lstrip('/')) if path.startswith('/') else ROOT / source.parent / path
        target = target.resolve()
        if path.endswith('/'):
            target /= 'index.html'
        return target.relative_to(ROOT)

    canonicals = set()
    descriptions = []
    nav_reference = [('home', '/'), ('services', '/ourservices/'), ('woodbank', '/wood-bank-software/'), ('values', '/ourvalues/'), ('about', '/aboutus/'), ('contact', '/contact/')]
    for name, page in pages.items():
        if name == 'sidebar.html':
            continue
        prefix = f'{name}: '
        require(not page.errors, prefix + '; '.join(page.errors))
        ids = [a['id'] for _, a in page.nodes if 'id' in a]
        require(len(ids) == len(set(ids)), prefix + 'duplicate IDs')
        for tag, attrs in page.nodes:
            for attr in ('href', 'src'):
                if attr not in attrs:
                    continue
                target = local_target(attrs[attr], Path(name))
                if urlsplit(attrs[attr]).hostname == 'lh3.googleusercontent.com':
                    image_connection = (tag == 'link' and attrs.get('rel') == 'preconnect'
                                        and attrs[attr] == 'https://lh3.googleusercontent.com')
                    require(image_connection or attrs[attr] in PUBLIC_IMAGE_URLS, prefix + 'unknown remote image ' + attrs[attr])
                if target is None:
                    continue
                require(str(target) in known, prefix + f'missing target {attrs[attr]}')
                fragment = unquote(urlsplit(attrs[attr]).fragment)
                if fragment and str(target) in pages:
                    require(any(a.get('id') == fragment for _, a in pages[str(target)].nodes), prefix + f'missing fragment {attrs[attr]}')
            if tag == 'img':
                require(bool(attrs.get('alt')) and 'width' in attrs and 'height' in attrs, prefix + 'image needs alt text and dimensions')
        if name == 'index-dev.html':
            require(any(t == 'meta' and a.get('name') == 'robots' and a.get('content') == 'noindex' for t, a in page.nodes), prefix + 'preview must be noindex')
            continue
        prices = re.findall(r'\$(\d+(?:\.\d+)?)', (ROOT / name).read_text(encoding='utf-8'))
        require(not prices, prefix + 'public prices need fresh owner approval')
        counts = Counter(tag for tag, _ in page.nodes)
        require(counts['h1'] == counts['main'] == counts['title'] == 1, prefix + 'needs one h1, main, and title')
        require(any(t == 'html' and a.get('lang') == 'en' for t, a in page.nodes), prefix + 'missing page language')
        levels = [int(t[1]) for t, _ in page.nodes if re.fullmatch('h[1-6]', t)]
        require(all(b <= a + 1 for a, b in zip(levels, levels[1:])), prefix + 'heading level skipped')
        require(any(t == 'a' and a.get('href') == '#main-content' for t, a in page.nodes), prefix + 'missing skip link')
        require(any(t == 'a' and a.get('href', '').split('?')[0] == 'mailto:traversertech@gmail.com' for t, a in page.nodes), prefix + 'missing contact link')
        nav_links = [(a['data-nav'], a.get('href')) for t, a in page.nodes if t == 'a' and 'data-nav' in a]
        require(nav_links == nav_reference, prefix + 'shared navigation differs')
        require(sum(a.get('aria-current') == 'page' for _, a in page.nodes) == 1, prefix + 'needs one current navigation link')
        nav = next((a for t, a in page.nodes if t == 'nav'), {})
        require('hidden' not in nav, prefix + 'navigation must work without JavaScript')
        canonical = next((a.get('href') for t, a in page.nodes if t == 'link' and a.get('rel') == 'canonical'), '')
        route = '/' if name == 'index.html' else '/' + Path(name).as_posix().removesuffix('index.html')
        require(canonical == ORIGIN + route, prefix + 'incorrect canonical')
        canonicals.add(canonical)
        metas = {a.get('name', a.get('property')): a.get('content') for t, a in page.nodes if t == 'meta'}
        for key in ('description', 'viewport', 'og:title', 'og:description', 'og:url', 'og:image', 'og:image:alt', 'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'):
            require(bool(metas.get(key)), prefix + f'missing {key}')
        require(metas.get('og:url') == canonical, prefix + 'Open Graph URL differs from canonical')
        source = (ROOT / name).read_text(encoding='utf-8')
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)
        require(len(blocks) == 1, prefix + 'needs one JSON-LD graph')
        for block in blocks:
            try:
                data = json.loads(block)
                require(data.get('@context') == 'https://schema.org', prefix + 'incorrect schema context')
                graph = data['@graph']
                entities = {entity['@id']: entity for entity in graph}
                require(len(entities) == len(graph), prefix + 'duplicate schema IDs')
                require(entities[ORIGIN + '/#organization']['@type'] == 'Organization', prefix + 'missing Organization')
                require(entities[ORIGIN + '/#website']['@type'] == 'WebSite', prefix + 'missing WebSite')
                webpage = entities[canonical + '#webpage']
                require(webpage.get('url') == canonical and webpage.get('description') == metas.get('description'), prefix + 'schema differs from page metadata')
                require(bool(webpage.get('name')), prefix + 'missing schema page name')

                def check_references(value):
                    if isinstance(value, dict):
                        if set(value) == {'@id'}:
                            require(value['@id'] in entities, prefix + 'unresolved schema reference ' + value['@id'])
                        for child in value.values():
                            check_references(child)
                    elif isinstance(value, list):
                        for child in value:
                            check_references(child)

                check_references(graph)
                csp = next((a.get('content', '') for t, a in page.nodes if t == 'meta' and a.get('http-equiv') == 'Content-Security-Policy'), '')
                require(digest(block) in csp, prefix + 'JSON-LD hash missing from CSP')
            except (ValueError, KeyError, TypeError) as error:
                require(False, prefix + f'invalid structured data: {error}')
        for key in ('og:image', 'twitter:image'):
            target = local_target(metas.get(key, ''), Path(name))
            require((target is not None and str(target) in known) or metas.get(key) in PUBLIC_IMAGE_URLS, prefix + f'missing {key} image')
        descriptions.append(metas.get('description'))
    require(len(descriptions) == len(set(descriptions)), 'meta descriptions must be unique')
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    urls = [n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    require(len(urls) == len(set(urls)) and set(urls) == canonicals, 'sitemap must match public canonical pages exactly')
    for name in ('robots.txt', 'bots.txt'):
        require('Sitemap: ' + ORIGIN + '/sitemap.xml' in (ROOT / name).read_text(), name + ': sitemap missing')
    for css in ROOT.rglob('*.css'):
        for url in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text()):
            target = local_target(url, css.relative_to(ROOT))
            require(target is None or str(target) in known, f'{css.name}: missing {url}')
    for svg in ROOT.rglob('*.svg'):
        ET.parse(svg)
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(canonicals)} public pages; local links, fragments, metadata, structured data, navigation, SVGs, crawler files, and sitemap.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path)
    args = parser.parse_args()
    check(json.loads(args.inventory.read_text()) if args.inventory else ())
