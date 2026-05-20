import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS classes with clsx.
 * Handles conditional classes and resolves conflicts.
 *
 * @example
 * cn("px-4 py-2", isActive && "bg-rose-500", className)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
