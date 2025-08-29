# Contributing to Retail Trade Scanner Theme

Thank you for considering contributing to the Retail Trade Scanner theme! We welcome contributions from the community and are grateful for any help you can provide.

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please read our Code of Conduct to understand the expectations for behavior in our community.

## How to Contribute

### Reporting Issues

Before creating an issue, please check if a similar issue already exists. If you find a bug or have a feature request:

1. Use the issue templates provided
2. Provide detailed information about the problem
3. Include steps to reproduce (for bugs)
4. Add screenshots or screen recordings if applicable

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/retail-trade-scanner-theme.git
   cd retail-trade-scanner-theme
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Start development**:
   ```bash
   npm run dev
   ```

### Development Guidelines

#### CSS/SCSS
- Use the existing design tokens and CSS custom properties
- Follow the established naming conventions
- Write mobile-first responsive code
- Ensure accessibility (focus states, color contrast)
- Test with `prefers-reduced-motion` and `prefers-color-scheme`

#### JavaScript
- Use ES6+ syntax
- Follow the ESLint configuration
- Ensure accessibility (ARIA attributes, keyboard navigation)
- Test with JavaScript disabled where appropriate

#### PHP
- Follow WordPress coding standards
- Use proper sanitization and escaping
- Add inline documentation for complex functions
- Ensure compatibility with WordPress 6.0+

### CSS Architecture

```
assets/scss/
├── main.scss           # Main entry point
├── base/
│   ├── _reset.scss     # CSS reset/normalize
│   ├── _typography.scss # Typography styles
│   └── _variables.scss  # SCSS variables
├── components/
│   ├── _buttons.scss   # Button styles
│   ├── _cards.scss     # Card components
│   ├── _forms.scss     # Form elements
│   └── _navigation.scss # Navigation styles
└── utilities/
    ├── _animations.scss # Animation utilities
    ├── _layout.scss    # Layout utilities
    └── _spacing.scss   # Spacing utilities
```

### Commit Message Format

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/modifying tests
- `chore`: Build process or auxiliary tool changes

Examples:
```
feat(buttons): add magnetic hover effect
fix(navigation): resolve mobile menu accessibility issue
docs(readme): update installation instructions
style(cards): improve glassmorphism effect consistency
```

### Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Run tests and linting**:
   ```bash
   npm run lint:css
   npm run lint:js
   npm test
   ```

4. **Build the production assets**:
   ```bash
   npm run build
   ```

5. **Commit your changes** using conventional commit format

6. **Push to your fork** and create a pull request

7. **Fill out the PR template** with:
   - Clear description of changes
   - Screenshots/videos of UI changes
   - Testing instructions
   - Breaking changes (if any)

### Testing Guidelines

#### Manual Testing
- Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- Test responsive behavior on different screen sizes
- Test keyboard navigation
- Test with screen readers (if accessibility changes)
- Test dark mode functionality
- Test performance with Lighthouse

#### Accessibility Testing
- Ensure color contrast meets WCAG AA standards
- Test keyboard navigation for all interactive elements
- Verify proper heading hierarchy
- Test with screen readers
- Ensure focus indicators are visible

#### Performance Testing
- Run Lighthouse audits
- Check Critical CSS is properly inlined
- Verify assets are properly minified
- Test loading performance

### Design System Guidelines

#### Colors
Use the established color tokens:
```css
/* Primary palette */
var(--primary-50) to var(--primary-900)

/* Semantic colors */
var(--success), var(--danger), var(--warning), var(--info)

/* Neutral palette */
var(--gray-50) to var(--gray-900)
```

#### Typography
Use fluid typography tokens:
```css
var(--text-xs) to var(--text-4xl)
```

#### Spacing
Use consistent spacing tokens:
```css
var(--spacing-xs) to var(--spacing-4xl)
```

#### Animations
- Use the established easing functions
- Respect `prefers-reduced-motion`
- Keep animations subtle and purposeful
- Use CSS transforms for better performance

### Browser Support

Ensure compatibility with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)

### Getting Help

If you need help:
1. Check the documentation in `/docs`
2. Search existing issues
3. Ask questions in discussions
4. Contact the maintainers

### Recognition

Contributors will be recognized in:
- CHANGELOG.md
- Contributors section in README.md
- Release notes for significant contributions

Thank you for contributing to make Retail Trade Scanner theme better!