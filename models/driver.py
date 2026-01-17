from dataclasses import dataclass
from enums.driver_status import DriverStatus

@dataclass
class Driver:
    id: str
    name: str
    status: DriverStatus = DriverStatus.AVAILABLE
    rating: float = 0.0
    order_count: int = 0
    # Internal usage for calculating average
    _total_rating_score: float = 0.0 
    _total_rated_orders: int = 0

    def add_rating(self, score: int):
        self._total_rating_score += score
        self._total_rated_orders += 1
        self.rating = self._total_rating_score / self._total_rated_orders
