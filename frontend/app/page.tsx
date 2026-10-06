import { Dashboard } from "@/components/Dashboard";
import { Glass } from "@/components/Glass";
import { LiquidBackground } from "@/components/LiquidBackground";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic"; // always read live data; nothing is prerendered at build time

export default async function Page() {
  try {
    const [overview, providers, aspects, examples] = await Promise.all([api.overview(), api.providers(), api.aspects(), api.examples()]);
    const first = examples[0];
    const initialResult = first ? await api.analyze(first.text).catch(() => null) : null;
    return <Dashboard overview={overview} providers={providers} aspects={aspects} examples={examples} initialText={first?.text ?? ""} initialResult={initialResult} />;
  } catch (e) {
    return (
      <>
        <LiquidBackground />
        <main className="shell center">
          <Glass className="card error-card" hoverable={false}>
            <div className="kicker">HomeLens AI</div>
            <h2>Could not load data</h2>
            <p>{(e as Error).message}</p>
            <p className="tiny">
              Start the backend (<code>cd backend &amp;&amp; uvicorn app.main:app --reload</code>) or set <code>API_BASE_URL</code>. See <code>docs/TEAM_GUIDE.md</code>.
            </p>
          </Glass>
        </main>
      </>
    );
  }
}
