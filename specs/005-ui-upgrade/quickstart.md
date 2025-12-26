# Quickstart: UI Upgrade for book_robotic_minds (Docusaurus)

## Prerequisites

- Node.js 18+ installed
- Git installed
- Basic knowledge of CSS and Docusaurus

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Navigate to the book directory:
   ```bash
   cd book_robotic_minds
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

## Development

1. Start the development server:
   ```bash
   npm start
   ```

2. The site will be available at `http://localhost:3000`

## UI Upgrade Implementation

### 1. Custom CSS
- Modify `src/css/custom.css` to update color variables and global styles
- Add responsive design rules for different screen sizes
- Implement accessibility enhancements

### 2. Homepage Customization
- Update `src/pages/index.js` to reflect robotics education content
- Modify `src/pages/index.module.css` for homepage-specific styles
- Update `src/components/HomepageFeatures/index.js` with robotics-focused features

### 3. Navigation Enhancement
- Update `sidebars.js` to improve module organization
- Modify `docusaurus.config.js` for enhanced navigation structure

### 4. Testing
- Test on different screen sizes (mobile, tablet, desktop)
- Verify accessibility with tools like axe-core
- Check cross-browser compatibility

## Build & Deployment

1. Build the static site:
   ```bash
   npm run build
   ```

2. The built site will be in the `build/` directory

3. Serve the build locally to test:
   ```bash
   npm run serve
   ```

## Customization Guidelines

- Always use CSS variables defined in `:root` for consistency
- Follow Docusaurus theme customization best practices
- Maintain accessibility standards (WCAG 2.1 AA)
- Test responsive behavior at common breakpoints (320px, 768px, 1024px, 1440px)