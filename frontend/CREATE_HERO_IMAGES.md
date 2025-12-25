# Hero Image Requirements

## Specifications

The homepage requires hero images in the following formats:

### Image 1: Main Hero (Wide)
- **Dimensions:** 1920x800px (2.4:1 aspect ratio)
- **File Size:** <200KB per format
- **Formats Required:**
  - `public/hero.webp` (WebP format, modern browsers)
  - `public/hero.avif` (AVIF format, best compression)
  - `public/hero.jpg` (JPG fallback, universal compatibility)

### Image 2: Mobile Hero (Optional)
- **Dimensions:** 800x600px (4:3 aspect ratio)
- **File Size:** <100KB per format
- **Formats:** Same as above with `-mobile` suffix

## Design Guidelines

### Visual Style
- **Theme:** Professional, modern, tech-forward
- **Colors:** Blues, grays, with accent colors matching brand (#2563eb blue primary)
- **Mood:** Confident, data-driven, professional trading platform

### Content Suggestions

**Option 1: Trading Dashboard Screenshot**
- Clean, modern trading interface
- Stock charts with upward trends
- Professional data visualization
- Subtle depth of field blur on edges

**Option 2: Abstract Financial Visualization**
- Geometric patterns suggesting data/charts
- Gradient overlays (dark blue to lighter blue)
- Floating UI elements/cards
- Modern, minimalist aesthetic

**Option 3: Hero Illustration**
- Professional trader/investor at desk
- Multiple monitors with charts
- Clean, vector-style illustration
- Modern color palette

### Technical Requirements

1. **No Text in Image**
   - Keep image text-free (text overlay done in HTML)
   - Allows for responsive text positioning

2. **Safe Zones**
   - Left 40%: Clear for text overlay
   - Right 60%: Primary visual interest
   - Vertical center: Most important elements

3. **Color Overlay Ready**
   - Should look good with dark gradient overlay
   - Consider contrast for white text overlay

4. **Responsive Considerations**
   - Important elements in center for mobile crop
   - Background should work at various aspect ratios

## Temporary Solution

Until final images are ready, use CSS gradient fallback:

```css
.hero-fallback {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Alternative: */
  background: linear-gradient(to right, #1e3a8a, #3b82f6, #60a5fa);
}
```

## Image Optimization

After creating images, optimize with:

```bash
# WebP conversion (requires cwebp)
cwebp -q 80 hero.jpg -o hero.webp

# AVIF conversion (requires avifenc)
avifenc --min 20 --max 25 hero.jpg hero.avif

# JPG optimization
jpegoptim --max=85 --strip-all hero.jpg
```

## Placement

Images go in:
- `frontend/public/hero.webp`
- `frontend/public/hero.avif`
- `frontend/public/hero.jpg`

Referenced in HTML as:
```html
<picture>
  <source srcset="/hero.avif" type="image/avif">
  <source srcset="/hero.webp" type="image/webp">
  <img src="/hero.jpg" alt="Trade Scan Pro Dashboard" />
</picture>
```

## Status

- [ ] Hero images designed
- [ ] Images optimized and exported
- [ ] WebP format created
- [ ] AVIF format created
- [ ] JPG fallback created
- [ ] Images placed in `public/` directory
- [ ] Verified on homepage
- [ ] Tested on mobile devices

## Contact

For hero image design, contact:
- Design team
- Or use stock photography from:
  - Unsplash (free, commercial use)
  - Pexels (free, commercial use)
  - Adobe Stock (paid, high quality)

## Sample Search Terms

If using stock photography:
- "trading dashboard"
- "stock market technology"
- "financial data visualization"
- "modern analytics interface"
- "business intelligence dashboard"
- "fintech technology"
