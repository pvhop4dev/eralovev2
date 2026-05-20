"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";

const LOVE_LANGUAGES = [
  { id: "words", emoji: "💬", label: "Lời khen ngợi", desc: "Thích được nghe lời yêu thương" },
  { id: "acts", emoji: "🤲", label: "Hành động", desc: "Thích được giúp đỡ, chăm sóc" },
  { id: "gifts", emoji: "🎁", label: "Quà tặng", desc: "Trân trọng những món quà ý nghĩa" },
  { id: "time", emoji: "⏰", label: "Thời gian", desc: "Thích dành thời gian bên nhau" },
  { id: "touch", emoji: "🤗", label: "Cử chỉ", desc: "Thích ôm, nắm tay, gần gũi" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    display_name: "",
    date_of_birth: "",
    love_language: "",
    avatar_url: "",
  });

  const steps = ["Chào mừng", "Thông tin", "Ngôn ngữ yêu", "Hoàn thành"];

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/users/me/onboarding`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            display_name: formData.display_name,
            date_of_birth: formData.date_of_birth || undefined,
            love_language: formData.love_language || undefined,
            avatar_url: formData.avatar_url || undefined,
          }),
        }
      );
      if (res.ok) {
        router.push("/match");
      }
    } catch {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--gradient-bg)",
        padding: "1rem",
      }}
    >
      <div style={{ width: "100%", maxWidth: "500px" }}>
        {/* Progress */}
        <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center", marginBottom: "2rem" }}>
          {steps.map((_, i) => (
            <div
              key={i}
              style={{
                width: i <= step ? "2rem" : "0.75rem",
                height: "0.75rem",
                borderRadius: "9999px",
                background: i <= step ? "var(--gradient-primary)" : "var(--border)",
                transition: "all 0.3s ease",
              }}
            />
          ))}
        </div>

        {/* Card */}
        <div
          style={{
            background: "var(--card)",
            borderRadius: "var(--radius-xl)",
            padding: "2.5rem 2rem",
            boxShadow: "var(--shadow-card)",
            border: "1px solid var(--border)",
          }}
        >
          {/* Step 0: Welcome */}
          {step === 0 && (
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>💗</div>
              <h1
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "1.75rem",
                  fontWeight: 800,
                  background: "var(--gradient-primary)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  marginBottom: "0.75rem",
                }}
              >
                Chào mừng đến Eralove!
              </h1>
              <p style={{ color: "var(--muted-foreground)", fontSize: "0.95rem", lineHeight: 1.6, marginBottom: "2rem" }}>
                Hãy hoàn thành vài bước nhỏ để bắt đầu hành trình yêu thương của bạn 💕
              </p>
              <Button onClick={() => setStep(1)} fullWidth size="lg">
                Bắt đầu nào! 🚀
              </Button>
            </div>
          )}

          {/* Step 1: Profile Info */}
          {step === 1 && (
            <div>
              <h2
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "1.25rem",
                  fontWeight: 700,
                  textAlign: "center",
                  marginBottom: "1.5rem",
                }}
              >
                Thông tin của bạn 📝
              </h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <FormField
                  label="Tên hiển thị"
                  name="display_name"
                  type="text"
                  placeholder="Bạn muốn được gọi là gì?"
                  value={formData.display_name}
                  onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                  required
                />
                <FormField
                  label="Ngày sinh"
                  name="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  hint="Để tính cung hoàng đạo ♈"
                />
              </div>
              <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
                <Button variant="ghost" onClick={() => setStep(0)} style={{ flex: 1 }}>
                  ← Quay lại
                </Button>
                <Button
                  onClick={() => setStep(2)}
                  disabled={!formData.display_name}
                  style={{ flex: 2 }}
                >
                  Tiếp tục →
                </Button>
              </div>
            </div>
          )}

          {/* Step 2: Love Language */}
          {step === 2 && (
            <div>
              <h2
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "1.25rem",
                  fontWeight: 700,
                  textAlign: "center",
                  marginBottom: "0.5rem",
                }}
              >
                Ngôn ngữ tình yêu 💕
              </h2>
              <p style={{ color: "var(--muted-foreground)", fontSize: "0.85rem", textAlign: "center", marginBottom: "1.25rem" }}>
                Bạn cảm thấy được yêu nhất khi...
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {LOVE_LANGUAGES.map((ll) => (
                  <button
                    key={ll.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, love_language: ll.id })}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      padding: "0.875rem 1rem",
                      borderRadius: "var(--radius-md)",
                      border: `2px solid ${formData.love_language === ll.id ? "var(--color-rose-petal)" : "var(--border)"}`,
                      background: formData.love_language === ll.id ? "rgba(255,107,157,0.08)" : "transparent",
                      cursor: "pointer",
                      textAlign: "left",
                      transition: "all 0.2s ease",
                      width: "100%",
                    }}
                  >
                    <span style={{ fontSize: "1.5rem" }}>{ll.emoji}</span>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--foreground)" }}>{ll.label}</div>
                      <div style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>{ll.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
              <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
                <Button variant="ghost" onClick={() => setStep(1)} style={{ flex: 1 }}>
                  ← Quay lại
                </Button>
                <Button onClick={() => setStep(3)} style={{ flex: 2 }}>
                  Tiếp tục →
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Complete */}
          {step === 3 && (
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎉</div>
              <h2
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "1.5rem",
                  fontWeight: 700,
                  marginBottom: "0.5rem",
                }}
              >
                Sẵn sàng rồi!
              </h2>
              <p style={{ color: "var(--muted-foreground)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
                Bước tiếp theo: Tìm và ghép đôi với người yêu của bạn 💕
              </p>
              <div
                style={{
                  background: "rgba(255,107,157,0.05)",
                  borderRadius: "var(--radius-md)",
                  padding: "1rem",
                  marginBottom: "1.5rem",
                  textAlign: "left",
                }}
              >
                <div style={{ fontSize: "0.85rem", color: "var(--muted-foreground)" }}>
                  <strong>📛</strong> {formData.display_name || "—"}<br />
                  <strong>🎂</strong> {formData.date_of_birth || "Chưa cập nhật"}<br />
                  <strong>💕</strong> {LOVE_LANGUAGES.find(l => l.id === formData.love_language)?.label || "Chưa chọn"}
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.75rem" }}>
                <Button variant="ghost" onClick={() => setStep(2)} style={{ flex: 1 }}>
                  ← Sửa lại
                </Button>
                <Button onClick={handleSubmit} isLoading={isLoading} style={{ flex: 2 }} size="lg">
                  Hoàn thành 🎉
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
