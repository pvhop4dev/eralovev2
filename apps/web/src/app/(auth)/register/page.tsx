"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    display_name: "",
    username: "",
    date_of_birth: "",
    gender: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error on change
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.email) newErrors.email = "Email là bắt buộc";
    if (!formData.password) newErrors.password = "Mật khẩu là bắt buộc";
    else if (formData.password.length < 8) newErrors.password = "Mật khẩu cần ít nhất 8 ký tự";
    if (formData.password !== formData.confirmPassword)
      newErrors.confirmPassword = "Mật khẩu xác nhận không khớp";
    if (!formData.display_name) newErrors.display_name = "Tên hiển thị là bắt buộc";
    if (!formData.username) newErrors.username = "Username là bắt buộc";
    else if (!/^[a-zA-Z0-9_]+$/.test(formData.username))
      newErrors.username = "Username chỉ được chứa chữ, số và _";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            display_name: formData.display_name,
            username: formData.username,
            date_of_birth: formData.date_of_birth || undefined,
            gender: formData.gender || undefined,
          }),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        setErrors({ form: data.error?.message || "Đăng ký thất bại" });
        return;
      }
      // Success — redirect to verify email
      router.push(`/verify-email?email=${encodeURIComponent(formData.email)}`);
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
          Tạo tài khoản 💕
        </h1>
        <p style={{ color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
          Bắt đầu hành trình yêu thương cùng Eralove
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
          label="Tên hiển thị"
          name="display_name"
          type="text"
          placeholder="Tên của bạn"
          value={formData.display_name}
          onChange={handleChange}
          error={errors.display_name}
          required
        />
        <FormField
          label="Username"
          name="username"
          type="text"
          placeholder="username_cua_ban"
          value={formData.username}
          onChange={handleChange}
          error={errors.username}
          hint="Chữ, số và dấu gạch dưới"
          required
        />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
          <FormField
            label="Ngày sinh"
            name="date_of_birth"
            type="date"
            value={formData.date_of_birth}
            onChange={handleChange}
          />
          <div className="space-y-1.5">
            <label htmlFor="gender" className="block text-sm font-medium text-[var(--foreground)]">
              Giới tính
            </label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className="w-full h-11 px-4 rounded-xl text-sm bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-rose-petal)]"
            >
              <option value="">Chọn...</option>
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
              <option value="other">Khác</option>
            </select>
          </div>
        </div>
        <FormField
          label="Mật khẩu"
          name="password"
          type="password"
          placeholder="Ít nhất 8 ký tự"
          value={formData.password}
          onChange={handleChange}
          error={errors.password}
          required
        />
        <FormField
          label="Xác nhận mật khẩu"
          name="confirmPassword"
          type="password"
          placeholder="Nhập lại mật khẩu"
          value={formData.confirmPassword}
          onChange={handleChange}
          error={errors.confirmPassword}
          required
        />

        <Button type="submit" fullWidth isLoading={isLoading} size="lg">
          Đăng ký 🎉
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
        Đã có tài khoản?{" "}
        <Link
          href="/login"
          style={{
            color: "var(--color-rose-petal)",
            fontWeight: 600,
            textDecoration: "none",
          }}
        >
          Đăng nhập
        </Link>
      </p>
    </>
  );
}
