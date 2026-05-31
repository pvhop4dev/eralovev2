"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";

const LOVE_LANGUAGES = [
  {
    id: "words",
    emoji: "💬",
    label: "Lời khen ngợi",
    desc: "Thích được nghe lời yêu thương",
  },
  {
    id: "acts",
    emoji: "🤲",
    label: "Hành động",
    desc: "Thích được giúp đỡ, chăm sóc",
  },
  {
    id: "gifts",
    emoji: "🎁",
    label: "Quà tặng",
    desc: "Trân trọng những món quà ý nghĩa",
  },
  {
    id: "time",
    emoji: "⏰",
    label: "Thời gian",
    desc: "Thích dành thời gian bên nhau",
  },
  {
    id: "touch",
    emoji: "🤗",
    label: "Cử chỉ",
    desc: "Thích ôm, nắm tay, gần gũi",
  },
];

const WALLPAPERS = [
  {
    id: "primary",
    name: "Hồng mộng mơ",
    value: "linear-gradient(135deg, #FFF0F5 0%, #F3E8FF 50%, #FFF0F5 100%)",
    preview: "linear-gradient(135deg, #FF6B9D 0%, #C084FC 100%)",
  },
  {
    id: "warm",
    name: "Cam hoàng hôn",
    value: "linear-gradient(135deg, #FFF7ED 0%, #FFE4E6 50%, #FFF7ED 100%)",
    preview: "linear-gradient(135deg, #FFB347 0%, #FF6B9D 100%)",
  },
  {
    id: "cool",
    name: "Mint tươi mát",
    value: "linear-gradient(135deg, #ECFDF5 0%, #EEF2F6 50%, #ECFDF5 100%)",
    preview: "linear-gradient(135deg, #C084FC 0%, #6EE7B7 100%)",
  },
  {
    id: "deep",
    name: "Tím quyến rũ",
    value: "linear-gradient(135deg, #FAF5FF 0%, #F5F3FF 50%, #FAF5FF 100%)",
    preview: "linear-gradient(135deg, #7C3AED 0%, #C084FC 100%)",
  },
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
    wallpaper: "primary",
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const handleWallpaperChange = (wpId: string) => {
    setFormData((prev) => ({ ...prev, wallpaper: wpId }));
    const selected = WALLPAPERS.find((w) => w.id === wpId);
    if (selected) {
      document.documentElement.style.setProperty(
        "--gradient-bg",
        selected.value,
      );
    }
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setUploadError("Kích thước ảnh tối đa là 5MB");
      return;
    }

    setIsUploading(true);
    setUploadError("");

    try {
      const { useAuthStore } = await import("@/stores/auth-store");
      const token = useAuthStore.getState().accessToken;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/storage/presigned-url`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token || localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            file_name: file.name,
            content_type: file.type,
            file_type: "avatar",
          }),
        },
      );

      const data = await res.json();
      if (!res.ok) {
        setUploadError(data.error?.message || "Không thể lấy link tải ảnh");
        return;
      }

      const { upload_url, file_url } = data.data;

      const putRes = await fetch(upload_url, {
        method: "PUT",
        headers: {
          "Content-Type": file.type,
        },
        body: file,
      });

      if (!putRes.ok) {
        throw new Error("Failed to upload file to storage");
      }

      setFormData((prev) => ({ ...prev, avatar_url: file_url }));
    } catch (err) {
      setUploadError("Lỗi tải ảnh lên server lưu trữ");
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const steps = [
    "Chào mừng",
    "Thông tin",
    "Ngôn ngữ yêu",
    "Hình nền",
    "Hoàn thành",
  ];

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
        },
      );
      if (res.ok) {
        localStorage.setItem("eralove_wallpaper", formData.wallpaper);
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
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            justifyContent: "center",
            marginBottom: "2rem",
          }}
        >
          {steps.map((_, i) => (
            <div
              key={i}
              style={{
                width: i <= step ? "2rem" : "0.75rem",
                height: "0.75rem",
                borderRadius: "9999px",
                background:
                  i <= step ? "var(--gradient-primary)" : "var(--border)",
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
              <p
                style={{
                  color: "var(--muted-foreground)",
                  fontSize: "0.95rem",
                  lineHeight: 1.6,
                  marginBottom: "2rem",
                }}
              >
                Hãy hoàn thành vài bước nhỏ để bắt đầu hành trình yêu thương của
                bạn 💕
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
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                }}
              >
                {/* Avatar upload */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    marginBottom: "0.5rem",
                  }}
                >
                  <div
                    style={{
                      position: "relative",
                      width: "90px",
                      height: "90px",
                      borderRadius: "50%",
                      border: "2px dashed var(--color-rose-petal)",
                      background: "rgba(255,107,157,0.02)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      cursor: "pointer",
                      overflow: "hidden",
                      transition: "all 0.2s ease",
                    }}
                    onClick={() =>
                      document.getElementById("avatar-input")?.click()
                    }
                  >
                    {formData.avatar_url ? (
                      <img
                        src={formData.avatar_url}
                        alt="Avatar Preview"
                        style={{
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                        }}
                      />
                    ) : (
                      <span style={{ fontSize: "1.5rem" }}>📷</span>
                    )}
                    {isUploading && (
                      <div
                        style={{
                          position: "absolute",
                          top: 0,
                          left: 0,
                          width: "100%",
                          height: "100%",
                          background: "rgba(0,0,0,0.5)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: "#fff",
                          fontSize: "0.75rem",
                        }}
                      >
                        Tải lên...
                      </div>
                    )}
                  </div>
                  <input
                    id="avatar-input"
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarChange}
                    style={{ display: "none" }}
                  />
                  <button
                    type="button"
                    onClick={() =>
                      document.getElementById("avatar-input")?.click()
                    }
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--color-rose-petal)",
                      fontSize: "0.8rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      marginTop: "0.5rem",
                    }}
                  >
                    Chọn ảnh đại diện
                  </button>
                  {uploadError && (
                    <div
                      style={{
                        color: "#ef4444",
                        fontSize: "0.75rem",
                        marginTop: "0.25rem",
                      }}
                    >
                      {uploadError}
                    </div>
                  )}
                </div>

                <FormField
                  label="Tên hiển thị"
                  name="display_name"
                  type="text"
                  placeholder="Bạn muốn được gọi là gì?"
                  value={formData.display_name}
                  onChange={(e) =>
                    setFormData({ ...formData, display_name: e.target.value })
                  }
                  required
                />
                <FormField
                  label="Ngày sinh"
                  name="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) =>
                    setFormData({ ...formData, date_of_birth: e.target.value })
                  }
                  hint="Để tính cung hoàng đạo ♈"
                />
              </div>
              <div
                style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}
              >
                <Button
                  variant="ghost"
                  onClick={() => setStep(0)}
                  style={{ flex: 1 }}
                >
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
              <p
                style={{
                  color: "var(--muted-foreground)",
                  fontSize: "0.85rem",
                  textAlign: "center",
                  marginBottom: "1.25rem",
                }}
              >
                Bạn cảm thấy được yêu nhất khi...
              </p>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                }}
              >
                {LOVE_LANGUAGES.map((ll) => (
                  <button
                    key={ll.id}
                    type="button"
                    onClick={() =>
                      setFormData({ ...formData, love_language: ll.id })
                    }
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      padding: "0.875rem 1rem",
                      borderRadius: "var(--radius-md)",
                      border: `2px solid ${formData.love_language === ll.id ? "var(--color-rose-petal)" : "var(--border)"}`,
                      background:
                        formData.love_language === ll.id
                          ? "rgba(255,107,157,0.08)"
                          : "transparent",
                      cursor: "pointer",
                      textAlign: "left",
                      transition: "all 0.2s ease",
                      width: "100%",
                    }}
                  >
                    <span style={{ fontSize: "1.5rem" }}>{ll.emoji}</span>
                    <div>
                      <div
                        style={{
                          fontWeight: 600,
                          fontSize: "0.9rem",
                          color: "var(--foreground)",
                        }}
                      >
                        {ll.label}
                      </div>
                      <div
                        style={{
                          fontSize: "0.75rem",
                          color: "var(--muted-foreground)",
                        }}
                      >
                        {ll.desc}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              <div
                style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}
              >
                <Button
                  variant="ghost"
                  onClick={() => setStep(1)}
                  style={{ flex: 1 }}
                >
                  ← Quay lại
                </Button>
                <Button onClick={() => setStep(3)} style={{ flex: 2 }}>
                  Tiếp tục →
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Wallpaper Chooser */}
          {step === 3 && (
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
                Chọn hình nền 🎨
              </h2>
              <p
                style={{
                  color: "var(--muted-foreground)",
                  fontSize: "0.85rem",
                  textAlign: "center",
                  marginBottom: "1.5rem",
                }}
              >
                Hình nền này sẽ được hiển thị cho không gian yêu thương của bạn.
              </p>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "0.75rem",
                  marginBottom: "1.5rem",
                }}
              >
                {WALLPAPERS.map((wp) => (
                  <button
                    key={wp.id}
                    type="button"
                    onClick={() => handleWallpaperChange(wp.id)}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      padding: "1rem 0.5rem",
                      borderRadius: "var(--radius-md)",
                      border: `2px solid ${formData.wallpaper === wp.id ? "var(--color-rose-petal)" : "var(--border)"}`,
                      background: "var(--card)",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      transform:
                        formData.wallpaper === wp.id
                          ? "scale(1.03)"
                          : "scale(1)",
                    }}
                  >
                    <div
                      style={{
                        width: "100%",
                        height: "60px",
                        borderRadius: "var(--radius-sm)",
                        background: wp.preview,
                        marginBottom: "0.5rem",
                      }}
                    />
                    <span
                      style={{
                        fontSize: "0.8rem",
                        fontWeight: 600,
                        color: "var(--foreground)",
                      }}
                    >
                      {wp.name}
                    </span>
                  </button>
                ))}
              </div>
              <div style={{ display: "flex", gap: "0.75rem" }}>
                <Button
                  variant="ghost"
                  onClick={() => setStep(2)}
                  style={{ flex: 1 }}
                >
                  ← Quay lại
                </Button>
                <Button onClick={() => setStep(4)} style={{ flex: 2 }}>
                  Tiếp tục →
                </Button>
              </div>
            </div>
          )}

          {/* Step 4: Complete */}
          {step === 4 && (
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
              <p
                style={{
                  color: "var(--muted-foreground)",
                  fontSize: "0.9rem",
                  marginBottom: "1.5rem",
                }}
              >
                Bước tiếp theo: Tìm và ghép đôi với người yêu của bạn 💕
              </p>
              <div
                style={{
                  background: "rgba(255,107,157,0.05)",
                  borderRadius: "var(--radius-md)",
                  padding: "1rem",
                  marginBottom: "1.5rem",
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  textAlign: "left",
                }}
              >
                {formData.avatar_url && (
                  <img
                    src={formData.avatar_url}
                    alt="Avatar"
                    style={{
                      width: "50px",
                      height: "50px",
                      borderRadius: "50%",
                      objectFit: "cover",
                      border: "1px solid var(--color-rose-petal)",
                    }}
                  />
                )}
                <div
                  style={{
                    fontSize: "0.85rem",
                    color: "var(--muted-foreground)",
                  }}
                >
                  <strong>📛</strong> {formData.display_name || "—"}
                  <br />
                  <strong>🎂</strong>{" "}
                  {formData.date_of_birth || "Chưa cập nhật"}
                  <br />
                  <strong>💕</strong>{" "}
                  {LOVE_LANGUAGES.find((l) => l.id === formData.love_language)
                    ?.label || "Chưa chọn"}
                  <br />
                  <strong>🎨</strong>{" "}
                  {WALLPAPERS.find((w) => w.id === formData.wallpaper)?.name ||
                    "Mặc định"}
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.75rem" }}>
                <Button
                  variant="ghost"
                  onClick={() => setStep(3)}
                  style={{ flex: 1 }}
                >
                  ← Sửa lại
                </Button>
                <Button
                  onClick={handleSubmit}
                  isLoading={isLoading}
                  style={{ flex: 2 }}
                  size="lg"
                >
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
