import { readFile, mkdir, copyFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
const root = resolve(import.meta.dirname, '..');
const sitemap = await readFile(resolve(root, 'sitemap.xml'), 'utf8');
const files = ['robots.txt', 'sitemap.xml', 'style.css', 'aboutus/style.css', 'script.js', 'contact.js'];
for (const match of sitemap.matchAll(/<loc>(.*?)<\/loc>/g)) {
  files.push(new URL(match[1]).pathname.slice(1) + 'index.html');
}
for (const file of files) {
  const target = resolve(root, 'public', file);
  await mkdir(dirname(target), { recursive: true });
  await copyFile(resolve(root, file), target);
}
console.log(`Prepared ${files.length} public files; source and secrets are not served.`);
