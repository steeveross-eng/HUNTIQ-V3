/**
 * SEO Head Component
 * Gère les balises meta, OpenGraph, Twitter Cards et Schema.org
 */

import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const SITE_URL = process.env.REACT_APP_BACKEND_URL || 'https://bionic-hunt.preview.emergentagent.com';

const SEOHead = () => {
  const location = useLocation();
  const [meta, setMeta] = useState(null);

  useEffect(() => {
    const fetchMeta = async () => {
      try {
        const path = location.pathname.replace(/^\//, '') || '';
        const response = await axios.get(`${API}/seo/meta/${path}`);
        setMeta(response.data);
        updateMetaTags(response.data);
      } catch (error) {
        // Use defaults
        updateMetaTags(getDefaultMeta());
      }
    };

    fetchMeta();
  }, [location.pathname]);

  const getDefaultMeta = () => ({
    title: 'Chasse Bionic TM | Votre parcours guidé vers une chasse parfaite',
    description: 'Votre parcours guidé vers une chasse parfaite. Analysez, comparez et trouvez les meilleurs attractants.',
    keywords: ['chasse', 'attractant', 'orignal', 'chevreuil', 'ours', 'Québec', 'BIONIC', 'Chasse Bionic'],
    og_image: `${SITE_URL}/og-image.jpg`,
    og_type: 'website',
    canonical: `${SITE_URL}${location.pathname}`
  });

  const updateMetaTags = (data) => {
    // Update title
    document.title = data.title || 'Chasse Bionic TM';

    // Update or create meta tags
    const updateMeta = (name, content, property = false) => {
      const attr = property ? 'property' : 'name';
      let element = document.querySelector(`meta[${attr}="${name}"]`);
      if (!element) {
        element = document.createElement('meta');
        element.setAttribute(attr, name);
        document.head.appendChild(element);
      }
      element.setAttribute('content', content);
    };

    // Basic meta
    updateMeta('description', data.description);
    updateMeta('keywords', data.keywords?.join(', ') || '');
    
    // OpenGraph
    updateMeta('og:title', data.title, true);
    updateMeta('og:description', data.description, true);
    updateMeta('og:type', data.og_type || 'website', true);
    updateMeta('og:url', data.canonical || `${SITE_URL}${location.pathname}`, true);
    updateMeta('og:image', data.og_image || `${SITE_URL}/og-image.jpg`, true);
    updateMeta('og:site_name', 'Chasse Bionic TM', true);
    updateMeta('og:locale', 'fr_CA', true);

    // Twitter Cards
    updateMeta('twitter:card', 'summary_large_image');
    updateMeta('twitter:title', data.title);
    updateMeta('twitter:description', data.description);
    updateMeta('twitter:image', data.og_image || `${SITE_URL}/og-image.jpg`);

    // Canonical
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', data.canonical || `${SITE_URL}${location.pathname}`);

    // Schema.org JSON-LD
    let schema = document.querySelector('script[type="application/ld+json"]');
    if (!schema) {
      schema = document.createElement('script');
      schema.setAttribute('type', 'application/ld+json');
      document.head.appendChild(schema);
    }
    
    const schemaData = data.schema || {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "Chasse Bionic TM",
      "url": SITE_URL,
      "description": data.description,
      "potentialAction": {
        "@type": "SearchAction",
        "target": `${SITE_URL}/shop?search={search_term_string}`,
        "query-input": "required name=search_term_string"
      }
    };
    schema.textContent = JSON.stringify(schemaData);
  };

  return null; // This component doesn't render anything
};

export default SEOHead;
