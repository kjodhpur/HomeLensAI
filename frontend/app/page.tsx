import { Dashboard } from "@/components/Dashboard";
import { aspects, examples, overview, providers } from "@/lib/data";
import { analyzeReview } from "@/lib/engine/analyze";

export default function Page() {
  const first = examples[0];
  return <Dashboard overview={overview} providers={providers} aspects={aspects} examples={examples} initialText={first.text} initialResult={analyzeReview(first.text)} />;
}
