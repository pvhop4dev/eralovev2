"use client";

import { Component, type ReactNode } from "react";
import { Button } from "@/components/atoms/button";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * ErrorBoundary — catches React render errors and shows a friendly fallback.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <PageContent />
 *   </ErrorBoundary>
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "3rem",
            textAlign: "center",
            minHeight: "300px",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>😢</div>
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "1.25rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
            }}
          >
            Ôi, có lỗi xảy ra rồi!
          </h2>
          <p
            style={{
              color: "var(--muted-foreground)",
              fontSize: "0.9rem",
              marginBottom: "1.5rem",
              maxWidth: "400px",
            }}
          >
            Đừng lo, hãy thử tải lại trang. Nếu lỗi vẫn tiếp tục, hãy liên hệ chúng mình nhé 💕
          </p>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <Button variant="ghost" onClick={this.handleReset}>
              Thử lại
            </Button>
            <Button onClick={() => (window.location.href = "/dashboard")}>
              Về trang chủ
            </Button>
          </div>
          {process.env.NODE_ENV === "development" && this.state.error && (
            <pre
              style={{
                marginTop: "1.5rem",
                padding: "1rem",
                borderRadius: "var(--radius-md)",
                background: "rgba(255,0,0,0.05)",
                border: "1px solid rgba(255,0,0,0.2)",
                fontSize: "0.75rem",
                textAlign: "left",
                maxWidth: "500px",
                overflow: "auto",
                color: "var(--muted-foreground)",
              }}
            >
              {this.state.error.message}
            </pre>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
