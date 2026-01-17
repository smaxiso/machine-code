
import uuid
import logging
from models.payment import Payment
from enums.payment_mode import PaymentMode
from repositories.in_memory_repository import InMemoryRepository
from services.interfaces import IPaymentService

logger = logging.getLogger(__name__)

class PaymentService(IPaymentService):
    def __init__(self, repo: InMemoryRepository[Payment]):
        self.repo = repo

    def process_payment(self, order_id: str, amount: float, mode: PaymentMode) -> Payment:
        payment_id = str(uuid.uuid4())
        payment = Payment(id=payment_id, order_id=order_id, amount=amount, mode=mode)
        
        logger.info(f"[PaymentGateway] Processing {mode.value} payment of INR {amount} for Order {order_id}...")
        logger.info(f"[PaymentGateway] Transaction {payment_id} SUCCESS.")
        
        self.repo.save(payment_id, payment)
        return payment

    def get_payment(self, payment_id: str):
        return self.repo.get(payment_id)
