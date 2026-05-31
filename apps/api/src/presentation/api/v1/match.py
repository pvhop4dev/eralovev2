"""Match API Routes.

POST /api/v1/match/request — Send match request
GET /api/v1/match/requests — Get sent/received requests
POST /api/v1/match/requests/{id}/accept — Accept
POST /api/v1/match/requests/{id}/decline — Decline
"""

from uuid import UUID

from fastapi import APIRouter

from application.dtos.match_dto import (
    AcceptMatchRequestDTO,
    MatchRequestResponse,
    SendMatchRequestDTO,
    UnmatchRequest,
)
from application.use_cases.match.accept_request import AcceptMatchRequestUseCase
from application.use_cases.match.decline_request import DeclineMatchRequestUseCase
from application.use_cases.match.send_request import SendMatchRequestUseCase
from application.use_cases.match.unmatch import UnmatchUseCase
from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.match_repository import PostgresMatchRequestRepository
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/match", tags=["Match"])


@router.post("/request", status_code=201)
async def send_match_request(
    body: SendMatchRequestDTO,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Send a match request to another user."""
    use_case = SendMatchRequestUseCase(
        user_repo=PostgresUserRepository(session),
        match_repo=PostgresMatchRequestRepository(session),
        couple_repo=PostgresCoupleRepository(session),
    )
    result = await use_case.execute(current_user.id, body)
    return {"data": result.model_dump(), "meta": None, "error": None}


@router.get("/requests")
async def get_match_requests(
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Get sent and received match requests."""
    match_repo = PostgresMatchRequestRepository(session)
    user_repo = PostgresUserRepository(session)

    sent = await match_repo.get_sent_by_user(current_user.id)
    received = await match_repo.get_pending_for_user(current_user.id)

    # Enrich with user info
    sent_responses = []
    for req in sent:
        receiver = await user_repo.get_by_id(req.receiver_id)
        sent_responses.append(MatchRequestResponse(
            id=str(req.id),
            sender_id=str(req.sender_id),
            receiver_id=str(req.receiver_id),
            message=req.message,
            status=req.status,
            proposed_start_date=req.proposed_start_date,
            expires_at=req.expires_at.isoformat() if req.expires_at else None,
            created_at=req.created_at.isoformat() if req.created_at else None,
            receiver_name=receiver.display_name if receiver else None,
            receiver_username=receiver.username if receiver else None,
        ))

    received_responses = []
    for req in received:
        sender = await user_repo.get_by_id(req.sender_id)
        received_responses.append(MatchRequestResponse(
            id=str(req.id),
            sender_id=str(req.sender_id),
            receiver_id=str(req.receiver_id),
            message=req.message,
            status=req.status,
            proposed_start_date=req.proposed_start_date,
            expires_at=req.expires_at.isoformat() if req.expires_at else None,
            created_at=req.created_at.isoformat() if req.created_at else None,
            sender_name=sender.display_name if sender else None,
            sender_username=sender.username if sender else None,
            sender_avatar=sender.avatar_url if sender else None,
        ))

    return {
        "data": {
            "sent": [r.model_dump() for r in sent_responses],
            "received": [r.model_dump() for r in received_responses],
        },
        "meta": None,
        "error": None,
    }


@router.post("/requests/{request_id}/accept")
async def accept_match_request(
    request_id: str,
    body: AcceptMatchRequestDTO,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Accept a match request and create a couple."""
    use_case = AcceptMatchRequestUseCase(
        match_repo=PostgresMatchRequestRepository(session),
        couple_repo=PostgresCoupleRepository(session),
    )
    result = await use_case.execute(current_user.id, UUID(request_id), body)
    return {"data": result.model_dump(), "meta": None, "error": None}


@router.post("/requests/{request_id}/decline", status_code=200)
async def decline_match_request(
    request_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Decline a match request."""
    use_case = DeclineMatchRequestUseCase(
        match_repo=PostgresMatchRequestRepository(session),
    )
    await use_case.execute(current_user.id, UUID(request_id))
    return {"data": {"declined": True}, "meta": None, "error": None}


@router.post("/unmatch", status_code=200)
async def unmatch_couple(
    body: UnmatchRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Unmatch from the current partner."""
    use_case = UnmatchUseCase(couple_repo=PostgresCoupleRepository(session))
    await use_case.execute(current_user.id)
    return {
        "data": {"message": "Unmatched successfully"},
        "meta": None,
        "error": None,
    }

