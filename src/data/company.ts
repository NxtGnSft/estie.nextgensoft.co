export const COMPANY = {
  name: 'Estie Kusuma Indonesia',
  legalName: 'PT. Estie Kusuma Indonesia',
  tagline: 'Export-quality teak furniture, made in Indonesia.',
  address: ['Puspanjolo Barat Raya 71-73', 'Semarang', 'Indonesia'],
  phoneDisplay: '+62 813 9119 9692',
  phoneE164: '6281391199692',
  email: 'ekusumaindonesia@gmail.com',
  pdf: '/ESTIE-KUSUMA-catalog.pdf',
} as const;

export const waLink = (message = 'Hello, I would like to ask about your furniture catalog.'): string =>
  `https://wa.me/${COMPANY.phoneE164}?text=${encodeURIComponent(message)}`;

export const productWaLink = (code: string, name: string): string =>
  waLink(`Hello, I'm interested in ${code} ${name}. Could you share availability, finish options and pricing?`);
