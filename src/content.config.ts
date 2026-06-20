import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const articleSchema = z.object({
  title: z.string(),
  titleAr: z.string(),
  titleEn: z.string(),
  theme: z.enum(['cx', 'research']),
  order: z.number(),
  linkedin: z.string().optional(),
  date: z.coerce.date().optional(),
});

// Write-first backup of the Thmanyah blog: write posts here as Markdown
// (they're versioned in git = your backup), then publish them to Thmanyah.
const blogSchema = z.object({
  title: z.string(),
  date: z.coerce.date(),
  description: z.string().optional(),
  cover: z.string().optional(),
  tags: z.array(z.string()).optional(),
  thmanyahUrl: z.string().optional(),
  draft: z.boolean().optional(),
});

export const collections = {
  ar: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/ar' }),
    schema: articleSchema,
  }),
  en: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/en' }),
    schema: articleSchema,
  }),
  blog: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
    schema: blogSchema,
  }),
};
