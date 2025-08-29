// Alternative image sources for when external images fail
export const imageFallbacks = {
  // Food category placeholders
  pizza: [
    'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'
  ],
  indian: [
    'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop'
  ],
  salad: [
    'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop'
  ],
  mexican: [
    'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=400&h=300&fit=crop'
  ],
  mediterranean: [
    'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop'
  ],
  japanese: [
    'https://images.unsplash.com/photo-1553621042-f6e147245754?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1563379091339-03246963d8a9?w=400&h=300&fit=crop'
  ],
  italian: [
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop'
  ],
  american: [
    'https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop', // burger
    'https://images.unsplash.com/photo-1550547660-8d8c1f1f1b42?w=400&h=300&fit=crop'
  ],
  greek: [
    'https://images.unsplash.com/photo-1604908176997-431682f63c85?w=400&h=300&fit=crop', // moussaka/platter
    'https://images.unsplash.com/photo-1523986371872-9d3ba2e2a389?w=400&h=300&fit=crop'
  ],
  dessert: [
    'https://images.unsplash.com/photo-1541781286675-80a6e37f6b8a?w=400&h=300&fit=crop', // pudding/cake
    'https://images.unsplash.com/photo-1544510808-91bcbee1df55?w=400&h=300&fit=crop'
  ]
};

// Generic placeholder images
// Inline SVG placeholders (no external network/DNS dependency)
const svgPlaceholder = (w: number, h: number) =>
  `data:image/svg+xml;utf8,` +
  encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' width='${w}' height='${h}' viewBox='0 0 ${w} ${h}'>` +
      `<rect width='100%' height='100%' fill='#f3f4f6'/>` +
      `<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#9ca3af' font-family='Arial, Helvetica, sans-serif' font-size='${Math.round(
        Math.min(w, h) / 12
      )}'>Image Not Available</text>` +
    `</svg>`
  );

export const placeholderImages = {
  small: svgPlaceholder(400, 300),
  medium: svgPlaceholder(600, 400),
  large: svgPlaceholder(800, 600)
};

// Function to get fallback image based on cuisine type
export const getFallbackImage = (cuisineType: string, size: 'small' | 'medium' | 'large' = 'small'): string => {
  const cuisine = cuisineType.toLowerCase();
  
  if (imageFallbacks[cuisine as keyof typeof imageFallbacks]) {
    const images = imageFallbacks[cuisine as keyof typeof imageFallbacks];
    return images[Math.floor(Math.random() * images.length)];
  }
  
  return placeholderImages[size];
};

// Function to handle image loading errors with fallbacks
export const handleImageError = (
  event: React.SyntheticEvent<HTMLImageElement, Event>,
  cuisineType?: string,
  size: 'small' | 'medium' | 'large' = 'small'
) => {
  const img = event.currentTarget;

  // Avoid infinite loops by trying cuisine fallback once, then generic
  const attemptedCuisineFallback = img.getAttribute('data-fallback-attempted') === 'true';
  if (cuisineType && !attemptedCuisineFallback) {
    const fallback = getFallbackImage(cuisineType, size);
    if (img.src !== fallback) {
      img.setAttribute('data-fallback-attempted', 'true');
      img.src = fallback;
      return;
    }
  }

  // Final fallback
  if (img.src !== placeholderImages[size]) {
    img.src = placeholderImages[size];
  }
};


