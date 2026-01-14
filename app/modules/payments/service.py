import stripe
import uuid
from ...config import settings
from ...core.exceptions import InfrastructureException
from ..users.interfaces import IUserRepository

class PaymentService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_payment_intent(self, user_id: int):
        try:
            # Simulação para fins de demonstração (como no app.py original)
            return {
                "client_secret": f"pi_simulated_{uuid.uuid4()}_secret_{uuid.uuid4()}",
                "payment_id": f"pi_simulated_{uuid.uuid4()}"
            }
        except Exception as e:
            raise InfrastructureException(f"Erro ao criar intenção de pagamento: {str(e)}")

    async def handle_webhook(self, payload: bytes, signature: str):
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                user_id = payment_intent.get('metadata', {}).get('user_id')
                if user_id:
                    user = self.user_repository.get_by_id(int(user_id))
                    if user:
                        self.user_repository.update(user, {"subscription_status": "premium"})
                        return True
            return False
        except stripe.error.SignatureVerificationError:
            raise InfrastructureException("Assinatura do webhook inválida")
        except Exception as e:
            raise InfrastructureException(f"Erro no processamento do webhook: {str(e)}")
