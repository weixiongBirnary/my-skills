# Frontend Implementation Standards

## 1. Component Architecture
- **Atomic Design**: Structure components into atoms, molecules, and organisms.
- **Props Safety**: Use TypeScript interfaces or PropTypes for robust data handling.
- **Style Isolation**: Use Tailwind CSS (Utility-first) or CSS Modules for clean, non-leaking styles.

## 2. Styling with Tailwind CSS
- **Standardize Spacing**: Use the 4px grid (e.g., `p-4`, `m-2`).
- **Custom Config**: Extend `tailwind.config.js` with project-specific colors, fonts, and box shadows.
- **Efficient Usage**: Avoid deep nesting; use `@apply` only for highly repetitive styles.

## 3. Interactive & Animations
- **GSAP (GreenSock)**: Use for complex timeline-based animations, SVG morphing, and scroll triggers.
- **Framer Motion**: The go-to choice for React transition animations (hover, tap, animate presence).
- **Lottie**: Use for high-quality, lightweight vector animations.
- **Micro-interactions**: 
  - Add hover transitions (0.2s - 0.3s duration, ease-in-out).
  - Implement focus states and active button feedback.

## 4. Modern JavaScript (ES6+)
- **Declarative Code**: Prefer `map`, `filter`, `reduce` over traditional loops.
- **Async/Await**: Handle API calls and side effects with clean async patterns.
- **Optimization**: Use Debounce/Throttle for scroll and resize events.

## 5. Responsive Design
- **Mobile First**: Develop for mobile screens (min-width) first, then scale up.
- **Flex/Grid**: Never use fixed widths; use percentages, `rem`, `em`, and fluid typography.
- **Media Queries**: Use standard breakpoints (640px, 768px, 1024px, 1280px).
