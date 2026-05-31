"use client";

import { useState, useRef, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/atoms/button";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [verified, setVerified] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return; // Only digits

    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);
    setError("");

    // Auto-focus next
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    const newOtp = [...otp];
    for (let i = 0; i < text.length; i++) {
      newOtp[i] = text[i];
    }
    setOtp(newOtp);
    inputRefs.current[Math.min(text.length, 5)]?.focus();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otp.join("");
    if (code.length !== 6) {
      setError("Vui lòng nhập đầy đủ 6 chữ số");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/verify-email`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, otp: code }),
        },
      );
      const data = await res.json();
      if (!res.ok) {
        setError(data.error?.message || "Xác minh thất bại");
        return;
      }
      setVerified(true);
      setTimeout(() => router.push("/login"), 2000);
    } catch {
      setError("Không thể kết nối đến server");
    } finally {
      setIsLoading(false);
    }
  };

  if (verified) {
    return (
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎉</div>
        <h1
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "1.25rem",
            fontWeight: 700,
            marginBottom: "0.5rem",
          }}
        >
          Email đã xác minh!
        </h1>
        <p style={{ color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
          Đang chuyển hướng đến trang đăng nhập...
        </p>
      </div>
    );
  }

  return (
    <>
      <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
        <h1
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "1.5rem",
            fontWeight: 700,
            marginBottom: "0.25rem",
          }}
        >
          Xác minh email 📧
        </h1>
        <p style={{ color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
          Nhập mã 6 chữ số đã gửi đến
          <br />
          <strong style={{ color: "var(--color-rose-petal)" }}>{email}</strong>
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "0.75rem 1rem",
            background: "rgba(239, 68, 68, 0.1)",
            borderRadius: "var(--radius-md)",
            color: "#ef4444",
            fontSize: "0.875rem",
            marginBottom: "1rem",
            textAlign: "center",
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            justifyContent: "center",
            marginBottom: "1.5rem",
          }}
          onPaste={handlePaste}
        >
          {otp.map((digit, i) => (
            <input
              key={i}
              ref={(el) => {
                inputRefs.current[i] = el;
              }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              style={{
                width: "48px",
                height: "56px",
                textAlign: "center",
                fontSize: "1.5rem",
                fontWeight: 700,
                fontFamily: "monospace",
                borderRadius: "var(--radius-md)",
                border: `2px solid ${digit ? "var(--color-rose-petal)" : "var(--border)"}`,
                background: "var(--card)",
                color: "var(--foreground)",
                outline: "none",
                transition: "var(--transition-fast)",
              }}
            />
          ))}
        </div>

        <Button type="submit" fullWidth isLoading={isLoading} size="lg">
          Xác minh ✅
        </Button>
      </form>

      <p
        style={{
          textAlign: "center",
          marginTop: "1.25rem",
          fontSize: "0.8rem",
          color: "var(--muted-foreground)",
        }}
      >
        Không nhận được mã?{" "}
        <button
          type="button"
          style={{
            color: "var(--color-lavender-dream)",
            fontWeight: 600,
            background: "none",
            border: "none",
            cursor: "pointer",
          }}
        >
          Gửi lại
        </button>
      </p>
    </>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div style={{ textAlign: "center", padding: "2rem" }}>Đang tải...</div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
