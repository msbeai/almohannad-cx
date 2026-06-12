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

export const collections = {
  ar: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/ar' }),
    schema: articleSchema,
  }),
  en: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/en' }),
    schema: articleSchema,
  }),
};
