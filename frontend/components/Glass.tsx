"use client";

import type { ComponentPropsWithoutRef, ElementType, ReactNode, Ref } from "react";
import { useCallback, useRef } from "react";

type GlassProps = {
  as?: ElementType;
  className?: string;
  children?: ReactNode;
  /** emit a soft ripple from the pointer on press */
  ripple?: boolean;
  /** pointer-tracked specular sheen (use on a few hero surfaces only) */
  lit?: boolean;
  /** lift slightly on hover */
  lift?: boolean;
  ref?: Ref<HTMLElement>;
} & Omit<ComponentPropsWithoutRef<"div">, "className" | "children">;

/**
 * A liquid-glass surface. Cheap by default (static CSS). `lit` adds a pointer-tracked highlight written as CSS variables,
 * so React never re-renders while the pointer moves; `ripple` emits a one-shot ripple on press.
 */
export function Glass({ as, className = "", children, ripple = false, lit = false, lift = false, onPointerMove, onPointerDown, ref, ...rest }: GlassProps) {
  const Tag = (as ?? "div") as ElementType;
  const el = useRef<HTMLElement | null>(null);
  const fx = useRef<HTMLDivElement | null>(null);
  const raf = useRef(0);

  const setRef = useCallback(
    (node: HTMLElement | null) => {
      el.current = node;
      if (typeof ref === "function") ref(node);
      else if (ref) (ref as { current: HTMLElement | null }).current = node;
    },
    [ref],
  );

  const move = (e: React.PointerEvent<HTMLDivElement>) => {
    onPointerMove?.(e);
    const node = el.current;
    if (!lit || !node || raf.current) return;
    const { clientX, clientY } = e;
    raf.current = requestAnimationFrame(() => {
      raf.current = 0;
      const r = node.getBoundingClientRect();
      node.style.setProperty("--px", `${clientX - r.left}px`);
      node.style.setProperty("--py", `${clientY - r.top}px`);
    });
  };

  const down = (e: React.PointerEvent<HTMLDivElement>) => {
    onPointerDown?.(e);
    const layer = fx.current;
    const node = el.current;
    if (!ripple || !layer || !node) return;
    const r = node.getBoundingClientRect();
    const span = document.createElement("span");
    span.className = "glass-ripple";
    span.style.setProperty("--rx", `${e.clientX - r.left}px`);
    span.style.setProperty("--ry", `${e.clientY - r.top}px`);
    span.style.setProperty("--rs", String(Math.max(14, Math.hypot(r.width, r.height) / 10)));
    span.addEventListener("animationend", () => span.remove());
    layer.appendChild(span);
  };

  return (
    <Tag ref={setRef} className={`glass${lit ? " lit" : ""}${lift ? " lift" : ""} ${className}`} onPointerMove={move} onPointerDown={down} {...rest}>
      {children}
      {ripple && <div ref={fx} className="glass-fx" aria-hidden="true" />}
    </Tag>
  );
}
