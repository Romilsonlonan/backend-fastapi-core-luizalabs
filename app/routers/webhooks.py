from fastapi import APIRouter, HTTPException, Header, Request, Depends
from sqlalchemy.orm import Session
import stripe
from .. import crud_modules as crud, database, config

router = APIRouter()
settings = config.settings

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request, 
    stripe_signature: str = Header(None),
    db: Session = Depends(database.get_db)
):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            user_id = payment_intent.get('metadata', {}).get('user_id')
            if user_id:
                # Atualizar usuário para premium
                crud.update_user_subscription(db, int(user_id), 'premium')
                print(f"✅ Usuário {user_id} atualizado para premium via webhook.")
            else:
                print("⚠️ Webhook recebido mas user_id não encontrado no metadata.")
                
        return {"status": "success"}
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
