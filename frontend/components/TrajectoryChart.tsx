"use client";

import { useId, useMemo, useState } from "react";
import { smoothPath } from "@/lib/curves";
import type { HistoryPoint } from "@/lib/types";

interface Props {
  history: HistoryPoint[];
  color: string;
  groupMedian?: number | null;
  groupLabel?: string;
}

const W = 400;
const H = 190;
const M = { l: 34, r: 14, t: 14, b: 26 };

/** Yearly mean model risk for one provider, drawn as a liquid area with review-volume beads. */
export function TrajectoryChart({ history, color, groupMedian, groupLabel }: Props) {
  const uid = useId().replace(/:/g, "");
  const [hover, setHover] = useState<number | null>(null);

  const g = useMemo(() => {
    if (!history.length) return null;
    const years = history.map((h) => h.year);
    const y0 = Math.min(...years);
    const y1 = Math.max(...years, y0 + 1);
    const px = (y: number) => M.l + ((y - y0) / (y1 - y0)) * (W - M.l - M.r);
    const py = (v: number) => M.t + (1 - v) * (H - M.t - M.b);
    const pts = history.map((h) => ({ x: px(h.year), y: py(h.risk) }));
    const maxN = Math.max(...history.map((h) => h.reviews));
    return { pts, px, py, y0, y1, maxN, line: smoothPath(pts), ticks: [y0, ...(y1 - y0 > 3 ? [Math.round((y0 + y1) / 2)] : []), y1] };
  }, [history]);

  if (!g) return <div className="traj-empty">No yearly history for this provider.</div>;
  const base = H - M.b;
  const area = history.length > 1 ? `${g.line} L${g.pts[g.pts.length - 1].x},${base} L${g.pts[0].x},${base} Z` : "";

  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * W;
    let best = 0;
    g.pts.forEach((p, i) => {
      if (Math.abs(p.x - x) < Math.abs(g.pts[best].x - x)) best = i;
    });
    setHover(best);
  };

  const hp = hover != null ? history[hover] : null;
  return (
    <div className="traj">
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" onPointerMove={onMove} onPointerLeave={() => setHover(null)} role="img" aria-label="Yearly mean model risk">
        <defs>
          <linearGradient id={`ta${uid}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor={color} stopOpacity="0.5" />
            <stop offset="1" stopColor={color} stopOpacity="0" />
          </linearGradient>
          <radialGradient id={`tb${uid}`} cx="35%" cy="30%" r="75%">
            <stop offset="0" stopColor="#fff" />
            <stop offset="0.55" stopColor={color} />
            <stop offset="1" stopColor={color} stopOpacity="0.55" />
          </radialGradient>
        </defs>
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1={M.l} x2={W - M.r} y1={g.py(v)} y2={g.py(v)} stroke="rgba(255,255,255,.1)" strokeDasharray={v === 0 ? "" : "2 5"} />
            <text x={M.l - 8} y={g.py(v) + 4} textAnchor="end" className="axis">
              {v.toFixed(1)}
            </text>
          </g>
        ))}
        {g.ticks.map((t) => (
          <text key={t} x={g.px(t)} y={H - 6} textAnchor="middle" className="axis">
            {t}
          </text>
        ))}
        {groupMedian != null && (
          <g>
            <line x1={M.l} x2={W - M.r} y1={g.py(groupMedian)} y2={g.py(groupMedian)} stroke="var(--accent-2)" strokeWidth={1.2} strokeDasharray="6 5" opacity={0.85} />
            <text x={W - M.r} y={g.py(groupMedian) - 6} textAnchor="end" className="axis accent">
              {groupLabel ?? "group median (recent)"} {groupMedian.toFixed(2)}
            </text>
          </g>
        )}
        {area && <path d={area} fill={`url(#ta${uid})`} className="traj-area" />}
        {history.length > 1 && <path d={g.line} fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" className="traj-line" pathLength={1} style={{ filter: `drop-shadow(0 0 8px ${color})` }} />}
        {g.pts.map((p, i) => (
          <circle key={history[i].year} cx={p.x} cy={p.y} r={4 + 6 * Math.sqrt(history[i].reviews / g.maxN)} fill={`url(#tb${uid})`} stroke="rgba(255,255,255,.7)" strokeWidth={0.8} className="traj-bead" style={{ animationDelay: `${i * 70}ms`, transformOrigin: `${p.x}px ${p.y}px` }} opacity={hover == null || hover === i ? 1 : 0.5} />
        ))}
      </svg>
      {hp && hover != null && (
        <div className="traj-tip glass-sm" style={{ left: `${(g.pts[hover].x / W) * 100}%`, top: `${(g.pts[hover].y / H) * 100}%` }}>
          <b>{hp.year}</b> · {hp.reviews} review{hp.reviews === 1 ? "" : "s"} · risk {hp.risk.toFixed(2)}
        </div>
      )}
      <p className="tiny">Bead size = reviews that year. Dashed line = median recent risk of the service group.</p>
    </div>
  );
}
