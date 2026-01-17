
import unittest
import time
import logging
from repositories.in_memory_repository import InMemoryRepository
from services.customer_service import CustomerService
from services.driver_service import DriverService
from services.order_service import OrderService
from services.assignment_service import AssignmentService
from services.notification_service import NotificationService
from services.payment_service import PaymentService
from enums.item_type import ItemType
from enums.order_status import OrderStatus
from enums.driver_status import DriverStatus
from enums.payment_mode import PaymentMode
from strategies.matching_strategy import FirstAvailableMatchingStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Real wiring, no mocks
        self.customer_repo = InMemoryRepository()
        self.driver_repo = InMemoryRepository()
        self.order_repo = InMemoryRepository()
        self.payment_repo = InMemoryRepository()

        self.customer_service = CustomerService(self.customer_repo)
        self.driver_service = DriverService(self.driver_repo)
        self.notification_service = NotificationService()
        self.payment_service = PaymentService(self.payment_repo)
        
        self.strategy = FirstAvailableMatchingStrategy()
        
        self.assignment_service = AssignmentService(
            self.driver_service, 
            self.order_repo, 
            self.strategy
        )
        self.order_service = OrderService(
            self.order_repo, 
            self.assignment_service, 
            self.notification_service, 
            self.payment_service,
            self.customer_service
        )

    def test_full_lifecycle_happy_path(self):
        # 1. Onboard
        c1 = self.customer_service.onboard_customer("C1", "Alice")
        d1 = self.driver_service.onboard_driver("D1", "Bob")
        
        # 2. Create Order
        order = self.order_service.create_order("O1", "C1", ItemType.FOOD)
        self.assertEqual(order.status, OrderStatus.ASSIGNED)
        self.assertEqual(order.driver_id, "D1")
        
        # 3. Pickup
        self.order_service.pickup_order("D1", "O1")
        order = self.order_service.get_order("O1")
        self.assertEqual(order.status, OrderStatus.PICKED_UP)
        
        # 4. Complete
        self.order_service.complete_order("D1", "O1")
        order = self.order_service.get_order("O1")
        self.assertEqual(order.status, OrderStatus.DELIVERED)
        
        # Driver should be free
        d1 = self.driver_service.get_driver("D1")
        self.assertEqual(d1.status, DriverStatus.AVAILABLE)
        
        # 5. Payment
        self.order_service.process_order_payment("O1", 100.0, PaymentMode.UPI)
        self.assertTrue(order.is_paid)

    def test_cancellation_flow(self):
        # 1. Onboard
        self.customer_service.onboard_customer("C1", "Alice")
        d1 = self.driver_service.onboard_driver("D1", "Bob")
        
        # 2. Create Order (Assigns to D1)
        self.order_service.create_order("O1", "C1", ItemType.FOOD)
        d1 = self.driver_service.get_driver("D1")
        self.assertEqual(d1.status, DriverStatus.BUSY)
        
        # 3. Cancel
        self.order_service.cancel_order("O1")
        order = self.order_service.get_order("O1")
        self.assertEqual(order.status, OrderStatus.CANCELLED)
        
        # 4. Verify Driver Free
        d1 = self.driver_service.get_driver("D1")
        self.assertEqual(d1.status, DriverStatus.AVAILABLE)

if __name__ == '__main__':
    unittest.main()
