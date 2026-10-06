"use client";

import { useCallback, useState } from "react";
import { usePointerVars } from "@/lib/hooks";
import type { AnalyzeResult, Aspect, Example, Overview, Provider, TriageContext } from "@/lib/types";
import { AspectBlob } from "./AspectBlob";
import { DisclaimerEtch } from "./DisclaimerEtch";
import { EvidenceFeed } from "./EvidenceFeed";
import { Header } from "./Header";
import { KpiPods } from "./KpiPods";
import { Leaderboard } from "./Leaderboard";
import { LiquidBackground } from "./LiquidBackground";
import { TriageDock } from "./TriageDock";

interface Props {
  overview: Overview;
  providers: Provider[];
  aspects: Aspect[];
  examples: Example[];
  initialText: string;
  initialResult: AnalyzeResult | null;
}

export function Dashboard({ overview, providers, aspects, examples, initialText, initialResult }: Props) {
  usePointerVars();
  const [selected, setSelected] = useState<string | null>(null);
  const [aspectFilter, setAspectFilter] = useState<string | null>(null);
  const [triage, setTriage] = useState<TriageContext | null>(null);

  const selectProvider = useCallback(
    (code: string | null) => {
      setSelected(code);
      const provider = code ? providers.find((p) => p.code === code) : null;
      setTriage((t) => (provider ? { kind: "provider", provider } : t?.kind === "provider" ? null : t));
    },
    [providers],
  );

  const selectAspect = useCallback(
    (name: string | null) => {
      setAspectFilter(name);
      const aspect = name ? aspects.find((a) => a.aspect === name) : null;
      setTriage((t) => (aspect ? { kind: "aspect", aspect } : t?.kind === "aspect" ? null : t));
    },
    [aspects],
  );

  const clearAspect = useCallback(() => selectAspect(null), [selectAspect]);

  return (
    <>
      <LiquidBackground />
      <main className="shell">
        <Header overview={overview} modelLabel={initialResult?.model.available ? `${initialResult.model.name} · ${initialResult.model.threshold?.toFixed(3)}` : null} />
        <KpiPods overview={overview} onSelectProvider={selectProvider} />
        <div className="mid">
          <Leaderboard providers={providers} overview={overview} selected={selected} onSelect={selectProvider} aspectFilter={aspectFilter} onClearAspect={clearAspect} />
          <AspectBlob aspects={aspects} active={aspectFilter} onSelect={selectAspect} />
        </div>
        <EvidenceFeed examples={examples} initialText={initialText} initialResult={initialResult} flagged={triage?.kind === "review"} onFlag={(result) => setTriage({ kind: "review", result })} />
      </main>
      <TriageDock context={triage} onClose={() => setTriage(null)} />
      <DisclaimerEtch />
    </>
  );
}
