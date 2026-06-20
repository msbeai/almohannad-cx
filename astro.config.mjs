// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { visit } from 'unist-util-visit';

/** add loading="lazy" to article images rendered from markdown */
function rehypeLazyImages() {
  return (tree) => {
    visit(tree, 'element', (node) => {
      if (node.tagName === 'img') {
        node.properties.loading = 'lazy';
        node.properties.decoding = 'async';
      }
    });
  };
}

export default defineConfig({
  site: 'https://almohannad.cx',
  trailingSlash: 'ignore',
  integrations: [
    sitemap({
      // keep the backup/recovery blog out of the sitemap (it's noindex)
      filter: (page) => !page.includes('/blog'),
      i18n: {
        defaultLocale: 'ar',
        locales: { ar: 'ar', en: 'en' },
      },
    }),
  ],
  markdown: {
    rehypePlugins: [rehypeLazyImages],
  },
});
