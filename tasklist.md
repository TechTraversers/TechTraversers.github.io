# Tech Traversers Improvement Tasklist

## 1. High Priority (Fix First)

- [x] Fix broken navigation: remove or restore `/downloads/index.html` link in `sidebar.html`.
- [ ] Add sidebar fetch fallback UI for non-HTTP contexts and failed loads.
- [ ] Run full link audit across all pages to remove 404s.
- [ ] Standardize text encoding (fix garbled punctuation in titles, e.g. dashes showing incorrectly).

## 2. Content and Messaging

- [ ] Expand homepage intro with clearer value proposition and service outcomes.
- [ ] Add more specific service details (what is included, response times, limits).
- [ ] Rewrite long dense paragraphs on service pages for readability.
- [ ] Replace/upgrade visuals (including the current AI image)

## 3. Design and UX

- [ ] Add section-level background color treatments on Services page.
- [ ] Improve button hierarchy and consistency (primary vs secondary actions).
- [ ] Add a clear contact call-to-action block on every page.
- [ ] Improve mobile spacing and typography rhythm for long-form text pages.

## 4. Accessibility

- [ ] Verify heading hierarchy (single clear page `h1`, ordered subheadings).
- [ ] Add/validate meaningful `alt` text for all images.
- [ ] Ensure keyboard-visible focus styles for links and buttons.
- [ ] Check color contrast ratios and adjust low-contrast elements.

## 5. SEO and Discovery

- [ ] Add unique meta descriptions for each page.
- [ ] Add Open Graph and Twitter card metadata.
- [ ] Create and publish `sitemap.xml`.
- [ ] Add/update `robots.txt`.

## 6. Performance

- [ ] Compress and resize large images (`Pictures/`) for web delivery.
- [ ] Add lazy loading for non-critical images.
- [ ] Set explicit image dimensions where possible to reduce layout shift.
- [ ] Remove unused CSS/JS and consolidate duplicate styles.

## 7. Maintainability

- [ ] Move repeated header/footer markup into shared includes (same pattern as sidebar).
- [ ] Split CSS into base/layout/page modules with clear ownership.
- [ ] Add a short contributor guide for page structure and naming conventions.
- [ ] Keep `changelog.txt` and `tasklist.md` updated each release.

## 8. QA and Release Process

- [ ] Add a pre-release checklist (links, mobile layout, console errors, accessibility spot-check).
- [ ] Test in current Chrome, Firefox, Edge, Vivaldi, and mobile browsers.
- [ ] Add lightweight smoke tests for critical routes/navigation.
- [ ] Set up preview deployment checks before production publish.
