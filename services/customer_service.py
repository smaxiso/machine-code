
from typing import Optional
from models.customer import Customer
from repositories.in_memory_repository import InMemoryRepository
from services.interfaces import ICustomerService
from exceptions.custom_exceptions import DuplicateCustomerException

class CustomerService(ICustomerService):
    def __init__(self, repo: InMemoryRepository[Customer]):
        self.repo = repo

    def onboard_customer(self, id: str, name: str) -> Customer:
        if self.repo.get(id):
            raise DuplicateCustomerException(id)
        customer = Customer(id=id, name=name)
        self.repo.save(id, customer)
        return customer

    def get_customer(self, id: str) -> Optional[Customer]:
        return self.repo.get(id)
