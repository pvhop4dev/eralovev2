"use client";

import { useState } from "react";
import { Avatar } from "@/components/atoms/avatar";
import { Button } from "@/components/atoms/button";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { useDashboardData, useCheckinMood } from "@/hooks/use-dashboard";
import { LoveEvent } from "@/hooks/use-events";

const MOOD_EMOJIS = ["😊", "😍", "🥰", "😢", "😤", "😴", "🤗", "😎"];

const SHORTCUTS = [
  { icon: "📅", label: "Lịch", href: "/calendar", color: "#FF6B9D" },
  { icon: "💬", label: "Chat", href: "/chat", color: "#C084FC" },
  { icon: "🗺️", label: "Bản đồ", href: "/map", color: "#34D399" },
  { icon: "🤖", label: "Ari", href: "/ari", color: "#F59E0B" },
];

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { data: dashboard, isLoading } = useDashboardData();
  const checkinMoodMutation = useCheckinMood();

  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [moodSubmitted, setMoodSubmitted] = useState(false);
  const [showUnmatchModal, setShowUnmatchModal] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [isUnmatching, setIsUnmatching] = useState(false);
  const [unmatchError, setUnmatchError] = useState("");

  const handleUnmatch = async () => {
    if (confirmText !== "UNMATCH") return;
    setIsUnmatching(true);
    setUnmatchError("");
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/match/unmatch`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({ confirmation_code: confirmText }),
        }
      );
      if (res.ok) {
        setShowUnmatchModal(false);
        setConfirmText("");
        queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      } else {
        const data = await res.json();
        setUnmatchError(data.error?.message || "Không thể hủy kết nối");
      }
    } catch {
      setUnmatchError("Đã có lỗi xảy ra. Vui lòng thử lại.");
    } finally {
      setIsUnmatching(false);
    }
  };

  const submitMood = async () => {
    if (!selectedMood) return;
    try {
      await checkinMoodMutation.mutateAsync({
        mood_emoji: selectedMood,
        mood_note: undefined,
      });
      setMoodSubmitted(true);
    } catch {}
  };

  const user = dashboard?.user;
  const couple = dashboard?.couple;
  const partner = dashboard?.partner;
  const quote = dashboard?.daily_quote;
  const daysCount = dashboard?.days_together || 0;
  const upcomingEvents = dashboard?.upcoming_events || [];
  const memoryFlashback = dashboard?.memory_flashback || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-rose-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

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
            <p style={{ color: "var(--muted-foreground)", fontSize: "0.85rem", marginBottom: "1rem" }}>
              ngày yêu thương 💗
            </p>
            <button
              onClick={() => setShowUnmatchModal(true)}
              style={{
                background: "none",
                border: "none",
                color: "var(--muted-foreground)",
                fontSize: "0.75rem",
                textDecoration: "underline",
                cursor: "pointer",
                transition: "color 0.2s ease",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-rose-petal)")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "var(--muted-foreground)")}
            >
              Hủy kết nối 💔
            </button>
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

      {/* Memory Flashback */}
      {couple && memoryFlashback.length > 0 && (
        <div
          style={{
            background: "var(--gradient-primary)",
            padding: "1px",
            borderRadius: "var(--radius-xl)",
            marginBottom: "1.5rem",
            boxShadow: "var(--shadow-card)",
          }}
        >
          <div
            style={{
              background: "var(--card)",
              borderRadius: "calc(var(--radius-xl) - 1px)",
              padding: "1.5rem",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: "-10px",
                right: "-10px",
                fontSize: "4rem",
                opacity: 0.1,
                pointerEvents: "none",
              }}
            >
              ✨
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
              <span style={{ fontSize: "1.25rem" }}>✨</span>
              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "1rem",
                  fontWeight: 700,
                  color: "var(--color-rose-petal)",
                }}
              >
                Ngày này năm xưa
              </h3>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {memoryFlashback.map((event: LoveEvent) => {
                const eventYear = new Date(event.event_date).getFullYear();
                const currentYear = new Date().getFullYear();
                const yearsAgo = currentYear - eventYear;
                return (
                  <div
                    key={event.id}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "0.75rem",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "1.5rem",
                        padding: "0.5rem",
                        background: "rgba(255, 107, 157, 0.1)",
                        borderRadius: "var(--radius-md)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {event.icon || "❤️"}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", flexWrap: "wrap" }}>
                        <h4 style={{ fontWeight: 600, fontSize: "0.95rem" }}>{event.title}</h4>
                        <span
                          style={{
                            fontSize: "0.75rem",
                            color: "white",
                            background: "var(--gradient-primary)",
                            padding: "0.15rem 0.5rem",
                            borderRadius: "var(--radius-full)",
                            fontWeight: 600,
                          }}
                        >
                          {yearsAgo} năm trước ({eventYear})
                        </span>
                      </div>
                      {event.description && (
                        <p style={{ color: "var(--muted-foreground)", fontSize: "0.85rem", marginTop: "0.25rem" }}>
                          {event.description}
                        </p>
                      )}
                      {event.location_name && (
                        <p style={{ color: "var(--muted-foreground)", fontSize: "0.75rem", marginTop: "0.25rem", display: "flex", alignItems: "center", gap: "0.25rem" }}>
                          📍 {event.location_name}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

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

      {/* Upcoming Events */}
      {couple && (
        <div
          style={{
            background: "var(--card)",
            borderRadius: "var(--radius-xl)",
            padding: "1.5rem",
            boxShadow: "var(--shadow-card)",
            border: "1px solid var(--border)",
            marginTop: "1.5rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "1rem",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
              }}
            >
              📅 Sự kiện sắp tới (7 ngày tới)
            </h3>
            <Link href="/calendar" style={{ fontSize: "0.8rem", color: "var(--color-rose-petal)", fontWeight: 600, textDecoration: "none" }}>
              Xem lịch →
            </Link>
          </div>

          {upcomingEvents.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {upcomingEvents.map((event: LoveEvent & { days_until: number }) => {
                const daysUntil = event.days_until;
                let daysText = "";
                if (daysUntil === 0) {
                  daysText = "Hôm nay";
                } else if (daysUntil === 1) {
                  daysText = "Ngày mai";
                } else {
                  daysText = `Còn ${daysUntil} ngày`;
                }

                // Format date
                const dateObj = new Date(event.event_date);
                const dateStr = dateObj.toLocaleDateString("vi-VN", {
                  weekday: "long",
                  day: "numeric",
                  month: "numeric",
                });

                return (
                  <div
                    key={event.id}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "0.75rem",
                      paddingBottom: "0.75rem",
                      borderBottom: "1px solid var(--border)",
                    }}
                    className="last:border-none last:pb-0"
                  >
                    <div
                      style={{
                        fontSize: "1.25rem",
                        padding: "0.4rem",
                        background: "var(--input)",
                        borderRadius: "var(--radius-md)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {event.icon || "📅"}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                        <h4 style={{ fontWeight: 600, fontSize: "0.9rem" }}>{event.title}</h4>
                        <span
                          style={{
                            fontSize: "0.7rem",
                            fontWeight: 600,
                            color: daysUntil <= 1 ? "var(--color-rose-petal)" : "var(--muted-foreground)",
                            background: daysUntil <= 1 ? "rgba(255, 107, 157, 0.1)" : "var(--input)",
                            padding: "0.15rem 0.5rem",
                            borderRadius: "var(--radius-full)",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {daysText}
                        </span>
                      </div>
                      <p style={{ color: "var(--muted-foreground)", fontSize: "0.8rem", marginTop: "0.15rem" }}>
                        {dateStr} {event.event_time ? ` lúc ${event.event_time.slice(0, 5)}` : ""}
                      </p>
                      {event.description && (
                        <p style={{ color: "var(--muted-foreground)", fontSize: "0.8rem", marginTop: "0.25rem", fontStyle: "italic" }}>
                          {event.description}
                        </p>
                      )}
                      {event.location_name && (
                        <p style={{ color: "var(--muted-foreground)", fontSize: "0.75rem", marginTop: "0.25rem" }}>
                          📍 {event.location_name}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "1.5rem 0", color: "var(--muted-foreground)" }}>
              <p style={{ fontSize: "0.85rem", marginBottom: "1rem" }}>
                Không có sự kiện nào sắp diễn ra trong 7 ngày tới.
              </p>
              <Link href="/calendar">
                <Button size="sm" variant="ghost">💕 Tạo sự kiện mới</Button>
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Unmatch Modal */}
      {showUnmatchModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "1rem",
          }}
        >
          <div
            style={{
              background: "var(--card)",
              borderRadius: "var(--radius-xl)",
              padding: "2rem 1.5rem",
              maxWidth: "400px",
              width: "100%",
              boxShadow: "var(--shadow-card)",
              border: "1px solid var(--border)",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>💔</div>
            <h2
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "1.25rem",
                fontWeight: 700,
                marginBottom: "0.75rem",
                color: "var(--foreground)",
              }}
            >
              Hủy kết nối với {partner?.display_name}?
            </h2>
            <p
              style={{
                color: "var(--muted-foreground)",
                fontSize: "0.85rem",
                lineHeight: 1.5,
                marginBottom: "1.5rem",
              }}
            >
              Tất cả các kỷ niệm và tin nhắn sẽ bị ẩn đi. Nhập từ khóa{" "}
              <strong style={{ color: "var(--color-rose-petal)" }}>UNMATCH</strong> để xác nhận.
            </p>
            <div style={{ marginBottom: "1.5rem" }}>
              <input
                type="text"
                placeholder="Nhập UNMATCH..."
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                style={{
                  width: "100%",
                  padding: "0.75rem 1rem",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--border)",
                  background: "var(--input)",
                  color: "var(--foreground)",
                  textAlign: "center",
                  fontSize: "1rem",
                  fontWeight: 600,
                  outline: "none",
                }}
              />
              {unmatchError && (
                <p style={{ color: "#ef4444", fontSize: "0.75rem", marginTop: "0.5rem" }}>
                  {unmatchError}
                </p>
              )}
            </div>
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowUnmatchModal(false);
                  setConfirmText("");
                  setUnmatchError("");
                }}
                style={{ flex: 1 }}
                disabled={isUnmatching}
              >
                Hủy bỏ
              </Button>
              <Button
                onClick={handleUnmatch}
                isLoading={isUnmatching}
                disabled={confirmText !== "UNMATCH" || isUnmatching}
                style={{
                  flex: 1,
                  background: "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",
                }}
              >
                Xác nhận 💔
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
