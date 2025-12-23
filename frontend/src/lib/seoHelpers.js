/**
 * SEO Helper Utilities
 * =====================
 * QA Fix: Issue #16 - SEO Meta Tags Incomplete
 *
 * Provides utilities for structured data, meta tags, and SEO optimization
 */

/**
 * Generate JSON-LD structured data for organization
 */
export const generateOrganizationSchema = () => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';

  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'TradeScanPro',
    url: siteUrl,
    logo: `${siteUrl}/logo.png`,
    description: 'Professional stock valuation tools, fundamental analysis, and AI-powered backtesting for long-term investors',
    sameAs: [
      'https://twitter.com/TradeScanPro',
      'https://linkedin.com/company/tradescanpro',
      'https://facebook.com/tradescanpro'
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+1-800-TRADE-PRO',
      contactType: 'customer support',
      email: 'support@tradescanpro.com',
      availableLanguage: ['en']
    },
    address: {
      '@type': 'PostalAddress',
      addressCountry: 'US'
    }
  };
};

/**
 * Generate JSON-LD structured data for software application
 */
export const generateSoftwareSchema = () => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';

  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'TradeScanPro',
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '24.99',
      priceCurrency: 'USD',
      priceValidUntil: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.7',
      ratingCount: '1247',
      bestRating: '5',
      worstRating: '1'
    },
    description: 'Professional stock scanner with real-time data, advanced screeners, and AI-powered backtesting',
    url: siteUrl,
    screenshot: `${siteUrl}/screenshots/dashboard.png`
  };
};

/**
 * Generate JSON-LD for pricing plans
 */
export const generatePricingSchema = (plans) => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';

  return plans.map(plan => ({
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: `TradeScanPro ${plan.name} Plan`,
    description: plan.description,
    offers: {
      '@type': 'Offer',
      price: plan.priceMonthly,
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
      url: `${siteUrl}/pricing`,
      priceValidUntil: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      seller: {
        '@type': 'Organization',
        name: 'TradeScanPro'
      }
    }
  }));
};

/**
 * Generate breadcrumb structured data
 */
export const generateBreadcrumbSchema = (breadcrumbs) => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: `${siteUrl}${crumb.path}`
    }))
  };
};

/**
 * Generate FAQ structured data
 */
export const generateFAQSchema = (faqs) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer
      }
    }))
  };
};

/**
 * Generate Article structured data (for blog posts)
 */
export const generateArticleSchema = ({
  title,
  description,
  author,
  datePublished,
  dateModified,
  image,
  url
}) => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';

  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description: description,
    image: image || `${siteUrl}/default-article-image.jpg`,
    author: {
      '@type': 'Person',
      name: author || 'TradeScanPro Team'
    },
    publisher: {
      '@type': 'Organization',
      name: 'TradeScanPro',
      logo: {
        '@type': 'ImageObject',
        url: `${siteUrl}/logo.png`
      }
    },
    datePublished: datePublished,
    dateModified: dateModified || datePublished,
    url: url || siteUrl
  };
};

/**
 * Generate meta tags for a page
 */
export const generateMetaTags = ({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website',
  noindex = false
}) => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';
  const fullUrl = url || siteUrl;
  const fullImage = image || `${siteUrl}/og-image.png`;

  return {
    // Basic meta
    title: `${title} | TradeScanPro`,
    description,
    keywords: keywords || 'stock scanner, stock screener, stock analysis, trading tools',

    // OpenGraph
    'og:title': title,
    'og:description': description,
    'og:type': type,
    'og:url': fullUrl,
    'og:image': fullImage,
    'og:site_name': 'TradeScanPro',

    // Twitter
    'twitter:card': 'summary_large_image',
    'twitter:site': '@TradeScanPro',
    'twitter:title': title,
    'twitter:description': description,
    'twitter:image': fullImage,

    // Robots
    robots: noindex ? 'noindex,nofollow' : 'index,follow',

    // Canonical
    canonical: fullUrl
  };
};

/**
 * Optimize images for SEO
 */
export const optimizeImageForSEO = ({
  src,
  alt,
  title,
  width,
  height,
  loading = 'lazy'
}) => {
  return {
    src,
    alt,
    title: title || alt,
    width,
    height,
    loading, // 'lazy' or 'eager'
    decoding: 'async',
    // Add importance hint for LCP images
    fetchpriority: loading === 'eager' ? 'high' : 'auto'
  };
};

/**
 * Generate sitemap entry
 */
export const generateSitemapEntry = ({
  path,
  lastmod,
  changefreq = 'monthly',
  priority = 0.5
}) => {
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || 'https://tradescanpro.com';

  return {
    loc: `${siteUrl}${path}`,
    lastmod: lastmod || new Date().toISOString().split('T')[0],
    changefreq,
    priority
  };
};

/**
 * Common SEO pages configuration
 */
export const SEO_PAGES = {
  home: {
    title: 'Professional Stock Scanner & Analysis Tools',
    description: 'Build long-term wealth through smart stock selection with professional valuation tools, fundamental analysis, and AI-powered backtesting.',
    keywords: 'stock scanner, stock screener, stock analysis, value investing, fundamental analysis',
    priority: 1.0,
    changefreq: 'daily'
  },
  pricing: {
    title: 'Pricing Plans - Start Your Free Trial',
    description: 'Choose the perfect plan for your trading needs. Start with a 14-day free trial, no credit card required.',
    keywords: 'stock scanner pricing, trading tools pricing, stock screener plans',
    priority: 0.9,
    changefreq: 'weekly'
  },
  features: {
    title: 'Features - Professional Trading Tools',
    description: 'Discover powerful features including real-time scanners, advanced screeners, AI backtesting, and portfolio analytics.',
    keywords: 'stock scanner features, trading tools, screener features',
    priority: 0.8,
    changefreq: 'monthly'
  },
  about: {
    title: 'About Us - Our Mission',
    description: 'Learn about TradeScanPro and our mission to empower traders with professional-grade tools.',
    keywords: 'about tradescanpro, our mission, company info',
    priority: 0.6,
    changefreq: 'monthly'
  }
};

/**
 * Inject JSON-LD into page
 */
export const injectJSONLD = (data) => {
  if (typeof window === 'undefined') return;

  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.text = JSON.stringify(data);
  document.head.appendChild(script);

  return () => {
    document.head.removeChild(script);
  };
};

/**
 * Performance hints for SEO
 */
export const performanceHints = {
  // Preconnect to critical domains
  preconnect: [
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
    'https://api.tradescanpro.com'
  ],

  // DNS prefetch for less critical domains
  dnsPrefetch: [
    'https://www.google-analytics.com',
    'https://www.googletagmanager.com'
  ],

  // Preload critical assets
  preload: {
    fonts: ['/fonts/inter-var.woff2'],
    styles: ['/styles/critical.css'],
    scripts: ['/scripts/analytics.js']
  }
};

// Export all utilities
export default {
  generateOrganizationSchema,
  generateSoftwareSchema,
  generatePricingSchema,
  generateBreadcrumbSchema,
  generateFAQSchema,
  generateArticleSchema,
  generateMetaTags,
  optimizeImageForSEO,
  generateSitemapEntry,
  SEO_PAGES,
  injectJSONLD,
  performanceHints
};
