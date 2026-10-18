# Tech Traversers Improvement Tasklist

## Completed in this update

- [x] Optimize phone banner downloads, mobile spacing, quote-form controls, safe areas, and touch targets; cover narrow and landscape layouts in browser checks.

- [x] Move repository images to the synced Documents/Tech Traversers/pictures folder and replace public image references with verified Google Drive image URLs.

- [x] Add prominent contact buttons and a static quote form with email drafting, webmail fallback, and service preselection.
- [ ] Add customer testimonials when approved quotes and attribution are supplied.
- [ ] Assess actual inquiry volume after release; direct website submissions require a configured form endpoint.

- [x] Add Microsoft Clarity project yzgnnv7sl9 to all public pages with CSP and Trusted Types compatibility.

- [x] Extend Schema.org JSON-LD to all ten public pages, including service, profile, and software entities; validate references, metadata, and CSP hashes.

- [x] Install the owner-provided Google Analytics tag across all public pages and verify page views without polluting reports.

- [x] Simplify mobile navigation and page layouts with compact headers, a labeled menu, consistent spacing, and subtle blue accents.

- [x] Review sitemap coverage and canonical URLs; record modification dates for the updated public pages.

- [x] Remove blocking style/script requests, enforce a hash-based CSP, add structured data, and check generated assets in CI.
- [ ] Configure longer asset caching and HSTS, COOP, and clickjacking response headers through a configurable host/CDN.
- [ ] Complete a human screen-reader review; automated keyboard tests cover navigation and focus behavior.

- [x] Compress original banner photos to WebP, preload the matching banner, and initialize mobile navigation before main content to reduce loading delays and layout shifts.

- [x] Clarify Buffalo, Wyoming as the base, with remote services available worldwide.

- [x] Enlarge desktop menu links, separate desktop sections, and consolidate contact content into a defined site footer.

- [x] Update biography and project experience, remove C++ and small-app limits, and add website development and maintenance.

- [x] Keep the original photo headers with top navigation, full-width content, and restrained styling.

- [x] Simplify typography, colors, service sections, profiles, and contact areas around the original photo header.

- [x] Embed navigation in each page so JavaScript and fetch failures do not remove it.
- [x] Add mobile menu keyboard support, hidden-state handling, focus restoration, and responsive focus behavior.
- [x] Fix nested interactive elements and heading hierarchy; add skip links and visible focus styles.
- [x] Keep original photo banners as requested; remove repeated service illustrations from the homepage.
- [x] Remove duplicated mobile images, obsolete per-page styles/scripts, and tracked OS metadata.
- [x] Make contact actions and service-area language consistent across public pages.
- [x] Remove public prices for the current copy revision; keep previously approved contact email only.
- [x] Clarify scope, estimated hours, delivery timing, compatibility, and maintenance.
- [x] Add a contact-based Wood Bank Software page with owner-confirmed features and Clear Creek Wood Bank usage.
- [x] Link the software page from the homepage, services page, and shared navigation.
- [x] Add unique descriptions, canonical URLs, Open Graph and Twitter metadata.
- [x] Add robots.txt, informational bots.txt, and a ten-page sitemap.xml.
- [x] Redirect the old development page home and mark it noindex.
- [x] Replace unrelated AGENTS.md instructions with relevant maintenance guidance.
- [x] Add static checks, menu regression tests, a browser suite, and a pull request check workflow.
- [x] Update documentation and record owner decisions in OWNER-NOTES.md.

## Owner decisions and release verification

- [ ] Review billing increments, minimum charges, estimates, and approval for extra hours.
- [ ] Confirm Wood Bank Software access/licensing terms, setup requirements, and support expectations.
- [ ] Optionally supply a product name, approved screenshots, and supported platforms for the contact page.
- [ ] Confirm DNS, HTTPS enforcement, and apex-to-www redirection in GitHub Pages.
- [x] Run the browser suite across all ten pages at four widths and inspect desktop/mobile screenshots.
- [ ] Review contrast, layout, and assistive-technology behavior in real browsers.
- [ ] Inspect social sharing previews and decide on a branded preview image.
- [ ] Review pull request checks before merging; verify the live site after publishing.
