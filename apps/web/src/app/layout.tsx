import type { Metadata } from "next";
import { Nunito, Inter } from "next/font/google";
import { Providers } from "./providers";
import "./globals.css";

const nunito = Nunito({
  subsets: ["latin", "vietnamese"],
  variable: "--font-nunito",
  display: "swap",
  weight: ["400", "600", "700", "800"],
});

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    template: "%s | Eralove",
    default: "Eralove — Nơi lưu giữ mọi khoảnh khắc yêu thương 💗",
  },
  description:
    "Ứng dụng dành riêng cho các cặp đôi — lưu giữ ký ức, kết nối mỗi ngày, và nhận gợi ý yêu thương từ AI.",
  keywords: ["couples app", "love", "dating", "memories", "eralove"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body
        className={`${nunito.variable} ${inter.variable} font-sans antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
