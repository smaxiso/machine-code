
from typing import List
from models.driver import Driver
from services.driver_service import DriverService
from services.interfaces import IDashboardService

class DashboardService(IDashboardService):
    def __init__(self, driver_service: DriverService):
        self.driver_service = driver_service

    def get_top_drivers(self, limit: int = 5, by_rating: bool = True) -> List[Driver]:
        drivers = self.driver_service.get_all_drivers()
        if by_rating:
            return sorted(drivers, key=lambda d: d.rating, reverse=True)[:limit]
        else:
            return sorted(drivers, key=lambda d: d.order_count, reverse=True)[:limit]
