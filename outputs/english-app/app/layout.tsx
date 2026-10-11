import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "English Garden — Mỗi ngày một bước tiến",
  description: "Học tiếng Anh, ôn từ vựng, nhập tài liệu và lưu tiến độ của bạn.",
  manifest: '/manifest.webmanifest',
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="antialiased">{children}</body>
    </html>
  );
}
