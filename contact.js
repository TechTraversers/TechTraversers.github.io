// Prepare a visitor-reviewed email; no form data is sent to a server.
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

  form.addEventListener('input', () => {
    result.hidden = true;
    emailLink.removeAttribute('href');
    draft.value = '';
    status.textContent = '';
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const fields = new FormData(form);
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
