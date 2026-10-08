import { defineCollection, z } from 'astro:content';
import { file } from 'astro/loaders';

const dimensions = z.union([
  z.object({ raw: z.string().min(1), w: z.number(), d: z.number(), h: z.number() }),
  z.object({ raw: z.string().min(1) }),
]);

const products = defineCollection({
  loader: file('src/data/products.json', {
    parser: (text) => JSON.parse(text).map((p: { slug: string }) => ({ id: p.slug, ...p })),
  }),
  schema: ({ image }) =>
    z.object({
      code: z.string().regex(/^[A-Z]{2}-\d{2}$/),
      slug: z.string(),
      category: z.enum([
        'dining-chairs', 'dining-tables', 'bar-stools', 'lounge-chairs', 'sofas',
        'benches', 'coffee-tables', 'nightstands', 'sideboards-tv-cabinets',
      ]),
      name: z.string().min(2),
      material: z.string().min(2),
      dimensions,
      finish: z.string().nullable(),
      fabric: z.string().nullable(),
      leather: z.string().nullable(),
      image: image(),
      page: z.number().int(),
    }),
});

export const collections = { products };
