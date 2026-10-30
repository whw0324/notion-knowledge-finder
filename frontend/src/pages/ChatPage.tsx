import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/client";

export function ChatPage() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [question, setQuestion] = useState("");

  const conversations = useQuery({
    queryKey: ["conversations"],
    queryFn: api.conversations,
  });
  const conversation = useQuery({
    queryKey: ["conversation", conversationId],
    queryFn: () => api.conversation(conversationId!),
    enabled: Boolean(conversationId),
  });

  const send = useMutation({
    mutationFn: async (content: string) => {
      let id = conversationId;
      if (!id) {
        const created = await api.createConversation();
        id = created.id;
        navigate(`/chat/${id}`);
      }
      return { id, message: await api.sendMessage(id, content) };
    },
    onSuccess: ({ id }) => {
      setQuestion("");
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["conversation", id] });
    },
  });

  const messages = useMemo(() => conversation.data?.messages ?? [], [conversation.data]);

  function submit(event: FormEvent) {
    event.preventDefault();
    const content = question.trim();
    if (content && !send.isPending) send.mutate(content);
  }

  return (
    <div className="chat-layout">
      <section className="conversation-panel">
        <button className="button primary full" onClick={() => navigate("/chat")}>+ New chat</button>
        <div className="conversation-list">
          {conversations.data?.map((item) => (
            <Link
              className={item.id === conversationId ? "conversation active" : "conversation"}
              key={item.id}
              to={`/chat/${item.id}`}
            >
              <strong>{item.title}</strong>
              <span>{new Date(item.updated_at).toLocaleDateString("en-US")}</span>
            </Link>
          ))}
          {conversations.isLoading && <p className="muted">Loading conversations…</p>}
        </div>
      </section>

      <section className="chat-main">
        <header className="page-header compact">
          <div>
            <p className="eyebrow">RAG ASSISTANT</p>
            <h1>{conversation.data?.title ?? "Ask your Notion knowledge base"}</h1>
          </div>
          <span className="grounded-label">Grounded answers</span>
        </header>

        <div className="messages" aria-live="polite">
          {!conversationId && (
            <div className="empty-chat">
              <div className="empty-orbit">N</div>
              <h2>Find answers across company knowledge</h2>
              <p>Questions are retrieved from Chroma before LangGraph generates a source-grounded answer.</p>
              <div className="suggestions">
                {["What are the most common Java data structures?", "Summarize the key points in this page", "Which documents discuss time complexity?"].map((text) => (
                  <button key={text} onClick={() => setQuestion(text)}>{text}</button>
                ))}
              </div>
            </div>
          )}
          {messages.map((message) => (
            <article className={`message ${message.role}`} key={message.id}>
              <div className="message-role">{message.role === "user" ? "YOU" : "AI"}</div>
              <div className="message-body">
                <p>{message.content}</p>
                {message.sources.length > 0 && (
                  <div className="sources">
                    <span>Sources</span>
                    {message.sources.map((source, index) => (
                      <a key={`${source.url}-${index}`} href={source.url} target="_blank" rel="noreferrer">
                        <strong>{source.title}</strong>
                        <small>Relevance {source.score?.toFixed(2) ?? "—"}</small>
                        <p>{source.excerpt}</p>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}
          {send.isPending && <div className="thinking">Retrieving knowledge and generating an answer…</div>}
          {send.error && <div className="error-banner">{send.error.message}</div>}
        </div>

        <form className="composer" onSubmit={submit}>
          <textarea
            aria-label="Question"
            placeholder="Ask about your synced Notion content…"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <button className="button primary" disabled={!question.trim() || send.isPending}>Send</button>
        </form>
      </section>
    </div>
  );
}
