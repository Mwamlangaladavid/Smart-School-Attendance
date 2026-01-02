import requests
import json
import uuid
import logging

logger = logging.getLogger(__name__)

class NextSMSService:
    """NextSMS API service following exact API patterns"""
    
    BASE_URL = "https://messaging-service.co.tz/api/sms/v1"
    AUTHORIZATION = "Basic ZGF2aWUzNjA6a2lueW9uZ2FAMjI="
    SENDER_ID = "S Security"
    
    @classmethod
    def send_single_sms(cls, phone_number, message, reference=None):
        """Send single SMS using exact NextSMS API pattern"""
        
        # Generate reference if not provided
        if not reference:
            reference = str(uuid.uuid4())[:10]
        
        # Clean phone number (ensure it starts with country code)
        original_phone = phone_number
        if not phone_number.startswith('255'):
            phone_number = '255' + phone_number.lstrip('0+')
        
        logger.info(f"Original phone: {original_phone}, Cleaned phone: {phone_number}")
        
        url = f"{cls.BASE_URL}/text/single"
        
        payload = json.dumps({
            "from": cls.SENDER_ID,
            "to": phone_number,
            "text": message,
            "reference": reference
        })
        
        headers = {
            'Authorization': cls.AUTHORIZATION,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        logger.info(f"SMS API URL: {url}")
        logger.info(f"SMS Payload: {payload}")
        logger.info(f"SMS Headers: {headers}")
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
            
            logger.info(f"SMS API Response Status: {response.status_code}")
            logger.info(f"SMS API Response Text: {response.text}")
            logger.info(f"SMS API Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"SMS sent successfully to {phone_number}, Reference: {reference}")
                    return {
                        'success': True,
                        'reference': reference,
                        'response': result,
                        'status_code': response.status_code
                    }
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response: {response.text}")
                    return {
                        'success': False,
                        'error': f"Invalid JSON response: {response.text}",
                        'status_code': response.status_code,
                        'reference': reference
                    }
            else:
                logger.error(f"SMS sending failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'status_code': response.status_code,
                    'reference': reference
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"SMS request timeout for {phone_number}")
            return {
                'success': False,
                'error': "Request timeout",
                'reference': reference
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'reference': reference
            }
    
    @classmethod
    def send_test_sms(cls, phone_number, message, reference=None):
        """Send test SMS using NextSMS test endpoint"""
        
        if not reference:
            reference = str(uuid.uuid4())[:10]
        
        if not phone_number.startswith('255'):
            phone_number = '255' + phone_number.lstrip('0+')
        
        url = f"{cls.BASE_URL}/test/text/single"
        
        payload = json.dumps({
            "from": cls.SENDER_ID,
            "to": phone_number,
            "text": message,
            "reference": reference
        })
        
        headers = {
            'Authorization': cls.AUTHORIZATION,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
            
            logger.info(f"Test SMS API Response: {response.status_code} - {response.text}")
            
            return {
                'success': response.status_code == 200,
                'reference': reference,
                'response': response.json() if response.status_code == 200 else response.text,
                'status_code': response.status_code
            }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send test SMS to {phone_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'reference': reference
            }

# Create an instance of the service for easy importing
nextsms_service = NextSMSService()
