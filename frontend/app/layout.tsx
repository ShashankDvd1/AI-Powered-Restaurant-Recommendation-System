import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zomato AI Recommendations",
  description: "AI-powered restaurant recommendations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
