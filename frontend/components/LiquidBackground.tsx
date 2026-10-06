"use client";

import { useEffect, useRef } from "react";

interface Blob {
  hue: string; // r,g,b
  x: number; // base position (0..1)
  y: number;
  r: number; // radius as a fraction of the shorter side
  fx: number; // drift frequencies
  fy: number;
  px: number; // drift phases
  py: number;
  follow: number; // how strongly it is drawn toward the pointer (0 = none)
  a: number; // alpha
}

const BLOBS: Blob[] = [
  { hue: "255,150,50", x: 0.2, y: 0.26, r: 0.46, fx: 0.11, fy: 0.09, px: 0.4, py: 1.7, follow: 0.55, a: 0.5 }, // sun orange
  { hue: "176,198,255", x: 0.82, y: 0.2, r: 0.42, fx: 0.08, fy: 0.12, px: 2.1, py: 0.3, follow: 0.28, a: 0.62 }, // periwinkle sky
  { hue: "255,205,70", x: 0.7, y: 0.8, r: 0.44, fx: 0.1, fy: 0.07, px: 4.2, py: 2.6, follow: 0.4, a: 0.55 }, // sun yellow
  { hue: "255,196,160", x: 0.1, y: 0.86, r: 0.36, fx: 0.07, fy: 0.1, px: 5.1, py: 3.3, follow: 0.18, a: 0.5 }, // peach
  { hue: "255,214,120", x: 0.5, y: 0.5, r: 0.5, fx: 0.06, fy: 0.05, px: 1.1, py: 4.4, follow: 0.7, a: 0.3 }, // warm glow that follows the pointer
  { hue: "206,214,255", x: 0.92, y: 0.6, r: 0.3, fx: 0.09, fy: 0.08, px: 3.3, py: 5.2, follow: 0.1, a: 0.4 },
];

/**
 * The aura beneath the glass: a few large, blurred liquid globs that drift on slow sine paths, merge additively
 * and are gently drawn toward the pointer. Rendered at low resolution (cheap) and softened with CSS blur.
 */
export function LiquidBackground() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const SCALE = 0.25; // draw at quarter resolution
    let w = 0;
    let h = 0;
    const resize = () => {
      w = Math.max(160, Math.round(window.innerWidth * SCALE));
      h = Math.max(100, Math.round(window.innerHeight * SCALE));
      canvas.width = w;
      canvas.height = h;
    };
    resize();
    window.addEventListener("resize", resize);

    const mouse = { x: 0.5, y: 0.4, tx: 0.5, ty: 0.4 };
    const onMove = (e: PointerEvent) => {
      mouse.tx = e.clientX / window.innerWidth;
      mouse.ty = e.clientY / window.innerHeight;
    };
    window.addEventListener("pointermove", onMove, { passive: true });

    let raf = 0;
    let last = 0;
    const draw = (now: number) => {
      raf = requestAnimationFrame(draw);
      if (now - last < 33) return; // ~30 fps is plenty for a slow aura
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      mouse.x += (mouse.tx - mouse.x) * Math.min(1, dt * 1.6);
      mouse.y += (mouse.ty - mouse.y) * Math.min(1, dt * 1.6);
      const t = now / 1000;

      ctx.globalCompositeOperation = "source-over";
      ctx.fillStyle = "#fff4e0";
      ctx.fillRect(0, 0, w, h);
      ctx.globalCompositeOperation = "source-over"; // light canvas: blobs layer over the cream instead of adding light
      const side = Math.min(w, h);
      for (const b of BLOBS) {
        const driftX = Math.sin(t * b.fx * 2 * Math.PI * 0.35 + b.px) * 0.16 + Math.sin(t * b.fx * 0.9 + b.py) * 0.06;
        const driftY = Math.cos(t * b.fy * 2 * Math.PI * 0.35 + b.py) * 0.14 + Math.sin(t * b.fy * 1.3 + b.px) * 0.05;
        const x = (b.x + driftX + (mouse.x - 0.5) * b.follow * 0.5) * w;
        const y = (b.y + driftY + (mouse.y - 0.5) * b.follow * 0.5) * h;
        const breathe = 1 + Math.sin(t * 0.5 + b.px) * 0.08;
        const r = b.r * side * 1.6 * breathe;
        const g = ctx.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, `rgba(${b.hue},${b.a})`);
        g.addColorStop(0.45, `rgba(${b.hue},${b.a * 0.45})`);
        g.addColorStop(1, `rgba(${b.hue},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }
      if (reduce) cancelAnimationFrame(raf);
    };
    raf = requestAnimationFrame(draw);

    const onVis = () => {
      if (document.hidden) cancelAnimationFrame(raf);
      else if (!reduce) raf = requestAnimationFrame(draw);
    };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", onMove);
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  return (
    <div className="aura" aria-hidden="true">
      <canvas ref={ref} />
      <div className="aura-rays" />
      <div className="aura-vignette" />
    </div>
  );
}
