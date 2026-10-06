import type { Tier } from "@/lib/types";

export function TierBadge({ tier }: { tier: Tier }) {
  return <span className={`badge badge-${tier.split(" ")[0].toLowerCase()}`}>{tier}</span>;
}
