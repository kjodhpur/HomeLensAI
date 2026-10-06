"use client";

import { useId, useMemo, useState } from "react";
import { smoothPath } from "@/lib/curves";
import type { SeriesPoint } from "@/lib/types";

interface Props {
  points: SeriesPoint[];
  format: (y: number) => string;
  /** accent for the end droplet and glow */
  tone?: string;
  height?: number;
}

const W = 240;
const PAD = 10;

/**
 * A sparkline drawn as flowing liquid metal: a chrome-gradient stroke with a bright sheen travelling along it,
 * a drop of mercury at the latest value, and a tooltip drop that follows the pointer.
 */
export function MercurySparkline({ points, format, tone = "var(--accent-2)", height = 46 }: Props) {
  const uid = useId().replace(/:/g, "");
  const [hover, setHover] = useState<number | null>(null);

  const geo = useMemo(() => {
    if (points.length < 2) return null;
    const xs = points.map((p) => p.x);
    const ys = points.map((p) => p.y);
    const [x0, x1] = [Math.min(...xs), Math.max(...xs)];
    const [y0, y1] = [Math.min(...ys), Math.max(...ys)];
    const span = y1 - y0 || 1;
    const px = (x: number) => PAD + ((x - x0) / (x1 - x0 || 1)) * (W - PAD * 2);
    const py = (y: number) => height - PAD - ((y - y0) / span) * (height - PAD * 2.4);
    const pts = points.map((p) => ({ x: px(p.x), y: py(p.y) }));
    const line = smoothPath(pts);
    const area = `${line} L${pts[pts.length - 1].x},${height} L${pts[0].x},${height} Z`;
    return { pts, line, area };
  }, [points, height]);

  if (!geo) return <div className="spark-empty">not enough history</div>;
  const last = geo.pts[geo.pts.length - 1];
  const hi = hover != null ? geo.pts[hover] : null;

  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * W;
    let best = 0;
    geo.pts.forEach((p, i) => {
      if (Math.abs(p.x - x) < Math.abs(geo.pts[best].x - x)) best = i;
    });
    setHover(best);
  };

  return (
    <div className="spark" style={{ ["--tone" as string]: tone }}>
      <svg viewBox={`0 0 ${W} ${height}`} width="100%" onPointerMove={onMove} onPointerLeave={() => setHover(null)} role="img" aria-label={`Trend: ${points.map((p) => `${p.x} ${format(p.y)}`).join(", ")}`}>
        <defs>
          <linearGradient id={`m${uid}`} x1="0" x2="1">
            <stop offset="0" stopColor="#8f9bd6" />
            <stop offset="0.35" stopColor="#ffffff" />
            <stop offset="0.7" stopColor="#b9c4ff" />
            <stop offset="1" stopColor="#ffffff" />
          </linearGradient>
          <linearGradient id={`a${uid}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor="#b7a6ff" stopOpacity="0.38" />
            <stop offset="1" stopColor="#b7a6ff" stopOpacity="0" />
          </linearGradient>
          <radialGradient id={`d${uid}`} cx="35%" cy="30%" r="75%">
            <stop offset="0" stopColor="#fff" />
            <stop offset="0.5" stopColor="#cfd6ff" />
            <stop offset="1" stopColor="#7d87d6" />
          </radialGradient>
        </defs>
        <path d={geo.area} fill={`url(#a${uid})`} className="spark-area" />
        <path d={geo.line} className="spark-line" pathLength={1} fill="none" stroke={`url(#m${uid})`} strokeWidth={2.6} strokeLinecap="round" />
        <path d={geo.line} className="spark-sheen" pathLength={1} fill="none" stroke="#fff" strokeWidth={3.4} strokeLinecap="round" />
        <g className="spark-drop" transform={`translate(${last.x} ${last.y})`}>
          <circle className="spark-halo" r={5} fill="none" stroke="var(--tone)" strokeWidth={1.2} />
          <circle r={4.6} fill={`url(#d${uid})`} stroke="rgba(255,255,255,.8)" strokeWidth={0.8} />
        </g>
        {hi && (
          <g className="spark-hover" transform={`translate(${hi.x} ${hi.y})`}>
            <line y1={-hi.y} y2={height - hi.y} stroke="rgba(255,255,255,.25)" strokeDasharray="2 3" />
            <circle r={6.5} fill={`url(#d${uid})`} stroke="#fff" strokeWidth={1} />
          </g>
        )}
      </svg>
      {hover != null && hi && (
        <div className="spark-tip glass-sm" style={{ left: `${(hi.x / W) * 100}%` }}>
          <b>{format(points[hover].y)}</b>
          <span>{points[hover].x}</span>
        </div>
      )}
    </div>
  );
}
