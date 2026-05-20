"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", icon: "🏠", label: "Trang chủ" },
  { href: "/calendar", icon: "📅", label: "Lịch" },
  { href: "/match", icon: "💕", label: "Ghép đôi" },
  { href: "/match/requests", icon: "💌", label: "Yêu cầu" },
  { href: "/onboarding", icon: "⚙️", label: "Cài đặt" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      style={{
        width: "240px",
        height: "100vh",
        position: "fixed",
        left: 0,
        top: 0,
        background: "var(--card)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        padding: "1.5rem 0.75rem",
        zIndex: 50,
      }}
    >
      {/* Logo */}
      <Link
        href="/dashboard"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          padding: "0 0.75rem",
          marginBottom: "2rem",
          textDecoration: "none",
        }}
      >
        <span style={{ fontSize: "1.5rem" }}>💗</span>
        <span
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "1.25rem",
            fontWeight: 800,
            background: "var(--gradient-primary)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Eralove
        </span>
      </Link>

      {/* Nav */}
      <nav style={{ display: "flex", flexDirection: "column", gap: "0.25rem", flex: 1 }}>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.75rem",
                borderRadius: "var(--radius-md)",
                textDecoration: "none",
                fontWeight: isActive ? 600 : 400,
                fontSize: "0.9rem",
                color: isActive ? "var(--foreground)" : "var(--muted-foreground)",
                background: isActive ? "rgba(255,107,157,0.1)" : "transparent",
                transition: "all 0.2s ease",
              }}
            >
              <span style={{ fontSize: "1.25rem" }}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
