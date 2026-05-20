"use client";

import { Sidebar } from "@/components/organisms/sidebar";
import { BottomNav } from "@/components/organisms/bottom-nav";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div style={{ minHeight: "100vh", background: "var(--gradient-bg)" }}>
      {/* Desktop Sidebar — hidden on mobile */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* Main Content */}
      <main
        style={{ paddingBottom: "80px" }}
        className="md:ml-[240px] md:pb-0"
      >
        {children}
      </main>

      {/* Mobile Bottom Nav — hidden on desktop */}
      <div className="block md:hidden">
        <BottomNav />
      </div>
    </div>
  );
}
