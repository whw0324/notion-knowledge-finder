import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function DocumentsPage() {
  const documents = useQuery({ queryKey: ["documents"], queryFn: api.documents });
  const active = documents.data?.filter((document) => document.sync_status === "indexed") ?? [];
  const chunks = active.reduce((total, document) => total + document.chunk_count, 0);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">KNOWLEDGE BASE</p>
          <h1>Knowledge Documents</h1>
          <p>Notion pages that have been processed and added to the Chroma vector index.</p>
        </div>
        <div className="header-metrics"><strong>{active.length}</strong> pages · <strong>{chunks}</strong> chunks</div>
      </header>

      {documents.error && <div className="error-banner">{documents.error.message}</div>}
      <div className="document-grid">
        {active.map((document) => (
          <a className="document-card" href={document.url} target="_blank" rel="noreferrer" key={document.id}>
            <div className="document-icon">N</div>
            <div>
              <h2>{document.title}</h2>
              <p>{document.chunk_count} vector chunks</p>
              <span>Notion updated: {document.last_edited_time ? new Date(document.last_edited_time).toLocaleString("en-US") : "Unknown"}</span>
            </div>
            <span className="status-pill">Indexed</span>
          </a>
        ))}
      </div>
      {!documents.isLoading && active.length === 0 && (
        <div className="empty-state"><h2>No synced documents yet</h2><p>Open Notion Sync to create your first indexing job.</p></div>
      )}
    </div>
  );
}
