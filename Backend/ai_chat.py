import os
import google.generativeai as genai
import logging
from dotenv import load_dotenv

class ChatBot:
    def __init__(self):
        load_dotenv()  # Load environment variables
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Google AI model: {str(e)}")
            
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_response(self, message):
        try:
            self.logger.info(f"Sending message to AI: {message}")
            response = self.chat.send_message(message)
            self.logger.info(f"Received response: {response.text}")
            return {
                'success': True,
                'message': response.text
            }
        except Exception as e:
            self.logger.error(f"Error in get_response: {str(e)}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }