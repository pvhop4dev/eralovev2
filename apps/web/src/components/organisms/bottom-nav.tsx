"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/dashboard", icon: "🏠", label: "Home" },
  { href: "/chat", icon: "💬", label: "Chat" },
  { href: "/calendar", icon: "📅", label: "Lịch" },
  { href: "/match", icon: "💕", label: "Match" },
  { href: "/onboarding", icon: "⚙️", label: "More" },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        height: "64px",
        background: "var(--card)",
        borderTop: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-around",
        paddingBottom: "env(safe-area-inset-bottom, 0px)",
        zIndex: 50,
      }}
    >
      {TABS.map((tab) => {
        const isActive = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "0.125rem",
              textDecoration: "none",
              fontSize: "0.7rem",
              fontWeight: isActive ? 600 : 400,
              color: isActive ? "var(--color-rose-petal)" : "var(--muted-foreground)",
              transition: "all 0.2s ease",
            }}
          >
            <span style={{ fontSize: "1.25rem" }}>{tab.icon}</span>
            <span>{tab.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
