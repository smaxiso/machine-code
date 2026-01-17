"""
Driver Service - Handles driver operations including onboarding, status, and ratings.
"""

from typing import List, Optional
from models.driver import Driver
from enums.driver_status import DriverStatus
from repositories.in_memory_repository import InMemoryRepository
from services.interfaces import IDriverService
from exceptions.custom_exceptions import (
    DriverNotFoundException,
    DuplicateDriverException,
    InvalidRatingException
)


class DriverService(IDriverService):
    """
    Manages driver lifecycle: registration, status updates, and ratings.
    """
    
    def __init__(self, repo: InMemoryRepository[Driver]):
        self.repo = repo

    def onboard_driver(self, id: str, name: str) -> Driver:
        """
        Register a new driver in the system.
        
        Args:
            id: Unique driver identifier
            name: Driver's name
            
        Returns:
            Created Driver object
            
        Raises:
            DuplicateDriverException: If driver ID already exists
        """
        if self.repo.get(id):
            raise DuplicateDriverException(id)
            
        driver = Driver(id=id, name=name)
        self.repo.save(id, driver)
        return driver

    def get_driver(self, id: str) -> Optional[Driver]:
        """Retrieve driver by ID"""
        return self.repo.get(id)
    
    def update_status(self, driver_id: str, status: DriverStatus) -> None:
        """
        Update driver's availability status.
        
        Args:
            driver_id: Driver to update
            status: New status (AVAILABLE/BUSY)
            
        Raises:
            DriverNotFoundException: If driver doesn't exist
        """
        driver = self.repo.get(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)
            
        driver.status = status
        self.repo.save(driver_id, driver)

    def get_all_drivers(self) -> List[Driver]:
        """Get all registered drivers"""
        return self.repo.all()
    
    def rate_driver(self, driver_id: str, rating: int) -> None:
        """
        Rate a driver after delivery.
        
        Args:
            driver_id: Driver to rate
            rating: Rating score (1-5)
            
        Raises:
            InvalidRatingException: If rating is not between 1-5
            DriverNotFoundException: If driver doesn't exist
        """
        # Validate rating range
        if not 1 <= rating <= 5:
            raise InvalidRatingException(rating)
        
        driver = self.repo.get(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)
        
        driver.add_rating(rating)
        self.repo.save(driver_id, driver)
    
    def show_driver_status(self, driver_id: str) -> str:
        """
        Get formatted driver status string.
        
        Args:
            driver_id: Driver to check
            
        Returns:
            Formatted status string with all driver details
        """
        driver = self.get_driver(driver_id)
        if not driver:
            return f"Driver {driver_id} not found"
        
        return (
            f"Driver {driver_id}: "
            f"Name={driver.name}, "
            f"Status={driver.status.value}, "
            f"Rating={driver.rating:.1f}, "
            f"Orders Completed={driver.order_count}"
        )
