"""
Order Service - Handles all order lifecycle operations.
"""

import time
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
from utils.config_loader import ConfigLoader
from utils.logger import setup_logger

logger = setup_logger("OrderService")
from exceptions.custom_exceptions import (
    OrderNotFoundException,
    DuplicateOrderException,
    OrderNotCancellableException,
    InvalidOrderStateException,
    CustomerNotFoundException,
    DriverNotAssignedException,
    InvalidItemTypeException
)


class OrderService(IOrderService):
    """
    Manages order lifecycle: creation, pickup, delivery, cancellation.
    """
    
    def __init__(self, 
                 order_repo: InMemoryRepository[Order], 
                 assignment_service: AssignmentService,
                 notification_service: NotificationService,
                 payment_service: IPaymentService,
                 customer_service: CustomerService):
        self.repo = order_repo
        self.assignment = assignment_service
        self.notification = notification_service
        self.payment_service = payment_service
        self.customer_service = customer_service

    def create_order(self, order_id: str, customer_id: str, item: ItemType) -> Order:
        """
        Create a new delivery order.
        
        Args:
            order_id: Unique identifier for the order
            customer_id: ID of the customer placing the order
            item: Type of item being delivered (must be valid ItemType)
            
        Returns:
            Created Order object
            
        Raises:
            DuplicateOrderException: If order_id already exists
            InvalidItemTypeException: If item is not a valid ItemType
            CustomerNotFoundException: If customer doesn't exist
        """
        # Duplicate check
        if self.repo.get(order_id):
            raise DuplicateOrderException(order_id)

        # Item type validation
        if not isinstance(item, ItemType):
            raise InvalidItemTypeException(item, [e.value for e in ItemType])

        # Customer validation
        customer = self.customer_service.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)

        # Create and save order
        order = Order(id=order_id, customer_id=customer_id, item=item)
        self.repo.save(order_id, order)
        
        # Notify customer
        self.notification.notify_email(
            f"{customer_id}@email.com", 
            f"Order {order_id} placed successfully."
        )
        
        # Attempt immediate assignment
        self.assignment.attempt_assignment(order_id)
        
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve order by ID"""
        return self.repo.get(order_id)
    
    def show_order_status(self, order_id: str) -> str:
        """
        Get formatted order status string.
        
        Args:
            order_id: Order to check
            
        Returns:
            Formatted status string
        """
        order = self.repo.get(order_id)
        if not order:
            return f"Order {order_id} not found"
        return f"Order {order_id}: Status={order.status.value}, Driver={order.driver_id}, Item={order.item.value}"

    def pickup_order(self, driver_id: str, order_id: str) -> None:
        """
        Mark order as picked up by driver.
        
        Args:
            driver_id: Driver picking up the order
            order_id: Order being picked up
            
        Raises:
            OrderNotFoundException: If order doesn't exist
            InvalidOrderStateException: If order is not in ASSIGNED state
            DriverNotAssignedException: If driver is not assigned to this order
        """
        order = self.repo.get(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
            
        if order.status != OrderStatus.ASSIGNED:
            raise InvalidOrderStateException(
                order_id, 
                order.status.value, 
                OrderStatus.ASSIGNED.value,
                "picked up"
            )

        if order.driver_id != driver_id:
            raise DriverNotAssignedException(driver_id, order_id)
             
        order.status = OrderStatus.PICKED_UP
        self.repo.save(order_id, order)
        
        # Notify driver and customer
        self.notification.notify_sms(
            f"+91-DRIVER-{driver_id}", 
            f"Order {order_id} picked up. Deliver to customer."
        )
        self.notification.notify_email(
            f"{order.customer_id}@email.com", 
            f"Order {order_id} is on the way!"
        )

    def complete_order(self, driver_id: str, order_id: str) -> None:
        """
        Mark order as delivered.
        
        Args:
            driver_id: Driver completing the delivery
            order_id: Order being completed
            
        Raises:
            OrderNotFoundException: If order doesn't exist
            InvalidOrderStateException: If order is not in PICKED_UP state
            DriverNotAssignedException: If driver is not assigned to this order
        """
        order = self.repo.get(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
             
        if order.status != OrderStatus.PICKED_UP:
            raise InvalidOrderStateException(
                order_id,
                order.status.value,
                OrderStatus.PICKED_UP.value,
                "completed"
            )

        if order.driver_id != driver_id:
            raise DriverNotAssignedException(driver_id, order_id)

        order.status = OrderStatus.DELIVERED
        self.repo.save(order_id, order)
            
        # Update driver status and stats
        if order.driver_id:
            driver_service = self.assignment.driver_service
            driver_service.update_status(order.driver_id, DriverStatus.AVAILABLE)
            
            driver = driver_service.get_driver(order.driver_id)
            if driver:
                driver.order_count += 1
                driver_service.repo.save(driver.id, driver)

            self.notification.notify(
                f"Order {order_id} delivered successfully by Driver {order.driver_id}"
            )
            
            # Trigger assignment for any pending orders
            self.assignment.on_driver_available(order.driver_id)
            
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel an order (only if not yet picked up).
        
        Args:
            order_id: Order to cancel
            
        Raises:
            OrderNotFoundException: If order doesn't exist
            OrderNotCancellableException: If order cannot be cancelled (already picked up)
        """
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

        # Free up driver if was assigned
        if prev_driver_id:
            driver_service = self.assignment.driver_service
            driver_service.update_status(prev_driver_id, DriverStatus.AVAILABLE)
            self.notification.notify(
                f"Driver {prev_driver_id} is now available due to order cancellation."
            )
            self.assignment.on_driver_available(prev_driver_id)

    def process_order_payment(self, order_id: str, amount: float, mode: PaymentMode) -> None:
        """
        Process payment for a delivered order.
        
        Args:
            order_id: Order to process payment for
            amount: Payment amount
            mode: Payment method (CASH/UPI/WALLET)
        """
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
        
        self.notification.notify(
            f"Payment of INR {amount} collected for Order {order_id}. Mode: {mode.value}"
        )

    def cleanup_expired_orders(self, timeout_seconds: int = None) -> None:
        """
        Cancel orders that have exceeded the timeout without being picked up.
        
        Args:
            timeout_seconds: Maximum age for unpicked orders (default from config)
        """
        if timeout_seconds is None:
            timeout_seconds = ConfigLoader().get("order_expiration_seconds", 1800)

        all_orders = self.repo.all()
        now = time.time()
        
        for order in all_orders:
            # Only expire PENDING or ASSIGNED orders (not PICKED_UP)
            if order.status in [OrderStatus.PENDING, OrderStatus.ASSIGNED]:
                if now - order.created_at > timeout_seconds:
                    logger.info(f"[Maintenance] Order {order.id} expired after {timeout_seconds}s. Cancelling...")
                    try:
                        self.cancel_order(order.id)
                    except OrderNotCancellableException:
                        # Order state changed between check and cancel
                        pass
