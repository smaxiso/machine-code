
import threading
import logging
from typing import List
from models.order import Order
from enums.order_status import OrderStatus
from enums.driver_status import DriverStatus
from repositories.in_memory_repository import InMemoryRepository
from strategies.matching_strategy import MatchingStrategy, FirstAvailableMatchingStrategy
from services.driver_service import DriverService
from services.interfaces import IAssignmentService

logger = logging.getLogger(__name__)

class AssignmentService(IAssignmentService):
    def __init__(self, driver_service: DriverService, order_repository: InMemoryRepository[Order], strategy: MatchingStrategy = FirstAvailableMatchingStrategy()):
        self.driver_service = driver_service
        self.order_repo = order_repository
        self.strategy = strategy
        self.pending_orders: List[str] = []
        self.lock = threading.RLock()

    def attempt_assignment(self, order_id: str) -> bool:
        with self.lock:
            order = self.order_repo.get(order_id)
            if not order or order.status != OrderStatus.PENDING:
                return False

            drivers = self.driver_service.get_all_drivers()
            driver = self.strategy.find_driver(drivers)
            
            if driver:
                driver.status = DriverStatus.BUSY
                self.driver_service.update_status(driver.id, DriverStatus.BUSY)
                
                order.driver_id = driver.id
                order.status = OrderStatus.ASSIGNED
                self.order_repo.save(order.id, order)
                
                logger.info(f"[Assignment] Order {order.id} assigned to Driver {driver.id}")
                return True
            else:
                if order_id not in self.pending_orders:
                    self.pending_orders.append(order_id)
                    logger.info(f"[Assignment] Order {order.id} queued. No drivers available.")
                return False

    def on_driver_available(self, driver_id: str):
        with self.lock:
            while self.pending_orders:
                order_id = self.pending_orders.pop(0)
                if self.attempt_assignment(order_id):
                    return
