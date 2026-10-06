export function ApiErrorPanel({ message }: { message: string }) {
  return (
    <div className="card error">
      <strong>Could not load data.</strong>
      <p>{message}</p>
      <p className="muted">
        Start the backend (<code>cd backend &amp;&amp; uvicorn app.main:app --reload</code>) or set <code>API_BASE_URL</code>. See{" "}
        <code>docs/TEAM_GUIDE.md</code>.
      </p>
    </div>
  );
}
