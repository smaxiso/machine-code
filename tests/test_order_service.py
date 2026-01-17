
import unittest
from unittest.mock import MagicMock
from models.order import Order
from enums.order_status import OrderStatus
from enums.item_type import ItemType
from services.order_service import OrderService
from exceptions.custom_exceptions import DuplicateOrderException, InvalidOrderStateException

class TestOrderService(unittest.TestCase):
    def setUp(self):
        # Mocks
        self.repo = MagicMock()
        self.assignment = MagicMock()
        self.notification = MagicMock()
        self.payment = MagicMock()
        self.customer = MagicMock()
        
        # SUT (System Under Test)
        self.service = OrderService(
            self.repo, 
            self.assignment, 
            self.notification, 
            self.payment,
            self.customer
        )

    def test_create_order_success(self):
        # Arrange
        self.repo.get.return_value = None # No duplicate
        self.customer.get_customer.return_value = MagicMock() # Customer exists
        
        # Act
        order = self.service.create_order("O1", "C1", ItemType.FOOD)
        
        # Assert
        self.repo.save.assert_called()
        self.assignment.attempt_assignment.assert_called_with("O1")
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_create_duplicate_order_throws(self):
        # Arrange
        self.repo.get.return_value = Order("O1", "C1", ItemType.FOOD) # Exists
        
        # Act & Assert
        with self.assertRaises(DuplicateOrderException):
            self.service.create_order("O1", "C1", ItemType.FOOD)

    def test_pickup_order_success(self):
        # Arrange
        order = Order("O1", "C1", ItemType.FOOD)
        order.status = OrderStatus.ASSIGNED
        order.driver_id = "D1"
        self.repo.get.return_value = order
        
        # Act
        self.service.pickup_order("D1", "O1")
        
        # Assert
        self.assertEqual(order.status, OrderStatus.PICKED_UP)
        self.repo.save.assert_called_with("O1", order)

    def test_pickup_invalid_state_throws(self):
        # Arrange
        order = Order("O1", "C1", ItemType.FOOD)
        order.status = OrderStatus.PENDING # Not ASSIGNED yet
        self.repo.get.return_value = order
        
        # Act & Assert
        with self.assertRaises(InvalidOrderStateException):
            self.service.pickup_order("D1", "O1")

    def test_create_order_exceeds_quantity_throws(self):
        # Arrange
        self.repo.get.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError):
            self.service.create_order("O1", "C1", ItemType.FOOD, quantity=100)

    def test_create_order_exceeds_weight_throws(self):
        # Arrange
        self.repo.get.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError):
            self.service.create_order("O1", "C1", ItemType.FOOD, weight=100.0)

if __name__ == '__main__':
    unittest.main()
