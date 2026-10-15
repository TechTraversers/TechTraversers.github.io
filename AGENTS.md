# Working on Tech Traversers

This is a static HTML, CSS, and JavaScript site hosted with GitHub Pages. Keep it usable without a build step or JavaScript.

- Read README.md for local preview and checks.
- Keep primary navigation in the HTML. sidebar.html is the reference markup; update each page when it changes.
- Use one page-specific h1, descriptive links, keyboard-visible focus, and a contact action on every public page.
- Keep prices, service coverage, and business commitments unchanged unless the task authorizes changing them. Flag business decisions for the owner.
- Use https://www.techtraversers.com as the canonical origin and directory URLs with trailing slashes. Update sitemap.xml when adding or removing public pages.
- Run python3 scripts/check_site.py, node --check script.js, and node scripts/menu_check.cjs before proposing a change. Run browser checks when dependencies are available; report checks that could not run.
- Keep changelog.txt and tasklist.md current. Do not merge a pull request or publish a deployment unless requested.

- Current public-copy policy: do not add age, personal schedules, new contact details, prices, or customer testimonials without owner approval. The existing business email is approved. Do not describe C++ as a current service or limit the business to small apps.
