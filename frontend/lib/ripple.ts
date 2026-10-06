/** Spawn an outward ripple inside `layer` at the pointer position. Pure DOM — no React re-render. */
export function spawnRipple(layer: HTMLElement | null, host: HTMLElement | null, e: { clientX: number; clientY: number }, className = "glass-ripple") {
  if (!layer || !host) return;
  const r = host.getBoundingClientRect();
  const span = document.createElement("span");
  span.className = className;
  span.style.setProperty("--rx", `${e.clientX - r.left}px`);
  span.style.setProperty("--ry", `${e.clientY - r.top}px`);
  span.style.setProperty("--rs", String(Math.max(14, Math.hypot(r.width, r.height) / 14)));
  span.addEventListener("animationend", () => span.remove());
  layer.appendChild(span);
}
