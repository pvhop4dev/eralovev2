"""Integration tests for Socket.IO WebSocket handlers."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import socketio

from domain.exceptions import InvalidTokenError
from presentation.socketio.handlers.chat import handle_message, handle_read, handle_typing
from presentation.socketio.handlers.love import handle_love_touch
from presentation.socketio.server import connect, disconnect


@pytest.mark.asyncio
@patch("presentation.socketio.server.get_user_id_from_token")
@patch("presentation.socketio.server.async_session_maker")
@patch("presentation.socketio.server.sio")
async def test_connect_success(mock_sio, mock_db_session_maker, mock_get_user_id):
    """Test successful socket connection with token verification and room joining."""
    user_id = uuid4()
    couple_id = uuid4()
    mock_get_user_id.return_value = user_id

    # Configure sio async mock methods
    mock_sio.enter_room = AsyncMock()
    mock_sio.emit = AsyncMock()

    # Mock user and couple database returns
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.display_name = "User A"

    mock_couple = MagicMock()
    mock_couple.id = couple_id

    mock_user_repo = AsyncMock()
    mock_user_repo.get_by_id.return_value = mock_user

    mock_couple_repo = AsyncMock()
    mock_couple_repo.get_active_for_user.return_value = mock_couple

    # Setup async context manager mock for db session
    mock_db_session = AsyncMock()
    mock_db_session_maker.return_value = mock_db_session
    mock_db_session.__aenter__.return_value = mock_db_session

    with patch("presentation.socketio.server.PostgresUserRepository", return_value=mock_user_repo), \
         patch("presentation.socketio.server.PostgresCoupleRepository", return_value=mock_couple_repo):
        
        # Call connection handler
        await connect("sid_123", {}, {"token": "valid_token"})

        # Assert token decoded
        mock_get_user_id.assert_called_once_with("valid_token", expected_type="access")

        # Assert rooms joined
        mock_sio.enter_room.assert_any_call("sid_123", f"couple:{couple_id}")
        mock_sio.enter_room.assert_any_call("sid_123", f"user:{user_id}")

        # Assert partner notified
        mock_sio.emit.assert_called_once_with(
            "partner_online",
            {"user_id": str(user_id), "display_name": "User A"},
            room=f"couple:{couple_id}",
            skip_sid="sid_123"
        )


@pytest.mark.asyncio
async def test_connect_missing_auth():
    """Test connect fails when auth or token is missing."""
    with pytest.raises(socketio.exceptions.ConnectionRefusedError, match="Missing auth token"):
        await connect("sid_123", {}, None)

    with pytest.raises(socketio.exceptions.ConnectionRefusedError, match="Missing auth token"):
        await connect("sid_123", {}, {})


@pytest.mark.asyncio
@patch("presentation.socketio.server.get_user_id_from_token")
async def test_connect_invalid_token(mock_get_user_id):
    """Test connect fails when JWT token is invalid."""
    mock_get_user_id.side_effect = InvalidTokenError("Invalid token")
    
    with pytest.raises(socketio.exceptions.ConnectionRefusedError, match="Invalid token"):
        await connect("sid_123", {}, {"token": "bad_token"})


@pytest.mark.asyncio
@patch("presentation.socketio.server.sio")
async def test_disconnect_emits_offline(mock_sio):
    """Test disconnecting notifies partner of offline status."""
    # Configure sio async mock methods
    mock_sio.emit = AsyncMock()

    # Setup mock session storage
    mock_session = {"user_id": "user_id_123", "couple_id": "couple_id_456"}
    
    # Mock context manager for session
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_sio.session.return_value = mock_ctx

    await disconnect("sid_123")

    mock_sio.emit.assert_called_once_with(
        "partner_offline",
        {"user_id": "user_id_123"},
        room="couple:couple_id_456",
        skip_sid="sid_123"
    )


@pytest.mark.asyncio
@patch("presentation.socketio.handlers.chat.sio")
@patch("presentation.socketio.handlers.chat.async_session_maker")
async def test_chat_message_success(mock_db_session_maker, mock_sio):
    """Test chat:message saves message to DB and broadcasts."""
    # Configure sio async mock methods
    mock_sio.emit = AsyncMock()

    user_id = uuid4()
    couple_id = uuid4()
    
    # Mock session
    mock_session = {"user_id": str(user_id), "couple_id": str(couple_id), "display_name": "User A"}
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_sio.session.return_value = mock_ctx

    # Mock DB repos
    mock_db_session = AsyncMock()
    mock_db_session_maker.return_value = mock_db_session
    mock_db_session.__aenter__.return_value = mock_db_session

    mock_message_entity = MagicMock()
    mock_message_entity.to_dict.return_value = {
        "id": "msg_uuid",
        "content": "hello world",
        "message_type": "text",
        "sender_id": str(user_id)
    }

    mock_msg_repo = AsyncMock()
    mock_msg_repo.create.return_value = mock_message_entity

    with patch("presentation.socketio.handlers.chat.PostgresMessageRepository", return_value=mock_msg_repo):
        await handle_message("sid_123", {"content": "hello world", "message_type": "text"})

        # Assert saved
        mock_msg_repo.create.assert_called_once()
        mock_db_session.commit.assert_called_once()

        # Assert broadcasted
        mock_sio.emit.assert_called_once_with(
            "chat:message",
            {
                "id": "msg_uuid",
                "content": "hello world",
                "message_type": "text",
                "sender_id": str(user_id)
            },
            room=f"couple:{couple_id}"
        )


@pytest.mark.asyncio
@patch("presentation.socketio.handlers.chat.sio")
async def test_chat_typing_broadcast(mock_sio):
    """Test chat:typing broadcasts status to partner."""
    # Configure sio async mock methods
    mock_sio.emit = AsyncMock()

    mock_session = {"user_id": "user_id_123", "couple_id": "couple_id_456"}
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_sio.session.return_value = mock_ctx

    await handle_typing("sid_123", {"is_typing": True})

    mock_sio.emit.assert_called_once_with(
        "chat:typing",
        {"user_id": "user_id_123", "is_typing": True},
        room="couple:couple_id_456",
        skip_sid="sid_123"
    )


@pytest.mark.asyncio
@patch("presentation.socketio.handlers.chat.sio")
@patch("presentation.socketio.handlers.chat.async_session_maker")
async def test_chat_read_success(mock_db_session_maker, mock_sio):
    """Test chat:read marks messages read in DB and broadcasts reader ID."""
    # Configure sio async mock methods
    mock_sio.emit = AsyncMock()

    user_id = uuid4()
    couple_id = uuid4()
    
    mock_session = {"user_id": str(user_id), "couple_id": str(couple_id)}
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_sio.session.return_value = mock_ctx

    mock_db_session = AsyncMock()
    mock_db_session_maker.return_value = mock_db_session
    mock_db_session.__aenter__.return_value = mock_db_session

    mock_msg_repo = AsyncMock()
    mock_msg_repo.mark_read_for_user.return_value = 5

    with patch("presentation.socketio.handlers.chat.PostgresMessageRepository", return_value=mock_msg_repo):
        await handle_read("sid_123")

        # Assert DB updated
        mock_msg_repo.mark_read_for_user.assert_called_once_with(couple_id, user_id)
        mock_db_session.commit.assert_called_once()

        # Assert broadcasted
        mock_sio.emit.assert_called_once_with(
            "chat:read",
            {"reader_id": str(user_id), "marked_read": 5},
            room=f"couple:{couple_id}",
            skip_sid="sid_123"
        )


@pytest.mark.asyncio
@patch("presentation.socketio.handlers.love.sio")
async def test_love_touch_broadcast(mock_sio):
    """Test love:touch broadcasts heart event to partner."""
    # Configure sio async mock methods
    mock_sio.emit = AsyncMock()

    mock_session = {"user_id": "user_id_123", "couple_id": "couple_id_456", "display_name": "User A"}
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_sio.session.return_value = mock_ctx

    await handle_love_touch("sid_123", {"intensity": "strong"})

    # Check emit was called with partner room, skipping sender
    called_args = mock_sio.emit.call_args
    assert called_args[0][0] == "love:touch"
    assert called_args[1]["room"] == "couple:couple_id_456"
    assert called_args[1]["skip_sid"] == "sid_123"
    
    payload = called_args[0][1]
    assert payload["sender_id"] == "user_id_123"
    assert payload["sender_name"] == "User A"
    assert payload["intensity"] == "strong"
    assert "timestamp" in payload
