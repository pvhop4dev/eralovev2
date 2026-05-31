---
name: socketio-realtime
description: Socket.IO and WebSocket real-time patterns — events, rooms, auth, Redis pub/sub
---

# Socket.IO & Real-Time Rules

## Architecture

```
Browser (socket.io-client)
    ↕ WebSocket / polling fallback
FastAPI + python-socketio (Server)
    ↕ Redis Pub/Sub (for multi-worker scaling)
Celery Worker → Redis Pub/Sub → Socket.IO Server → Client
```

## Server Setup

### FastAPI + Socket.IO Integration

```python
# apps/api/src/presentation/socketio/server.py
import socketio
from infrastructure.config import get_settings

settings = get_settings()

# Create Socket.IO server with Redis manager (for scaling)
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    client_manager=socketio.AsyncRedisManager(settings.REDIS_URL),
    logger=True,
    engineio_logger=False,
    ping_timeout=20,
    ping_interval=25,
    max_http_buffer_size=1_000_000,  # 1MB max message
)

# Wrap FastAPI app with Socket.IO
socket_app = socketio.ASGIApp(sio, other_app=fastapi_app)
```

### Mount in FastAPI

```python
# apps/api/src/presentation/main.py
from presentation.socketio.server import socket_app

# Use socket_app as the ASGI app (wraps FastAPI)
# In uvicorn: uvicorn presentation.main:socket_app
```

## Authentication

### Connection Authentication (Middleware)

```python
# apps/api/src/presentation/socketio/middleware.py

@sio.event
async def connect(sid, environ, auth):
    """Authenticate on connection using JWT token."""
    if not auth or "token" not in auth:
        raise socketio.exceptions.ConnectionRefusedError("Missing auth token")

    try:
        payload = verify_jwt(auth["token"])
        user_id = payload["sub"]
        user = await get_user_by_id(user_id)
        couple = await get_couple_by_user(user_id)

        if not user or not couple:
            raise socketio.exceptions.ConnectionRefusedError("Unauthorized")

        # Store user context in session
        async with sio.session(sid) as session:
            session["user_id"] = str(user.id)
            session["couple_id"] = str(couple.id)
            session["display_name"] = user.display_name

        # Join couple's private room
        couple_room = f"couple:{couple.id}"
        await sio.enter_room(sid, couple_room)

        # Join user's personal room (for direct notifications)
        user_room = f"user:{user.id}"
        await sio.enter_room(sid, user_room)

        # Notify partner about online status
        await sio.emit("partner_online", {
            "user_id": str(user.id),
            "display_name": user.display_name,
        }, room=couple_room, skip_sid=sid)

        logger.info("ws_connected", sid=sid, user_id=str(user.id))

    except JWTError:
        raise socketio.exceptions.ConnectionRefusedError("Invalid token")


@sio.event
async def disconnect(sid):
    """Handle client disconnect."""
    async with sio.session(sid) as session:
        user_id = session.get("user_id")
        couple_room = session.get("couple_id")

    if couple_room:
        await sio.emit("partner_offline", {
            "user_id": user_id,
        }, room=f"couple:{couple_room}", skip_sid=sid)

    logger.info("ws_disconnected", sid=sid, user_id=user_id)
```

## Event Naming Convention

### Pattern: `{domain}:{action}`

```
# Chat events
chat:message          → New message sent
chat:typing           → Partner is typing
chat:read             → Messages marked as read
chat:react            → Message reaction added

# Love Touch events
love:touch            → Love touch sent (heartbeat haptic)
love:miss             → "Miss you" signal

# Ari events
ari:sentiment_warning → Tension detected in chat
ari:daily_quiz        → New daily quiz available
ari:quest_complete    → Quest completed

# Status events
status:mood           → Mood check-in updated
status:battery        → Battery level updated
status:location       → Location updated (if sharing)
status:weather        → Weather data updated

# Notification events
notify:event_reminder → Event/anniversary reminder
notify:match_request  → New match request
notify:general        → General notification

# System events (built-in)
connect               → Client connected
disconnect            → Client disconnected
```

## Event Handlers

### Chat Events

```python
# apps/api/src/presentation/socketio/handlers/chat.py

@sio.on("chat:message")
async def handle_message(sid, data):
    """Handle incoming chat message."""
    async with sio.session(sid) as session:
        user_id = session["user_id"]
        couple_id = session["couple_id"]

    # Validate payload
    try:
        msg = ChatMessagePayload(**data)
    except ValidationError as e:
        await sio.emit("error", {"message": "Invalid message format"}, to=sid)
        return

    # Save to database via use case
    message = await send_message_use_case.execute(
        content=msg.content,
        message_type=msg.type,
        user_id=UUID(user_id),
        couple_id=UUID(couple_id),
    )

    # Broadcast to couple room (both users)
    await sio.emit("chat:message", {
        "id": str(message.id),
        "sender_id": user_id,
        "content": message.content,
        "type": message.message_type,
        "created_at": message.created_at.isoformat(),
    }, room=f"couple:{couple_id}")


@sio.on("chat:typing")
async def handle_typing(sid, data):
    """Broadcast typing indicator to partner."""
    async with sio.session(sid) as session:
        couple_id = session["couple_id"]
        user_id = session["user_id"]

    await sio.emit("chat:typing", {
        "user_id": user_id,
        "is_typing": data.get("is_typing", True),
    }, room=f"couple:{couple_id}", skip_sid=sid)


@sio.on("chat:read")
async def handle_read(sid, data):
    """Mark messages as read."""
    async with sio.session(sid) as session:
        user_id = session["user_id"]
        couple_id = session["couple_id"]

    message_ids = data.get("message_ids", [])
    await mark_messages_read(message_ids, UUID(user_id))

    await sio.emit("chat:read", {
        "reader_id": user_id,
        "message_ids": message_ids,
    }, room=f"couple:{couple_id}", skip_sid=sid)
```

