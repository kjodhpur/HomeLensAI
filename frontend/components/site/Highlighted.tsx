import { Fragment } from "react";

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Underline the dictionary phrases that matched inside a sentence, so the reader sees exactly what triggered a signal. */
export function Highlighted({ text, phrases }: { text: string; phrases: Record<string, string[]> }) {
  const list = [...new Set(Object.values(phrases).flat())].sort((a, b) => b.length - a.length);
  if (!list.length) return <>{text}</>;
  const re = new RegExp(`(${list.map(esc).join("|")})`, "gi");
  return (
    <>
      {text.split(re).map((part, i) => (i % 2 ? <mark key={i} className="hit">{part}</mark> : <Fragment key={i}>{part}</Fragment>))}
    </>
  );
}
