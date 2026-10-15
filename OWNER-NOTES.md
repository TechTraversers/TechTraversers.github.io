# Decisions for the site owner

## Pricing

The public rate is now $25 per hour for IT help and custom development. Fixed app prices have been removed. Discuss scope, estimated working hours, and delivery time before starting work.

This is a customer billing rate, not take-home pay. One billed hour plus 30 minutes of unpaid admin time brings $25 down to about $16.67 per hour of total work, before expenses and taxes. Travel, research, testing, email, and follow-up can change the effective rate further.

Decide on a minimum charge, billing increments, whether estimates include testing and communication, and when a customer needs to approve extra hours. Track actual project time before promising delivery dates or tightening estimates. These policies have not been invented for the public site.

## Wood Bank Software

The contact-based page says that the application is currently used by Clear Creek Wood Bank and is available for interested organizations. It lists the owner-confirmed features: hours tracking, wood tracking, donation tracking, advanced analysis, spreadsheet exports, and extensive controls geared toward wood banks. Inquiries go to your existing email address.

Useful next additions are the actual product name, screenshots with private data removed, and supported operating systems. No demo, repository link, or download is advertised; the owner chose a contact-based page. The page does not invent scheduling, integrations, security guarantees, or other unconfirmed capabilities.

Availability is not described as free, open source, or a particular license. Choose access and licensing terms, setup requirements, and ongoing support expectations before offering a public download. The $25 service rate is distinguished from any software access costs, which remain a discussion with you.

## Visual design

All nine pages share a warm neutral palette, forest-green accents, a compact branded masthead, horizontal desktop navigation, larger headings, and consistent cards and buttons. The homepage and contact panels have clearer visual hierarchy. The Wood Bank Software page has a lightweight firewood illustration and feature grid. System fonts keep the design independent of external font services. Prices, product features, and contact-based access remain unchanged.

Rendered layout still needs browser verification because this environment blocks Chromium and local sockets.

## Hosting and discovery

- The canonical origin matches CNAME: https://www.techtraversers.com. Verify DNS, apex-to-www redirection, and GitHub Pages HTTPS enforcement in the hosting account; these could not be confirmed through the available connection.
- robots.txt is the standard crawler file. bots.txt is included as requested but has no standard enforcement role. Both allow crawling and reference sitemap.xml. Neither file protects private data or guarantees indexing.
- The sitemap lists the nine public pages. The old index-dev.html redirects home and is marked noindex.
- The existing pic2.jpg remains the social preview image. Replace it with an approved branded image when available; rendered sharing previews still need checking.

## Repository and downloads

The original large images and downloadable executable are preserved. Public pages use small SVG graphics instead of downloading the large hero and support images. Repository storage size has not been reduced by that change.

The original AGENTS.md instructed tools to abandon project work and copy Walden. It has been replaced with relevant site maintenance guidance. Obsolete per-page CSS/JS and the tracked .DS_Store are removed; original downloads and testing media are retained.

BookCatalog.exe was not executed or audited. If you want to promote it later, provide source, a version, supported platforms, and release information before linking it as a trusted download.

## Verification limits

The static checker verifies links, fragments, metadata, headings, shared navigation, crawler files, and sitemap coverage. The menu tests exercise state and focus decisions without a browser. The full Playwright suite also checks rendering at four widths, navigation with JavaScript disabled or blocked, and keyboard behavior.

The managed environment prevented local sockets and Chromium startup, so the full browser suite could not run here. Original binary assets could not be downloaded through the text-only GitHub connector; their existence was checked against the source revision inventory. Run the full checks from a complete checkout or inspect the pull request checks before merging. Live DNS, HTTPS, visual appearance, and social previews still need confirmation.
