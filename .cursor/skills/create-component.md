---
name: create-component
description: Create a new React component following Eralove design system
---

# Create Component

When asked to create a new UI component, follow the Eralove design system:

## Structure

```
apps/web/src/components/{level}/{component-name}.tsx
```

Levels:
- `atoms/` — Button, Input, Badge, Avatar, Spinner, Icon
- `molecules/` — Card, FormField, SearchBar, DatePicker, EmojiPicker
- `organisms/` — Header, Sidebar, ChatBubble, EventCard, PhotoGrid

## Template

```tsx
"use client"; // Only if component needs interactivity

import { cn } from "@/lib/utils";
import { type ComponentPropsWithoutRef } from "react";

interface {ComponentName}Props extends ComponentPropsWithoutRef<"div"> {
  // typed props
  variant?: "default" | "outline";
}

export function {ComponentName}({
  className,
  variant = "default",
  children,
  ...props
}: {ComponentName}Props) {
  return (
    <div
      className={cn(
        "base-styles-here",
        variant === "outline" && "outline-styles",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
```

## Design System Rules

### Colors (use Tailwind classes)
- Primary: `bg-rose-500` / `text-rose-500` (#FF6B9D)
- Secondary: `bg-purple-400` / `text-purple-400` (#C084FC)
- Background: `bg-pink-50` (#FFF0F5)
- Text: `text-purple-900` (#7C3AED)
- Success: `text-emerald-400` (#6EE7B7)
- Warning: `text-amber-400` (#FFB347)

### Dark Mode
Always include `dark:` variants:
```tsx
className="bg-pink-50 dark:bg-gray-900 text-purple-900 dark:text-pink-100"
```

### Border Radius
- Cards: `rounded-xl` (12px)
- Buttons: `rounded-full`
- Inputs: `rounded-lg`

### Shadows
Use pink-tinted shadows:
```tsx
className="shadow-lg shadow-rose-500/10"
```

### Animations
Use Framer Motion for animations:
```tsx
import { motion } from "framer-motion";

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
```

### Typography
- Headings: `font-heading` (Nunito)
- Body: `font-sans` (Inter)

### Responsive
Always design mobile-first:
```tsx
className="px-4 md:px-6 lg:px-8"
```

## Checklist
- [ ] TypeScript props interface defined
- [ ] `cn()` utility used for conditional classes
- [ ] Dark mode classes included
- [ ] Responsive breakpoints considered
- [ ] Accessibility: proper aria labels, keyboard support
- [ ] `"use client"` only if needed
- [ ] Exported from component's index
