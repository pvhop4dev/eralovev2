"use client";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
}

export function LoadingSpinner({ size = "md", text }: LoadingSpinnerProps) {
  const sizeMap = { sm: "text-2xl", md: "text-4xl", lg: "text-6xl" };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={`${sizeMap[size]} animate-[heartbeat_1.2s_ease-in-out_infinite]`}>
        💗
      </div>
      {text && (
        <p className="text-sm text-[var(--muted-foreground)] animate-pulse">
          {text}
        </p>
      )}
      <style>{`
        @keyframes heartbeat {
          0%, 100% { transform: scale(1); }
          25% { transform: scale(1.15); }
          50% { transform: scale(1); }
          75% { transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}
