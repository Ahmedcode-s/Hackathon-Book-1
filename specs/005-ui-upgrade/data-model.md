# Data Model: UI Upgrade for book_robotic_minds (Docusaurus)

## Visual Design Elements

**Entity**: VisualDesignElement
- **Properties**:
  - name: string (e.g., "primary-color", "heading-font-size")
  - type: string (e.g., "color", "dimension", "typography")
  - value: string (e.g., "#2563eb", "1.5rem", "system-ui")
  - scope: string (e.g., "global", "component", "module")
- **Validation**:
  - All color values must be valid CSS color formats
  - All dimension values must be valid CSS units
  - All typography values must be valid CSS font stacks

## Navigation Components

**Entity**: NavigationComponent
- **Properties**:
  - componentType: string (e.g., "sidebar", "breadcrumb", "navbar")
  - label: string (display text)
  - link: string (URL path)
  - hierarchyLevel: integer (nesting depth)
  - moduleId: string (associated module identifier)
- **Validation**:
  - All links must be valid relative paths
  - Hierarchy levels must be consistent within modules
  - Module IDs must correspond to existing modules

## Responsive Layout

**Entity**: ResponsiveBreakpoint
- **Properties**:
  - name: string (e.g., "mobile", "tablet", "desktop")
  - minWidth: string (CSS media query value)
  - maxWidth: string (CSS media query value, optional)
  - styles: object (CSS properties for this breakpoint)
- **Validation**:
  - Min/max width values must be valid CSS dimensions
  - Breakpoints must not overlap
  - All breakpoints must be used in actual CSS

## UI Component States

**Entity**: UIComponentState
- **Properties**:
  - componentName: string (e.g., "button", "link", "sidebar-item")
  - state: string (e.g., "default", "hover", "active", "focus")
  - styles: object (CSS properties for this state)
  - accessibilityAttributes: object (aria attributes, focus management)
- **Validation**:
  - All states must have appropriate visual feedback
  - Accessibility attributes must follow WCAG guidelines
  - State transitions must be smooth and accessible

## Module Organization

**Entity**: ModuleSection
- **Properties**:
  - moduleId: string (unique identifier for module)
  - moduleName: string (display name)
  - sections: array of objects (navigation items in module)
  - colorTheme: string (module-specific accent color)
- **Validation**:
  - Module IDs must be unique
  - Section links must exist in the documentation
  - Color themes must meet accessibility contrast ratios