### Love Touch Event

```python
# apps/api/src/presentation/socketio/handlers/love.py

@sio.on("love:touch")
async def handle_love_touch(sid, data):
    """Handle love touch — send heartbeat haptic to partner."""
    async with sio.session(sid) as session:
        user_id = session["user_id"]
        couple_id = session["couple_id"]
        display_name = session["display_name"]

    # Emit to partner (skip sender)
    await sio.emit("love:touch", {
        "sender_id": user_id,
        "sender_name": display_name,
        "intensity": data.get("intensity", "normal"),  # normal | strong
        "timestamp": datetime.now(UTC).isoformat(),
    }, room=f"couple:{couple_id}", skip_sid=sid)

    # Also send push notification (partner might not have app open)
    send_push_notification.delay(
        user_id=get_partner_id(user_id, couple_id),
        title=f"💓 {display_name}",
        body="đang gửi nhịp tim đến bạn...",
        data={"type": "love_touch"},
    )
```

## Room Strategy

```python
# Room naming convention
f"couple:{couple_id}"    # Private room for a couple (2 users max)
f"user:{user_id}"        # Personal room for direct notifications
```

### Rules

- **NEVER** use global broadcast (`sio.emit("event", data)`) — always specify room
- Each couple has ONE room: `couple:{couple_id}`
- Users join their couple room on `connect`, leave on `disconnect`
- All chat/love events go to the couple room
- User-specific events (notifications) go to `user:{user_id}` room

## Emitting from Celery Tasks

### Via Redis Pub/Sub (Cross-process)

```python
# From Celery worker — emit through Redis manager
import socketio

# External Socket.IO client (Celery → Redis → Socket.IO server → Client)
external_sio = socketio.AsyncRedisManager(
    settings.REDIS_URL,
    write_only=True,
)

def emit_from_celery(event: str, data: dict, room: str):
    """Emit Socket.IO event from Celery worker via Redis."""
    external_sio.emit(event, data, room=room)
```

### Common Pattern: Celery → WebSocket Notification

```python
@celery_app.task(name="tasks.notifications.send_event_reminder")
def send_event_reminder(couple_id: str, event_title: str, event_date: str):
    """Send event reminder via both WebSocket and push notification."""
    # 1. WebSocket (if user is online)
    emit_from_celery("notify:event_reminder", {
        "title": event_title,
        "date": event_date,
        "message": f"📅 Ngày mai là {event_title}!",
    }, room=f"couple:{couple_id}")

    # 2. Push notification (always, in case user is offline)
    couple = get_couple(couple_id)
    for user_id in [couple.user1_id, couple.user2_id]:
        send_push_notification.delay(str(user_id), "📅 Nhắc nhở", f"Ngày mai là {event_title}!")
```

## Frontend Client (Next.js)

### Socket.IO Client Setup

```typescript
// apps/web/src/lib/socket.ts
import { io, Socket } from "socket.io-client";
import { useAuthStore } from "@/stores/auth-store";

let socket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    const token = useAuthStore.getState().accessToken;

    socket = io(process.env.NEXT_PUBLIC_WS_URL!, {
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
      // If auth error, try refreshing token
      if (err.message === "Invalid token") {
        refreshAndReconnect();
      }
    });
  }
  return socket;
}

export function disconnectSocket() {
  socket?.disconnect();
  socket = null;
}
```

### React Hook Pattern

```typescript
// apps/web/src/hooks/use-socket-event.ts
import { useEffect } from "react";
import { getSocket } from "@/lib/socket";

export function useSocketEvent<T = unknown>(
  event: string,
  handler: (data: T) => void,
) {
  useEffect(() => {
    const socket = getSocket();
    socket.on(event, handler);
    return () => {
      socket.off(event, handler);
    };
  }, [event, handler]);
}

// Usage in component
function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);

  useSocketEvent<Message>("chat:message", (msg) => {
    setMessages((prev) => [...prev, msg]);
  });

  useSocketEvent<TypingEvent>("chat:typing", (data) => {
    setPartnerTyping(data.is_typing);
  });
}
```

## Rules

### MUST

- Authenticate WebSocket connections using JWT (on `connect` event)
- Store user session data (user_id, couple_id) in Socket.IO session
- Always emit to specific rooms, never broadcast globally
- Validate all incoming event payloads with Pydantic
- Use Redis manager for multi-worker deployment
- Handle reconnection gracefully on frontend

### MUST NOT

- Never trust client-provided user_id/couple_id in events (use session)
- Never send sensitive data (passwords, tokens) via WebSocket events
- Never use WebSocket for large file transfers (use S3 presigned URLs)
- Never keep WebSocket connections without heartbeat/ping

### SHOULD

- Use `skip_sid=sid` when broadcasting to avoid echo back to sender
- Implement typing indicators with debounce (300ms)
- Send push notification as fallback when partner is offline
- Log connection/disconnection events with user context
- Implement exponential backoff for client reconnection
