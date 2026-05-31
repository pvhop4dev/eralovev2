"use client";

import { useEffect } from "react";
import { getSocket } from "@/lib/socket";

export function useSocketEvent<T = unknown>(
  event: string,
  handler: (data: T) => void
) {
  useEffect(() => {
    if (typeof window === "undefined") return;

    const socket = getSocket();
    
    // Check if the socket object actually has the 'on' method (in case of SSR fallback object)
    if (socket && typeof socket.on === "function") {
      socket.on(event, handler);
    }

    return () => {
      if (socket && typeof socket.off === "function") {
        socket.off(event, handler);
      }
    };
  }, [event, handler]);
}
