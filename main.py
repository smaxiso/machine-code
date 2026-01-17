
import time
import threading
import logging
from enums.order_status import OrderStatus
from enums.driver_status import DriverStatus
from repositories.in_memory_repository import InMemoryRepository
from services.customer_service import CustomerService
from services.driver_service import DriverService
from services.order_service import OrderService
from services.assignment_service import AssignmentService
from services.notification_service import NotificationService
from services.dashboard_service import DashboardService
from services.payment_service import PaymentService
from services.scheduler_service import OrderExpirationScheduler
from enums.payment_mode import PaymentMode
from enums.item_type import ItemType
from strategies.matching_strategy import FirstAvailableMatchingStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Starting Peer-to-Peer Delivery System (Realistic 2-hour version) ===")

    customer_repo = InMemoryRepository()
    driver_repo = InMemoryRepository()
    order_repo = InMemoryRepository()
    payment_repo = InMemoryRepository()

    customer_service = CustomerService(customer_repo)
    driver_service = DriverService(driver_repo)
    notification_service = NotificationService()
    dashboard_service = DashboardService(driver_service)
    payment_service = PaymentService(payment_repo)
    
    strategy = FirstAvailableMatchingStrategy()
    assignment_service = AssignmentService(driver_service, order_repo, strategy)
    order_service = OrderService(order_repo, assignment_service, notification_service, payment_service, customer_service)

    # Simplified Scheduler: Check every 2 seconds
    scheduler = OrderExpirationScheduler(order_service, check_interval_seconds=2)
    scheduler.start()

    try:
        logger.info("--- Onboarding Users ---")
        c1 = customer_service.onboard_customer("C1", "Sumit")
        c2 = customer_service.onboard_customer("C2", "Alice")
        d1 = driver_service.onboard_driver("D1", "Bob") 
        d2 = driver_service.onboard_driver("D2", "Charlie") 
        
        logger.info(f"Customer C1: {c1.name}")
        logger.info(f"Driver D1: {driver_service.show_driver_status('D1')}")

        logger.info("--- Creating Order 1 (Should assign immediately) ---")
        o1 = order_service.create_order("O1", c1.id, ItemType.ELECTRONICS)
        time.sleep(0.1) 
        
        o1 = order_service.get_order("O1")
        logger.info(f"Order O1 Status: {o1.status}, Assigned Driver: {o1.driver_id}")
        
        logger.info("--- Driver D1 picking up O1 ---")
        order_service.pickup_order("D1", "O1")
        o1 = order_service.get_order("O1")
        logger.info(f"Order O1 Status: {o1.status}")

        logger.info("--- Creating Order 2 (Should assign to D2) ---")
        o2 = order_service.create_order("O2", c2.id, ItemType.BOOKS)
        time.sleep(0.1)
        o2 = order_service.get_order("O2")
        logger.info(f"Order O2 Status: {o2.status}, Assigned Driver: {o2.driver_id}")

        logger.info("--- Creating Order 3 (No driver available) ---")
        o3 = order_service.create_order("O3", c1.id, ItemType.DOCUMENTS)
        time.sleep(0.1)
        o3 = order_service.get_order("O3")
        logger.info(f"Order O3 Status: {o3.status}, Assigned Driver: {o3.driver_id}")

        logger.info("--- Completing Order 1 (D1 becomes free) ---")
        order_service.complete_order("D1", "O1")
        time.sleep(0.1) 
        
        o3 = order_service.get_order("O3")
        logger.info(f"Order O3 Status: {o3.status}, Assigned Driver: {o3.driver_id}") 
        
        if o3.driver_id == "D1":
            logger.info("SUCCESS: Order O3 auto-assigned to Driver D1")
        else:
            logger.error("FAILURE: Order O3 not assigned correctly.")

        logger.info("--- Cancellation Test ---")
        order_service.cancel_order("O3")
        o3 = order_service.get_order("O3")
        logger.info(f"Order O3 Status: {o3.status}")
        
        logger.info("--- Concurrency Stress Test ---")
        threads = []
        for i in range(20):
            t = threading.Thread(target=order_service.create_order, args=(f"OC_{i}", c1.id, ItemType.FOOD))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
            
        time.sleep(1) 
        busy_drivers = [d.id for d in driver_service.get_all_drivers() if d.status == DriverStatus.BUSY]
        logger.info(f"Busy Drivers: {len(busy_drivers)}/2")
        
        logger.info("--- Rating Demo ---")
        driver_service.rate_driver("D1", 5)
        top_drivers = dashboard_service.get_top_drivers(by_rating=True)
        logger.info(f"Top Driver: {top_drivers[0].name} ({top_drivers[0].rating} stars)")

        logger.info("--- Order Expiration Test ---")
        # Create an old order to test scheduler
        old_order = order_service.create_order("O_OLD", c1.id, ItemType.CLOTHING)
        # Manually backdate creation time to 2000s ago (exceeding default 1800s)
        old_order.created_at = time.time() - 2000
        order_repo.save(old_order.id, old_order)
        logger.info(f"Created Old Order O_OLD (Backdated). Waiting for scheduler...")
        
        time.sleep(3) # Wait for scheduler cycle
        old_order = order_service.get_order("O_OLD")
        logger.info(f"Old Order Status: {old_order.status}")

        logger.info("--- Payment Demo ---")
        order_service.process_order_payment("O1", 150.00, PaymentMode.UPI)

    finally:
        logger.info("--- Shutting down ---")
        scheduler.stop()
        logger.info("=== Demo Completed ===")

if __name__ == "__main__":
    main()
