"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light") {
      setIsDark(false);
      document.documentElement.setAttribute("data-theme", "light");
    }
  }, []);

  const toggle = () => {
    const newTheme = isDark ? "light" : "dark";
    setIsDark(!isDark);
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="Toggle theme"
      title={isDark ? "Chuyển sang sáng" : "Chuyển sang tối"}
      style={{
        width: "40px",
        height: "40px",
        borderRadius: "50%",
        border: "1px solid var(--border)",
        background: "var(--card)",
        cursor: "pointer",
        fontSize: "1.1rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transition: "all 0.3s ease",
      }}
    >
      {isDark ? "🌙" : "☀️"}
    </button>
  );
}
