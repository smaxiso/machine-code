from dataclasses import dataclass, field
import time
from enums.payment_mode import PaymentMode

@dataclass
class Payment:
    id: str
    order_id: str
    amount: float
    mode: PaymentMode
    status: str = "SUCCESS" # Assuming synchronous success for now
    timestamp: float = field(default_factory=time.time)
