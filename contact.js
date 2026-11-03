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
  const errors = document.getElementById('quote-errors');
  const fieldsToValidate = [...form.querySelectorAll('[required]')];
  const help = document.getElementById('details-help');
  const details = document.getElementById('quote-details');
  const prompts = {
    'Website development': 'What is your website for, and what should visitors be able to do? Share an existing website link if you have one.',
    'Website maintenance': 'What needs updating or fixing? Include your website link and what you would like to change.',
    'Custom software and automation': 'What task takes too much time? Describe how you do it now and what you would like to make easier.',
    'IT help': 'What device or software are you using, and what is going wrong? Please leave out passwords.',
    'Wood Bank Software': 'Tell me about your organization and how you manage check-ins or volunteer time today.',
  };
  function describeService() {
    help.textContent = prompts[service.value] || 'What would you like to do, improve, or fix? A few sentences are enough to start.';
  }
  describeService();
  service.addEventListener('change', describeService);
  details.addEventListener('input', () => {
    document.getElementById('details-count').textContent = `${details.value.length.toLocaleString()} / 1,500 characters`;
  });
  // Inline errors and a linked summary complement native validity rules.
  form.noValidate = true;
  function clearErrors() {
    errors.hidden = true;
    errors.querySelector('ul').replaceChildren();
    for (const field of fieldsToValidate) {
      field.removeAttribute('aria-invalid');
      const id = field.id + '-error';
      document.getElementById(id)?.remove();
      const remaining = (field.getAttribute('aria-describedby') || '').split(' ').filter(value => value && value !== id);
      if (remaining.length) field.setAttribute('aria-describedby', remaining.join(' '));
      else field.removeAttribute('aria-describedby');
    }
  }
  function validate() {
    clearErrors();
    for (const field of fieldsToValidate) {
      if (field.validity.valid && field.value.trim()) continue;
      const label = document.querySelector(`label[for="${field.id}"]`).textContent;
      const message = field.type === 'email' && field.validity.typeMismatch
        ? 'Enter an email address in the format name@example.com.'
        : field === service ? 'Choose a service, or select Not sure yet.' : `Please complete: ${label.toLowerCase()}.`;
      field.setAttribute('aria-invalid', 'true');
      const error = document.createElement('p');
      error.id = field.id + '-error';
      error.className = 'field-error';
      error.textContent = message;
      field.insertAdjacentElement('afterend', error);
      field.setAttribute('aria-describedby', [field.getAttribute('aria-describedby'), error.id].filter(Boolean).join(' '));
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + field.id;
      link.textContent = message;
      link.addEventListener('click', event => { event.preventDefault(); field.focus(); });
      item.append(link);
      errors.querySelector('ul').append(item);
    }
    if (!errors.querySelector('li')) return true;
    errors.hidden = false;
    errors.focus();
    return false;
  }
  document.getElementById('copy-message').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(draft.value);
      status.textContent = 'Message copied. Paste it into your email app to send it.';
    } catch {
      draft.focus();
      draft.select();
      status.textContent = 'Select and copy the message, then paste it into your email app.';
    }
  });
  let config = null;
  let configLoadedAt = Date.now();
  let busy = false;
  if (document.querySelector('meta[name="contact-api"]')) fetch('/api/contact/config', { cache: 'no-store' }).then(response => response.ok ? response.json() : null).then(value => {
    if (!value?.enabled) return;
    config = value;
    configLoadedAt = Date.now();
    submit.textContent = 'Send inquiry';
    document.getElementById('quote-instructions').textContent = 'Share a little about what you need. Send your inquiry directly to Tech Traversers.';
    document.getElementById('quote-delivery-note').textContent = 'Your message is delivered by email using Resend.';
  }).catch(() => {});

  form.addEventListener('input', () => {
    if (busy) return;
    status.removeAttribute('data-state');
    clearErrors();
    result.hidden = true;
    emailLink.removeAttribute('href');
    draft.value = '';
    status.textContent = '';
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !validate()) return;
    const fields = new FormData(form);
    if (config) {
      busy = true;
      submit.disabled = true;
      submit.textContent = 'Sending…';
      form.querySelectorAll('fieldset').forEach(fieldset => { fieldset.disabled = true; });
      status.dataset.state = 'sending';
      form.setAttribute('aria-busy', 'true');
      status.textContent = 'Sending your inquiry…';
      try {
        // Refresh the signed form token after long editing sessions.
        if (Date.now() - configLoadedAt > 45 * 60 * 1000) {
          const refreshed = await fetch('/api/contact/config', { cache: 'no-store' });
          const next = await refreshed.json();
          if (!refreshed.ok || !next.enabled) throw new Error('Sending is temporarily unavailable. Your message is still here; please email us directly.');
          config = next;
          configLoadedAt = Date.now();
          // The server rejects tokens younger than two seconds.
          await new Promise(resolve => setTimeout(resolve, 2100));
        }
        const response = await fetch('/api/contact', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...Object.fromEntries(fields), token: config.token }),
          signal: AbortSignal.timeout(20000),
        });
        const outcome = await response.json();
        if (!response.ok || !outcome.ok) throw new Error(outcome.error || 'Sending could not be confirmed. Please retry or email us directly.');
        status.dataset.state = 'success';
        status.textContent = 'Your inquiry has been sent to Tech Traversers. Thank you.';
        // Keep the existing accessible result region and its completion animation.
        result.hidden = false;
        result.querySelector('h2').lastChild.textContent = 'Inquiry sent';
        result.querySelector('p').textContent = 'Thank you for getting in touch. You can reply to our response by email.';
        for (const child of result.children) if (!['H2', 'P'].includes(child.tagName) || child.id === 'copy-help') child.hidden = true;
        form.hidden = true;
        document.getElementById('quote-result-heading').focus();
      } catch (error) {
        status.dataset.state = 'error';
        status.textContent = error.name === 'TimeoutError' || error.name === 'TypeError'
          ? 'Sending could not be confirmed. Your message is still here. Retry or email traversertech@gmail.com.' : error.message;
        status.focus();
      } finally {
        busy = false;
        submit.disabled = false;
        submit.textContent = 'Send inquiry';
        form.querySelectorAll('fieldset').forEach(fieldset => { fieldset.disabled = false; });
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
