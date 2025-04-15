"""
Notification manager for alerting users via various channels like Email, Telegram, and SMS.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manager class for sending notifications through different channels
    """
    
    def __init__(self):
        self.email_configured = False
        self.telegram_configured = False
        self.sms_configured = False
        
        # Check for configuration in environment
        self._check_email_config()
        self._check_telegram_config()
        self._check_sms_config()
    
    def _check_email_config(self) -> None:
        """Check if email configuration is available"""
        if os.environ.get('SENDGRID_API_KEY'):
            self.email_configured = True
        else:
            logger.warning("SendGrid API key not found. Email notifications disabled.")
    
    def _check_telegram_config(self) -> None:
        """Check if Telegram configuration is available"""
        if os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHAT_ID'):
            self.telegram_configured = True
        else:
            logger.warning("Telegram configuration not found. Telegram notifications disabled.")
    
    def _check_sms_config(self) -> None:
        """Check if SMS configuration is available"""
        if (os.environ.get('TWILIO_ACCOUNT_SID') and 
            os.environ.get('TWILIO_AUTH_TOKEN') and 
            os.environ.get('TWILIO_PHONE_NUMBER')):
            self.sms_configured = True
        else:
            logger.warning("Twilio configuration not found. SMS notifications disabled.")
    
    def get_available_channels(self) -> List[str]:
        """Get list of available notification channels"""
        channels = []
        if self.email_configured:
            channels.append('email')
        if self.telegram_configured:
            channels.append('telegram')
        if self.sms_configured:
            channels.append('sms')
        return channels
    
    def send_notification(self, 
                         message: str, 
                         subject: str = 'AITradeStrategist Alert', 
                         channels: List[str] = None,
                         recipients: Dict[str, List[str]] = None) -> Dict[str, bool]:
        """
        Send a notification through selected channels
        
        Args:
            message: The message content
            subject: The subject line (for email)
            channels: List of channels to use (email, telegram, sms)
            recipients: Dictionary of recipients by channel type
                       Example: {'email': ['user@example.com'], 'sms': ['+12345678']}
        
        Returns:
            Dictionary of channel-success pairs
        """
        if not channels:
            channels = self.get_available_channels()
        
        if not recipients:
            recipients = {}
        
        results = {}
        
        for channel in channels:
            if channel == 'email' and self.email_configured:
                email_recipients = recipients.get('email', [])
                if not email_recipients:
                    logger.warning("No email recipients specified")
                    results['email'] = False
                    continue
                
                for recipient in email_recipients:
                    success = self._send_email(recipient, subject, message)
                    results['email'] = success
            
            elif channel == 'telegram' and self.telegram_configured:
                success = self._send_telegram(message)
                results['telegram'] = success
            
            elif channel == 'sms' and self.sms_configured:
                sms_recipients = recipients.get('sms', [])
                if not sms_recipients:
                    logger.warning("No SMS recipients specified")
                    results['sms'] = False
                    continue
                
                for recipient in sms_recipients:
                    success = self._send_sms(recipient, message)
                    results['sms'] = success
            
            else:
                logger.warning(f"Channel {channel} not available or not recognized")
                results[channel] = False
        
        return results
    
    def _send_email(self, recipient: str, subject: str, message: str) -> bool:
        """Send notification via email"""
        try:
            # Lazy import to avoid dependencies until needed
            import os
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message_obj = Mail(
                from_email='noreply@aitradestrategist.com',
                to_emails=recipient,
                subject=subject,
                html_content=message)
            
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message_obj)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send email: Status code {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _send_telegram(self, message: str) -> bool:
        """Send notification via Telegram"""
        try:
            # Lazy import to avoid dependencies until needed
            import requests
            
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def _send_sms(self, recipient: str, message: str) -> bool:
        """Send notification via SMS"""
        try:
            # Lazy import to avoid dependencies until needed
            from twilio.rest import Client
            
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            from_number = os.environ.get('TWILIO_PHONE_NUMBER')
            
            client = Client(account_sid, auth_token)
            
            sms = client.messages.create(
                body=message,
                from_=from_number,
                to=recipient
            )
            
            logger.info(f"SMS sent successfully, SID: {sms.sid}")
            return True
                
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    def send_profit_alert(self, pair: str, profit: float, trade_type: str = 'close') -> Dict[str, bool]:
        """
        Send profit/loss alert
        
        Args:
            pair: Trading pair (e.g., BTC/USDT)
            profit: Profit percentage
            trade_type: Type of trade ('open', 'close')
        """
        emoji = '🟢' if profit > 0 else '🔴'
        subject = f"{emoji} {pair} Trade {trade_type.capitalize()}: {profit:.2f}%"
        
        from datetime import datetime
        message = f"""
        <h3>{subject}</h3>
        <p>Trading pair: <strong>{pair}</strong></p>
        <p>Profit/Loss: <strong>{profit:.2f}%</strong></p>
        <p>Trade action: <strong>{trade_type.capitalize()}</strong></p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        return self.send_notification(message, subject)
    
    def send_drawdown_alert(self, drawdown: float, threshold: float) -> Dict[str, bool]:
        """
        Send maximum drawdown alert
        
        Args:
            drawdown: Current drawdown percentage
            threshold: Alert threshold percentage
        """
        subject = f"⚠️ Drawdown Alert: {drawdown:.2f}% exceeded threshold"
        
        from datetime import datetime
        message = f"""
        <h3>{subject}</h3>
        <p>Current drawdown: <strong>{drawdown:.2f}%</strong></p>
        <p>Threshold: <strong>{threshold:.2f}%</strong></p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Please review your trading strategy and consider adjusting parameters.</p>
        """
        
        return self.send_notification(message, subject)
    
    def send_system_resource_alert(self, resource: str, usage: float, threshold: float) -> Dict[str, bool]:
        """
        Send system resource usage alert
        
        Args:
            resource: Resource type (CPU, Memory, Disk, GPU)
            usage: Current usage percentage
            threshold: Alert threshold percentage
        """
        subject = f"⚙️ System Alert: {resource} usage at {usage:.2f}%"
        
        from datetime import datetime
        message = f"""
        <h3>{subject}</h3>
        <p>{resource} Usage: <strong>{usage:.2f}%</strong></p>
        <p>Threshold: <strong>{threshold:.2f}%</strong></p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Please check system resources and consider optimizing your application.</p>
        """
        
        return self.send_notification(message, subject)
    
    def send_trade_count_alert(self, count: int, threshold: int, timeframe: str = '24h') -> Dict[str, bool]:
        """
        Send trade count alert
        
        Args:
            count: Current trade count
            threshold: Alert threshold count
            timeframe: Time period (e.g., 1h, 24h, 7d)
        """
        subject = f"🔢 Trade Count Alert: {count} trades in {timeframe}"
        
        from datetime import datetime
        message = f"""
        <h3>{subject}</h3>
        <p>Number of trades: <strong>{count}</strong></p>
        <p>Timeframe: <strong>{timeframe}</strong></p>
        <p>Threshold: <strong>{threshold}</strong></p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        return self.send_notification(message, subject)
    
    def send_price_alert(self, pair: str, price: float, threshold: float, direction: str) -> Dict[str, bool]:
        """
        Send price alert
        
        Args:
            pair: Trading pair (e.g., BTC/USDT)
            price: Current price
            threshold: Alert threshold price
            direction: Price direction ('above', 'below')
        """
        emoji = '⬆️' if direction == 'above' else '⬇️'
        subject = f"{emoji} Price Alert: {pair} {direction} {threshold}"
        
        from datetime import datetime
        message = f"""
        <h3>{subject}</h3>
        <p>Trading pair: <strong>{pair}</strong></p>
        <p>Current price: <strong>{price:.2f}</strong></p>
        <p>Threshold: <strong>{threshold:.2f}</strong></p>
        <p>Direction: <strong>{direction}</strong></p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        return self.send_notification(message, subject)


# Create a singleton instance
notification_manager = NotificationManager()