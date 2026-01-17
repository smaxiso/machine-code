from abc import ABC, abstractmethod
from typing import List, Optional
from models.driver import Driver
from enums.driver_status import DriverStatus

class MatchingStrategy(ABC):
    @abstractmethod
    def find_driver(self, drivers: List[Driver]) -> Optional[Driver]:
        pass

class FirstAvailableMatchingStrategy(MatchingStrategy):
    """
    Returns the first driver who is AVAILABLE.
    """
    def find_driver(self, drivers: List[Driver]) -> Optional[Driver]:
        for driver in drivers:
            if driver.status == DriverStatus.AVAILABLE:
                return driver
        return None

class RatingBasedMatchingStrategy(MatchingStrategy):
    """
    Returns the AVAILABLE driver with the highest rating.
    """
    def find_driver(self, drivers: List[Driver]) -> Optional[Driver]:
        available_drivers = [d for d in drivers if d.status == DriverStatus.AVAILABLE]
        if not available_drivers:
            return None
        # Sort by rating desc
        return max(available_drivers, key=lambda d: d.rating)
