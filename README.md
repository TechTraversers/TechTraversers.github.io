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
- Use one descriptive h1, a skip link to `#main-content`, image alt text and dimensions, and a direct contact action in the shared site footer.
- Put shared styles in `style.css`. About/profile styles live in `aboutus/style.css`.
- Match metadata and canonical URLs to the page. Canonical URLs use `https://www.techtraversers.com` and directory paths with trailing slashes.
- Add public pages to `sitemap.xml`. `robots.txt` is the crawler standard; `bots.txt` is an informational companion. Neither controls access to private files.
- Keep prices and service commitments consistent across pages. Do not publish prices without current owner approval. Website development, maintenance, custom software, automation, and IT help are the current service areas.
- See `OWNER-NOTES.md` for business decisions and verification limits. Update `tasklist.md` and `changelog.txt` with releases.

## Images in Google Drive

Website images now load from the public `pictures` folder in Google Drive, synced from `Documents/Tech Traversers/pictures`. Original image files are no longer kept in this repository. `image-assets.json` records all 16 archived files, their Drive IDs and original SHA-256 hashes, and the five public image URLs used by the site. The originals include unused artwork and the old testing image.

Keep the pictures folder accessible to anyone with the link as Viewer. This exposes the image folder only; its parent folder is not shared. Drive preview-page links cannot replace image URLs in HTML or CSS. Verify direct image URLs without a Google session whenever changing them, and update the manifest, CSS, HTML metadata, preload links, and favicons together. Google serves the images through `lh3.googleusercontent.com`, which the CSP permits for images only. WebP banner URLs request WebP output at up to 1920 pixels on desktop and 960 pixels on phones, with matching media-specific preloads to avoid downloading both; PNG favicon and JPEG social-preview URLs preserve their respective formats. Remote availability and sharing settings now affect image loading. Browser checks fetch each image anonymously once, verify its image MIME type, and reuse those real bytes across all layout checks; browser decoding and CSP enforcement still run on every page.

## Embedded assets and security

After editing `style.css`, `aboutus/style.css`, `script.js`, `analytics.js`, `clarity.js`, `contact.js`, page headings/descriptions/canonical URLs, or `scripts/structured_data.py`, run `python scripts/sync_assets.py`. This embeds the shared sources in the public HTML and regenerates CSP hashes. Do not edit generated blocks directly. There is no build step required to serve the checked-in pages. The navigation runs before main content to avoid layout shifts.

Every public page includes Schema.org JSON-LD for the Organization, WebSite, and page, linked by stable canonical IDs. Service detail pages add Service entities, profiles add Person entities within ProfilePage, and Wood Bank Software adds SoftwareApplication. Page names and descriptions come from the existing h1 and meta description. Keep business details in `scripts/structured_data.py` consistent with visible, approved copy. No prices, reviews, or unsupported platform claims are inferred. `check_site.py` checks JSON parsing, entity references, metadata consistency, and CSP hashes; this is local validation, not a guarantee of search rich results. After publishing, check representative URLs with the [Schema.org validator](https://validator.schema.org/) and [Google Rich Results Test](https://search.google.com/test/rich-results).

Every public page includes the asynchronous Google tag for Analytics property `G-YHRY359L0X`. The generated CSP allows Google's Analytics endpoints and the tag's `goog#html` Trusted Types policy while retaining inline-script hashes and Trusted Types enforcement. See [Google's CSP guidance](https://developers.google.com/tag-platform/security/guides/csp). Layout tests stub the external tag; `scripts/analytics_check.py` loads the real tag and intercepts collection requests so test visits do not enter reports.

Every public page also includes Microsoft Clarity project `yzgnnv7sl9`. The generator permits the [Clarity CSP endpoints](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-csp). A restricted default Trusted Types policy accepts only this project tag and versioned Clarity runtime script URLs; HTML and other script URLs remain blocked. Browser layout checks stub Clarity to avoid recording test sessions.

The CSP meta policy restricts resources, disallows unapproved scripts/styles, and enforces Trusted Types in supporting browsers. It cannot set HSTS, COOP, or frame-ancestors. GitHub Pages controls response headers and currently serves assets with a ten-minute cache lifetime. Full header hardening and longer caching require a configurable host/CDN; HTML meta tags and a `_headers` file do not change these GitHub Pages response headers. Keep HTML revalidated; use versioned asset names before setting long immutable asset caching. Stage HSTS after checking all affected domains; do not enable includeSubDomains/preload without reviewing them.

## Contact and quote requests

`/contact/` works on static GitHub Pages without a submission service. The form validates locally and prepares a `mailto:` draft for the visitor to review and send. It never claims an inquiry was submitted or stores form content. A read-only message lets webmail users copy it manually; the business email remains visible if JavaScript or the form enhancement is unavailable. Service-page calls to action preselect a known service via `?service=`; other query values are ignored. Form and draft regions are masked for Clarity.

Edit the form markup in `contact/index.html` and behavior in `contact.js`, then regenerate embedded assets and CSP hashes. A server or configured form service is required before adding direct website submissions. Do not mark draft preparation as a completed lead. Customer testimonials require supplied, approved wording and attribution; the current site uses approved project descriptions instead.

## Checks

These checks use Python's standard library and Node's built-in test runner:

```sh
python3 scripts/sync_assets.py --check
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

On Linux, use `python3 -m playwright install --with-deps chromium` if system dependencies are missing. The browser suite starts a loopback server, checks all eleven public pages at 320, 360, 390, 768, 1024, and 1440 pixels, plus short-screen, landscape, and touch-emulated phone checks, and writes homepage screenshots under ignored `test-results/`. A system browser can be selected with `--executable /usr/bin/chromium`.

The GitHub Actions workflow runs static, menu, and browser checks on pull requests and pushes to main. It validates changes; it does not deploy them.

## Release checklist

1. Run the checks above and inspect the browser screenshots.
2. Review desktop and mobile layouts, keyboard focus, email links, and software details.
3. Confirm sitemap/canonical URLs and any changes to prices or service scope.
4. Check GitHub Pages domain settings, HTTPS, and the apex-domain redirect.
5. Merge only after reviewing the pull request. Confirm the live site after publishing.
