"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/atoms/button";
import { Input } from "@/components/atoms/input";
import { Avatar } from "@/components/atoms/avatar";
import { useAuthStore } from "@/stores/auth-store";

export default function MatchPage() {
  const { user: currentUser } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [sendingTo, setSendingTo] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState<"search" | "qr">("search");
  
  // QR State
  const [qrCodeInput, setQrCodeInput] = useState("");
  const [qrScanError, setQrScanError] = useState("");
  const [qrScanResult, setQrScanResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleQRScan = async () => {
    setQrScanError("");
    setQrScanResult(null);
    let username = qrCodeInput.trim();
    if (username.startsWith("eralove:match:")) {
      username = username.replace("eralove:match:", "");
    }
    
    if (!username) {
      setQrScanError("Mã QR hoặc tên đối phương không hợp lệ.");
      return;
    }

    setIsSearching(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/users/search?q=${encodeURIComponent(username)}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        }
      );
      const data = await res.json();
      const users = data.data?.users || [];
      const foundUser = users.find((u: any) => u.username.toLowerCase() === username.toLowerCase());
      if (foundUser) {
        setQrScanResult(foundUser);
      } else {
        setQrScanError("Không tìm thấy người dùng này. Vui lòng kiểm tra lại.");
      }
    } catch {
      setQrScanError("Đã xảy ra lỗi khi kết nối máy chủ.");
    } finally {
      setIsSearching(false);
    }
  };

  const copyToClipboard = () => {
    if (!currentUser?.username) return;
    navigator.clipboard.writeText(`eralove:match:${currentUser.username}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };


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
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
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
            Kết nối trái tim bằng cách tìm kiếm hoặc quét mã QR nhanh
          </p>
        </div>

        {/* Navigation Tabs */}
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
          <button
            type="button"
            onClick={() => setActiveTab("search")}
            style={{
              flex: 1,
              padding: "0.625rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.875rem",
              background: activeTab === "search" ? "var(--gradient-primary)" : "transparent",
              color: activeTab === "search" ? "white" : "var(--muted-foreground)",
              transition: "all 0.2s ease",
            }}
          >
            🔍 Tìm thủ công
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("qr")}
            style={{
              flex: 1,
              padding: "0.625rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.875rem",
              background: activeTab === "qr" ? "var(--gradient-primary)" : "transparent",
              color: activeTab === "qr" ? "white" : "var(--muted-foreground)",
              transition: "all 0.2s ease",
            }}
          >
            📸 Ghép đôi bằng QR
          </button>
        </div>

        {activeTab === "search" ? (
          <>
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
                  Tìm
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
          </>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {/* My QR Code Card */}
            <div
              style={{
                background: "var(--card)",
                borderRadius: "var(--radius-xl)",
                padding: "2rem 1.5rem",
                boxShadow: "var(--shadow-card)",
                border: "1px solid var(--border)",
                textAlign: "center",
                position: "relative",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  height: "4px",
                  background: "var(--gradient-primary)",
                }}
              />
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                <Avatar fallback={currentUser?.display_name || "Me"} size="md" />
                <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--foreground)" }}>
                  {currentUser?.display_name}
                </h3>
                <span style={{ fontSize: "0.8rem", color: "var(--muted-foreground)" }}>
                  @{currentUser?.username}
                </span>
              </div>

              {currentUser?.username ? (
                <div
                  style={{
                    background: "white",
                    padding: "0.75rem",
                    borderRadius: "var(--radius-md)",
                    display: "inline-block",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                    marginBottom: "1rem",
                  }}
                >
                  <img
                    src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=eralove:match:${currentUser.username}`}
                    alt="My Eralove Match QR Code"
                    style={{ width: "180px", height: "180px", display: "block" }}
                  />
                </div>
              ) : (
                <div style={{ height: "180px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  Đang tải...
                </div>
              )}

              <div>
                <button
                  type="button"
                  onClick={copyToClipboard}
                  style={{
                    background: "rgba(255,107,157,0.05)",
                    border: "1px dashed var(--color-rose-petal)",
                    color: "var(--color-rose-petal)",
                    padding: "0.5rem 1rem",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  {copied ? "✅ Đã sao chép!" : "📋 Sao chép mã định dạng QR"}
                </button>
              </div>
            </div>

            {/* QR Scanner Simulator */}
            <div
              style={{
                background: "var(--card)",
                borderRadius: "var(--radius-xl)",
                padding: "2rem 1.5rem",
                boxShadow: "var(--shadow-card)",
                border: "1px solid var(--border)",
              }}
            >
              <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--foreground)", marginBottom: "0.5rem", textAlign: "center" }}>
                Quét mã của đối phương 📸
              </h3>
              <p style={{ color: "var(--muted-foreground)", fontSize: "0.8rem", textAlign: "center", marginBottom: "1.5rem" }}>
                Nhập chuỗi mã QR của người ấy để giả lập quá trình quét camera.
              </p>

              <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
                <div style={{ flex: 1 }}>
                  <Input
                    type="text"
                    placeholder="Nhập eralove:match:username..."
                    value={qrCodeInput}
                    onChange={(e) => setQrCodeInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleQRScan()}
                  />
                </div>
                <Button onClick={handleQRScan} isLoading={isSearching}>
                  Quét
                </Button>
              </div>

              {qrScanError && (
                <p style={{ color: "#ef4444", fontSize: "0.75rem", textAlign: "center", marginBottom: "1rem" }}>
                  {qrScanError}
                </p>
              )}

              {/* Scanned result card */}
              {qrScanResult && (
                <div
                  style={{
                    background: "rgba(255,107,157,0.03)",
                    borderRadius: "var(--radius-lg)",
                    border: "1px solid var(--border)",
                    padding: "1rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "1rem",
                    animation: "fadeIn 0.3s ease-out",
                  }}
                >
                  <Avatar fallback={qrScanResult.display_name} size="md" />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: "var(--foreground)", fontSize: "0.9rem" }}>
                      {qrScanResult.display_name}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>
                      @{qrScanResult.username}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    isLoading={sendingTo === qrScanResult.id}
                    onClick={() => handleSendRequest(qrScanResult.id)}
                  >
                    💗 Kết nối
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
