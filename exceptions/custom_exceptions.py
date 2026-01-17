"""
Custom exceptions for the P2P Delivery System.
Provides clear, specific error handling for different failure scenarios.
"""

class DeliverySystemException(Exception):
    """Base exception for all delivery system errors"""
    pass


# ============ Order Exceptions ============

class OrderNotFoundException(DeliverySystemException):
    """Raised when an order cannot be found"""
    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order {order_id} not found")


class DuplicateOrderException(DeliverySystemException):
    """Raised when attempting to create an order with existing ID"""
    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order {order_id} already exists")


class OrderNotCancellableException(DeliverySystemException):
    """Raised when attempting to cancel an order that cannot be cancelled"""
    def __init__(self, order_id: str, status: str):
        self.order_id = order_id
        self.status = status
        super().__init__(f"Order {order_id} cannot be cancelled. Current status: {status}")


class InvalidOrderStateException(DeliverySystemException):
    """Raised when order is in invalid state for requested operation"""
    def __init__(self, order_id: str, current_status: str, expected_status: str, operation: str):
        self.order_id = order_id
        super().__init__(
            f"Order {order_id} cannot be {operation}. "
            f"Current status: {current_status}, Expected: {expected_status}"
        )


# ============ Customer Exceptions ============

class CustomerNotFoundException(DeliverySystemException):
    """Raised when a customer cannot be found"""
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer {customer_id} not found")


class DuplicateCustomerException(DeliverySystemException):
    """Raised when attempting to create a customer with existing ID"""
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer {customer_id} already exists")


# ============ Driver Exceptions ============

class DriverNotFoundException(DeliverySystemException):
    """Raised when a driver cannot be found"""
    def __init__(self, driver_id: str):
        self.driver_id = driver_id
        super().__init__(f"Driver {driver_id} not found")


class DriverNotAssignedException(DeliverySystemException):
    """Raised when driver attempts action on order not assigned to them"""
    def __init__(self, driver_id: str, order_id: str):
        self.driver_id = driver_id
        self.order_id = order_id
        super().__init__(f"Driver {driver_id} is not assigned to order {order_id}")


class DuplicateDriverException(DeliverySystemException):
    """Raised when attempting to create a driver with existing ID"""
    def __init__(self, driver_id: str):
        self.driver_id = driver_id
        super().__init__(f"Driver {driver_id} already exists")


# ============ Validation Exceptions ============

class InvalidItemTypeException(DeliverySystemException):
    """Raised when an invalid item type is provided"""
    def __init__(self, item, valid_types: list):
        self.item = item
        super().__init__(f"Invalid item type: {item}. Must be one of {valid_types}")


class InvalidRatingException(DeliverySystemException):
    """Raised when rating is outside valid range"""
    def __init__(self, rating: int, min_rating: int = 1, max_rating: int = 5):
        self.rating = rating
        super().__init__(f"Rating must be between {min_rating} and {max_rating}. Got: {rating}")
