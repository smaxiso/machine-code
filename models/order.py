from dataclasses import dataclass, field
import time
from typing import Optional
from enums.order_status import OrderStatus
from enums.item_type import ItemType

@dataclass
class Order:
    id: str
    customer_id: str
    item: ItemType
    quantity: int = 1
    weight: float = 0.0
    driver_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: float = field(default_factory=time.time)
    
    # Payment Info
    payment_id: Optional[str] = None
    is_paid: bool = False
    
    def can_be_cancelled(self) -> bool:
        """
        Policy: Once a driver picks up an order, it cannot be canceled.
        Implies PENDING and ASSIGNED are cancellable.
        """
        return self.status in [OrderStatus.PENDING, OrderStatus.ASSIGNED]
