"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/atoms/button";
import { Avatar } from "@/components/atoms/avatar";
import { getSocket, disconnectSocket } from "@/lib/socket";
import { useSocketEvent } from "@/hooks/use-socket-event";

const LOVE_TOUCH_EMOJIS = ["💗", "💕", "😘", "🥰", "💋", "❤️‍🔥"];

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [showLoveTouch, setShowLoveTouch] = useState(false);
  const [loveAnimation, setLoveAnimation] = useState(false);
  const [partnerTyping, setPartnerTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentUserId = typeof window !== "undefined" ? localStorage.getItem("user_id") : null;

  // Initialize socket on mount, disconnect on unmount
  useEffect(() => {
    getSocket();
    fetchMessages();
    return () => {
      disconnectSocket();
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  // Listen to socket events
  useSocketEvent("chat:message", (newMsg: any) => {
    setMessages((prev) => {
      // Prevent duplicate messages in list
      if (prev.some((m) => m.id === newMsg.id)) {
        return prev;
      }
      return [...prev, newMsg];
    });
  });

  useSocketEvent("chat:typing", (data: any) => {
    setPartnerTyping(data.is_typing);
  });

  useSocketEvent("chat:read", (data: any) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.sender_id !== data.reader_id ? { ...m, status: "read" } : m
      )
    );
  });

  useSocketEvent("chat:delete", (data: any) => {
    setMessages((prev) => prev.filter((m) => m.id !== data.message_id));
  });

  useSocketEvent("love:touch", () => {
    setLoveAnimation(true);
    setTimeout(() => setLoveAnimation(false), 2000);
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/messages?limit=50`,
        { headers: { Authorization: `Bearer ${localStorage.getItem("access_token") || ""}` } }
      );
      if (res.ok) {
        const data = await res.json();
        setMessages(data.data?.messages || []);
      }
    } catch {}
  };

  const sendMessage = async (type: string = "text", content?: string) => {
    const msgContent = content || input.trim();
    if (!msgContent && type === "text") return;

    const socket = getSocket();
    if (socket && socket.connected) {
      socket.emit("chat:message", {
        content: msgContent,
        message_type: type,
      });
      setInput("");
      
      // Stop typing status immediately
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
        socket.emit("chat:typing", { is_typing: false });
        typingTimeoutRef.current = null;
      }
    } else {
      // Fallback to HTTP POST
      setIsSending(true);
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/messages`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
            },
            body: JSON.stringify({ content: msgContent, message_type: type }),
          }
        );
        if (res.ok) {
          setInput("");
          fetchMessages();
        }
      } catch {} finally {
        setIsSending(false);
      }
    }
  };

  const handleInputChange = (val: string) => {
    setInput(val);
    
    const socket = getSocket();
    if (socket && socket.connected) {
      // Emit typing=true if not already typing
      if (!typingTimeoutRef.current) {
        socket.emit("chat:typing", { is_typing: true });
      }
      
      // Clear previous timeout and set new one to emit typing=false after 2s of inactivity
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      typingTimeoutRef.current = setTimeout(() => {
        socket.emit("chat:typing", { is_typing: false });
        typingTimeoutRef.current = null;
      }, 2000);
    }
  };

  const sendLoveTouch = () => {
    setLoveAnimation(true);
    const socket = getSocket();
    if (socket && socket.connected) {
      socket.emit("love:touch", { intensity: "normal" });
      socket.emit("chat:message", {
        content: "💗 Love Touch 💗",
        message_type: "love_message",
      });
    } else {
      sendMessage("love_message", "💗 Love Touch 💗");
    }
    setTimeout(() => setLoveAnimation(false), 2000);
    setShowLoveTouch(false);
  };

  const markRead = async () => {
    const socket = getSocket();
    if (socket && socket.connected) {
      socket.emit("chat:read");
    } else {
      try {
        await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/messages/read`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${localStorage.getItem("access_token") || ""}` },
          }
        );
      } catch {}
    }
  };

  useEffect(() => {
    markRead();
  }, [messages]);

  const isMyMessage = (msg: any) => msg.sender_id === currentUserId;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 64px)", maxWidth: "800px", margin: "0 auto" }}>
      {/* Header */}
      <div
        style={{
          padding: "1rem 1.5rem",
          borderBottom: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "var(--card)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <Avatar fallback="💕" size="md" />
          <div>
            <div style={{ fontWeight: 600 }}>Chat Yêu Thương 💬</div>
            <div style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>
              {partnerTyping ? (
                <span style={{ color: "var(--pink-500)", fontWeight: 500 }}>Đang nhập tin nhắn... 💬</span>
              ) : (
                `${messages.length} tin nhắn`
              )}
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowLoveTouch(!showLoveTouch)}
          style={{
            width: "44px",
            height: "44px",
            borderRadius: "50%",
            border: "none",
            background: "var(--gradient-primary)",
            cursor: "pointer",
            fontSize: "1.25rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "transform 0.2s",
            transform: showLoveTouch ? "scale(1.1)" : "scale(1)",
          }}
        >
          💗
        </button>
      </div>

      {/* Love Touch Panel */}
      {showLoveTouch && (
        <div
          style={{
            padding: "0.75rem 1.5rem",
            background: "rgba(255,107,157,0.05)",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "0.75rem",
          }}
        >
          <span style={{ fontSize: "0.8rem", color: "var(--muted-foreground)" }}>Gửi Love Touch:</span>
          <button
            type="button"
            onClick={sendLoveTouch}
            style={{
              padding: "0.5rem 1.5rem",
              borderRadius: "9999px",
              border: "none",
              background: "var(--gradient-primary)",
              color: "white",
              fontWeight: 600,
              fontSize: "0.9rem",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            💗 Gửi rung tim
          </button>
        </div>
      )}

      {/* Love Animation Overlay */}
      {loveAnimation && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 200,
            pointerEvents: "none",
          }}
        >
          {LOVE_TOUCH_EMOJIS.map((e, i) => (
            <span
              key={i}
              style={{
                position: "absolute",
                fontSize: "2.5rem",
                animation: `float-heart 2s ease-out forwards`,
                animationDelay: `${i * 0.15}s`,
                left: `${20 + i * 12}%`,
                top: "50%",
                opacity: 0,
                userSelect: "none",
              }}
            >
              {e}
            </span>
          ))}
          <style>{`
            @keyframes float-heart {
              0% { opacity: 1; transform: translateY(0) scale(0.5); }
              50% { opacity: 1; transform: translateY(-80px) scale(1.2); }
              100% { opacity: 0; transform: translateY(-200px) scale(0.8); }
            }
          `}</style>
        </div>
      )}

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "1rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: "center", padding: "3rem", color: "var(--muted-foreground)" }}>
            <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>💬</div>
            <p>Bắt đầu cuộc trò chuyện yêu thương!</p>
          </div>
        )}

        {messages.map((msg) => {
          const mine = isMyMessage(msg);
          const isLove = msg.message_type === "love_message";

          return (
            <div
              key={msg.id}
              style={{
                display: "flex",
                justifyContent: mine ? "flex-end" : "flex-start",
                marginBottom: "0.25rem",
              }}
            >
              <div
                style={{
                  maxWidth: "75%",
                  padding: isLove ? "1rem 1.25rem" : "0.625rem 1rem",
                  borderRadius: mine
                    ? "1rem 1rem 0.25rem 1rem"
                    : "1rem 1rem 1rem 0.25rem",
                  background: isLove
                    ? "var(--gradient-primary)"
                    : mine
                    ? "var(--gradient-primary)"
                    : "var(--card)",
                  color: mine || isLove ? "white" : "var(--foreground)",
                  border: mine ? "none" : "1px solid var(--border)",
                  boxShadow: isLove ? "0 4px 20px rgba(255,107,157,0.3)" : "none",
                  position: "relative",
                }}
              >
                {isLove && (
                  <div style={{ textAlign: "center", fontSize: "1.5rem", marginBottom: "0.25rem" }}>
                    💗
                  </div>
                )}
                <p style={{ margin: 0, fontSize: "0.9rem", lineHeight: 1.5 }}>
                  {msg.content}
                </p>
                <div
                  style={{
                    fontSize: "0.65rem",
                    opacity: 0.7,
                    marginTop: "0.25rem",
                    textAlign: "right",
                  }}
                >
                  {msg.created_at ? new Date(msg.created_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }) : ""}
                  {mine && (
                    <span style={{ marginLeft: "0.25rem" }}>
                      {msg.status === "read" ? "✓✓" : "✓"}
                    </span>
                  )}
                </div>
                {msg.is_pinned && (
                  <span style={{ position: "absolute", top: "-8px", right: "-4px", fontSize: "0.7rem" }}>
                    📌
                  </span>
                )}
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: "0.75rem 1rem",
          borderTop: "1px solid var(--border)",
          background: "var(--card)",
          display: "flex",
          gap: "0.5rem",
          alignItems: "flex-end",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          placeholder="Nhập tin nhắn... 💕"
          style={{
            flex: 1,
            padding: "0.75rem 1rem",
            borderRadius: "9999px",
            border: "1px solid var(--border)",
            background: "var(--background)",
            fontSize: "0.9rem",
            outline: "none",
            color: "var(--foreground)",
          }}
        />
        <Button
          onClick={() => sendMessage()}
          disabled={!input.trim() || isSending}
          size="sm"
          style={{
            borderRadius: "50%",
            width: "44px",
            height: "44px",
            padding: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {isSending ? "..." : "💌"}
        </Button>
      </div>
    </div>
  );
}

