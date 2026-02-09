/**
 * BionicLogo - Bilingual logo component
 * Uses the unified Bionic logo that fits both FR/EN
 */

import React, { useContext } from 'react';
import LanguageContext, { BRAND_NAMES } from '@/contexts/LanguageContext';

const BionicLogo = ({ 
  size = "default", 
  variant = "full", // "full", "icon", "text"
  className = "",
  forceLanguage = null, // Override language if needed
  fillContainer = false // Make logo fill available space
}) => {
  // Get language from context or use default
  const ctx = useContext(LanguageContext);
  const language = forceLanguage || ctx?.language || 'fr';

  const brand = BRAND_NAMES[language];
  
  const sizeClasses = {
    small: fillContainer ? "h-full max-h-8" : "h-8",
    default: fillContainer ? "h-full max-h-12" : "h-12",
    large: fillContainer ? "h-full max-h-16" : "h-16",
    xlarge: fillContainer ? "h-full max-h-24" : "h-24"
  };

  const logoSrc = brand.logo;
  const altText = brand.full;

  if (variant === "text") {
    return (
      <span className={`font-bold text-[#f5a623] ${className}`}>
        {brand.full}
      </span>
    );
  }

  return (
    <img 
      src={logoSrc} 
      alt={altText}
      className={`${sizeClasses[size] || sizeClasses.default} w-auto object-contain ${fillContainer ? 'max-w-full' : ''} ${className}`}
      data-testid="bionic-logo"
    />
  );
};

// Export both default and named
export { BionicLogo };
export default BionicLogo;
