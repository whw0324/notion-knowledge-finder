import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function SettingsPage() {
  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const value = health.data;

  return (
    <div className="page narrow">
      <header className="page-header">
        <div><p className="eyebrow">RUNTIME</p><h1>System Settings</h1><p>Model credentials remain in the backend .env file and are never exposed to the frontend.</p></div>
      </header>
      <div className="settings-list">
        <div><span>Backend status</span><strong className="online">{value?.status ?? "checking"}</strong></div>
        <div><span>Chat provider</span><strong>{value?.chat_provider ?? "—"}</strong></div>
        <div><span>Chat model</span><strong>{value?.chat_model ?? "—"}</strong></div>
        <div><span>Embedding provider</span><strong>{value?.embedding_provider ?? "—"}</strong></div>
        <div><span>Embedding model</span><strong>{value?.embedding_model ?? "—"}</strong></div>
        <div><span>Vector database</span><strong>Chroma · local persistent</strong></div>
      </div>
      {health.error && <div className="error-banner">{health.error.message}</div>}
    </div>
  );
}
