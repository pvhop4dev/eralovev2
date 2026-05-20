---
name: create-socketio-handler
description: Create a new Socket.IO event handler for real-time communication
---

# Create Socket.IO Event Handler

When asked to add a real-time feature, follow this pattern:

## 1. Define Event Payload Schema

```python
# apps/api/src/presentation/socketio/schemas/{domain}.py
from pydantic import BaseModel, Field

class {Event}Payload(BaseModel):
    """Incoming payload from client."""
    # ... fields
    content: str = Field(..., max_length=2000)

class {Event}Response(BaseModel):
    """Outgoing payload to client(s)."""
    # ... fields
    sender_id: str
    created_at: str
```

## 2. Create the Event Handler

```python
# apps/api/src/presentation/socketio/handlers/{domain}.py
from presentation.socketio.server import sio
from presentation.socketio.schemas.{domain} import {Event}Payload, {Event}Response
from pydantic import ValidationError
import structlog

logger = structlog.get_logger()

@sio.on("{domain}:{action}")
async def handle_{domain}_{action}(sid, data):
    """Handle {description}."""
    # 1. Get user context from session
    async with sio.session(sid) as session:
        user_id = session["user_id"]
        couple_id = session["couple_id"]

    # 2. Validate incoming payload
    try:
        payload = {Event}Payload(**data)
    except ValidationError as e:
        await sio.emit("error", {
            "event": "{domain}:{action}",
            "message": "Invalid payload",
            "details": e.errors(),
        }, to=sid)
        return

    # 3. Execute business logic (via use case)
    try:
        result = await {domain}_{action}_use_case.execute(
            payload=payload,
            user_id=UUID(user_id),
            couple_id=UUID(couple_id),
        )
    except DomainError as e:
        await sio.emit("error", {
            "event": "{domain}:{action}",
            "message": str(e),
        }, to=sid)
        return

    # 4. Broadcast response to couple room
    response = {Event}Response(
        sender_id=user_id,
        # ... map result fields
        created_at=datetime.now(UTC).isoformat(),
    )

    await sio.emit(
        "{domain}:{action}",
        response.model_dump(),
        room=f"couple:{couple_id}",
        # skip_sid=sid,  # Uncomment to skip echo back to sender
    )

    logger.info("ws_event_handled",
        event="{domain}:{action}",
        user_id=user_id,
        couple_id=couple_id,
    )
```

## 3. Register Handler

```python
# apps/api/src/presentation/socketio/handlers/__init__.py
# Import to register event handlers
from .chat import *
from .love import *
from .status import *
from .{domain} import *  # Add new handler
```

## 4. Create Frontend Hook

```typescript
// apps/web/src/features/{domain}/hooks/use-{domain}-socket.ts
import { useCallback } from "react";
import { useSocketEvent } from "@/hooks/use-socket-event";
import { getSocket } from "@/lib/socket";

interface {Event}Data {
  sender_id: string;
  // ... fields
  created_at: string;
}

export function use{Domain}Socket(
  onEvent: (data: {Event}Data) => void,
) {
  // Listen for incoming events
  useSocketEvent<{Event}Data>("{domain}:{action}", onEvent);

  // Emit function
  const emit{Action} = useCallback((payload: Omit<{Event}Data, "sender_id" | "created_at">) => {
    const socket = getSocket();
    socket.emit("{domain}:{action}", payload);
  }, []);

  return { emit{Action} };
}
```

## 5. Use in Component

```tsx
// apps/web/src/features/{domain}/components/{domain}-view.tsx
"use client";

import { use{Domain}Socket } from "../hooks/use-{domain}-socket";

export function {Domain}View() {
  const [items, setItems] = useState<{Event}Data[]>([]);

  const { emit{Action} } = use{Domain}Socket((data) => {
    setItems((prev) => [...prev, data]);
  });

  const handleSubmit = () => {
    emit{Action}({ content: "..." });
  };

  return (
    // ... UI
  );
}
```

## Event Naming Convention
- Format: `{domain}:{action}` (lowercase, colon separator)
- Examples: `chat:message`, `chat:typing`, `love:touch`, `status:mood`, `ari:quest_complete`

## Checklist
- [ ] Event payload validated with Pydantic
- [ ] User context from Socket.IO session (not client data)
- [ ] Business logic in use case (not in handler)
- [ ] Response broadcast to couple room
- [ ] Error events emitted back to sender on failure
- [ ] Handler registered in `__init__.py`
- [ ] Frontend hook created with `useSocketEvent`
- [ ] Push notification fallback (for offline partner)
- [ ] Logging for event handling
