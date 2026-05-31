"use client";

import { cn } from "@/lib/utils";

interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeMap = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-14 w-14 text-base",
  xl: "h-20 w-20 text-lg",
};

function getInitials(name?: string): string {
  if (!name) return "?";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function Avatar({
  src,
  alt,
  fallback,
  size = "md",
  className,
}: AvatarProps) {
  return (
    <div
      className={cn(
        "relative rounded-full overflow-hidden flex items-center justify-center font-semibold",
        "bg-gradient-to-br from-[var(--color-rose-petal)] to-[var(--color-lavender-dream)] text-white",
        "ring-2 ring-white/20",
        sizeMap[size],
        className,
      )}
    >
      {src ? (
        <img
          src={src}
          alt={alt || "Avatar"}
          className="h-full w-full object-cover"
        />
      ) : (
        <span>{getInitials(fallback || alt)}</span>
      )}
    </div>
  );
}
