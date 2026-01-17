"""
Abstract interfaces for all services.
Ensures consistent contracts and enables easy mocking for tests.
"""

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
    """Interface for Customer operations"""
    
    @abstractmethod
    def onboard_customer(self, id: str, name: str) -> Customer:
        """Register a new customer"""
        pass
    
    @abstractmethod
    def get_customer(self, id: str) -> Optional[Customer]:
        """Retrieve customer by ID"""
        pass


class IDriverService(ABC):
    """Interface for Driver operations"""
    
    @abstractmethod
    def onboard_driver(self, id: str, name: str) -> Driver:
        """Register a new driver"""
        pass
    
    @abstractmethod
    def get_driver(self, id: str) -> Optional[Driver]:
        """Retrieve driver by ID"""
        pass
    
    @abstractmethod
    def update_status(self, driver_id: str, status: DriverStatus) -> None:
        """Update driver availability status"""
        pass
    
    @abstractmethod
    def get_all_drivers(self) -> List[Driver]:
        """Get all registered drivers"""
        pass
    
    @abstractmethod
    def rate_driver(self, driver_id: str, rating: int) -> None:
        """Rate a driver (1-5 stars)"""
        pass
    
    @abstractmethod
    def show_driver_status(self, driver_id: str) -> str:
        """Get formatted driver status string"""
        pass


class IOrderService(ABC):
    """Interface for Order operations"""
    
    @abstractmethod
    def create_order(self, order_id: str, customer_id: str, item: ItemType) -> Order:
        """Create a new delivery order"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve order by ID"""
        pass
    
    @abstractmethod
    def show_order_status(self, order_id: str) -> str:
        """Get formatted order status string"""
        pass
    
    @abstractmethod
    def pickup_order(self, driver_id: str, order_id: str) -> None:
        """Mark order as picked up by driver"""
        pass
    
    @abstractmethod
    def complete_order(self, driver_id: str, order_id: str) -> None:
        """Mark order as delivered"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """Cancel an order (if allowed)"""
        pass
    
    @abstractmethod
    def process_order_payment(self, order_id: str, amount: float, mode: PaymentMode) -> None:
        """Process payment for an order"""
        pass
    
    @abstractmethod
    def cleanup_expired_orders(self, timeout_seconds: Optional[int] = None) -> None:
        """Cancel orders that exceeded timeout"""
        pass


class IAssignmentService(ABC):
    """Interface for Order-Driver assignment"""
    
    @abstractmethod
    def attempt_assignment(self, order_id: str) -> bool:
        """Try to assign order to available driver"""
        pass
    
    @abstractmethod
    def on_driver_available(self, driver_id: str) -> None:
        """Handle driver becoming available"""
        pass


class INotificationService(ABC):
    """Interface for sending notifications"""
    
    @abstractmethod
    def notify(self, message: str) -> None:
        """Send generic notification"""
        pass
    
    @abstractmethod
    def notify_email(self, recipient: str, message: str) -> None:
        """Send email notification"""
        pass
    
    @abstractmethod
    def notify_sms(self, phone: str, message: str) -> None:
        """Send SMS notification"""
        pass


class IDashboardService(ABC):
    """Interface for Dashboard/Analytics"""
    
    @abstractmethod
    def get_top_drivers(self, limit: int, by_rating: bool) -> List[Driver]:
        """Get top performing drivers"""
        pass


class IPaymentService(ABC):
    """Interface for Payment processing"""
    
    @abstractmethod
    def process_payment(self, order_id: str, amount: float, mode: PaymentMode) -> "Payment":
        """Process a payment"""
        pass
    
    @abstractmethod
    def get_payment(self, payment_id: str) -> Optional["Payment"]:
        """Retrieve payment details"""
        pass
