import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Eralove — Nơi lưu giữ mọi khoảnh khắc yêu thương 💗",
};

export default function WelcomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--gradient-bg)",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      {/* Animated Heart */}
      <div
        style={{
          fontSize: "5rem",
          marginBottom: "1.5rem",
          animation: "pulse 2s ease-in-out infinite",
        }}
      >
        💗
      </div>

      {/* Logo */}
      <h1
        style={{
          fontFamily: "var(--font-heading)",
          fontSize: "clamp(2.5rem, 6vw, 4rem)",
          fontWeight: 800,
          background: "var(--gradient-primary)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          marginBottom: "0.5rem",
          letterSpacing: "-0.02em",
        }}
      >
        Eralove
      </h1>

      {/* Tagline */}
      <p
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "clamp(1rem, 2.5vw, 1.25rem)",
          color: "var(--muted-foreground)",
          maxWidth: "500px",
          lineHeight: 1.6,
          marginBottom: "2.5rem",
        }}
      >
        Nơi lưu giữ mọi khoảnh khắc yêu thương
        <br />
        <span style={{ fontSize: "0.9em", opacity: 0.8 }}>
          Không gian riêng tư dành cho hai bạn 🌸
        </span>
      </p>

      {/* CTA Buttons */}
      <div
        style={{
          display: "flex",
          gap: "1rem",
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        <a
          href="/register"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            padding: "0.875rem 2rem",
            background: "var(--gradient-primary)",
            color: "#fff",
            borderRadius: "var(--radius-full)",
            fontFamily: "var(--font-heading)",
            fontWeight: 700,
            fontSize: "1.05rem",
            textDecoration: "none",
            boxShadow: "var(--shadow-rose)",
            transition: "var(--transition-base)",
          }}
        >
          Bắt đầu ngay 💕
        </a>
        <a
          href="/login"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            padding: "0.875rem 2rem",
            background: "var(--card)",
            color: "var(--foreground)",
            borderRadius: "var(--radius-full)",
            fontFamily: "var(--font-heading)",
            fontWeight: 600,
            fontSize: "1.05rem",
            textDecoration: "none",
            border: "1px solid var(--border)",
            transition: "var(--transition-base)",
          }}
        >
          Đăng nhập
        </a>
      </div>

      {/* Version */}
      <p
        style={{
          marginTop: "3rem",
          fontSize: "0.8rem",
          color: "var(--muted-foreground)",
          opacity: 0.6,
        }}
      >
        v0.1.0 — Made with 💗 in Vietnam
      </p>

      {/* Pulse Animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
      `}</style>
    </main>
  );
}
