
import unittest
from unittest.mock import MagicMock
from models.order import Order
from models.driver import Driver
from enums.order_status import OrderStatus
from enums.driver_status import DriverStatus
from enums.item_type import ItemType
from services.assignment_service import AssignmentService

class TestAssignmentService(unittest.TestCase):
    def setUp(self):
        self.driver_service = MagicMock()
        self.order_repo = MagicMock()
        self.strategy = MagicMock()
        
        self.service = AssignmentService(
            self.driver_service, 
            self.order_repo, 
            self.strategy
        )

    def test_attempt_assignment_success(self):
        # Arrange
        order = Order("O1", "C1", ItemType.FOOD)
        self.order_repo.get.return_value = order
        
        driver = Driver("D1", "Bob")
        self.driver_service.get_all_drivers.return_value = [driver]
        self.strategy.find_driver.return_value = driver # Strategy finds a driver
        
        # Act
        result = self.service.attempt_assignment("O1")
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(order.driver_id, "D1")
        self.assertEqual(order.status, OrderStatus.ASSIGNED)
        self.assertEqual(driver.status, DriverStatus.BUSY)

    def test_attempt_assignment_queues_if_no_driver(self):
        # Arrange
        order = Order("O1", "C1", ItemType.FOOD)
        self.order_repo.get.return_value = order
        
        self.driver_service.get_all_drivers.return_value = []
        self.strategy.find_driver.return_value = None # No driver found
        
        # Act
        result = self.service.attempt_assignment("O1")
        
        # Assert
        self.assertFalse(result)
        self.assertIn("O1", self.service.pending_orders)
        self.assertEqual(order.status, OrderStatus.PENDING)

if __name__ == '__main__':
    unittest.main()
