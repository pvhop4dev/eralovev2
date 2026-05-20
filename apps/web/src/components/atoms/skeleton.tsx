"use client";

/**
 * Skeleton — loading placeholder with shimmer animation.
 *
 * Usage:
 *   <Skeleton width="100%" height="120px" />
 *   <Skeleton width="60%" height="1rem" />
 */
export function Skeleton({
  width = "100%",
  height = "1rem",
  borderRadius = "var(--radius-md)",
  style,
}: {
  width?: string;
  height?: string;
  borderRadius?: string;
  style?: React.CSSProperties;
}) {
  return (
    <>
      <div
        className="skeleton"
        style={{
          width,
          height,
          borderRadius,
          background: "var(--border)",
          position: "relative",
          overflow: "hidden",
          ...style,
        }}
      >
        <div
          className="skeleton-shimmer"
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 50%, transparent 100%)",
            animation: "shimmer 1.5s ease-in-out infinite",
          }}
        />
      </div>
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </>
  );
}

/**
 * DashboardSkeleton — full dashboard loading state.
 */
export function DashboardSkeleton() {
  return (
    <div style={{ padding: "1.5rem", maxWidth: "800px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1.5rem" }}>
        <Skeleton width="200px" height="2rem" />
        <Skeleton width="40px" height="40px" borderRadius="50%" />
      </div>

      {/* Hero card */}
      <Skeleton width="100%" height="180px" borderRadius="var(--radius-xl)" style={{ marginBottom: "1rem" }} />

      {/* Quote card */}
      <Skeleton width="100%" height="100px" borderRadius="var(--radius-xl)" style={{ marginBottom: "1rem" }} />

      {/* Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
        <Skeleton width="100%" height="120px" borderRadius="var(--radius-xl)" />
        <Skeleton width="100%" height="120px" borderRadius="var(--radius-xl)" />
        <Skeleton width="100%" height="120px" borderRadius="var(--radius-xl)" />
        <Skeleton width="100%" height="120px" borderRadius="var(--radius-xl)" />
      </div>
    </div>
  );
}

/**
 * ChatSkeleton — chat loading state.
 */
export function ChatSkeleton() {
  return (
    <div style={{ padding: "1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.5rem 0" }}>
        <Skeleton width="44px" height="44px" borderRadius="50%" />
        <div>
          <Skeleton width="120px" height="1rem" style={{ marginBottom: "0.25rem" }} />
          <Skeleton width="80px" height="0.75rem" />
        </div>
      </div>

      {/* Messages */}
      <div style={{ display: "flex", justifyContent: "flex-start", marginTop: "1rem" }}>
        <Skeleton width="60%" height="48px" borderRadius="1rem" />
      </div>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <Skeleton width="45%" height="48px" borderRadius="1rem" />
      </div>
      <div style={{ display: "flex", justifyContent: "flex-start" }}>
        <Skeleton width="70%" height="48px" borderRadius="1rem" />
      </div>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <Skeleton width="50%" height="48px" borderRadius="1rem" />
      </div>
      <div style={{ display: "flex", justifyContent: "flex-start" }}>
        <Skeleton width="40%" height="48px" borderRadius="1rem" />
      </div>
    </div>
  );
}
