import time
import threading
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
from models.payment import Payment
from strategies.matching_strategy import FirstAvailableMatchingStrategy
from utils.logger import setup_logger

logger = setup_logger("Main")

def main():
    logger.info("=== Starting Peer-to-Peer Delivery System Demo (Refactored) ===")

    # 1. Initialize Components
    customer_repo = InMemoryRepository()
    driver_repo = InMemoryRepository()
    order_repo = InMemoryRepository()
    payment_repo = InMemoryRepository()

    customer_service = CustomerService(customer_repo)
    driver_service = DriverService(driver_repo)
    notification_service = NotificationService()
    dashboard_service = DashboardService(driver_service)
    payment_service = PaymentService(payment_repo)
    
    # Strategy
    strategy = FirstAvailableMatchingStrategy()
    
    assignment_service = AssignmentService(driver_service, order_repo, strategy)
    order_service = OrderService(order_repo, assignment_service, notification_service, payment_service, customer_service)

    # Scheduler (BONUS FEATURE)
    # Check every 2 seconds for demo purposes
    scheduler = OrderExpirationScheduler(order_service, check_interval_seconds=2)
    scheduler.start()

    try:
        # 2. Onboard Users
        logger.info("--- Onboarding Users ---")
        c1 = customer_service.onboard_customer("C1", "Sumit")
        c2 = customer_service.onboard_customer("C2", "Alice")
        
        d1 = driver_service.onboard_driver("D1", "Bob") 
        d2 = driver_service.onboard_driver("D2", "Charlie") 
        
        logger.info(f"Customer C1: {c1}")
        logger.info(f"Driver D1: {driver_service.get_driver('D1')}")
        logger.info(f"Driver D1 (formatted): {driver_service.show_driver_status('D1')}")

        # 3. Create Orders (Happy Path)
        logger.info("--- Creating Order 1 (Should assign immediately) ---")
        o1 = order_service.create_order("O1", c1.id, ItemType.ELECTRONICS)
        time.sleep(0.1) 
        
        # Verify assignment
        o1 = order_service.get_order("O1")
        logger.info(f"Order O1 Status: {o1.status}, Assigned Driver: {o1.driver_id}")
        logger.info(f"Order O1 (formatted): {order_service.show_order_status('O1')}")
        
        # 4. Pickup Order 1
        logger.info("--- Driver D1 picking up O1 ---")
        order_service.pickup_order("D1", "O1")
        o1 = order_service.get_order("O1")
        logger.info(f"Order O1 Status: {o1.status}")

        # 5. Create Order 2 (Should assign to D2)
        logger.info("--- Creating Order 2 (Should assign to D2) ---")
        o2 = order_service.create_order("O2", c2.id, ItemType.BOOKS)
        time.sleep(0.1)
        o2 = order_service.get_order("O2")
        logger.info(f"Order O2 Status: {o2.status}, Assigned Driver: {o2.driver_id}")

        # 6. Create Order 3 (No driver available -> Pending)
        logger.info("--- Creating Order 3 (No driver available) ---")
        o3 = order_service.create_order("O3", c1.id, ItemType.DOCUMENTS)
        time.sleep(0.1)
        o3 = order_service.get_order("O3")
        logger.info(f"Order O3 Status: {o3.status}, Assigned Driver: {o3.driver_id}")

        # 7. Complete Order 1 -> Driver D1 becomes free -> Should assign O3 (queued) to D1
        logger.info("--- Completing Order 1 (D1 becomes free) ---")
        order_service.complete_order("D1", "O1")
        
        # Wait for async assignment if any (though we made create_order sync, on_driver_available triggers effectively sync/async depending on lock)
        time.sleep(0.1) 
        
        o1 = order_service.get_order("O1")
        logger.info(f"Order O1 Status: {o1.status}") 

        o3 = order_service.get_order("O3")
        logger.info(f"Order O3 Status: {o3.status}, Assigned Driver: {o3.driver_id}") 
        
        if o3.driver_id == "D1":
            logger.info("SUCCESS: Order O3 auto-assigned to Driver D1")
        else:
            logger.error("FAILURE: Order O3 not assigned correctly.")

        # 8. Cancellation Logic
        logger.info("--- Cancellation Test ---")
        order_service.cancel_order("O3")
        o3 = order_service.get_order("O3")
        logger.info(f"Order O3 Status: {o3.status}")
        
        d1 = driver_service.get_driver("D1")
        logger.info(f"Driver D1 Status: {d1.status}") 

        # 9. Concurrency Test
        logger.info("--- Concurrency Stress Test ---")
        # 20 concurrent orders
        threads = []
        for i in range(20):
            t = threading.Thread(target=order_service.create_order, args=(f"OC_{i}", c1.id, ItemType.FOOD))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
            
        time.sleep(1) 
        
        logger.info("Checking how many orders assigned (We have 2 drivers)...")
        busy_drivers = [d.id for d in driver_service.get_all_drivers() if d.status == DriverStatus.BUSY]
        logger.info(f"Busy Drivers: {len(busy_drivers)}/2")
        
        # 10. Bonus: Dashboard and Expiration
        logger.info("--- Bonus Features Demo ---")
        
        logger.info("Rating Driver D1 (5 stars)...")
        driver_service.rate_driver("D1", 5)
        d1 = driver_service.get_driver("D1")
        logger.info(f"Driver D1: {d1}")

        logger.info("Top Drivers by Rating:")
        top_drivers = dashboard_service.get_top_drivers(by_rating=True)
        for d in top_drivers:
            logger.info(f" - {d.name}: {d.rating} stars, {d.order_count} orders")

        logger.info("--- Edge Case: Invalid Rating ---")
        try:
            driver_service.rate_driver("D1", 10)  # Invalid rating
        except Exception as e:
            logger.info(f"Caught expected error: {e}")

        # Expiration
        logger.info("--- Order Expiration Test (Using Scheduler) ---")
        old_order = order_service.create_order("O_OLD", c1.id, ItemType.CLOTHING)
        old_order.created_at = time.time() - 2000 
        order_repo.save(old_order.id, old_order) 
        
        logger.info(f"Created Old Order {old_order.id}, Status: {old_order.status}")
        logger.info("Waiting for scheduler to pick it up (2s interval)...")
        time.sleep(3) # Wait for scheduler
        
        old_order = order_service.get_order("O_OLD")
        logger.info(f"Old Order Status after wait: {old_order.status}")

        # 11. Payment Demo
        logger.info("--- Payment Demo ---")
        # Pay for Order 1
        logger.info("Processing payment for Order O1 (Delivered)...")
        order_service.process_order_payment("O1", 150.00, PaymentMode.UPI)
        o1 = order_service.get_order("O1")
        logger.info(f"Order O1 Payment Status: Paid={o1.is_paid}, Transaction ID={o1.payment_id}")

    finally:
        logger.info("--- Shutting down ---")
        scheduler.stop()
        logger.info("=== Demo Completed ===")

if __name__ == "__main__":
    main()
