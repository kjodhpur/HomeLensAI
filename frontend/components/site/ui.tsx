import Link from "next/link";
import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";

export function PageHero({ eyebrow, title, lead, children }: { eyebrow?: string; title: ReactNode; lead?: ReactNode; children?: ReactNode }) {
  return (
    <section className="page-hero">
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

export function CtaBand({ title, lead, primary = { href: "/demo", label: "Open the live demo" }, secondary }: { title: ReactNode; lead?: ReactNode; primary?: { href: string; label: string }; secondary?: { href: string; label: string } }) {
  return (
    <section className="section tight">
      <div className="container">
        <div className="cta-band glass">
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
