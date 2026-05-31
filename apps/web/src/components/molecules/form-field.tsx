"use client";

import { Input, type InputProps } from "@/components/atoms/input";

interface FormFieldProps extends InputProps {
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
}

export function FormField({
  label,
  error,
  hint,
  required,
  id,
  ...inputProps
}: FormFieldProps) {
  const fieldId = id || label.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className="space-y-1.5">
      <label
        htmlFor={fieldId}
        className="block text-sm font-medium text-[var(--foreground)]"
      >
        {label}
        {required && <span className="text-[var(--color-rose-petal)] ml-0.5">*</span>}
      </label>
      <Input id={fieldId} error={error} {...inputProps} />
      {error && (
        <p className="text-xs text-red-500 flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {error}
        </p>
      )}
      {hint && !error && (
        <p className="text-xs text-[var(--muted-foreground)]">{hint}</p>
      )}
    </div>
  );
}
