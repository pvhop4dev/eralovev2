"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/atoms/button";
import { Avatar } from "@/components/atoms/avatar";

interface MatchRequest {
  id: string;
  sender_id: string;
  sender_name: string;
  sender_username: string;
  receiver_id: string;
  receiver_name: string;
  receiver_username: string;
  status: string;
  message?: string;
}

export default function MatchRequestsPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"received" | "sent">("received");
  const [requests, setRequests] = useState<{
    sent: MatchRequest[];
    received: MatchRequest[];
  }>({
    sent: [],
    received: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchRequests = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/match/requests`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        },
      );
      const data = await res.json();
      setRequests(data.data || { sent: [], received: [] });
    } catch {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setTimeout(() => {
      fetchRequests();
    }, 0);
  }, []);

  const handleAccept = async (requestId: string) => {
    setActionLoading(requestId);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/match/requests/${requestId}/accept`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            start_date: new Date().toISOString().split("T")[0],
          }),
        },
      );
      if (res.ok) {
        router.push("/dashboard");
      }
    } catch {
      // Handle error
    } finally {
      setActionLoading(null);
    }
  };

  const handleDecline = async (requestId: string) => {
    setActionLoading(requestId);
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/match/requests/${requestId}/decline`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        },
      );
      await fetchRequests();
    } catch {
      // Handle error
    } finally {
      setActionLoading(null);
    }
  };

  const currentList = tab === "received" ? requests.received : requests.sent;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--gradient-bg)",
        padding: "2rem 1rem",
      }}
    >
      <div style={{ maxWidth: "600px", margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "1.5rem",
              fontWeight: 700,
              marginBottom: "0.25rem",
            }}
          >
            Yêu cầu ghép đôi 💌
          </h1>
        </div>

        {/* Tabs */}
        <div
          style={{
            display: "flex",
            gap: "0.25rem",
            background: "var(--card)",
            borderRadius: "var(--radius-md)",
            padding: "0.25rem",
            marginBottom: "1.5rem",
            border: "1px solid var(--border)",
          }}
        >
          {(["received", "sent"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              style={{
                flex: 1,
                padding: "0.625rem",
                borderRadius: "var(--radius-sm)",
                border: "none",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.875rem",
                background:
                  tab === t ? "var(--gradient-primary)" : "transparent",
                color: tab === t ? "white" : "var(--muted-foreground)",
                transition: "all 0.2s ease",
              }}
            >
              {t === "received"
                ? `📥 Nhận (${requests.received.length})`
                : `📤 Gửi (${requests.sent.length})`}
            </button>
          ))}
        </div>

        {/* List */}
        {isLoading ? (
          <div style={{ textAlign: "center", padding: "3rem" }}>
            <div
              className="animate-[heartbeat_1.2s_ease-in-out_infinite]"
              style={{ fontSize: "2rem" }}
            >
              💗
            </div>
          </div>
        ) : currentList.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              padding: "3rem",
              color: "var(--muted-foreground)",
            }}
          >
            <div style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>
              {tab === "received" ? "📭" : "📮"}
            </div>
            <p>
              {tab === "received"
                ? "Chưa có yêu cầu nào"
                : "Bạn chưa gửi yêu cầu nào"}
            </p>
          </div>
        ) : (
          <div
            style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}
          >
            {currentList.map((req) => (
              <div
                key={req.id}
                style={{
                  background: "var(--card)",
                  borderRadius: "var(--radius-xl)",
                  padding: "1.25rem",
                  boxShadow: "var(--shadow-card)",
                  border: "1px solid var(--border)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    marginBottom: "0.75rem",
                  }}
                >
                  <Avatar
                    fallback={
                      tab === "received" ? req.sender_name : req.receiver_name
                    }
                    size="md"
                  />
                  <div style={{ flex: 1 }}>
                    <div
                      style={{ fontWeight: 600, color: "var(--foreground)" }}
                    >
                      {tab === "received" ? req.sender_name : req.receiver_name}
                    </div>
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: "var(--muted-foreground)",
                      }}
                    >
                      @
                      {tab === "received"
                        ? req.sender_username
                        : req.receiver_username}
                    </div>
                  </div>
                  <div
                    style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "9999px",
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      background:
                        req.status === "pending"
                          ? "rgba(255,107,157,0.1)"
                          : req.status === "accepted"
                            ? "rgba(52,211,153,0.1)"
                            : "rgba(156,163,175,0.1)",
                      color:
                        req.status === "pending"
                          ? "var(--color-rose-petal)"
                          : req.status === "accepted"
                            ? "#34d399"
                            : "var(--muted-foreground)",
                    }}
                  >
                    {req.status === "pending"
                      ? "⏳ Chờ"
                      : req.status === "accepted"
                        ? "✅ Đã chấp nhận"
                        : "❌ Từ chối"}
                  </div>
                </div>

                {req.message && (
                  <p
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--foreground)",
                      marginBottom: "0.75rem",
                      fontStyle: "italic",
                    }}
                  >
                    &ldquo;{req.message}&rdquo;
                  </p>
                )}

                {tab === "received" && req.status === "pending" && (
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <Button
                      size="sm"
                      onClick={() => handleAccept(req.id)}
                      isLoading={actionLoading === req.id}
                      style={{ flex: 1 }}
                    >
                      💕 Chấp nhận
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDecline(req.id)}
                      style={{ flex: 1 }}
                    >
                      Từ chối
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
