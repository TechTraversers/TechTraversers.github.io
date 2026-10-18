# Decisions for the site owner

## Public copy and approvals

Current service areas are website development, website maintenance, custom software, automation, and general IT help. The business is based in Buffalo, Wyoming, with remote services available worldwide and local in-person help by arrangement. Public copy no longer advertises C++ work or limits development to small applications.

The owner supplied updated background and asked for a practical, friendly, professional voice. Project descriptions distinguish software in use from redesign work not adopted by the customer. The wood bank role is specifically software development.

Public prices are removed from this revision. The previously approved business email remains; no new contact information or customer testimonials are added. Personal schedules and other private background are not included.

## Wood Bank Software

The contact-based page says that the application is currently used by Clear Creek Wood Bank and is available for interested organizations. It lists the owner-confirmed features: hours tracking, wood tracking, donation tracking, advanced analysis, spreadsheet exports, and extensive controls geared toward wood banks. Inquiries go to your existing email address.

Useful next additions are the actual product name, screenshots with private data removed, and supported operating systems. No demo, repository link, or download is advertised; the owner chose a contact-based page. The page does not invent scheduling, integrations, security guarantees, or other unconfirmed capabilities.

Availability is not described as free, open source, or a particular license. Choose access and licensing terms, setup requirements, and ongoing support expectations before offering a public download. Access and service costs are discussed privately rather than published.

## Visual design

The original programming-language image header and centered Tech Traversers title are restored. Services and Software Development use their original page-specific banner images. The content keeps top navigation and a full-width layout, with blue links, conventional typography, simple rules, and a white background. Homepage services use three unboxed columns on desktop and a single column on mobile. Contact actions are grouped in a single, full-width dark footer rather than repeated in page-level contact panels. Desktop navigation has larger targets, and light section backgrounds separate the content; mobile retains the simple single-column layout. Decorative monograms, oversized slogans, rounded marketing panels, and feature illustrations are removed from the pages. Pricing and product claims are unchanged.

Restoring the original header also restores its image download size (about 1.55 MB for the default banner); this honors the owner's preference for the original image. The image is preserved without alteration.

## Hosting and discovery

- The canonical origin matches CNAME: https://www.techtraversers.com. Verify DNS, apex-to-www redirection, and GitHub Pages HTTPS enforcement in the hosting account; these could not be confirmed through the available connection.
- robots.txt is the standard crawler file. bots.txt is included as requested but has no standard enforcement role. Both allow crawling and reference sitemap.xml. Neither file protects private data or guarantees indexing.
- The sitemap lists the ten public pages. The old index-dev.html redirects home and is marked noindex.
- The existing pic2.jpg remains the social preview image. Replace it with an approved branded image when available; rendered sharing previews still need checking.

## Repository and downloads

The original large images and downloadable executable are preserved. Public pages use the original photo banners again. The large support image is not loaded by the homepage. Repository storage size has not been reduced by that change.

The original AGENTS.md instructed tools to abandon project work and copy Walden. It has been replaced with relevant site maintenance guidance. Obsolete per-page CSS/JS and the tracked .DS_Store are removed; original downloads and testing media are retained.

BookCatalog.exe was not executed or audited. If you want to promote it later, provide source, a version, supported platforms, and release information before linking it as a trusted download.

## Verification limits

The static checker verifies links, fragments, metadata, headings, shared navigation, crawler files, and sitemap coverage. The menu tests exercise state and focus decisions without a browser. The full Playwright suite also checks rendering at four widths, navigation with JavaScript disabled or blocked, and keyboard behavior.

The current header-restoration update passed the static checker, JavaScript syntax checks, three menu behavior tests, and the full Chromium suite across all ten pages at four widths. Original banner and favicon assets were downloaded, and desktop/mobile homepage screenshots were inspected. Live DNS, HTTPS, social previews, and assistive-technology behavior still need separate confirmation.

## Contact flow update — 2026-10-18

Contact and quote buttons now appear near page introductions, in primary navigation, and in the shared footer. Service pages link to a quote form with their service preselected. The static form prepares a visitor-reviewed email and provides a copyable draft for webmail; it does not submit requests to a server. No third-party form account or endpoint is configured. The public email remains the fallback with JavaScript unavailable.

The owner has no approved testimonials to supply at this time. Keep existing project evidence and add customer quotes only when the wording and attribution are supplied and approved. No response-time, pricing, or outcome guarantees have been added. Conversion improvement should be assessed using actual inquiries after release; draft preparation alone does not prove a lead was sent.

## Image storage update - 2026-10-18

At the owner's request, all 16 image files were moved from the website repository into Documents/Tech Traversers/pictures, which syncs to the Tech Traverser Google Drive account. Destination copies were checked against the originals before repository copies were removed. Only this pictures folder was made publicly viewable, with Viewer access; the Tech Traversers parent folder remains unchanged. The five images used by public pages now load from Google Drive's image host. The image manifest records the original file hashes and cloud IDs. Site image loading now depends on Google Drive access and availability.

## Mobile optimization - 2026-10-18

Phone layouts use a shorter original-photo header, tighter content spacing, full-width primary contact actions, larger service-link targets, and less form padding. Form controls keep a 16px font and explicit email keyboard settings. Safe-area spacing accounts for phone cutouts. Short landscape windows use a compact banner. Phone banners and their preloads request 960px WebP images from the existing Drive files. The measured homepage banner is 63,964 bytes instead of 96,928 bytes (34% less); the services banner is 50,956 bytes instead of 90,536 bytes (44% less). The software banner is already below 960px and remains unchanged. Desktop images and original archived files remain unchanged.
