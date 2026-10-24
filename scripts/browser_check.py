"""Browser regression checks. Install requirements-test.txt and Playwright Chromium.

Use --executable /usr/bin/chromium for a system browser. --text-only-checkout
skips the remote PNG favicon request; public image URLs must be verified
separately when using that option. Banner checks still load the public images.
"""
from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from threading import Thread
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen
from time import sleep
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ASSETS = json.loads((ROOT / 'image-assets.json').read_text(encoding='utf-8'))['files']
ICON_URL = IMAGE_ASSETS['ttIcon.png']['url']
ROUTES = ['/', '/aboutus/', '/aboutus/levi-bryan/', '/codesmith95/', '/ourservices/', '/ourservices/it-help-guidance/', '/ourservices/softwaredevelopment/', '/ourvalues/', '/wood-bank-software/', '/ourservices/websites/', '/contact/']


def stub_analytics(context):
    # Layout tests stay offline and never send synthetic visits to Analytics.
    context.route('https://www.googletagmanager.com/**', lambda route: route.fulfill(
        status=200, content_type='application/javascript', body=''))
    context.route('https://*.clarity.ms/**', lambda route: route.fulfill(
        status=200, content_type='application/javascript', body=''))


def public_images():
    """Fetch each real image anonymously once, then reuse its bytes for layout checks."""
    images = {}
    variants = [(name, {'url': asset[key]}) for name, asset in IMAGE_ASSETS.items()
                for key in ('url', 'mobile_url') if key in asset]
    for name, asset in variants:
        if 'url' not in asset:
            continue
        expected = 'image/webp' if name.endswith('.webp') else ('image/png' if name.endswith('.png') else 'image/jpeg')
        for attempt in range(3):
            try:
                with urlopen(Request(asset['url'], headers={'User-Agent': 'TechTraversers image check'}), timeout=20) as response:
                    body = response.read()
                    content_type = response.headers.get_content_type()
                    assert response.status == 200 and content_type == expected and body, (name, content_type)
                    images[asset['url']] = (content_type, body)
                break
            except Exception:
                if attempt == 2:
                    raise
                sleep(attempt + 1)
        print(f'PASS: anonymous public image {name}', flush=True)
    return images


