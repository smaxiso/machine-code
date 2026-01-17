
import time
import logging
from typing import Optional
from models.order import Order
from enums.order_status import OrderStatus
from enums.driver_status import DriverStatus
from enums.item_type import ItemType
from enums.payment_mode import PaymentMode
from repositories.in_memory_repository import InMemoryRepository
from services.interfaces import IOrderService, IPaymentService
from services.assignment_service import AssignmentService
from services.notification_service import NotificationService
from services.payment_service import PaymentService
from services.customer_service import CustomerService
from exceptions.custom_exceptions import (
    OrderNotFoundException,
    DuplicateOrderException,
    OrderNotCancellableException,
    InvalidOrderStateException,
    CustomerNotFoundException,
    DriverNotAssignedException,
    InvalidItemTypeException
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderService(IOrderService):
    def __init__(self, order_repo: InMemoryRepository[Order], assignment_service: AssignmentService, notification_service: NotificationService, payment_service: IPaymentService, customer_service: CustomerService):
        self.repo = order_repo
        self.assignment = assignment_service
        self.notification = notification_service
        self.payment_service = payment_service
        self.customer_service = customer_service

    MAX_QUANTITY = 10
    MAX_WEIGHT = 50.0

    def create_order(self, order_id: str, customer_id: str, item: ItemType, quantity: int = 1, weight: float = 0.0) -> Order:
        if self.repo.get(order_id):
            raise DuplicateOrderException(order_id)

        if not isinstance(item, ItemType):
            raise InvalidItemTypeException(item, [e.value for e in ItemType])
        
        # Guardrails
        if quantity > self.MAX_QUANTITY:
            raise ValueError(f"Order quantity {quantity} exceeds maximum limit of {self.MAX_QUANTITY}")
        
        if weight > self.MAX_WEIGHT:
            raise ValueError(f"Order weight {weight}kg exceeds maximum limit of {self.MAX_WEIGHT}kg")

        customer = self.customer_service.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)

        order = Order(id=order_id, customer_id=customer_id, item=item, quantity=quantity, weight=weight)
        self.repo.save(order_id, order)
        
        self.notification.notify_email(f"{customer_id}@email.com", f"Order {order_id} placed successfully.")
        self.assignment.attempt_assignment(order_id)
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.repo.get(order_id)
    
    def show_order_status(self, order_id: str) -> str:
        order = self.repo.get(order_id)
        if not order:
            return f"Order {order_id} not found"
        return f"Order {order_id}: Status={order.status.value}, Driver={order.driver_id}, Item={order.item.value}"

    def pickup_order(self, driver_id: str, order_id: str) -> None:
        order = self.repo.get(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
            
        if order.status != OrderStatus.ASSIGNED:
            raise InvalidOrderStateException(order_id, order.status.value, OrderStatus.ASSIGNED.value, "picked up")

        if order.driver_id != driver_id:
            raise DriverNotAssignedException(driver_id, order_id)
             
        order.status = OrderStatus.PICKED_UP
        self.repo.save(order_id, order)
        
        self.notification.notify_sms(f"+91-DRIVER-{driver_id}", f"Order {order_id} picked up. Deliver to customer.")
        self.notification.notify_email(f"{order.customer_id}@email.com", f"Order {order_id} is on the way!")

    def complete_order(self, driver_id: str, order_id: str) -> None:
        order = self.repo.get(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
             
        if order.status != OrderStatus.PICKED_UP:
            raise InvalidOrderStateException(order_id, order.status.value, OrderStatus.PICKED_UP.value, "completed")

        if order.driver_id != driver_id:
            raise DriverNotAssignedException(driver_id, order_id)

        order.status = OrderStatus.DELIVERED
        self.repo.save(order_id, order)
            
        if order.driver_id:
            driver_service = self.assignment.driver_service
            driver_service.update_status(order.driver_id, DriverStatus.AVAILABLE)
            
            driver = driver_service.get_driver(order.driver_id)
            if driver:
                driver.order_count += 1
                driver_service.repo.save(driver.id, driver)

            self.notification.notify(f"Order {order_id} delivered successfully by Driver {order.driver_id}")
            self.assignment.on_driver_available(order.driver_id)
            
    def cancel_order(self, order_id: str) -> None:
        order = self.repo.get(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
        
        if not order.can_be_cancelled():
            raise OrderNotCancellableException(order_id, order.status.value)

        prev_driver_id = order.driver_id
        order.status = OrderStatus.CANCELLED
        order.driver_id = None
        self.repo.save(order_id, order)
        
        self.notification.notify(f"Order {order_id} has been cancelled.")

        if prev_driver_id:
            driver_service = self.assignment.driver_service
            driver_service.update_status(prev_driver_id, DriverStatus.AVAILABLE)
            self.notification.notify(f"Driver {prev_driver_id} is now available due to order cancellation.")
            self.assignment.on_driver_available(prev_driver_id)

    def process_order_payment(self, order_id: str, amount: float, mode: PaymentMode) -> None:
        order = self.repo.get(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
            
        if order.is_paid:
            self.notification.notify(f"Order {order_id} is already paid.")
            return
            
        payment = self.payment_service.process_payment(order_id, amount, mode)
        order.payment_id = payment.id
        order.is_paid = True
        self.repo.save(order_id, order)
        
        self.notification.notify(f"Payment of INR {amount} collected for Order {order_id}. Mode: {mode.value}")

    def cleanup_expired_orders(self, timeout_seconds: int = 1800) -> None:
        all_orders = self.repo.all()
        now = time.time()
        
        for order in all_orders:
            if order.status in [OrderStatus.PENDING, OrderStatus.ASSIGNED]:
                if now - order.created_at > timeout_seconds:
                    logger.info(f"[Maintenance] Order {order.id} expired after {timeout_seconds}s. Cancelling...")
                    try:
                        self.cancel_order(order.id)
                    except OrderNotCancellableException:
                        pass
