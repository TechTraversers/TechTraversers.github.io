// Exercise the shipped navigation script without browser or network dependencies.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function fixture(isMobile) {
  const documentListeners = new Map();
  const classes = new Set();
  const document = {
    activeElement: null,
    addEventListener: (name, callback) => documentListeners.set(name, callback),
    body: { classList: { toggle: (name, enabled) => enabled ? classes.add(name) : classes.delete(name) } },
  };
  function element() {
    const handlers = new Map();
    return {
      hidden: false,
      attributes: {},
      children: [],
      addEventListener: (event, callback) => handlers.set(event, callback),
      setAttribute(name, value) { this.attributes[name] = value; },
      focus() { document.activeElement = this; },
      contains(target) { return target === this || this.children.includes(target); },
      dispatch(name, event = {}) { handlers.get(name)?.(event); },
    };
  }
  const toggle = element();
  const nav = element();
  const link = element();
  link.closest = selector => selector === 'a' ? link : null;
  nav.children = [link];
  nav.querySelector = () => link;
  document.getElementById = id => id === 'menu-toggle' ? toggle : nav;
  let resize;
  const media = { matches: isMobile, addEventListener: (_, callback) => { resize = callback; } };
  // No fetch exists in this context: navigation must never require a request.
  vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname, '..', 'script.js'), 'utf8'), {
    document, window: { matchMedia: () => media },
  });
  return {
    document, nav, toggle, link, classes,
    resize(value) { media.matches = value; resize(); },
    event(name, event) { documentListeners.get(name)?.(event); },
  };
}

test('mobile menu opens, focuses a link, and closes on Escape with focus restored', () => {
  const f = fixture(true);
  assert.equal(f.nav.hidden, true);
  assert.equal(f.toggle.hidden, false);
  f.toggle.dispatch('click');
  assert.equal(f.nav.hidden, false);
  assert.equal(f.toggle.attributes['aria-expanded'], 'true');
  assert.equal(f.document.activeElement, f.link);
  let prevented = false;
  f.event('keydown', { key: 'Escape', preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(f.nav.hidden, true);
  assert.equal(f.document.activeElement, f.toggle);
  assert.equal(f.toggle.attributes['aria-expanded'], 'false');
});

test('link and outside clicks close the menu; toggle clicks do not immediately close it', () => {
  const f = fixture(true);
  f.toggle.dispatch('click');
  f.event('click', { target: f.toggle });
  assert.equal(f.nav.hidden, false);
  f.nav.dispatch('click', { target: f.link });
  assert.equal(f.nav.hidden, true);
  f.toggle.dispatch('click');
  f.event('click', { target: {} });
  assert.equal(f.nav.hidden, true);
  assert.equal(f.document.activeElement, f.toggle);
});

test('responsive layout changes preserve visible focus and desktop navigation', () => {
  const f = fixture(false);
  assert.equal(f.toggle.hidden, true);
  assert.equal(f.nav.hidden, false);
  f.link.focus();
  f.resize(true);
  assert.equal(f.nav.hidden, true);
  assert.equal(f.document.activeElement, f.toggle);
  f.toggle.dispatch('click');
  f.toggle.focus();
  f.resize(false);
  assert.equal(f.nav.hidden, false);
  assert.equal(f.toggle.hidden, true);
  assert.equal(f.document.activeElement, f.link);
  assert.equal(f.classes.has('menu-open'), false);
});
