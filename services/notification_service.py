
import logging
from services.interfaces import INotificationService

logger = logging.getLogger(__name__)

class NotificationService(INotificationService):
    def notify(self, message: str):
        logger.info(f"[NOTIFICATION] {message}")

    def notify_email(self, recipient: str, message: str):
        logger.info(f"[EmailVendor] Sending to {recipient}: {message}")
    
    def notify_sms(self, phone: str, message: str):
        logger.info(f"[SMSVendor] Sending to {phone}: {message}")
