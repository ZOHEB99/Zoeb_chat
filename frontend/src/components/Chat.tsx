"use client";

import { FormEvent, KeyboardEvent, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import styles from "./Chat.module.css";

type Role = "user" | "assistant";

type Message = {
  role: Role;
  content: string;
};

const WELCOME: Message = {
  role: "assistant",
  content:
    "Hi! I'm FitCoach AI. I help with nutrition, workouts, sleep, and wellness.\n\nAsk me anything — even general questions — and I'll guide you toward healthier choices.\n\nTry: \"Should I eat rice?\" or \"What's a good morning routine?\"",
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  const historyRef = useRef<Message[]>([]);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      if (chatRef.current) {
        chatRef.current.scrollTop = chatRef.current.scrollHeight;
      }
    });
  };

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMessage: Message = { role: "user", content: trimmed };
    historyRef.current = [...historyRef.current, userMessage];

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    scrollToBottom();

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: historyRef.current }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        const detail =
          typeof error.detail === "string"
            ? error.detail
            : "Something went wrong. Please try again.";
        setMessages((prev) => [...prev, { role: "assistant", content: detail }]);
        historyRef.current = historyRef.current.slice(0, -1);
        return;
      }

      const data = await response.json();
      const assistantMessage: Message = { role: "assistant", content: data.reply };
      historyRef.current = [...historyRef.current, assistantMessage];
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Network error. Check your connection and try again." },
      ]);
      historyRef.current = historyRef.current.slice(0, -1);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void sendMessage(input);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage(input);
    }
  };

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <div className={styles.logo}>FC</div>
          <div>
            <h1>FitCoach AI</h1>
            <p>Your proactive health & fitness advisor</p>
            <div className={styles.builtBy}>built by Zoehb</div>
          </div>
        </div>
        <span className={styles.badge}>Health First</span>
      </header>

      <main className={styles.chat} ref={chatRef}>
        {messages.map((message, index) => (
          <div key={index} className={`${styles.message} ${styles[message.role]}`}>
            <div className={styles.avatar}>{message.role === "user" ? "You" : "AI"}</div>
            <div className={styles.bubble}>
              {message.role === "assistant" ? (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              ) : (
                message.content
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={styles.avatar}>AI</div>
            <div className={styles.bubble}>
              <div className={styles.typing}>
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className={styles.composer}>
        <form onSubmit={onSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
            placeholder="Ask about food, workouts, sleep, or wellness..."
            maxLength={4000}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()} aria-label="Send message">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </form>
        <p className={styles.disclaimer}>
          General wellness guidance only — not medical advice. Consult a doctor for health conditions.
        </p>
      </footer>
    </div>
  );
}
