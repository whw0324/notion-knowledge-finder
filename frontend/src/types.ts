export interface Source {
  title: string;
  url: string;
  excerpt: string;
  score: number | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  grounded: boolean | null;
  created_at: string;
  sources: Source[];
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface Document {
  id: string;
  notion_page_id: string;
  title: string;
  url: string;
  last_edited_time: string;
  chunk_count: number;
  sync_status: string;
  updated_at: string;
}

export interface SyncJob {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  pages_processed: number;
  chunks_created: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface Health {
  status: string;
  chat_provider: string;
  embedding_provider: string;
  chat_model: string;
  embedding_model: string;
}
