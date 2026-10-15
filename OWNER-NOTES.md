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

The original programming-language image header and centered Tech Traversers title are restored. Services and Software Development use their original page-specific banner images. The content uses blue links, a desktop sidebar, conventional typography, simple rules, and a white background. Decorative monograms, oversized slogans, rounded marketing panels, and feature illustrations are removed from the pages. Pricing and product claims are unchanged.

Restoring the original header also restores its image download size (about 1.55 MB for the default banner); this honors the owner's preference for the original image. The image is preserved without alteration.

## Hosting and discovery

- The canonical origin matches CNAME: https://www.techtraversers.com. Verify DNS, apex-to-www redirection, and GitHub Pages HTTPS enforcement in the hosting account; these could not be confirmed through the available connection.
- robots.txt is the standard crawler file. bots.txt is included as requested but has no standard enforcement role. Both allow crawling and reference sitemap.xml. Neither file protects private data or guarantees indexing.
- The sitemap lists the nine public pages. The old index-dev.html redirects home and is marked noindex.
- The existing pic2.jpg remains the social preview image. Replace it with an approved branded image when available; rendered sharing previews still need checking.

## Repository and downloads

The original large images and downloadable executable are preserved. Public pages use the original photo banners again. The large support image is not loaded by the homepage. Repository storage size has not been reduced by that change.

The original AGENTS.md instructed tools to abandon project work and copy Walden. It has been replaced with relevant site maintenance guidance. Obsolete per-page CSS/JS and the tracked .DS_Store are removed; original downloads and testing media are retained.

BookCatalog.exe was not executed or audited. If you want to promote it later, provide source, a version, supported platforms, and release information before linking it as a trusted download.

## Verification limits

The static checker verifies links, fragments, metadata, headings, shared navigation, crawler files, and sitemap coverage. The menu tests exercise state and focus decisions without a browser. The full Playwright suite also checks rendering at four widths, navigation with JavaScript disabled or blocked, and keyboard behavior.

The current header-restoration update passed the static checker, JavaScript syntax checks, three menu behavior tests, and the full Chromium suite across all nine pages at four widths. Original banner and favicon assets were downloaded, and desktop/mobile homepage screenshots were inspected. Live DNS, HTTPS, social previews, and assistive-technology behavior still need separate confirmation.
