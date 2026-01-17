"""
Customer Service - Handles customer onboarding and retrieval.
"""

from typing import Optional
from models.customer import Customer
from repositories.in_memory_repository import InMemoryRepository
from services.interfaces import ICustomerService
from exceptions.custom_exceptions import DuplicateCustomerException


class CustomerService(ICustomerService):
    """
    Manages customer registration and lookup.
    """
    
    def __init__(self, repo: InMemoryRepository[Customer]):
        self.repo = repo

    def onboard_customer(self, id: str, name: str) -> Customer:
        """
        Register a new customer.
        
        Args:
            id: Unique customer identifier
            name: Customer's name
            
        Returns:
            Created Customer object
            
        Raises:
            DuplicateCustomerException: If customer ID already exists
        """
        if self.repo.get(id):
            raise DuplicateCustomerException(id)
            
        customer = Customer(id=id, name=name)
        self.repo.save(id, customer)
        return customer

    def get_customer(self, id: str) -> Optional[Customer]:
        """Retrieve customer by ID"""
        return self.repo.get(id)
