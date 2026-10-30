import type {
  Conversation,
  ConversationDetail,
  Document,
  Health,
  Message,
  SyncJob,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<Health>("/health"),
  conversations: () => request<Conversation[]>("/conversations"),
  conversation: (id: string) => request<ConversationDetail>(`/conversations/${id}`),
  createConversation: () =>
    request<Conversation>("/conversations", { method: "POST", body: "{}" }),
  deleteConversation: (id: string) =>
    request<void>(`/conversations/${id}`, { method: "DELETE" }),
  sendMessage: (id: string, content: string) =>
    request<Message>(`/conversations/${id}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  documents: () => request<Document[]>("/documents"),
  syncJobs: () => request<SyncJob[]>("/sync-jobs"),
  syncJob: (id: string) => request<SyncJob>(`/sync-jobs/${id}`),
  startSync: () => request<SyncJob>("/sync-jobs", { method: "POST", body: "{}" }),
};
