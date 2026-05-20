"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";
import { useAuthStore } from "@/stores/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};
    if (!formData.email) newErrors.email = "Email là bắt buộc";
    if (!formData.password) newErrors.password = "Mật khẩu là bắt buộc";
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(formData),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        setErrors({ form: data.error?.message || "Đăng nhập thất bại" });
        return;
      }
      // Set auth state
      setAuth(data.data.user, data.data.access_token);
      router.push("/dashboard");
    } catch {
      setErrors({ form: "Không thể kết nối đến server" });
    } finally {
      setIsLoading(false);
    }
  };

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
          Chào mừng trở lại 💗
        </h1>
        <p style={{ color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
          Đăng nhập để tiếp tục hành trình yêu thương
        </p>
      </div>

      {errors.form && (
        <div
          style={{
            padding: "0.75rem 1rem",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "var(--radius-md)",
            color: "#ef4444",
            fontSize: "0.875rem",
            marginBottom: "1rem",
          }}
        >
          {errors.form}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <FormField
          label="Email"
          name="email"
          type="email"
          placeholder="love@example.com"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
          required
        />
        <FormField
          label="Mật khẩu"
          name="password"
          type="password"
          placeholder="Nhập mật khẩu"
          value={formData.password}
          onChange={handleChange}
          error={errors.password}
          required
        />

        <div style={{ textAlign: "right" }}>
          <Link
            href="/forgot-password"
            style={{
              fontSize: "0.8rem",
              color: "var(--color-lavender-dream)",
              textDecoration: "none",
            }}
          >
            Quên mật khẩu?
          </Link>
        </div>

        <Button type="submit" fullWidth isLoading={isLoading} size="lg">
          Đăng nhập 💕
        </Button>
      </form>

      {/* Divider */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          margin: "1.25rem 0",
        }}
      >
        <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
        <span style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>
          hoặc
        </span>
        <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
      </div>

      {/* Google Login (placeholder) */}
      <Button variant="secondary" fullWidth size="lg" disabled>
        <svg width="18" height="18" viewBox="0 0 24 24">
          <path
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
            fill="#4285F4"
          />
          <path
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            fill="#34A853"
          />
          <path
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            fill="#FBBC05"
          />
          <path
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            fill="#EA4335"
          />
        </svg>
        Đăng nhập với Google (sắp ra mắt)
      </Button>

      <p
        style={{
          textAlign: "center",
          marginTop: "1.25rem",
          fontSize: "0.875rem",
          color: "var(--muted-foreground)",
        }}
      >
        Chưa có tài khoản?{" "}
        <Link
          href="/register"
          style={{
            color: "var(--color-rose-petal)",
            fontWeight: 600,
            textDecoration: "none",
          }}
        >
          Đăng ký ngay
        </Link>
      </p>
    </>
  );
}
