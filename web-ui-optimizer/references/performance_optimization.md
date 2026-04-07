# Performance Optimization & Quality Audit

## 1. Core Web Vitals
- **LCP (Largest Contentful Paint)**: Keep under 2.5s. Optimize images, prioritize critical assets.
- **FID (First Input Delay)**: Keep under 100ms. Reduce main thread work, minimize JS.
- **CLS (Cumulative Layout Shift)**: Keep under 0.1. Set fixed dimensions for images/ads.

## 2. Image Optimization
- **Next-Gen Formats**: Use WebP or AVIF for all images.
- **Lazy Loading**: Use `loading="lazy"` for off-screen images.
- **Responsive Images**: Use `srcset` and `sizes` for different screen widths.

## 3. Code Optimization
- **Tree Shaking**: Ensure only used code is bundled.
- **Dynamic Imports**: Use `React.lazy` or Next.js `dynamic()` for code splitting.
- **Compression**: Enable Gzip or Brotli for all assets.

## 4. Engineering Standards
- **ESLint/Prettier**: Enforce consistent code style and identify errors early.
- **Type Safety**: Use TypeScript to prevent runtime errors.
- **DRY (Don't Repeat Yourself)**: Abstract common logic into reusable hooks or utilities.

## 5. Audit Checklist
1. Run Lighthouse Audit (Performance, Accessibility, Best Practices, SEO).
2. Check for unused CSS/JS.
3. Validate mobile responsiveness.
4. Verify accessibility (Aria-labels, semantic HTML).
