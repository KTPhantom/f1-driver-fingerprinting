import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

export const metadata: Metadata = {
  title: "F1 Driver Fingerprinting — Behavioral Telemetry Analytics",
  description: "Identify Formula 1 drivers purely from telemetry patterns using UMAP + HDBSCAN unsupervised clustering. 30-dimensional behavioral fingerprints across braking, throttle, cornering, gear shifts, and speed profiles. Powered by 2025 season data.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geist.variable} ${geistMono.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
