"""Load the real Google tag; intercept reporting so tests never record visits."""
from argparse import ArgumentParser
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import sync_playwright, expect
from browser_check import ROOT, ROUTES, QuietHandler

TAG_URL = 'https://www.googletagmanager.com/gtag/js?id=G-YHRY359L0X'


def run(executable=None):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**({'executable_path': executable} if executable else {}))
            context = browser.new_context()
            collections = []
            unexpected = []

            def intercept(route):
                request = route.request
                url = urlsplit(request.url)
                if request.url.startswith(origin + '/') or request.url == TAG_URL:
                    route.continue_()
                    return
                if url.hostname and url.hostname.endswith('.google-analytics.com') and url.path == '/g/collect':
                    collections.append(request)
                else:
                    unexpected.append(request.url)
                route.fulfill(status=204, headers={'Access-Control-Allow-Origin': '*'})

            context.route('**/*', intercept)
            context.route('https://*.clarity.ms/**', lambda route: route.fulfill(
                status=200, content_type='application/javascript', body=''))
            context.add_init_script("""
                window.cspViolations = [];
                document.addEventListener('securitypolicyviolation', event => {
                    window.cspViolations.push(event.effectiveDirective + ': ' + event.blockedURI);
                });
            """)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))

            def is_pageview(request):
                params = parse_qs(urlsplit(request.url).query + '&' + (request.post_data or ''))
                return params.get('tid') == ['G-YHRY359L0X'] and params.get('en') == ['page_view']

            for path in ROUTES:
                with page.expect_response(lambda response: is_pageview(response.request), timeout=20000) as event:
                    page.goto(origin + path)
                request = event.value.request
                params = parse_qs(urlsplit(request.url).query + '&' + (request.post_data or ''))
                location = urlsplit(params['dl'][0])
                # Google normalizes page_location by dropping the preview server's port.
                assert location.hostname == '127.0.0.1' and location.path == path, (path, location)
                expect(page.locator('script[src]')).to_have_count(2)
                expect(page.locator('script[data-analytics]')).to_have_count(1)
                assert not page.evaluate('window.cspViolations'), (path, page.evaluate('window.cspViolations'))
            assert len([request for request in collections if is_pageview(request)]) == len(ROUTES)
            assert not errors, errors
            assert not unexpected, unexpected
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: real Google tag sends one page_view per public page, with no CSP errors; all reporting intercepted.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--executable')
    run(parser.parse_args().executable)
