
from abc import ABC, abstractmethod
from typing import Optional, List
from models.order import Order
from models.driver import Driver
from models.customer import Customer
from enums.item_type import ItemType
from enums.driver_status import DriverStatus
from enums.payment_mode import PaymentMode
from models.payment import Payment

class ICustomerService(ABC):
    @abstractmethod
    def onboard_customer(self, id: str, name: str) -> Customer: pass
    
    @abstractmethod
    def get_customer(self, id: str) -> Optional[Customer]: pass

class IDriverService(ABC):
    @abstractmethod
    def onboard_driver(self, id: str, name: str) -> Driver: pass
    
    @abstractmethod
    def get_driver(self, id: str) -> Optional[Driver]: pass
    
    @abstractmethod
    def update_status(self, driver_id: str, status: DriverStatus) -> None: pass
    
    @abstractmethod
    def get_all_drivers(self) -> List[Driver]: pass
    
    @abstractmethod
    def rate_driver(self, driver_id: str, rating: int) -> None: pass
    
    @abstractmethod
    def show_driver_status(self, driver_id: str) -> str: pass

class IOrderService(ABC):
    @abstractmethod
    def create_order(self, order_id: str, customer_id: str, item: ItemType, quantity: int = 1, weight: float = 0.0) -> Order: pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]: pass
    
    @abstractmethod
    def show_order_status(self, order_id: str) -> str: pass
    
    @abstractmethod
    def pickup_order(self, driver_id: str, order_id: str) -> None: pass
    
    @abstractmethod
    def complete_order(self, driver_id: str, order_id: str) -> None: pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> None: pass
    
    @abstractmethod
    def process_order_payment(self, order_id: str, amount: float, mode: PaymentMode) -> None: pass
    
    @abstractmethod
    def cleanup_expired_orders(self, timeout_seconds: Optional[int] = None) -> None: pass

class IAssignmentService(ABC):
    @abstractmethod
    def attempt_assignment(self, order_id: str) -> bool: pass
    
    @abstractmethod
    def on_driver_available(self, driver_id: str) -> None: pass

class INotificationService(ABC):
    @abstractmethod
    def notify(self, message: str) -> None: pass
    
    @abstractmethod
    def notify_email(self, recipient: str, message: str) -> None: pass
    
    @abstractmethod
    def notify_sms(self, phone: str, message: str) -> None: pass

class IDashboardService(ABC):
    @abstractmethod
    def get_top_drivers(self, limit: int, by_rating: bool) -> List[Driver]: pass

class IPaymentService(ABC):
    @abstractmethod
    def process_payment(self, order_id: str, amount: float, mode: PaymentMode) -> "Payment": pass
    
    @abstractmethod
    def get_payment(self, payment_id: str) -> Optional["Payment"]: pass
