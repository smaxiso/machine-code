
import threading
import time
import logging
from services.order_service import OrderService

logger = logging.getLogger(__name__)

class OrderExpirationScheduler:
    def __init__(self, order_service: OrderService, check_interval_seconds: int = 60):
        self.order_service = order_service
        self.interval = check_interval_seconds
        self.running = False
        self.thread = None

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Order Expiration Scheduler started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Order Expiration Scheduler stopped.")

    def _run_loop(self):
        while self.running:
            try:
                self.order_service.cleanup_expired_orders()
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
            time.sleep(self.interval)