def reuse_public_images(context, images):
    for url, (content_type, body) in images.items():
        context.route(url, lambda route, request, content_type=content_type, body=body: route.fulfill(
            status=200, content_type=content_type, body=body))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(executable=None, text_only=False):
    images = public_images()
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
            reuse_public_images(context, images)
            stub_analytics(context)
            if text_only:
                context.route(ICON_URL, lambda route: route.fulfill(status=204))
            context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
            page = context.new_page()
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
            page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}') if response.status >= 400 else None)
            banner_urls = {asset[key] for name, asset in IMAGE_ASSETS.items() if name.endswith('.webp') and 'mobile_url' in asset
                           for key in ('url', 'mobile_url')}
            banner_requests = []
            page.on('request', lambda request: banner_requests.append(request.url) if request.url in banner_urls else None)
            for width in (320, 360, 390, 768, 1024, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                for route in ROUTES:
                    banner_requests.clear()
                    response = page.goto(origin + route)
                    assert response.status == 200, route
                    assert page.evaluate('''() => {
                        const head = [...document.head.children];
                        const viewport = head.findIndex(el => el.name === 'viewport');
                        const connection = head.findIndex(el => el.rel === 'preconnect' &&
                            el.href === 'https://lh3.googleusercontent.com/');
                        const preloads = head.map((el, index) => el.rel === 'preload' ? index : -1)
                            .filter(index => index >= 0);
                        const firstWork = head.findIndex(el => el.tagName === 'STYLE' || el.tagName === 'SCRIPT');
                        return viewport >= 0 && connection > viewport && preloads.length === 2 &&
                            preloads.every(index => index > connection && index < firstWork);
                    }'''), (route, 'LCP hints must follow viewport metadata and precede styles/scripts')
                    expect(page.locator('h1')).to_have_count(1)
                    expect(page.locator('main')).to_be_visible()
                    # Decode the page's real remote banner without a signed-in Google session.
                    assert page.evaluate('''async () => {
                        const image = new Image();
                        const preload = [...document.querySelectorAll('link[rel="preload"][as="image"]')]
                            .find(link => matchMedia(link.media).matches);
                        image.src = preload.href;
                        await image.decode();
                        return image.naturalWidth > 0;
                    }'''), (route, 'remote banner failed to decode')
                    banner_name = ('pic2.webp' if route == '/ourservices/' else
                                   'pic1.webp' if route == '/ourservices/softwaredevelopment/' else
                                   'what_is_a_programming_language.webp')
                    expected_banner = IMAGE_ASSETS[banner_name]['mobile_url' if width <= 768 else 'url']
                    assert set(banner_requests) == {expected_banner}, (width, route, 'wrong or duplicate banner download', banner_requests)
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
                        for action in page.locator('main .cta-primary, #footer .cta-primary').all():
                            if action.is_visible():
                                assert action.bounding_box()['height'] >= 48, (route, 'small contact target')
                        for field in page.locator('#quote-form input, #quote-form select, #quote-form textarea').all():
                            assert field.evaluate('el => parseFloat(getComputedStyle(el).fontSize)') >= 16
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
            reuse_public_images(performance, images)
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
            assert measured.locator('link[rel="preload"][as="image"][media="(max-width: 768px)"]').get_attribute('fetchpriority') == 'high'
            assert IMAGE_ASSETS['what_is_a_programming_language.webp']['mobile_url'] in measured.locator('#image').evaluate('el => getComputedStyle(el).backgroundImage')
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
            reuse_public_images(no_js, images)
            if text_only:
                no_js.route(ICON_URL, lambda route: route.fulfill(status=204))
            plain = no_js.new_page()
            for route in ROUTES:
                plain.goto(origin + route)
                expect(plain.locator('nav')).to_be_visible()
                expect(plain.locator('#menu-toggle')).to_be_hidden()
            expect(plain.locator('#quote-form')).to_be_hidden()
            expect(plain.locator('main a[href="mailto:traversertech@gmail.com"]')).to_be_visible()
            page.goto(origin + '/')
            for width, height in ((320, 480), (844, 390)):
                page.set_viewport_size({'width': width, 'height': height})
                for route in ('/', '/contact/'):
                    page.goto(origin + route)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, height, route)
                    page.locator('#footer a.cta-primary').scroll_into_view_if_needed()
                    expect(page.locator('#footer a.cta-primary')).to_be_visible()
            page.goto(origin + '/')
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.screenshot(path=str(ROOT / 'test-results' / 'home-desktop.png'), full_page=True)
            page.set_viewport_size({'width': 360, 'height': 900})
            page.screenshot(path=str(ROOT / 'test-results' / 'home-mobile.png'), full_page=True)
            page.evaluate('window.scrollTo(0, 0)')
            page.set_viewport_size({'width': 390, 'height': 844})
            page.screenshot(path=str(ROOT / 'test-results' / 'home-mobile-viewport.png'))
            touch = browser.new_context(is_mobile=True, has_touch=True, device_scale_factor=3,
                                        viewport={'width': 390, 'height': 844})
            reuse_public_images(touch, images)
            stub_analytics(touch)
            phone = touch.new_page()
            phone.on('pageerror', lambda error: errors.append(str(error)))
            phone.goto(origin + '/')
            primary = phone.locator('main .cta-primary').first.bounding_box()
            assert primary['y'] + primary['height'] <= 844, 'primary contact action is below the first phone screen'
            phone.locator('#menu-toggle').tap()
            expect(phone.locator('nav')).to_be_visible()
            phone.locator('nav a[data-nav="contact"]').tap()
            expect(phone).to_have_url(origin + '/contact/')
            expect(phone.locator('nav')).to_be_hidden()
            phone.locator('#quote-email-address').tap()
            expect(phone.locator('#quote-email-address')).to_be_focused()
            phone.screenshot(path=str(ROOT / 'test-results' / 'contact-mobile-initial.png'), full_page=True)
            touch.close()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: eleven pages at six widths, short screens and landscape; mobile banner selection, touch targets, form sizing, navigation, and JavaScript disabled.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--executable')
    parser.add_argument('--text-only-checkout', action='store_true')
    args = parser.parse_args()
    run(args.executable, args.text_only_checkout)
