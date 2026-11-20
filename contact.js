// Submit from the website to the CRM's public quote endpoint.
(() => {
  const form = document.getElementById('quote-form');
  if (!form) return;
  const service = document.getElementById('quote-service');
  const requested = new URLSearchParams(location.search).get('service');
  if (Array.from(service.options).some(option => option.value === requested)) service.value = requested;
  const result = document.getElementById('quote-result');
  const heading = document.getElementById('quote-result-heading');
  const status = document.getElementById('quote-status');
  const submit = form.querySelector('button[type="submit"]');
  const preference = document.getElementById('quote-preference');
  const phone = document.getElementById('quote-phone');
  let busy = false;
  let key = crypto.randomUUID();
  const updatePhone = () => { phone.required = preference.value === 'Phone'; };
  preference.addEventListener('change', updatePhone);
  updatePhone();
  form.addEventListener('input', () => {
    if (busy) return;
    key = crypto.randomUUID();
    result.hidden = true;
    status.textContent = '';
    status.setAttribute('role', 'status');
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    busy = true;
    submit.disabled = true;
    submit.textContent = 'Submitting…';
    form.setAttribute('aria-busy', 'true');
    result.hidden = true;
    status.setAttribute('role', 'status');
    status.textContent = 'Sending your request securely…';
    const fields = new FormData(form);
    const timing = String(fields.get('timing') || '').trim();
    const payload = {
      name: String(fields.get('name') || '').trim(),
      business: String(fields.get('business') || '').trim(),
      email: String(fields.get('email') || '').trim(),
      phone: String(fields.get('phone') || '').trim(),
      service: service.value,
      description: String(fields.get('details') || '').trim() + (timing ? '\n\nPreferred timing: ' + timing : ''),
      preferred_contact: preference.value,
      website: String(fields.get('website') || ''),
      idempotency_key: key,
    };
    try {
      const response = await fetch('https://portal.techtraversers.com/api/public/quote', {
        method: 'POST', mode: 'cors', credentials: 'omit',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload), signal: AbortSignal.timeout(20000),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Your request could not be submitted. Please try again.');
      heading.textContent = response.status === 202 ? 'Check your email to confirm your request' : 'Your quote request has been received';
      document.getElementById('quote-result-message').textContent = data.message;
      result.hidden = false;
      status.textContent = response.status === 202 ? 'Verification email requested. Open the link in your inbox to confirm your quote request.' : 'Your quote request has been saved.';
      for (const control of form.elements) control.disabled = true;
      heading.focus();
    } catch (error) {
      status.setAttribute('role', 'alert');
      status.textContent = error.name === 'TimeoutError' ? 'The request timed out. Your details are still here; retrying will not create a duplicate request.' : error.message || 'Could not connect. Please try again or email us directly.';
      submit.disabled = false;
    } finally {
      busy = false;
      submit.textContent = 'Submit quote request';
      form.removeAttribute('aria-busy');
    }
  });
  document.getElementById('quote-again').addEventListener('click', () => {
    for (const control of form.elements) control.disabled = false;
    form.reset();
    updatePhone();
    key = crypto.randomUUID();
    result.hidden = true;
    status.textContent = '';
    form.querySelector('input').focus();
  });
  form.hidden = false;
})();
