import React, { useEffect } from "react";

function upsertMetaByName(name, content) {
  if (!content) return;
  let tag = document.querySelector(`meta[name='${name}']`);
  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute('name', name);
    document.head.appendChild(tag);
  }
  tag.setAttribute('content', content);
}

function upsertMetaByProperty(property, content) {
  if (!content) return;
  let tag = document.querySelector(`meta[property='${property}']`);
  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute('property', property);
    document.head.appendChild(tag);
  }
  tag.setAttribute('content', content);
}

function upsertLink(rel, href) {
  if (!href) return;
  let link = document.querySelector(`link[rel='${rel}']`);
  if (!link) {
    link = document.createElement('link');
    link.setAttribute('rel', rel);
    document.head.appendChild(link);
  }
  link.setAttribute('href', href);
}

const SEO = ({
  title,
  description,
  canonical,
  ogType = 'website',
  ogImage = '/og-image.png',
  twitterCard = 'summary_large_image',
  jsonLdSrcs = [],
  robots
}) => {
  useEffect(() => {
    if (title) {
      document.title = title;
      upsertMetaByProperty('og:title', title);
      upsertMetaByName('twitter:title', title);
    }
    if (description) {
      upsertMetaByName('description', description);
      upsertMetaByProperty('og:description', description);
      upsertMetaByName('twitter:description', description);
    }
    const resolvedCanonical = canonical || (typeof window !== 'undefined' ? window.location.href : undefined);
    if (resolvedCanonical) {
      upsertLink('canonical', resolvedCanonical);
      upsertMetaByProperty('og:url', resolvedCanonical);
      upsertMetaByName('twitter:url', resolvedCanonical);
      try {
        const domain = new URL(resolvedCanonical).hostname;
        upsertMetaByName('twitter:domain', domain);
      } catch {}
    }
    upsertMetaByProperty('og:type', ogType);
    upsertMetaByProperty('og:site_name', 'Trade Scan Pro');
    upsertMetaByProperty('og:locale', 'en_US');
    if (ogImage) {
      upsertMetaByProperty('og:image', ogImage);
      if (title) {
        upsertMetaByProperty('og:image:alt', title);
        upsertMetaByName('twitter:image:alt', title);
      }
      upsertMetaByName('twitter:image', ogImage);
    }
    upsertMetaByName('twitter:card', twitterCard);
    // Defaults for X/Twitter card site/creator
    upsertMetaByName('twitter:site', '@TradeScanProLLC');
    upsertMetaByName('twitter:creator', '@TradeScanProLLC');

    if (robots) {
      upsertMetaByName('robots', robots);
    }

    // Attach external JSON-LD scripts (to comply with strict CSP)
    jsonLdSrcs.forEach((src) => {
      if (!src) return;
      const existing = Array.from(document.querySelectorAll("script[type='application/ld+json']"))
        .find(s => s.getAttribute('src') === src);
      if (!existing) {
        const s = document.createElement('script');
        s.setAttribute('type', 'application/ld+json');
        s.setAttribute('src', src);
        s.setAttribute('data-managed', 'seo');
        document.head.appendChild(s);
      }
    });
  }, [title, description, canonical, ogType, ogImage, twitterCard, jsonLdSrcs, robots]);

  return null;
};

export default SEO;

