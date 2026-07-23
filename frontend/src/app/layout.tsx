import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FitCoach AI — Health & Fitness Advisor",
  description: "Proactive health and fitness AI chatbot",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
