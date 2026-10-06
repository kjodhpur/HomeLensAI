"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { ASPECT_ORDER, fmtInt, fmtPct } from "@/lib/format";
import { prefersReducedMotion } from "@/lib/hooks";
import type { Aspect } from "@/lib/types";
import { Glass } from "./Glass";

type Metric = "lift" | "signal" | "negative";
const METRICS: { key: Metric; label: string; hint: string }[] = [
  { key: "lift", label: "Lift", hint: "how much more often a review is negative when the aspect is mentioned" },
  { key: "signal", label: "Frequency", hint: "reviews whose text matches the aspect's keyword cluster" },
  { key: "negative", label: "Negative rate", hint: "share of matching reviews that are negative" },
];

const SIZE = 540;
const C = SIZE / 2;
const R0 = 168; // radius of a "full" lobe
const N = ASPECT_ORDER.length;
const SAMPLES = 96;
const SIGMA = 0.4; // angular softness of a lobe (rad)
const ANG = (i: number) => -Math.PI / 2 + (i * 2 * Math.PI) / N;
const angDiff = (a: number, b: number) => {
  let d = a - b;
  while (d > Math.PI) d -= 2 * Math.PI;
  while (d < -Math.PI) d += 2 * Math.PI;
  return d;
};

interface Wave {
  theta: number;
  t0: number;
  amp: number;
}

interface Props {
  aspects: Aspect[];
  active: string | null;
  onSelect: (aspect: string | null) => void;
}

