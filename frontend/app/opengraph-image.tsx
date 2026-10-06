import { ImageResponse } from "next/og";

export const alt = "HomeLens AI — review-based risk intelligence for home-service providers";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", padding: 72, background: "linear-gradient(135deg,#eef1ff,#f6f4f1 55%,#ffe9d2)", color: "#14141a" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18, fontSize: 34, fontWeight: 700 }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: "linear-gradient(160deg,#ffb23c,#f5780f)" }} />
          HomeLens AI
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ fontSize: 80, fontWeight: 700, letterSpacing: -3, lineHeight: 1.02, maxWidth: 940 }}>Know which providers need attention, and why.</div>
          <div style={{ fontSize: 30, color: "#55566a" }}>Review-based risk signals for home-service providers</div>
        </div>
      </div>
    ),
    size,
  );
}
