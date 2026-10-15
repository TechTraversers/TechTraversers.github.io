// Navigation remains usable without JavaScript.
(() => {
  const toggle = document.getElementById('menu-toggle');
  const navigation = document.getElementById('primary-navigation');
  if (!toggle || !navigation) return;
  const mobile = window.matchMedia('(max-width: 768px)');
  let open = false;
  function render() {
    toggle.hidden = !mobile.matches;
    navigation.hidden = mobile.matches && !open;
    toggle.setAttribute('aria-expanded', String(mobile.matches && open));
    toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    document.body.classList.toggle('menu-open', mobile.matches && open);
  }
  function closeMenu(restoreFocus = false) {
    open = false;
    render();
    if (restoreFocus && mobile.matches) toggle.focus();
  }
  toggle.addEventListener('click', () => {
    open = !open;
    render();
    if (open) navigation.querySelector('a')?.focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && open && mobile.matches) {
      event.preventDefault();
      closeMenu(true);
    }
  });
  document.addEventListener('click', event => {
    if (open && mobile.matches && !navigation.contains(event.target) && !toggle.contains(event.target)) {
      closeMenu(navigation.contains(document.activeElement));
    }
  });
  navigation.addEventListener('click', event => {
    if (mobile.matches && event.target.closest('a')) closeMenu(true);
  });
  mobile.addEventListener('change', () => {
    const focused = document.activeElement;
    open = false;
    render();
    if (mobile.matches && navigation.contains(focused)) toggle.focus();
    if (!mobile.matches && focused === toggle) navigation.querySelector('a')?.focus();
  });
  render();
})();
