
import threading
import time
from services.order_service import OrderService
from utils.logger import setup_logger

logger = setup_logger("SchedulerService")

class OrderExpirationScheduler:
    """
    Runs a background thread to periodically cleanup expired orders.
    """
    def __init__(self, order_service: OrderService, check_interval_seconds: int = 5):
        self.order_service = order_service
        self.interval = check_interval_seconds
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True, name="SchedulerThread")

    def start(self):
        logger.info("Starting Order Expiration Scheduler...")
        self.thread.start()

    def stop(self):
        logger.info("Stopping Order Expiration Scheduler...")
        self._stop_event.set()
        # Join with timeout to avoid hanging if thread is stuck (unlikely here)
        self.thread.join(timeout=2.0)

    def _run(self):
        logger.info(f"Scheduler running every {self.interval} seconds.")
        while not self._stop_event.is_set():
            try:
                self.order_service.cleanup_expired_orders()
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
            
            # Sleep in chunks to allow faster shutdown
            time.sleep(self.interval)
