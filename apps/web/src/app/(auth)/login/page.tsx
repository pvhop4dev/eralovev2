"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Script from "next/script";
import { useRouter } from "next/navigation";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";
import { useAuthStore } from "@/stores/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleGoogleCredentialResponse = async (response: any) => {
    setIsLoading(true);
    setErrors({});
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/oauth`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            provider: "google",
            token: response.credential,
          }),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        setErrors({ form: data.error?.message || "Đăng nhập bằng Google thất bại" });
        return;
      }

      // Set auth state
      setAuth(data.data.user, data.data.access_token);

      // Chuyển hướng sang onboarding nếu chưa onboard, ngược lại dashboard
      if (!data.data.user.is_onboarded) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } catch {
      setErrors({ form: "Không thể kết nối đến server để đăng nhập Google" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const google = (window as any).google;
    if (scriptLoaded || (typeof window !== "undefined" && google)) {
      try {
        google.accounts.id.initialize({
          client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "629910543789-fakeclientid.apps.googleusercontent.com",
          callback: handleGoogleCredentialResponse,
        });
        google.accounts.id.renderButton(
          document.getElementById("google-signin-btn"),
          {
            theme: "outline",
            size: "large",
            width: "360",
            shape: "rectangular",
          }
        );
      } catch (err) {
        console.error("Failed to initialize Google Sign-In:", err);
      }
    }
  }, [scriptLoaded]);

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

      {/* Google Login button */}
      <div style={{ display: "flex", justifyContent: "center", width: "100%", minHeight: "40px" }}>
        <div id="google-signin-btn" />
      </div>

      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setScriptLoaded(true)}
      />

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
