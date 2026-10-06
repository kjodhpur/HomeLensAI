"use client";

import { useEffect, useState } from "react";
import { qualityAudit, triageEmail, triageMeta } from "@/lib/playbooks";
import type { TriageContext } from "@/lib/types";
import { Glass } from "./Glass";

type View = "menu" | "email" | "audit";

/**
 * Persistent action drawer. It stays a tiny bubble under the surface until a risk flag is selected, then breaks the
 * surface and swells into a panel whose playbook buttons bubble up one after another. Drafts only — nothing is sent.
 */
export function TriageDock({ context, onClose }: { context: TriageContext | null; onClose: () => void }) {
  const [view, setView] = useState<View>("menu");
  const [done, setDone] = useState<Record<number, boolean>>({});
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    setView("menu");
    setDone({});
    setCopied(null);
  }, [context]);

  useEffect(() => {
    if (!context) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [context, onClose]);

  const open = context != null;
  const meta = context ? triageMeta(context) : null;
  const email = context ? triageEmail(context) : null;
  const audit = context ? qualityAudit(context) : null;

  const copy = async (label: string, value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(label);
      window.setTimeout(() => setCopied(null), 1600);
    } catch {
      setCopied("Copy not available in this browser");
    }
  };

  return (
    <Glass as="aside" className="dock" data-open={open} aria-hidden={!open} aria-label="Action triage dock" ripple>
      {meta && email && audit && (
        <div className="dock-in" key={meta.subject}>
          <header className="dock-head">
            <div>
              <div className="kicker">Action triage</div>
              <h3>{meta.subject}</h3>
              <span className="dock-tag">{meta.tag}</span>
            </div>
            <button className="dock-x" onClick={onClose} aria-label="Close triage dock">
              ✕
            </button>
          </header>

          {view === "menu" && (
            <>
              <p className="dock-rec">
                <b>Recommended action.</b> {meta.action}
              </p>
              <div className="dock-actions">
                <button className="btn dock-btn" style={{ ["--i" as string]: 0 }} onClick={() => setView("email")}>
                  ✉ Triage Response Email
                </button>
                <button className="btn dock-btn" style={{ ["--i" as string]: 1 }} onClick={() => setView("audit")}>
                  ✓ Initiate Quality Audit
                </button>
                <button className="btn ghost dock-btn" style={{ ["--i" as string]: 2 }} onClick={onClose}>
                  Dismiss
                </button>
              </div>
            </>
          )}

          {view === "email" && (
            <div className="dock-view">
              <div className="kicker">Draft · internal email</div>
              <p className="dock-subject">{email.subject}</p>
              <pre className="dock-pre">{email.body}</pre>
              <div className="dock-row">
                <button className="btn" onClick={() => copy("email", `Subject: ${email.subject}\n\n${email.body}`)}>
                  {copied === "email" ? "Copied ✓" : "Copy draft"}
                </button>
                <button className="btn ghost" onClick={() => setView("menu")}>
                  Back
                </button>
              </div>
            </div>
          )}

          {view === "audit" && (
            <div className="dock-view">
              <div className="kicker">Checklist · quality audit</div>
              <p className="dock-subject">{audit.title}</p>
              <ol className="dock-steps">
                {audit.steps.map((s, i) => (
                  <li key={s} style={{ ["--i" as string]: i }}>
                    <label>
                      <input type="checkbox" checked={!!done[i]} onChange={() => setDone((d) => ({ ...d, [i]: !d[i] }))} />
                      <span>{s}</span>
                    </label>
                  </li>
                ))}
              </ol>
              <div className="dock-row">
                <button className="btn" onClick={() => copy("audit", `${audit.title}\n\n${audit.steps.map((s, i) => `${done[i] ? "[x]" : "[ ]"} ${s}`).join("\n")}`)}>
                  {copied === "audit" ? "Copied ✓" : "Copy checklist"}
                </button>
                <button className="btn ghost" onClick={() => setView("menu")}>
                  Back
                </button>
              </div>
            </div>
          )}
          <p className="tiny dock-foot">Drafts for human review — nothing is sent. Signals come from customer reviews and are not verified findings.</p>
        </div>
      )}
    </Glass>
  );
}
