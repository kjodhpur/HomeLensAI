import type { Metadata, Viewport } from "next";
import "./liquid.css";
import "./dashboard.css";

export const metadata: Metadata = {
  title: "HomeLens AI — Business Risk Command Center",
  description: "Review-based risk intelligence for home-service providers: complaint aspects, provider trajectories and explainable evidence.",
  icons: { icon: "/logo-mark.svg" },
};
export const viewport: Viewport = { themeColor: "#0D0D11", colorScheme: "dark" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
