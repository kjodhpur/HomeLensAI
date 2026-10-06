import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";

/** Concentric sun rays (the site's brand motif), drawn as a light SVG. */
export function SunMark({ className = "sun-mark" }: { className?: string }) {
  const rays = Array.from({ length: 36 }, (_, i) => {
    const a = (i / 36) * Math.PI * 2;
    const r0 = 92 + (i % 2) * 8;
    const r1 = 150 + (i % 3) * 14;
    return <line key={i} x1={200 + Math.cos(a) * r0} y1={200 + Math.sin(a) * r0} x2={200 + Math.cos(a) * r1} y2={200 + Math.sin(a) * r1} />;
  });
  return (
    <svg className={className} viewBox="0 0 400 400" fill="none" stroke="#f5780f" strokeWidth="5" strokeLinecap="round" aria-hidden="true">
      <circle cx="200" cy="200" r="52" fill="#ffc933" stroke="none" />
      {rays}
    </svg>
  );
}

export function PageHero({ eyebrow, title, lead, children }: { eyebrow?: string; title: ReactNode; lead?: ReactNode; children?: ReactNode }) {
  return (
    <section className="page-hero">
      <SunMark />
      <div className="container">
        {eyebrow && <span className="eyebrow glass-sm">{eyebrow}</span>}
        <h1 className="h1">{title}</h1>
        {lead && <p className="lead">{lead}</p>}
        {children && <div className="hero-actions">{children}</div>}
      </div>
    </section>
  );
}

export function Section({ id, title, lead, eyebrow, center, tight, children }: { id?: string; title?: ReactNode; lead?: ReactNode; eyebrow?: string; center?: boolean; tight?: boolean; children: ReactNode }) {
  return (
    <section id={id} className={`section${tight ? " tight" : ""}`}>
      <div className="container">
        {(title || lead) && (
          <div className={`section-head${center ? " center" : ""}`}>
            {eyebrow && <span className="kicker">{eyebrow}</span>}
            {title && <h2 className="h2">{title}</h2>}
            {lead && <p className="lead">{lead}</p>}
          </div>
        )}
        {children}
      </div>
    </section>
  );
}

export function Card({ icon, title, children, tag }: { icon?: IconName; title: ReactNode; children: ReactNode; tag?: string }) {
  return (
    <article className="card glass lift">
      {icon && (
        <span className="icon-chip" aria-hidden="true">
          <Icon name={icon} size={22} />
        </span>
      )}
      {tag && <span className="card-tag">{tag}</span>}
      <h3>{title}</h3>
      <div className="card-body">{children}</div>
    </article>
  );
}

export function Stat({ value, label, note }: { value: ReactNode; label: string; note?: string }) {
  return (
    <div className="stat">
      <b>{value}</b>
      <span>{label}</span>
      {note && <small>{note}</small>}
    </div>
  );
}

/** Dark photographic call to action. */
export function CtaBand({ title, lead, primary = { href: "/demo", label: "Open the live demo" }, secondary }: { title: ReactNode; lead?: ReactNode; primary?: { href: string; label: string }; secondary?: { href: string; label: string } }) {
  return (
    <section className="section tight">
      <div className="container">
        <div className="cta-photo on-dark">
          <Image className="band-bg" src="/img/dusk.webp" alt="" fill sizes="(max-width: 1180px) 100vw, 1180px" quality={65} />
          <h2 className="h2">{title}</h2>
          {lead && <p className="lead">{lead}</p>}
          <div className="hero-actions">
            <Link href={primary.href} className="btn lg">
              {primary.label} <Icon name="arrow" size={18} />
            </Link>
            {secondary && (
              <Link href={secondary.href} className="btn ghost lg">
                {secondary.label}
              </Link>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

/** Full-bleed sunset with numbered yellow cards (mono labels), like a step-by-step path. */
export function SunsetCards({ label, title, lead, cards }: { label: string; title: ReactNode; lead?: ReactNode; cards: { label: string; title: string; body: ReactNode[] }[] }) {
  return (
    <section className="band-sunset on-dark">
      <Image className="band-bg" src="/img/sunset.webp" alt="" fill sizes="100vw" quality={65} />
      <div className="container">
        <div className="section-head" style={{ marginBottom: 0 }}>
          <span className="kicker" style={{ color: "rgba(255,244,224,.75)" }}>
            {label}
          </span>
          <h2 className="h2">{title}</h2>
          {lead && <p className="lead">{lead}</p>}
        </div>
        <div className="ycards">
          {cards.map((c) => (
            <article key={c.title} className="ycard">
              <span className="mono-label">{c.label}</span>
              <h3>{c.title}</h3>
              {c.body.map((b, i) => (
                <p key={i}>{b}</p>
              ))}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/** Periwinkle band with a navy serif headline and a photo carrying a blue plan-view rectangle. */
export function SkyBand({ label, title, left, right }: { label: string; title: ReactNode; left: { title: string; items: string[] }; right: { title: string; items: string[] } }) {
  return (
    <section className="band-sky">
      <div className="sky-grid">
        <div className="sky-photo" aria-hidden="true">
          <Image src="/img/sunset.webp" alt="" fill sizes="(max-width: 960px) 100vw, 45vw" quality={60} style={{ objectPosition: "60% 50%" }} />
          <div className="plan-grid" />
          <div className="plan-rect" />
        </div>
        <div className="sky-copy">
          <div>
            <span className="mono-label">{label}</span>
            <h2 className="h2">{title}</h2>
          </div>
          <div className="sky-cols">
            <div>
              <h3>{left.title}</h3>
              <Checklist items={left.items} />
            </div>
            <div>
              <h3>{right.title}</h3>
              <Checklist items={right.items} positive={false} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Checklist({ items, positive = true }: { items: string[]; positive?: boolean }) {
  return (
    <ul className={`checklist ${positive ? "yes" : "no"}`}>
      {items.map((t) => (
        <li key={t}>
          <span aria-hidden="true">
            <Icon name={positive ? "check" : "minus"} size={14} stroke={2.4} />
          </span>
          {t}
        </li>
      ))}
    </ul>
  );
}

export function Faq({ items }: { items: { q: string; a: ReactNode }[] }) {
  return (
    <div className="faq">
      {items.map((f) => (
        <details key={f.q} className="glass">
          <summary>
            <span>{f.q}</span>
            <Icon name="arrow" size={16} />
          </summary>
          <div className="faq-a">{f.a}</div>
        </details>
      ))}
    </div>
  );
}

/** Prose wrapper for legal/long-form pages. */
export function Prose({ children }: { children: ReactNode }) {
  return <div className="prose">{children}</div>;
}
