import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { SITE } from '../site';
import { getArticles, excerpt } from '../lib/articles';

export async function GET(context: APIContext) {
  const articles = await getArticles('ar');
  return rss({
    title: `${SITE.nameAr} — ${SITE.taglineAr}`,
    description: SITE.descriptionAr,
    site: context.site!,
    items: articles.map((a) => ({
      title: a.data.title,
      link: `/articles/${a.id.replace(/\.md$/, '')}`,
      description: excerpt(a.body, 300),
      pubDate: a.data.date,
    })),
    customData: '<language>ar</language>',
  });
}
