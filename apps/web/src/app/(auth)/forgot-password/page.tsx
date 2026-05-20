"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError("Vui lòng nhập email");
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/forgot-password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );
      if (res.ok) {
        setSent(true);
      }
    } catch {
      setError("Không thể kết nối đến server");
    } finally {
      setIsLoading(false);
    }
  };

  if (sent) {
    return (
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📧</div>
        <h1
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "1.25rem",
            fontWeight: 700,
            marginBottom: "0.5rem",
          }}
        >
          Kiểm tra email
        </h1>
        <p style={{ color: "var(--muted-foreground)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>
          Nếu email <strong>{email}</strong> tồn tại, bạn sẽ nhận được link đặt lại mật khẩu.
        </p>
        <Link
          href="/login"
          style={{
            color: "var(--color-rose-petal)",
            fontWeight: 600,
            textDecoration: "none",
          }}
        >
          ← Quay lại đăng nhập
        </Link>
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
            color: "var(--foreground)",
            marginBottom: "0.25rem",
          }}
        >
          Quên mật khẩu? 🔑
        </h1>
        <p style={{ color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
          Nhập email để nhận link đặt lại mật khẩu
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
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <FormField
          label="Email"
          name="email"
          type="email"
          placeholder="love@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Button type="submit" fullWidth isLoading={isLoading} size="lg">
          Gửi link đặt lại 📧
        </Button>
      </form>

      <p
        style={{
          textAlign: "center",
          marginTop: "1.25rem",
          fontSize: "0.875rem",
          color: "var(--muted-foreground)",
        }}
      >
        <Link
          href="/login"
          style={{ color: "var(--color-lavender-dream)", textDecoration: "none" }}
        >
          ← Quay lại đăng nhập
        </Link>
      </p>
    </>
  );
}
