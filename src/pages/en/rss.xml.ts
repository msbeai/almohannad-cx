import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { SITE } from '../../site';
import { getArticles, excerpt } from '../../lib/articles';

export async function GET(context: APIContext) {
  const articles = await getArticles('en');
  return rss({
    title: `${SITE.nameEn} — ${SITE.taglineEn}`,
    description: SITE.descriptionEn,
    site: context.site!,
    items: articles.map((a) => ({
      title: a.data.title,
      link: `/en/articles/${a.id.replace(/\.md$/, '')}`,
      description: excerpt(a.body, 300),
      pubDate: a.data.date,
    })),
    customData: '<language>en</language>',
  });
}
