"""Build JSON-LD from public page metadata and existing public business details."""
from html.parser import HTMLParser

ORIGIN = 'https://www.techtraversers.com'
ORGANIZATION = ORIGIN + '/#organization'
WEBSITE = ORIGIN + '/#website'
SERVICE_ROUTES = {
    '/ourservices/websites/',
    '/ourservices/softwaredevelopment/',
    '/ourservices/it-help-guidance/',
}
PROFILE_ROUTES = {'/aboutus/levi-bryan/', '/codesmith95/'}


class Metadata(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.canonical = ''
        self.description = ''
        self.heading = ''
        self.in_heading = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href']
        if tag == 'meta' and attrs.get('name') == 'description':
            self.description = attrs['content']
        if tag == 'h1':
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_heading = False

    def handle_data(self, data):
        if self.in_heading:
            self.heading += data


def build_schema(text):
    metadata = Metadata(text)
    url = metadata.canonical
    if not url.startswith(ORIGIN + '/') or not url.endswith('/'):
        raise ValueError('Structured data requires a canonical directory URL')
    route = url.removeprefix(ORIGIN)
    page_type = 'WebPage'
    if route in PROFILE_ROUTES:
        page_type = 'ProfilePage'
    elif route == '/aboutus/':
        page_type = 'AboutPage'
    elif route == '/ourservices/':
        page_type = 'CollectionPage'
    page = {
        '@type': page_type, '@id': url + '#webpage', 'url': url,
        'name': metadata.heading.strip(), 'description': metadata.description,
        'inLanguage': 'en', 'isPartOf': {'@id': WEBSITE},
        'publisher': {'@id': ORGANIZATION},
    }
    graph = [
        {'@type': 'Organization', '@id': ORGANIZATION, 'name': 'Tech Traversers',
         'url': ORIGIN + '/', 'email': 'traversertech@gmail.com'},
        {'@type': 'WebSite', '@id': WEBSITE, 'url': ORIGIN + '/',
         'name': 'Tech Traversers', 'inLanguage': 'en',
         'publisher': {'@id': ORGANIZATION}},
        page,
    ]
    entity = None
    if route in SERVICE_ROUTES:
        entity = {
            '@type': 'Service', '@id': url + '#service',
            'provider': {'@id': ORGANIZATION},
        }
    elif route in PROFILE_ROUTES:
        entity = {'@type': 'Person', '@id': url + '#person'}
    elif route == '/wood-bank-software/':
        entity = {
            '@type': 'SoftwareApplication', '@id': url + '#software',
            'applicationCategory': 'BusinessApplication',
            'creator': {'@id': ORGANIZATION},
        }
    if entity:
        entity.update({
            'name': metadata.heading.strip(), 'url': url,
            'description': metadata.description,
            'mainEntityOfPage': {'@id': page['@id']},
        })
        page['mainEntity'] = {'@id': entity['@id']}
        graph.append(entity)
    elif route == '/aboutus/':
        page['mainEntity'] = {'@id': ORGANIZATION}
    return {'@context': 'https://schema.org', '@graph': graph}