export function AspectBlob({ aspects, active, onSelect }: Props) {
  const uid = useId().replace(/:/g, "");
  const [metric, setMetric] = useState<Metric>("lift");
  const [hover, setHover] = useState<number | null>(null);
  const [bubble, setBubble] = useState<{ x: number; y: number } | null>(null);
  const [rings, setRings] = useState<{ id: number; x: number; y: number }[]>([]);

  const ordered = useMemo(
    () => ASPECT_ORDER.map((o) => aspects.find((a) => a.aspect === o.aspect)).filter((a): a is Aspect => Boolean(a)),
    [aspects],
  );
  const value = useCallback((a: Aspect) => (metric === "lift" ? a.lift : metric === "signal" ? a.reviews_with_signal : a.negative_rate_when_mentioned), [metric]);

  const focusIdx = hover ?? (active ? ordered.findIndex((a) => a.aspect === active) : -1);

  // Target lobe radii: normalised metric, the focused aspect swells and its neighbours yield.
  const targets = useMemo(() => {
    const vals = ordered.map(value);
    const lo = Math.min(...vals);
    const hi = Math.max(...vals);
    return ordered.map((a, i) => {
      const norm = hi === lo ? 0.8 : 0.6 + 0.4 * ((vals[i] - lo) / (hi - lo));
      const f = focusIdx < 0 ? 1 : i === focusIdx ? 1.24 : 0.92;
      return R0 * norm * f;
    });
  }, [ordered, value, focusIdx]);

  // ----- physics (springs + travelling pressure waves), drawn straight into the SVG -----
  const targetsRef = useRef<number[]>(targets);
  targetsRef.current = targets;
  const pos = useRef<number[]>(targets.map((t) => t * 0.6));
  const vel = useRef<number[]>(targets.map(() => 0));
  const waves = useRef<Wave[]>([]);
  const body = useRef<SVGPathElement>(null);
  const glows = useRef<(SVGPathElement | null)[]>([]);
  const clip = useRef<SVGPathElement>(null);
  const fig = useRef<HTMLDivElement>(null);
  const beads = useRef<(SVGGElement | null)[]>([]);
  const labels = useRef<(SVGTextElement | null)[]>([]);
  const beadXY = useRef<{ x: number; y: number }[]>(targets.map(() => ({ x: C, y: C })));

  useEffect(() => {
    const reduce = prefersReducedMotion();
    let raf = 0;
    let last = performance.now();
    const radiusAt = (th: number, t: number) => {
      let num = 0;
      let den = 0;
      for (let i = 0; i < N; i++) {
        const d = angDiff(th, ANG(i));
        const w = Math.exp(-(d * d) / (2 * SIGMA * SIGMA));
        num += pos.current[i] * w;
        den += w;
      }
      let r = num / den;
      if (!reduce) {
        r += R0 * (0.026 * Math.sin(3 * th + t * 0.8) + 0.018 * Math.sin(5 * th - t * 0.6 + 1.3) + 0.01 * Math.sin(2 * th + t * 1.15));
        for (const w of waves.current) {
          const age = t - w.t0;
          const d = Math.abs(angDiff(th, w.theta));
          const front = 2.3 * age;
          r += w.amp * Math.exp(-age * 1.15) * Math.exp(-((d - front) ** 2) / (2 * 0.42 * 0.42)) * Math.cos(7 * (d - front));
        }
      }
      return r;
    };
    let lastDraw = 0;
    const frame = (now: number) => {
      raf = requestAnimationFrame(frame);
      const dt = Math.min(0.033, (now - last) / 1000);
      last = now;
      const t = now / 1000;
      // Idle breathing only needs ~20 fps; full rate while a spring is moving, a wave travels or a bead is focused.
      const moving = waves.current.length > 0 || focusRef.current >= 0 || vel.current.some((v) => Math.abs(v) > 0.4);
      if (!moving && now - lastDraw < 48) return;
      lastDraw = now;
      waves.current = waves.current.filter((w) => t - w.t0 < 2.6);
      const k = reduce ? 400 : 62;
      const c = reduce ? 40 : 8.5;
      for (let s = 0; s < 2; s++) {
        for (let i = 0; i < N; i++) {
          const a = k * (targetsRef.current[i] - pos.current[i]) - c * vel.current[i];
          vel.current[i] += (a * dt) / 2;
          pos.current[i] += (vel.current[i] * dt) / 2;
        }
      }
      let d = "";
      for (let j = 0; j < SAMPLES; j++) {
        const th = (j / SAMPLES) * Math.PI * 2 - Math.PI / 2;
        const r = radiusAt(th, t);
        d += `${j ? "L" : "M"}${(C + r * Math.cos(th)).toFixed(1)},${(C + r * Math.sin(th)).toFixed(1)}`;
      }
      d += "Z";
      body.current?.setAttribute("d", d);
      for (const g of glows.current) g?.setAttribute("d", d);
      clip.current?.setAttribute("d", d);
      for (let i = 0; i < N; i++) {
        const th = ANG(i);
        const r = radiusAt(th, t);
        const x = C + r * Math.cos(th);
        const y = C + r * Math.sin(th);
        beadXY.current[i] = { x, y };
        beads.current[i]?.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
        const lr = R0 * 1.3 + (i === focusRef.current ? 10 : 0);
        const lx = C + lr * Math.cos(th);
        const ly = C + lr * Math.sin(th);
        const el = labels.current[i];
        if (el) {
          el.setAttribute("x", lx.toFixed(1));
          el.setAttribute("y", (ly + 4).toFixed(1));
        }
      }
    };
    // Run only while the figure is on screen and the tab is visible.
    let onScreen = true;
    const start = () => {
      cancelAnimationFrame(raf);
      if (onScreen && !document.hidden) {
        last = performance.now();
        raf = requestAnimationFrame(frame);
      }
    };
    const io = new IntersectionObserver(([e]) => {
      onScreen = e.isIntersecting;
      start();
    });
    if (fig.current) io.observe(fig.current);
    document.addEventListener("visibilitychange", start);
    start();
    return () => {
      cancelAnimationFrame(raf);
      io.disconnect();
      document.removeEventListener("visibilitychange", start);
    };
  }, []);

  const focusRef = useRef(focusIdx);
  focusRef.current = focusIdx;

  const ringId = useRef(0);
  const enter = (i: number) => {
    setHover(i);
    const t = performance.now() / 1000;
    waves.current.push({ theta: ANG(i), t0: t, amp: 15 });
    const { x, y } = beadXY.current[i];
    setBubble({ x, y });
    const id = ++ringId.current;
    setRings((r) => [...r, { id, x, y }]);
    window.setTimeout(() => setRings((r) => r.filter((q) => q.id !== id)), 1500);
  };
  const leave = () => {
    setHover(null);
    setBubble(null);
  };


  const shown = hover != null ? ordered[hover] : null;
  const bubbleStyle = bubble
    ? {
        left: `${Math.min(Math.max(bubble.x / SIZE, 0.3), 0.7) * 100}%`,
        top: bubble.y < C ? `${((bubble.y + 40) / SIZE) * 100}%` : `${((bubble.y - 40) / SIZE) * 100}%`,
        transform: bubble.y < C ? "translate(-50%, 0)" : "translate(-50%, -100%)",
      }
    : undefined;

  return (
    <Glass as="section" id="aspects" className="panel blob-card" aria-label="Complaint aspect radar">
      <header className="card-head">
        <div>
          <div className="kicker">Complaint signals</div>
          <h2>Aspect Radar</h2>
          <p className="sub">8 extracted aspects · size by {METRICS.find((m) => m.key === metric)?.label.toLowerCase()}</p>
        </div>
        <div className="seg" role="group" aria-label="Blob metric">
          {METRICS.map((m) => (
            <button key={m.key} className="pill" aria-pressed={metric === m.key} onClick={() => setMetric(m.key)} title={m.hint}>
              {m.label}
            </button>
          ))}
        </div>
      </header>

      <div className="blob-stage">
        <div className="blob-fig" ref={fig}>
          <svg viewBox={`0 0 ${SIZE} ${SIZE}`} width="100%" role="group" aria-label="Aspect radar blob">
            <defs>
              <radialGradient id={`bg${uid}`} cx="34%" cy="28%" r="85%">
                <stop offset="0" stopColor="#ffffff" stopOpacity="0.85" />
                <stop offset="0.28" stopColor="#ffe08a" stopOpacity="0.62" />
                <stop offset="0.65" stopColor="#ff9a3c" stopOpacity="0.4" />
                <stop offset="1" stopColor="#a8420a" stopOpacity="0.42" />
              </radialGradient>
              <radialGradient id={`in${uid}`} cx="62%" cy="68%" r="70%">
                <stop offset="0" stopColor="#bcd0ff" stopOpacity="0.7" />
                <stop offset="0.6" stopColor="#ffd9b0" stopOpacity="0.25" />
                <stop offset="1" stopColor="#ffc933" stopOpacity="0" />
              </radialGradient>
              <linearGradient id={`ed${uid}`} x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor="#fff" stopOpacity="1" />
                <stop offset="0.35" stopColor="#ffc933" stopOpacity="0.85" />
                <stop offset="0.7" stopColor="#f5780f" stopOpacity="0.9" />
                <stop offset="1" stopColor="#bcd0ff" stopOpacity="0.9" />
              </linearGradient>
              <radialGradient id={`bd${uid}`} cx="35%" cy="30%" r="75%">
                <stop offset="0" stopColor="#fff" />
                <stop offset="0.5" stopColor="#ffd9b0" />
                <stop offset="1" stopColor="#d4600a" />
              </radialGradient>
              <linearGradient id={`sp${uid}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#fff" stopOpacity="0.75" />
                <stop offset="1" stopColor="#fff" stopOpacity="0" />
              </linearGradient>
              <clipPath id={`cp${uid}`}>
                <path ref={clip} d="" />
              </clipPath>
            </defs>

            {/* rings of the radar, barely visible: they only give the blob a scale */}
            {[0.5, 1].map((s) => (
              <circle key={s} cx={C} cy={C} r={R0 * s} fill="none" stroke="rgba(86,52,18,.2)" strokeDasharray="2 6" />
            ))}
            {ordered.map((_, i) => (
              <line key={i} x1={C} y1={C} x2={C + R0 * 1.08 * Math.cos(ANG(i))} y2={C + R0 * 1.08 * Math.sin(ANG(i))} stroke="rgba(86,52,18,.14)" />
            ))}

            {/* the liquid body */}
            {/* soft glow: stacked wide strokes stand in for a blur (SVG blur filters are CPU-bound when animated) */}
            <g transform="translate(0 20)">
              {[34].map((w, i) => (
                <path key={w} d="" ref={(el) => { glows.current[i] = el; }} fill="rgba(245,120,15,.14)" stroke="rgba(255,154,60,.12)" strokeWidth={w} strokeLinejoin="round" />
              ))}
            </g>
            <path d="" ref={body} fill={`url(#bg${uid})`} stroke={`url(#ed${uid})`} strokeWidth={1.8} strokeLinejoin="round" />
            <g clipPath={`url(#cp${uid})`}>
              <rect x={0} y={0} width={SIZE} height={SIZE} fill={`url(#in${uid})`} />
              <g className="blob-spec">
                <ellipse cx={C - 62} cy={C - 78} rx={92} ry={48} fill={`url(#sp${uid})`} opacity={0.5} transform={`rotate(-28 ${C - 62} ${C - 78})`} />
                <ellipse cx={C + 70} cy={C + 96} rx={64} ry={20} fill="#fff" opacity={0.35} transform={`rotate(-24 ${C + 70} ${C + 96})`} />
              </g>
            </g>

            {rings.map((r) => (
              <g key={r.id} transform={`translate(${r.x} ${r.y})`}>
                <circle className="blob-ring" r={10} fill="none" stroke="#f5780f" strokeWidth={1.6} />
                <circle className="blob-ring r2" r={10} fill="none" stroke="var(--accent-2)" strokeWidth={1.2} />
              </g>
            ))}

            {ordered.map((a, i) => {
              const isFocus = focusIdx === i;
              const isActive = active === a.aspect;
              return (
                <g
                  key={a.aspect}
                  ref={(el) => {
                    beads.current[i] = el;
                  }}
                  className={`bead${isFocus ? " focus" : ""}${isActive ? " active" : ""}`}
                  tabIndex={0}
                  role="button"
                  aria-label={`${a.aspect}: ${fmtInt(a.reviews_with_signal)} reviews, ${a.lift.toFixed(1)} times lift. ${isActive ? "Selected" : "Select to filter the leaderboard"}`}
                  aria-pressed={isActive}
                  onPointerEnter={() => enter(i)}
                  onPointerLeave={leave}
                  onFocus={() => enter(i)}
                  onBlur={leave}
                  onClick={() => onSelect(isActive ? null : a.aspect)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onSelect(isActive ? null : a.aspect);
                    }
                  }}
                >
                  <circle r={24} fill="transparent" />
                  <circle className="bead-halo" r={12} fill="none" stroke="#b94d06" strokeOpacity={0.4} />
                  <circle className="bead-core" r={7} fill={`url(#bd${uid})`} stroke="#fff" strokeOpacity={1} strokeWidth={1.2} />
                  {isActive && <circle className="bead-sel" r={21} fill="none" stroke="var(--accent-2)" strokeWidth={1.6} strokeDasharray="3 4" />}
                </g>
              );
            })}

            {ordered.map((a, i) => {
              const th = ANG(i);
              const anchor = Math.cos(th) > 0.3 ? "start" : Math.cos(th) < -0.3 ? "end" : "middle";
              return (
                <text
                  key={a.aspect}
                  ref={(el) => {
                    labels.current[i] = el;
                  }}
                  textAnchor={anchor}
                  className={`blob-label${focusIdx === i ? " on" : ""}`}
                >
                  {ASPECT_ORDER[i].short}
                </text>
              );
            })}
          </svg>

          {shown && bubble && (
            <div className="bubble glass-sm" style={bubbleStyle} role="status">
              <div className="bubble-head">
                <b>{shown.aspect}</b>
                {shown.high_severity && <span className="sev">high severity</span>}
              </div>
              <div className="bubble-stats">
                <div>
                  <em>{fmtInt(shown.reviews_with_signal)}</em>
                  <span>reviews matched ({fmtPct(shown.share_of_corpus, 1)} of corpus)</span>
                </div>
                <div>
                  <em>{fmtPct(shown.negative_rate_when_mentioned)}</em>
                  <span>negative when mentioned</span>
                </div>
                <div>
                  <em>{shown.lift.toFixed(2)}×</em>
                  <span>lift vs baseline</span>
                </div>
                <div>
                  <em>{shown.providers_led}</em>
                  <span>providers led</span>
                </div>
              </div>
              <div className="kicker">Keyword cluster · {shown.keywords.length} phrases</div>
              <div className="bubble-kw">
                {shown.keywords.slice(0, 10).map((k) => (
                  <span key={k}>{k}</span>
                ))}
                {shown.keywords.length > 10 && <span className="more">+{shown.keywords.length - 10}</span>}
              </div>
              <div className="tiny">{active === shown.aspect ? "Click to clear the leaderboard filter" : "Click to filter the leaderboard and open its playbook"}</div>
            </div>
          )}
        </div>
      </div>
      <p className="tiny blob-foot">Shape is driven by corpus statistics from the phrase dictionary; hover or focus a bead to see its keyword cluster.</p>
    </Glass>
  );
}
