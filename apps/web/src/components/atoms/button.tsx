"use client";

import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const variants = {
  primary:
    "bg-gradient-to-r from-[var(--color-rose-petal)] to-[var(--color-lavender-dream)] text-white shadow-[var(--shadow-rose)] hover:shadow-[var(--shadow-card-hover)] hover:brightness-110",
  secondary:
    "bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:border-[var(--color-rose-petal)] hover:shadow-[var(--shadow-rose)]",
  outline:
    "bg-transparent border-2 border-[var(--color-rose-petal)] text-[var(--color-rose-petal)] hover:bg-[var(--color-rose-petal)] hover:text-white",
  ghost:
    "bg-transparent text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)]",
  danger:
    "bg-gradient-to-r from-red-500 to-red-600 text-white hover:brightness-110",
} as const;

const sizes = {
  sm: "h-8 px-3 text-sm rounded-lg gap-1.5",
  md: "h-10 px-5 text-sm rounded-xl gap-2",
  lg: "h-12 px-6 text-base rounded-xl gap-2.5",
} as const;

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  isLoading?: boolean;
  fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      isLoading = false,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-semibold transition-all duration-300 cursor-pointer select-none",
          "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-rose-petal)]",
          "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
          "active:scale-[0.97]",
          variants[variant],
          sizes[size],
          fullWidth && "w-full",
          className,
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Đang xử lý...</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  },
);

Button.displayName = "Button";
export { Button, type ButtonProps };
