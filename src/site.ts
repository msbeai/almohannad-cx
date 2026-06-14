export const SITE = {
  domain: 'almohannad.cx',
  nameAr: 'المهند السبيعي',
  nameEn: 'Almohannad Alsbeai',
  taglineAr: 'قائد تجربة عملاء، مؤلف ومتحدث',
  taglineEn: 'Customer experience leader, author & speaker',
  descriptionAr:
    'الموقع الشخصي للمهند السبيعي — مقالات وكتب وحوارات في تجربة العميل والأبحاث التسويقية، بالعربية.',
  descriptionEn:
    'Personal site of Almohannad Alsbeai — articles, books, and podcast conversations on customer experience and marketing research.',
  linkedin: 'https://www.linkedin.com/in/almohannadalsbeai',
  linkedinAuthor: 'https://www.linkedin.com/today/author/almohannadalsbeai',
  // Newsletter: Netlify Forms captures subscribers until an external tool is chosen.
  // When ready, replace form action/handling in src/components/NewsletterForm.astro.
};

export const THEMES = {
  cx: { ar: 'تجربة العميل', en: 'Customer Experience' },
  research: { ar: 'الأبحاث التسويقية والمؤشرات', en: 'Marketing Research & Metrics' },
} as const;

export type Lang = 'ar' | 'en';

export const T = {
  ar: {
    nav: [
      { href: '/', label: 'الرئيسية' },
      { href: '/articles', label: 'المقالات' },
      { href: '/books', label: 'الكتب' },
      { href: '/podcasts', label: 'البودكاست' },
      { href: '/newsletter', label: 'النشرة' },
      { href: '/about', label: 'عنّي' },
    ],
    switchLabel: 'English',
    rss: 'خلاصة RSS',
    rights: 'جميع الحقوق محفوظة',
    readMore: 'اقرأ المقال',
    minutes: 'دقائق قراءة',
    publishedOn: 'نُشر في',
    onLinkedIn: 'المقال الأصلي على لينكدإن',
  },
  en: {
    nav: [
      { href: '/en', label: 'Home' },
      { href: '/en/articles', label: 'Articles' },
      { href: '/en/podcasts', label: 'Podcasts' },
      { href: '/en/about', label: 'About' },
    ],
    switchLabel: 'العربية',
    rss: 'RSS feed',
    rights: 'All rights reserved',
    readMore: 'Read article',
    minutes: 'min read',
    publishedOn: 'Published',
    onLinkedIn: 'Original article on LinkedIn',
  },
} as const;
