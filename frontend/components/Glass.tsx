"use client";

import type { ComponentPropsWithoutRef, ElementType, ReactNode, Ref } from "react";
import { useCallback, useRef } from "react";

type GlassProps = {
  as?: ElementType;
  className?: string;
  children?: ReactNode;
  /** emit an outward ripple from the pointer on press */
  ripple?: boolean;
  /** morph the membrane on hover (default true) */
  hoverable?: boolean;
  ref?: Ref<HTMLElement>;
} & Omit<ComponentPropsWithoutRef<"div">, "className" | "children">;

/**
 * A liquid-glass surface. The pointer position drives the specular highlight (--px/--py); presses emit a ripple.
 * All effects are CSS variables / DOM nodes — React does not re-render while the pointer moves.
 */
export function Glass({ as, className = "", children, ripple = false, hoverable = true, onPointerMove, onPointerDown, ref, ...rest }: GlassProps) {
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
    if (!node || raf.current) return;
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
    span.style.setProperty("--rs", String(Math.max(14, Math.hypot(r.width, r.height) / 14)));
    span.addEventListener("animationend", () => span.remove());
    layer.appendChild(span);
  };

  return (
    <Tag ref={setRef} className={`glass${hoverable ? " hoverable" : ""} ${className}`} onPointerMove={move} onPointerDown={down} {...rest}>
      {children}
      <div ref={fx} className="glass-fx" aria-hidden="true" />
    </Tag>
  );
}
