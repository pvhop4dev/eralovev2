"use client";

import { useState, useEffect } from "react";
import { Avatar } from "@/components/atoms/avatar";
import { Button } from "@/components/atoms/button";
import Link from "next/link";

const MOOD_EMOJIS = ["😊", "😍", "🥰", "😢", "😤", "😴", "🤗", "😎"];

const SHORTCUTS = [
  { icon: "📅", label: "Lịch", href: "/calendar", color: "#FF6B9D" },
  { icon: "💬", label: "Chat", href: "/chat", color: "#C084FC" },
  { icon: "🗺️", label: "Bản đồ", href: "/map", color: "#34D399" },
  { icon: "🤖", label: "Ari", href: "/ari", color: "#F59E0B" },
];

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [moodNote, setMoodNote] = useState("");
  const [moodSubmitted, setMoodSubmitted] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/dashboard`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        }
      );
      if (res.ok) {
        const data = await res.json();
        setDashboard(data.data);
      }
    } catch {
      // Offline — show placeholder
    }
  };

  const submitMood = async () => {
    if (!selectedMood) return;
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/mood/checkin`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({ mood_emoji: selectedMood, mood_note: moodNote || undefined }),
        }
      );
      setMoodSubmitted(true);
    } catch {}
  };

  const user = dashboard?.user;
  const couple = dashboard?.couple;
  const partner = dashboard?.partner;
  const quote = dashboard?.daily_quote;
  const daysCount = dashboard?.days_together || 0;

  return (
    <div style={{ padding: "1.5rem", maxWidth: "800px", margin: "0 auto" }}>
      {/* Hero — Couple Info */}
      <div
        style={{
          background: "var(--card)",
          borderRadius: "var(--radius-xl)",
          padding: "2rem",
          textAlign: "center",
          boxShadow: "var(--shadow-card)",
          border: "1px solid var(--border)",
          marginBottom: "1.5rem",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Gradient accent */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "4px",
            background: "var(--gradient-primary)",
          }}
        />

        {couple && partner ? (
          <>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "1rem", marginBottom: "1rem" }}>
              <Avatar fallback={user?.display_name} size="lg" />
              <div style={{ fontSize: "1.5rem" }}>💕</div>
              <Avatar fallback={partner?.display_name} size="lg" />
            </div>
            <h1
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "1.25rem",
                fontWeight: 700,
                marginBottom: "0.5rem",
              }}
            >
              {user?.display_name} & {partner?.display_name}
            </h1>
            <div
              style={{
                fontSize: "2.5rem",
                fontWeight: 800,
                background: "var(--gradient-primary)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                lineHeight: 1.2,
              }}
            >
              {daysCount}
            </div>
            <p style={{ color: "var(--muted-foreground)", fontSize: "0.85rem" }}>
              ngày yêu thương 💗
            </p>
          </>
        ) : (
          <>
            <div style={{ fontSize: "3rem", marginBottom: "0.75rem" }}>💗</div>
            <h1
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "1.25rem",
                fontWeight: 700,
                marginBottom: "0.5rem",
              }}
            >
              Xin chào, {user?.display_name || "bạn"} 💕
            </h1>
            <p style={{ color: "var(--muted-foreground)", fontSize: "0.9rem", marginBottom: "1rem" }}>
              Hãy ghép đôi với người yêu để bắt đầu!
            </p>
            <Link href="/match">
              <Button>💕 Tìm người yêu</Button>
            </Link>
          </>
        )}
      </div>

      {/* Quick Shortcuts */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "0.75rem",
          marginBottom: "1.5rem",
        }}
      >
        {SHORTCUTS.map((s) => (
          <Link
            key={s.href}
            href={s.href}
            style={{
              background: "var(--card)",
              borderRadius: "var(--radius-lg)",
              padding: "1rem 0.5rem",
              textAlign: "center",
              textDecoration: "none",
              boxShadow: "var(--shadow-card)",
              border: "1px solid var(--border)",
              transition: "all 0.2s ease",
            }}
          >
            <div style={{ fontSize: "1.75rem", marginBottom: "0.25rem" }}>{s.icon}</div>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--muted-foreground)" }}>
              {s.label}
            </div>
          </Link>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.5rem" }} className="md:grid-cols-2">
        {/* Daily Quote */}
        <div
          style={{
            background: "var(--gradient-primary)",
            borderRadius: "var(--radius-xl)",
            padding: "1.5rem",
            color: "white",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-20px",
              right: "-20px",
              fontSize: "5rem",
              opacity: 0.15,
            }}
          >
            💗
          </div>
          <p style={{ fontSize: "0.75rem", opacity: 0.8, marginBottom: "0.5rem", fontWeight: 600 }}>
            ✨ Câu nói hôm nay
          </p>
          <p style={{ fontSize: "1rem", fontWeight: 600, lineHeight: 1.6, marginBottom: "0.75rem" }}>
            &ldquo;{quote?.text || "Yêu nhau là cùng nhìn về một hướng."}&rdquo;
          </p>
          <p style={{ fontSize: "0.75rem", opacity: 0.7 }}>
            — {quote?.author || "Eralove"}
          </p>
        </div>

        {/* Mood Check-in */}
        <div
          style={{
            background: "var(--card)",
            borderRadius: "var(--radius-xl)",
            padding: "1.5rem",
            boxShadow: "var(--shadow-card)",
            border: "1px solid var(--border)",
          }}
        >
          <p style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.75rem" }}>
            Hôm nay bạn cảm thấy thế nào? 💭
          </p>
          {moodSubmitted ? (
            <div style={{ textAlign: "center", padding: "0.5rem 0" }}>
              <div style={{ fontSize: "2rem", marginBottom: "0.25rem" }}>{selectedMood}</div>
              <p style={{ fontSize: "0.8rem", color: "var(--muted-foreground)" }}>
                Đã ghi nhận tâm trạng! 🎉
              </p>
            </div>
          ) : (
            <>
              <div
                style={{
                  display: "flex",
                  gap: "0.5rem",
                  flexWrap: "wrap",
                  marginBottom: "0.75rem",
                }}
              >
                {MOOD_EMOJIS.map((emoji) => (
                  <button
                    key={emoji}
                    type="button"
                    onClick={() => setSelectedMood(emoji)}
                    style={{
                      width: "40px",
                      height: "40px",
                      borderRadius: "50%",
                      border: `2px solid ${selectedMood === emoji ? "var(--color-rose-petal)" : "var(--border)"}`,
                      background: selectedMood === emoji ? "rgba(255,107,157,0.1)" : "transparent",
                      fontSize: "1.25rem",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      transform: selectedMood === emoji ? "scale(1.15)" : "scale(1)",
                    }}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
              {selectedMood && (
                <Button size="sm" onClick={submitMood} fullWidth>
                  Ghi nhận {selectedMood}
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
