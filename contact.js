// Static hosting keeps the email-draft fallback; Railway enables direct sending.
(() => {
  const form = document.getElementById('quote-form');
  if (!form) return;
  const service = document.getElementById('quote-service');
  const requestedService = new URLSearchParams(window.location.search).get('service');
  if (Array.from(service.options).some(option => option.value === requestedService)) {
    service.value = requestedService;
  }
  const result = document.getElementById('quote-result');
  const draft = document.getElementById('quote-draft');
  const emailLink = document.getElementById('quote-email');
  const status = document.getElementById('quote-status');
  const submit = form.querySelector('button[type="submit"]');
  let config = null;
  let busy = false;
  if (document.querySelector('meta[name="contact-api"]')) fetch('/api/contact/config', { cache: 'no-store' }).then(response => response.ok ? response.json() : null).then(value => {
    if (!value?.enabled) return;
    config = value;
    submit.textContent = 'Send inquiry';
    document.getElementById('quote-instructions').textContent = 'Send your inquiry directly to Tech Traversers. We use Resend to deliver your message by email.';
  }).catch(() => {});

  form.addEventListener('input', () => {
    result.hidden = true;
    emailLink.removeAttribute('href');
    draft.value = '';
    status.textContent = '';
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    const fields = new FormData(form);
    if (config) {
      busy = true;
      submit.disabled = true;
      form.setAttribute('aria-busy', 'true');
      status.textContent = 'Sending your inquiry…';
      try {
        const response = await fetch('/api/contact', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...Object.fromEntries(fields), token: config.token }),
          signal: AbortSignal.timeout(20000),
        });
        const outcome = await response.json();
        if (!response.ok || !outcome.ok) throw new Error(outcome.error || 'Sending could not be confirmed. Please retry or email us directly.');
        status.textContent = 'Your inquiry has been sent to Tech Traversers. Thank you.';
        // Keep the existing accessible result region and its completion animation.
        result.hidden = false;
        result.querySelector('h2').lastChild.textContent = 'Inquiry sent';
        result.querySelector('p').textContent = 'Thank you for getting in touch. You can reply to our response by email.';
        for (const child of result.children) if (!['H2', 'P'].includes(child.tagName) || child.id === 'copy-help') child.hidden = true;
        form.hidden = true;
        document.getElementById('quote-result-heading').focus();
      } catch (error) {
        status.textContent = error.name === 'TimeoutError' || error.name === 'TypeError'
          ? 'Sending could not be confirmed. Your message is still here. Retry or email traversertech@gmail.com.' : error.message;
      } finally {
        busy = false;
        submit.disabled = false;
        form.removeAttribute('aria-busy');
      }
      return;
    }
    const body = [
      'Hi Levi,', '',
      `I would like to discuss: ${service.value}`, '',
      String(fields.get('details')).trim(), '',
      `Preferred timing: ${String(fields.get('timing')).trim() || 'To discuss'}`,
      `Name: ${String(fields.get('name')).trim()}`,
      `Reply email: ${String(fields.get('email')).trim()}`,
    ].join('\n');
    draft.value = body;
    emailLink.href = 'mailto:traversertech@gmail.com?subject=' +
      encodeURIComponent('Project inquiry: ' + service.value) + '&body=' + encodeURIComponent(body);
    result.hidden = false;
    status.textContent = 'Your email draft is ready. Nothing has been sent.';
    document.getElementById('quote-result-heading').focus();
  });
  form.hidden = false;
})();
