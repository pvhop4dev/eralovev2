"use client";

import { useState } from "react";
import { Button } from "@/components/atoms/button";
import { Input } from "@/components/atoms/input";
import { Avatar } from "@/components/atoms/avatar";

export default function MatchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [sendingTo, setSendingTo] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/users/search?q=${encodeURIComponent(searchQuery)}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        }
      );
      const data = await res.json();
      setSearchResults(data.data?.users || []);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSendRequest = async (receiverId: string) => {
    setSendingTo(receiverId);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/match/request`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            receiver_id: receiverId,
            message: message || undefined,
          }),
        }
      );
      if (res.ok) {
        setSuccess(true);
      }
    } catch {
      // Handle error
    } finally {
      setSendingTo(null);
    }
  };

  if (success) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--gradient-bg)",
          textAlign: "center",
          padding: "2rem",
        }}
      >
        <div>
          <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>💌</div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            Đã gửi yêu cầu ghép đôi!
          </h1>
          <p style={{ color: "var(--muted-foreground)", marginBottom: "1.5rem" }}>
            Đang chờ đối phương chấp nhận... 💕
          </p>
          <Button onClick={() => setSuccess(false)} variant="secondary">
            Quay lại tìm kiếm
          </Button>
        </div>
      </div>
    );
  }

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
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "1.75rem",
              fontWeight: 800,
              background: "var(--gradient-primary)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              marginBottom: "0.5rem",
            }}
          >
            Tìm người yêu 💕
          </h1>
          <p style={{ color: "var(--muted-foreground)", fontSize: "0.9rem" }}>
            Tìm kiếm bằng username hoặc tên hiển thị
          </p>
        </div>

        {/* Search */}
        <div
          style={{
            background: "var(--card)",
            borderRadius: "var(--radius-xl)",
            padding: "1.5rem",
            boxShadow: "var(--shadow-card)",
            border: "1px solid var(--border)",
            marginBottom: "1.5rem",
          }}
        >
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <Input
                type="text"
                placeholder="Nhập username hoặc tên..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch} isLoading={isSearching}>
              🔍
            </Button>
          </div>
        </div>

        {/* Results */}
        {searchResults.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {searchResults.map((user) => (
              <div
                key={user.id}
                style={{
                  background: "var(--card)",
                  borderRadius: "var(--radius-xl)",
                  padding: "1.25rem",
                  boxShadow: "var(--shadow-card)",
                  border: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                }}
              >
                <Avatar fallback={user.display_name} size="lg" />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: "1rem", color: "var(--foreground)" }}>
                    {user.display_name}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--muted-foreground)" }}>
                    @{user.username}
                    {user.zodiac_sign && ` · ${user.zodiac_sign}`}
                  </div>
                </div>
                <Button
                  size="sm"
                  isLoading={sendingTo === user.id}
                  onClick={() => handleSendRequest(user.id)}
                >
                  💗 Ghép đôi
                </Button>
              </div>
            ))}
          </div>
        )}

        {searchResults.length === 0 && searchQuery && !isSearching && (
          <div style={{ textAlign: "center", padding: "3rem 1rem", color: "var(--muted-foreground)" }}>
            <div style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>🔍</div>
            <p>Không tìm thấy ai. Thử username khác nhé!</p>
          </div>
        )}
      </div>
    </div>
  );
}
