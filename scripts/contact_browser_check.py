"""Exercise the real server and form with mocked email transport; never sends mail."""
from pathlib import Path
from argparse import ArgumentParser
import subprocess
import socket
from time import sleep
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
parser = ArgumentParser(description=__doc__)
parser.add_argument('--executable')
args = parser.parse_args()
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
origin = f'http://localhost:{port}'
code = """
import {createApp} from './server.mjs';
createApp({env:{PORT:'3219',APP_ORIGIN:'http://localhost:3219',RESEND_API_KEY:'test-only',CONTACT_FROM:'test@example.com'},
fetchEmail:async (_,request)=> JSON.parse(request.body).text.includes('SIMULATE_FAILURE') ? Response.json({error:'test'},{status:500}) : Response.json({id:'mock-email'})}).listen(3219,'127.0.0.1');
"""
code = code.replace('3219', str(port))
server = subprocess.Popen(['node','--input-type=module','-e',code],cwd=root)
try:
    for _ in range(40):
        try:
            urlopen(origin+'/healthz'); break
        except OSError: sleep(.1)
    with sync_playwright() as p:
        browser=p.chromium.launch(**({'executable_path':args.executable} if args.executable else {}))
        for width in [360,1440]:
            context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
            context.route('https://**/*',lambda route:route.abort())
            page=context.new_page()
            page.goto(origin+'/contact/')
            expect(page.get_by_role('button',name='Send inquiry')).to_be_visible()
            page.get_by_label('Your name',exact=True).fill('Preview Test')
            page.get_by_label('Your email address').fill('visitor@example.com')
            page.get_by_label('What do you need help with?').select_option('Website development')
            page.get_by_label('Tell me about your project or question').fill('SIMULATE_FAILURE')
            sleep(2.1)
            page.get_by_role('button',name='Send inquiry').click()
            expect(page.locator('#quote-status')).to_contain_text('could not send')
            expect(page.locator('#quote-details')).to_have_value('SIMULATE_FAILURE')
            page.locator('#quote-details').fill('Test inquiry — no email will be sent by this test.')
            page.get_by_role('button',name='Send inquiry').click()
            expect(page.locator('#quote-result')).to_be_visible()
            expect(page.locator('#quote-result-heading')).to_contain_text('Inquiry sent')
            expect(page.locator('#quote-form')).to_be_hidden()
            expect(page.locator('#quote-email')).to_be_hidden()
            assert page.locator('#quote-result-heading').evaluate('(el)=>document.activeElement===el')
            assert page.locator('#quote-result').evaluate('(el)=>getComputedStyle(el).animationName')=='none'
            page.screenshot(path=str(root/'test-results'/f'contact-direct-{width}.png'),full_page=True)
            context.close()
        browser.close()
    print('PASS: direct form success, provider failure, retained input, focus, reduced motion, desktop and phone.')
finally:
    server.terminate()
    server.wait(timeout=10)
