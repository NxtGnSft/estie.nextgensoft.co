export type CategorySlug =
  | 'dining-chairs' | 'dining-tables' | 'bar-stools' | 'lounge-chairs' | 'sofas'
  | 'benches' | 'coffee-tables' | 'nightstands' | 'sideboards-tv-cabinets';

export interface Category {
  slug: CategorySlug;
  title: string;
  blurb: string;
  prefixes: string[];
}

export const CATEGORIES: Category[] = [
  { slug: 'dining-chairs', title: 'Dining Chairs', prefixes: ['DC'],
    blurb: 'Elevate your dining space with our chic and ergonomic dining chairs, expertly designed to blend modern aesthetics with everyday comfort for a seamless dining experience.' },
  { slug: 'dining-tables', title: 'Dining Tables', prefixes: ['DT'],
    blurb: 'An exquisite centerpiece for every meal. Our dining tables combine sleek craftsmanship with timeless elegance, designed to inspire gatherings at everyday dinners and special occasions.' },
  { slug: 'bar-stools', title: 'Bar Stools', prefixes: ['BT'],
    blurb: 'Sleek, sturdy, and stylish. Perfect for kitchens, bars, or casual dining, blending comfort and contemporary design effortlessly.' },
  { slug: 'lounge-chairs', title: 'Lounge Chairs', prefixes: ['LC'],
    blurb: 'Unwind in elegance. Contemporary design and soft cushions provide the ideal mix of comfort and sophistication for relaxation whenever you need it.' },
  { slug: 'sofas', title: 'Sofas', prefixes: ['SF'],
    blurb: 'Cozy meets chic. Upholstered in soft, textured fabrics and supported by natural wood legs, the modular design adapts effortlessly to your space.' },
  { slug: 'benches', title: 'Benches', prefixes: ['BC'],
    blurb: 'Solid teak benches, with rope, rattan, or upholstered seats, for dining tables, entryways, and bedroom ends.' },
  { slug: 'coffee-tables', title: 'Coffee Tables', prefixes: ['CT'],
    blurb: 'Sleek design meets practicality. Perfect for lounging, entertaining, or displaying decor, a functional centerpiece with timeless appeal.' },
  { slug: 'nightstands', title: 'Nightstands', prefixes: ['NS'],
    blurb: 'Sleek, functional, and designed for modern living. Convenient storage and a chic aesthetic for your nightly essentials.' },
  { slug: 'sideboards-tv-cabinets', title: 'Sideboards & TV Cabinets', prefixes: ['SB', 'TC'],
    blurb: 'Sophisticated storage with contemporary aesthetics. Dual-purpose pieces that move from entertainment system to elegant dining storage.' },
];

export const categoryBySlug = (slug: string): Category => {
  const c = CATEGORIES.find((c) => c.slug === slug);
  if (!c) throw new Error(`Unknown category: ${slug}`);
  return c;
};
