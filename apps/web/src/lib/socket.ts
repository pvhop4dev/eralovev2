import { io, Socket } from "socket.io-client";
import { useAuthStore } from "@/stores/auth-store";

let socket: Socket | null = null;
let currentToken: string | null = null;

export function getSocket(): Socket {
  if (typeof window === "undefined") {
    return {} as Socket;
  }

  const token = useAuthStore.getState().accessToken;

  // Re-establish connection if the token changed (e.g. login/logout/refresh)
  if (socket && currentToken !== token) {
    console.log("Token changed, disconnecting old socket...");
    socket.disconnect();
    socket = null;
  }

  if (!socket) {
    currentToken = token;
    
    // In next.js client-side, NEXT_PUBLIC_WS_URL might be wss://api-love... or http://localhost:8000
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "http://localhost:8000";
    
    console.log("Connecting to WebSocket server at:", wsUrl);

    socket = io(wsUrl, {
      auth: { token },
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    socket.on("connect", () => {
      console.log("Socket connected:", socket?.id);
    });

    socket.on("connect_error", (err) => {
      console.error("Socket connection error:", err.message);
    });

    socket.on("disconnect", (reason) => {
      console.log("Socket disconnected:", reason);
    });
  }
  return socket;
}

export function disconnectSocket() {
  if (socket) {
    console.log("Disconnecting socket...");
    socket.disconnect();
    socket = null;
    currentToken = null;
  }
}
