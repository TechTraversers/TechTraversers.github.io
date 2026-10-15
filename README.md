# Tech Traversers Website

A static business website for IT help, custom software and automation, and Wood Bank Software. GitHub Pages serves the HTML, CSS, and JavaScript directly; no build step is required.

## Local preview

From the repository folder:

```sh
python3 -m http.server 8000
```

On Windows, use `python` if `python3` is unavailable. Open http://localhost:8000. Navigation is included in the HTML and remains available if JavaScript is disabled. Root-relative links require serving the repository at the origin root; opening HTML files directly is not a supported preview.

## Editing pages

- Keep the primary navigation in every page. `sidebar.html` is the reference snippet; update matching navigation markup on all public pages when it changes. Each page uses `aria-current="page"` on its active section.
- Use one descriptive h1, a skip link to `#main-content`, image alt text and dimensions, and a direct contact action.
- Put shared styles in `style.css`. About/profile styles live in `aboutus/style.css`.
- Match metadata and canonical URLs to the page. Canonical URLs use `https://www.techtraversers.com` and directory paths with trailing slashes.
- Add public pages to `sitemap.xml`. `robots.txt` is the crawler standard; `bots.txt` is an informational companion. Neither controls access to private files.
- Keep prices and service commitments consistent across pages. Do not publish prices without current owner approval. Website development, maintenance, custom software, automation, and IT help are the current service areas.
- See `OWNER-NOTES.md` for business decisions and verification limits. Update `tasklist.md` and `changelog.txt` with releases.

## Checks

These checks use Python's standard library and Node's built-in test runner:

```sh
python3 scripts/check_site.py
node --check script.js
node scripts/menu_check.cjs
```

For browser checks in a complete checkout:

```sh
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium
python3 scripts/browser_check.py
```

On Linux, use `python3 -m playwright install --with-deps chromium` if system dependencies are missing. The browser suite starts a loopback server, checks all ten public pages at 360, 768, 1024, and 1440 pixels, and writes homepage screenshots under ignored `test-results/`. A system browser can be selected with `--executable /usr/bin/chromium`.

The GitHub Actions workflow runs static, menu, and browser checks on pull requests and pushes to main. It validates changes; it does not deploy them.

## Release checklist

1. Run the checks above and inspect the browser screenshots.
2. Review desktop and mobile layouts, keyboard focus, email links, and software details.
3. Confirm sitemap/canonical URLs and any changes to prices or service scope.
4. Check GitHub Pages domain settings, HTTPS, and the apex-domain redirect.
5. Merge only after reviewing the pull request. Confirm the live site after publishing.
