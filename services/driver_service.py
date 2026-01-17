
from typing import List, Optional
from models.driver import Driver
from enums.driver_status import DriverStatus
from repositories.in_memory_repository import InMemoryRepository
from services.interfaces import IDriverService
from exceptions.custom_exceptions import DriverNotFoundException, DuplicateDriverException, InvalidRatingException

class DriverService(IDriverService):
    def __init__(self, repo: InMemoryRepository[Driver]):
        self.repo = repo

    def onboard_driver(self, id: str, name: str) -> Driver:
        if self.repo.get(id):
            raise DuplicateDriverException(id)
        driver = Driver(id=id, name=name)
        self.repo.save(id, driver)
        return driver

    def get_driver(self, id: str) -> Optional[Driver]:
        return self.repo.get(id)
    
    def update_status(self, driver_id: str, status: DriverStatus) -> None:
        driver = self.repo.get(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)
        driver.status = status
        self.repo.save(driver_id, driver)

    def get_all_drivers(self) -> List[Driver]:
        return self.repo.all()
    
    def rate_driver(self, driver_id: str, rating: int) -> None:
        if not 1 <= rating <= 5:
            raise InvalidRatingException(rating)
        
        driver = self.repo.get(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)
        
        driver.add_rating(rating)
        self.repo.save(driver_id, driver)
    
    def show_driver_status(self, driver_id: str) -> str:
        driver = self.get_driver(driver_id)
        if not driver:
            return f"Driver {driver_id} not found"
        return f"Driver {driver_id}: Name={driver.name}, Status={driver.status.value}, Rating={driver.rating:.1f}, Orders Completed={driver.order_count}"
