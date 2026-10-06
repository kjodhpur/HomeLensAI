"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { NAV } from "@/lib/site";
import { Icon } from "./Icon";

/** Sticky glass navigation. One backdrop-filter surface; the mobile menu is a plain disclosure (no animation library). */
export function SiteHeader() {
  const path = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [path]);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <header className="site-header">
      <div className="site-bar glass">
        <Link href="/" className="logo" aria-label="HomeLens AI home">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo-mark.svg" alt="" width={28} height={28} />
          <span>HomeLens AI</span>
        </Link>
        <nav className="site-nav" aria-label="Primary">
          {NAV.map((l) => (
            <Link key={l.href} href={l.href} aria-current={path === l.href ? "page" : undefined}>
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="site-actions">
          <Link href="/demo" className="btn sm">
            Open demo
          </Link>
          <button className="menu-btn" aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} aria-controls="mobile-menu" onClick={() => setOpen((v) => !v)}>
            <Icon name={open ? "x" : "menu"} size={20} />
          </button>
        </div>
      </div>
      {open && (
        <nav id="mobile-menu" className="mobile-menu glass" aria-label="Mobile">
          {[...NAV, { href: "/about", label: "About" }, { href: "/faq", label: "FAQ" }, { href: "/contact", label: "Contact" }].map((l) => (
            <Link key={l.href} href={l.href} aria-current={path === l.href ? "page" : undefined}>
              {l.label}
            </Link>
          ))}
          <Link href="/demo" className="btn">
            Open the live demo
          </Link>
        </nav>
      )}
    </header>
  );
}
