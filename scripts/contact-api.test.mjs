import { test } from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { createApp } from '../server.mjs';

async function setup(t, options = {}) {
  let time = Date.now();
  const sent = [];
  const server = createApp({ env: { RESEND_API_KEY: 'test-only', CONTACT_FROM: 'Test <contact@example.com>', APP_ORIGIN: 'https://preview.example.com', ...options.env }, now: () => time,
    fetchEmail: options.fetchEmail || (async (url, request) => { sent.push({url, request}); return Response.json({id:'test-id'}); }) });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => { server.closeAllConnections(); server.close(); });
  const base = `http://127.0.0.1:${server.address().port}`;
  const config = await (await fetch(base + '/api/contact/config')).json();
  const data = {name:'Test Visitor', email:'visitor@example.com', service:'Website development', details:'A website inquiry.', timing:'', website:'', token:config.token};
  const post = (body = data, origin = 'https://preview.example.com') => fetch(base + '/api/contact', {method:'POST', headers:{Origin:origin,'Content-Type':'application/json'}, body:JSON.stringify(body)});
  return {base, data, sent, post, advance:ms => time += ms};
}
test('sends only to configured inbox, sets reply-to, and deduplicates retries', async t => {
  const app = await setup(t); app.advance(2100);
  assert.equal((await app.post()).status, 200);
  assert.equal((await app.post()).status, 200);
  assert.equal(app.sent.length, 1);
  const message = JSON.parse(app.sent[0].request.body);
  assert.deepEqual(message.to, ['traversertech@gmail.com']);
  assert.equal(message.reply_to, app.data.email);
  assert.match(app.sent[0].request.headers['Idempotency-Key'], /^contact-/);
});
test('rejects other origins, invalid payloads, spam and forged or expired tokens', async t => {
  const app = await setup(t);
  assert.equal((await app.post()).status, 400);
  app.advance(2100);
  assert.equal((await app.post(app.data,'https://attacker.example')).status,403);
  for (const changed of [{email:'bad'}, {service:'Fake service'}, {details:'x'.repeat(1501)}, {website:'spam'}, {token:'fake'}]) assert.equal((await app.post({...app.data,...changed})).status,400);
  app.advance(3600000);
  assert.equal((await app.post()).status,400);
  assert.equal(app.sent.length,0);
});
test('provider failure never reports success', async t => {
  const app = await setup(t, {fetchEmail: async () => Response.json({error:'rejected'},{status:403})}); app.advance(2100);
  assert.equal((await app.post()).status,502);
});
test('disabled configuration fails closed; source files never served; preview noindex', async t => {
  const app = await setup(t,{env:{RESEND_API_KEY:''}});
  assert.equal((await app.post()).status,503);
  for (const path of ['/server.mjs','/.env','/package.json','/scripts/sync_assets.py','/.git/config']) assert.equal((await fetch(app.base+path)).status,404);
  const home = await fetch(app.base+'/');
  assert.equal(home.status,200); assert.equal(home.headers.get('x-robots-tag'),'noindex, nofollow');
});
test('rate limits repeated attempts', async t => {
  const app = await setup(t); app.advance(2100);
  for (let i=0;i<10;i++) await app.post({...app.data,website:'spam'});
  assert.equal((await app.post()).status,429);
});
