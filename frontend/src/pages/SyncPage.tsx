import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

export function SyncPage() {
  const queryClient = useQueryClient();
  const jobs = useQuery({
    queryKey: ["sync-jobs"],
    queryFn: api.syncJobs,
    refetchInterval: (query) =>
      query.state.data?.some((job) => job.status === "pending" || job.status === "running") ? 1500 : false,
  });
  const start = useMutation({
    mutationFn: api.startSync,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sync-jobs"] }),
  });
  const busy = jobs.data?.some((job) => job.status === "pending" || job.status === "running");

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">NOTION CONNECTOR</p>
          <h1>Sync Knowledge Base</h1>
          <p>Read pages available to the integration, split their content, and rebuild the Chroma index.</p>
        </div>
        <button className="button primary" disabled={busy || start.isPending} onClick={() => start.mutate()}>
          {busy ? "Syncing…" : "Start sync"}
        </button>
      </header>

      {start.error && <div className="error-banner">{start.error.message}</div>}
      <section className="sync-explainer">
        <span>Notion API</span><i>→</i><span>Text chunking</span><i>→</i><span>Gemini Embedding</span><i>→</i><span>Chroma</span>
      </section>

      <section className="table-section">
        <h2>Sync history</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Created</th><th>Status</th><th>Pages</th><th>Chunks</th><th>Details</th></tr></thead>
            <tbody>
              {jobs.data?.map((job) => (
                <tr key={job.id}>
                  <td>{new Date(job.created_at).toLocaleString("en-US")}</td>
                  <td><span className={`job-status ${job.status}`}>{job.status}</span></td>
                  <td>{job.pages_processed}</td>
                  <td>{job.chunks_created}</td>
                  <td className={job.error_message ? "error-text" : "muted"}>{job.error_message ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
