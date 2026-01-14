from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session
from ...dependencies import get_current_active_user, get_db
from ...core.container import DIContainer
from .service import PaymentService
from ... import schemas

router = APIRouter(tags=["Payments"])

def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return DIContainer.get_payment_service(db)

@router.post("/create-payment-intent")
async def create_payment_intent(
    current_user: schemas.User = Depends(get_current_active_user),
    service: PaymentService = Depends(get_payment_service),
):
    return await service.create_payment_intent(current_user.id)

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    service: PaymentService = Depends(get_payment_service),
):
    payload = await request.body()
    await service.handle_webhook(payload, stripe_signature)
    return {"status": "success"}
