from services.interfaces import INotificationService
from utils.logger import setup_logger

logger = setup_logger("NotificationService")

class NotificationService(INotificationService):
    def notify(self, message: str):
        # Default fallback
        logger.info(f"[NOTIFICATION] {message}")

    def notify_email(self, recipient: str, message: str):
        logger.info(f"[EmailVendor] Sending to {recipient}: {message}")
    
    def notify_sms(self, phone: str, message: str):
        logger.info(f"[SMSVendor] Sending to {phone}: {message}")
