import { getCollection, type CollectionEntry } from 'astro:content';
import type { Lang } from '../site';

export type Article = CollectionEntry<'ar'> | CollectionEntry<'en'>;

/** strip markdown syntax for plain-text excerpts */
export function excerpt(body: string | undefined, max = 220): string {
  if (!body) return '';
  const text = body
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^#+\s.*$/gm, '')
    .replace(/[*_>`#]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  const cut = text.slice(0, max);
  return cut.length < text.length ? cut.slice(0, cut.lastIndexOf(' ')) + '…' : cut;
}

export function readingMinutes(body: string | undefined): number {
  if (!body) return 1;
  return Math.max(1, Math.round(body.split(/\s+/).length / 200));
}

/** newest dated first, then by theme order descending (later articles are more mature) */
export function sortArticles<T extends Article>(items: T[]): T[] {
  return [...items].sort((a, b) => {
    const da = a.data.date?.getTime() ?? 0;
    const db = b.data.date?.getTime() ?? 0;
    if (da !== db) return db - da;
    return b.data.order - a.data.order;
  });
}

export async function getArticles(lang: Lang) {
  const items = await getCollection(lang);
  return sortArticles(items);
}
