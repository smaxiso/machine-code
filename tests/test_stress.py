
import unittest
import threading
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
from strategies.matching_strategy import FirstAvailableMatchingStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StressTest")

class TestStress(unittest.TestCase):
    def setUp(self):
        self.customer_repo = InMemoryRepository()
        self.driver_repo = InMemoryRepository()
        self.order_repo = InMemoryRepository()
        self.payment_repo = InMemoryRepository()

        self.customer_service = CustomerService(self.customer_repo)
        self.driver_service = DriverService(self.driver_repo)
        self.notification = NotificationService()
        self.payment = PaymentService(self.payment_repo)
        self.strategy = FirstAvailableMatchingStrategy()
        
        self.assignment = AssignmentService(self.driver_service, self.order_repo, self.strategy)
        self.order = OrderService(self.order_repo, self.assignment, self.notification, self.payment, self.customer_service)

        # Setup: 1 Customer, 2 Drivers
        self.c1 = self.customer_service.onboard_customer("C1", "Alice")
        self.driver_service.onboard_driver("D1", "Bob")
        self.driver_service.onboard_driver("D2", "Charlie")

    def test_concurrent_order_creation(self):
        """
        Simulate 50 concurrent order requests.
        Only 2 should be assigned immediately, rest queued.
        """
        thread_count = 50
        threads = []
        errors = []

        def create_order_task(idx):
            try:
                self.order.create_order(f"O{idx}", "C1", ItemType.FOOD)
            except Exception as e:
                errors.append(e)

        # Start threads
        for i in range(thread_count):
            t = threading.Thread(target=create_order_task, args=(i,))
            threads.append(t)
            t.start()
        
        # Join threads
        for t in threads:
            t.join()

        # Assertions
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Check Assignment Logic
        assigned_count = 0
        pending_count = 0
        
        all_orders = self.order_repo.all()
        self.assertEqual(len(all_orders), 50)
        
        for o in all_orders:
            if o.status == OrderStatus.ASSIGNED:
                assigned_count += 1
            elif o.status == OrderStatus.PENDING:
                pending_count += 1
        
        self.assertEqual(assigned_count, 2, "Only 2 orders should be assigned (since 2 drivers)")
        self.assertEqual(pending_count, 48, "Rest should be pending")

if __name__ == '__main__':
    unittest.main()
