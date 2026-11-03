import { createServer } from 'node:http';
import { createHmac, randomBytes, timingSafeEqual, createHash } from 'node:crypto';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const services = new Set(['Website development', 'Website maintenance', 'Custom software and automation', 'IT help', 'Wood Bank Software', 'Not sure yet']);
export function createApp({ env = process.env, fetchEmail = fetch, now = Date.now } = {}) {
  const secret = randomBytes(32);
  const publicRoot = resolve(import.meta.dirname, 'public');
  const counters = new Map();
  const completed = new Map();
  const configured = Boolean(env.RESEND_API_KEY && env.CONTACT_FROM);
  const origin = env.APP_ORIGIN || (env.RAILWAY_PUBLIC_DOMAIN ? `https://${env.RAILWAY_PUBLIC_DOMAIN}` : `http://localhost:${env.PORT || 3000}`);
  const sign = value => createHmac('sha256', secret).update(value).digest('hex');
  function token() {
    const value = `${now()}.${randomBytes(16).toString('hex')}`;
    return `${value}.${sign(value)}`;
  }
  function validToken(value) {
    if (typeof value !== 'string' || !/^\d+\.[a-f0-9]{32}\.[a-f0-9]{64}$/.test(value)) return false;
    const [time, nonce, mac] = value.split('.');
    const age = now() - Number(time);
    return age >= 2000 && age < 3600000 && timingSafeEqual(Buffer.from(mac), Buffer.from(sign(`${time}.${nonce}`)));
  }
  function limited(key, max, window) {
    const time = now();
    for (const [key, item] of counters) if (item.until <= time) counters.delete(key);
    const item = counters.get(key) || { count: 0, until: time + window };
    item.count++;
    counters.set(key, item);
    return item.count > max;
  }
  return createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    if (env.PREVIEW_MODE !== 'false') res.setHeader('X-Robots-Tag', 'noindex, nofollow');
    const json = (code, body) => {
      res.writeHead(code, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
      res.end(JSON.stringify(body));
    };
    try {
      const url = new URL(req.url, origin);
      if (url.pathname === '/healthz' && req.method === 'GET') return json(200, { ok: true });
      if (url.pathname === '/api/contact/config' && req.method === 'GET') {
        return json(200, { enabled: configured, token: configured ? token() : null });
      }
      if (url.pathname === '/api/contact') {
        if (req.method !== 'POST') return json(405, { error: 'Use POST.' });
        if (req.headers.origin !== origin) return json(403, { error: 'Please submit from this website.' });
        if (!configured) return json(503, { error: 'Online sending is unavailable. Please email traversertech@gmail.com.' });
        if (req.headers['content-type']?.split(';')[0] !== 'application/json') return json(415, { error: 'Expected JSON.' });
        // Railway appends the proxy-observed client to X-Forwarded-For. Global
        // limits also bound sending even if clients spoof proxy headers.
        const ip = String(req.headers['x-forwarded-for'] || req.socket.remoteAddress).split(',').at(-1).trim();
        if (limited('attempts', 120, 900000) || limited(`ip:${ip}`, 10, 900000)) {
          res.setHeader('Retry-After', '900');
          return json(429, { error: 'Too many attempts. Please try later or email us directly.' });
        }
        const chunks = [];
        let size = 0;
        for await (const chunk of req) {
          size += chunk.length;
          if (size > 12000) return json(413, { error: 'Message is too large.' });
          chunks.push(chunk);
        }
        let data;
        try { data = JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { return json(400, { error: 'Invalid request.' }); }
        if (!data || typeof data !== 'object' || Array.isArray(data)) return json(400, { error: 'Invalid request.' });
        if (data.website || !validToken(data.token)) return json(400, { error: 'Please refresh the page, then complete the form and try again.' });
        for (const [field, max] of [['name', 100], ['email', 200], ['service', 100], ['details', 1500], ['timing', 100]]) {
          if (typeof data[field] !== 'string' || data[field].length > max || (field !== 'timing' && !data[field].trim())) return json(400, { error: 'Please check the required fields and their lengths.' });
          data[field] = data[field].trim();
        }
        if (!services.has(data.service) || !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(data.email) || /[\r\n]/.test(data.name)) return json(400, { error: 'Please check your name, email, and service.' });
        for (const [key, item] of completed) if (item.until <= now()) completed.delete(key);
        const key = createHash('sha256').update(JSON.stringify([data.token, data.name, data.email, data.service, data.details, data.timing])).digest('hex');
        if (completed.has(key)) return json(200, { ok: true });
        if (limited('send-hour', 30, 3600000) || limited('send-day', 80, 86400000)) return json(429, { error: 'Online sending has reached its limit. Please email us directly.' });
        const response = await fetchEmail('https://api.resend.com/emails', {
          method: 'POST', signal: AbortSignal.timeout(15000),
          headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json', 'Idempotency-Key': `contact-${key}` },
          body: JSON.stringify({
            from: env.CONTACT_FROM, to: [env.CONTACT_TO || 'traversertech@gmail.com'], reply_to: data.email,
            subject: `Website inquiry: ${data.service}`,
            text: `Name: ${data.name}\nReply email: ${data.email}\nService: ${data.service}\nPreferred timing: ${data.timing || 'To discuss'}\n\n${data.details}`,
          }),
        });
        if (!response.ok) return json(502, { error: 'We could not send your inquiry. Your message is still here; please retry or email us directly.' });
        const delivered = await response.json();
        if (!delivered.id) return json(502, { error: 'Sending could not be confirmed. Please retry or email us directly.' });
        completed.set(key, { until: now() + 3600000 });
        return json(200, { ok: true });
      }
      if (!['GET', 'HEAD'].includes(req.method)) return json(405, { error: 'Method not allowed.' });
      if (url.pathname.startsWith('/api/')) return json(404, { error: 'Not found.' });
      if (url.pathname === '/robots.txt' && env.PREVIEW_MODE !== 'false') {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        return res.end('User-agent: *\nDisallow: /\n');
      }
      const path = decodeURIComponent(url.pathname);
      if (path.includes('\\') || path.includes('\0') || path.split('/').some(p => p.startsWith('.'))) return json(404, { error: 'Not found.' });
      let file = resolve(publicRoot, '.' + path);
      if (!file.startsWith(publicRoot + sep) && file !== publicRoot) return json(404, { error: 'Not found.' });
      let info;
      try { info = await stat(file); } catch { return json(404, { error: 'Not found.' }); }
      if (info.isDirectory()) {
        if (!path.endsWith('/')) { res.writeHead(308, { Location: url.pathname + '/' + url.search }); return res.end(); }
        file = resolve(file, 'index.html');
      }
      let body = await readFile(file);
      if (path === '/contact/') body = body.toString('utf8').replace('</head>', '<meta name="contact-api" content="same-origin" /></head>');
      const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.xml': 'application/xml', '.txt': 'text/plain' };
      res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
      res.end(req.method === 'HEAD' ? undefined : body);
    } catch {
      if (!res.headersSent) json(502, { error: 'Sending could not be confirmed. Please retry or email traversertech@gmail.com.' });
      else res.end();
    }
  });
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const server = createApp();
  server.requestTimeout = 20000;
  server.listen(Number(process.env.PORT || 3000), '0.0.0.0', () => console.log('Website ready'));
  process.on('SIGTERM', () => server.close(() => process.exit(0)));
}
