"""Browser regression checks. Install requirements-test.txt and Playwright Chromium.

Use --executable /usr/bin/chromium for a system browser. --text-only-checkout
skips the original PNG favicon request when binary downloads are unavailable;
the file's presence must be verified separately with check_site.py --inventory.
"""
from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ['/', '/aboutus/', '/aboutus/levi-bryan/', '/codesmith95/', '/ourservices/', '/ourservices/it-help-guidance/', '/ourservices/softwaredevelopment/', '/ourvalues/', '/wood-bank-software/', '/ourservices/websites/', '/contact/']


def stub_analytics(context):
    # Layout tests stay offline and never send synthetic visits to Analytics.
    context.route('https://www.googletagmanager.com/**', lambda route: route.fulfill(
        status=200, content_type='application/javascript', body=''))
    context.route('https://*.clarity.ms/**', lambda route: route.fulfill(
        status=200, content_type='application/javascript', body=''))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(executable=None, text_only=False):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            options = {'headless': True}
            if executable:
                options['executable_path'] = executable
            browser = p.chromium.launch(**options)
            errors = []
            context = browser.new_context()
            stub_analytics(context)
            if text_only:
                context.route('**/Pictures/ttIcon.png', lambda route: route.fulfill(status=204))
            context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
            page = context.new_page()
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
            page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}') if response.status >= 400 else None)
            for width in (360, 768, 1024, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                for route in ROUTES:
                    response = page.goto(origin + route)
                    assert response.status == 200, route
                    expect(page.locator('h1')).to_have_count(1)
                    expect(page.locator('main')).to_be_visible()
                    expect(page.locator('a[aria-current="page"]')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, route, 'horizontal overflow')
                    assert page.locator('a button, button a').count() == 0
                    assert page.locator('#footer a[href^="mailto:"]').count() > 0
                    expect(page.locator('#footer a[href="/contact/"]')).to_be_visible()
                    assert page.locator('main .contact-card').count() == 0
                    for image in page.locator('img').all():
                        image.scroll_into_view_if_needed()
                        expect(image).to_have_js_property('complete', True)
                        assert image.evaluate('(img) => img.naturalWidth > 0'), route
                    toggle = page.locator('#menu-toggle')
                    nav = page.locator('#primary-navigation')
                    if width <= 768:
                        expect(toggle).to_be_visible()
                        expect(nav).to_be_hidden()
                        # Hidden links must not remain in the keyboard tab order.
                        assert nav.evaluate('(nav) => nav.hidden')
                        toggle.focus()
                        page.keyboard.press('Enter')
                        expect(nav).to_be_visible()
                        expect(toggle).to_have_attribute('aria-expanded', 'true')
                        expect(nav.locator('a').first).to_be_focused()
                        page.keyboard.press('Escape')
                        expect(nav).to_be_hidden()
                        expect(toggle).to_be_focused()
                        toggle.click()
                        page.locator('#footer').click()
                        expect(nav).to_be_hidden()
                    else:
                        expect(toggle).to_be_hidden()
                        expect(nav).to_be_visible()
            # Embedded assets must avoid blocking requests and load without shifts.
            performance = browser.new_context(viewport={'width': 360, 'height': 900})
            stub_analytics(performance)
            performance.add_init_script("""
                window.layoutShiftScore = 0;
                new PerformanceObserver(list => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) window.layoutShiftScore += entry.value;
                    }
                }).observe({type: 'layout-shift', buffered: true});
            """)
            measured = performance.new_page()
            security_errors = []
            measured.on('console', lambda message: security_errors.append(message.text) if message.type == 'error' else None)
            measured.goto(origin + '/')
            measured.wait_for_timeout(300)
            assert measured.evaluate('window.layoutShiftScore') < 0.01, 'mobile load shifts content'
            assert measured.locator('link[rel="preload"][as="image"]').get_attribute('fetchpriority') == 'high'
            assert measured.locator('#image').evaluate("el => getComputedStyle(el).backgroundImage.includes('.webp')")
            assert measured.locator('link[rel=stylesheet], script[src]:not([async])').count() == 0
            expect(measured.locator('script[src]')).to_have_count(2)
            expect(measured.locator('script[data-analytics]')).to_have_count(1)
            assert not security_errors, security_errors
            # The policy must reject injected inline scripts and unsafe DOM HTML.
            assert measured.evaluate('''() => {
                window.cspProbe = false;
                const script = document.createElement('script');
                try {
                    script.textContent = 'window.cspProbe = true';
                    document.head.append(script);
                } catch (error) {
                    if (!(error instanceof TypeError)) throw error;
                }
                return window.cspProbe === false;
            }''')
            assert measured.evaluate('''() => {
                try { document.createElement('div').innerHTML = '<b>unsafe</b>'; return false; }
                catch (error) { return error instanceof TypeError; }
            }''')
            performance.close()
            # Resizing must not strand keyboard focus inside a hidden menu.
            page.set_viewport_size({'width': 1000, 'height': 900})
            page.goto(origin + '/')
            page.locator('nav a').first.focus()
            page.set_viewport_size({'width': 360, 'height': 900})
            expect(page.locator('#menu-toggle')).to_be_focused()
            page.locator('#menu-toggle').click()
            page.locator('nav a[data-nav="services"]').click()
            expect(page).to_have_url(origin + '/ourservices/')
            expect(page.locator('#primary-navigation')).to_be_hidden()
            # Skip navigation goes directly to the main content.
            page.goto(origin + '/')
            page.keyboard.press('Tab')
            expect(page.locator('.skip-link')).to_be_focused()
            page.keyboard.press('Enter')
            expect(page.locator('main')).to_be_focused()
            # The static quote form validates locally and prepares, but never sends, an email.
            page.goto(origin + '/contact/?service=Website%20maintenance')
            expect(page.locator('#quote-service')).to_have_value('Website maintenance')
            expect(page.locator('#quote-form')).to_be_visible()
            expect(page.locator('#quote-result')).to_be_hidden()
            page.get_by_role('button', name='Prepare email', exact=True).click()
            expect(page.locator('#quote-name')).to_be_focused()
            expect(page.locator('#quote-result')).to_be_hidden()
            page.locator('#quote-name').fill('Test & Example')
            page.locator('#quote-email-address').fill('visitor@example.com')
            page.locator('#quote-details').fill('Improve my site & contact flow. <b>Example</b>\nKeep the current content.')
            page.locator('#quote-timing').fill('Next month')
            contact_requests = []
            page.on('request', lambda request: contact_requests.append(request))
            page.get_by_role('button', name='Prepare email', exact=True).click()
            expect(page.locator('#quote-result')).to_be_visible()
            expect(page.locator('#quote-result-heading')).to_be_focused()
            expect(page.locator('#quote-status')).to_contain_text('Nothing has been sent')
            email = urlsplit(page.locator('#quote-email').get_attribute('href'))
            assert email.scheme == 'mailto' and email.path == 'traversertech@gmail.com'
            params = parse_qs(email.query)
            assert params['subject'] == ['Project inquiry: Website maintenance']
            body = params['body'][0]
            assert 'Test & Example' in body and 'visitor@example.com' in body
            assert '<b>Example</b>\nKeep the current content.' in body
            assert 'Next month' in body
            expect(page.locator('#quote-draft')).to_have_value(body)
            assert not contact_requests, 'Preparing the draft must not send visitor data'
            page.locator('#quote-details').fill('Updated request')
            expect(page.locator('#quote-result')).to_be_hidden()
            assert page.locator('#quote-email').get_attribute('href') is None
            page.get_by_role('button', name='Prepare email', exact=True).click()
            assert 'Updated request' in page.locator('#quote-draft').input_value()
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.screenshot(path=str(ROOT / 'test-results' / 'contact-desktop.png'), full_page=True)
            page.set_viewport_size({'width': 360, 'height': 900})
            page.screenshot(path=str(ROOT / 'test-results' / 'contact-mobile.png'), full_page=True)
            page.goto(origin + '/contact/?service=unrecognized')
            expect(page.locator('#quote-service')).to_have_value('')
            # Navigation works with the enhancement request blocked.
            import re
            def remove_enhancement(route):
                response = route.fetch()
                html = re.sub(r'<script data-navigation>.*?</script>', '', response.text(), flags=re.S)
                route.fulfill(response=response, body=html)
            context.route(origin + '/', remove_enhancement)
            page.goto(origin + '/')
            expect(page.locator('nav')).to_be_visible()
            context.unroute(origin + '/')
            # Test the actual JavaScript-disabled experience on every page.
            no_js = browser.new_context(java_script_enabled=False, viewport={'width': 360, 'height': 900})
            if text_only:
                no_js.route('**/Pictures/ttIcon.png', lambda route: route.fulfill(status=204))
            plain = no_js.new_page()
            for route in ROUTES:
                plain.goto(origin + route)
                expect(plain.locator('nav')).to_be_visible()
                expect(plain.locator('#menu-toggle')).to_be_hidden()
            expect(plain.locator('#quote-form')).to_be_hidden()
            expect(plain.locator('main a[href="mailto:traversertech@gmail.com"]')).to_be_visible()
            page.goto(origin + '/')
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.screenshot(path=str(ROOT / 'test-results' / 'home-desktop.png'), full_page=True)
            page.set_viewport_size({'width': 360, 'height': 900})
            page.screenshot(path=str(ROOT / 'test-results' / 'home-mobile.png'), full_page=True)
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: eleven pages at four widths; navigation, accessibility, static quote form, email encoding, no submission, and JavaScript disabled.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--executable')
    parser.add_argument('--text-only-checkout', action='store_true')
    args = parser.parse_args()
    run(args.executable, args.text_only_checkout)
