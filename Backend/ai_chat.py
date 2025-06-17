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
        
        # Define the initial context for Elden Ring specific responses
        initial_context = """
        You are an Elden Ring expert assistant. You specialize in:
        1. Elden Ring build recommendations (including stats, weapons, armor, talismans)
        2. Game mechanics and strategies
        3. Boss fight strategies
        4. Item locations and quest guides
        5. PvP and PvE strategies
        
        Only provide information related to Elden Ring. If asked about other games, politely remind the user that you are an Elden Ring specialist.
        When recommending builds, always include:
        - Required stats
        - Recommended weapons and their upgrade paths
        - Armor recommendations
        - Talisman choices
        - Spell/incantation recommendations if applicable
        - Basic combat strategy

        With your respond format:
        1. Use multiple paragraphs if the sentence is extensively long
        2. Use dotpoints and other listings if you need to
        """
        
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.chat = self.model.start_chat(history=[])
            # Set the initial context
            self.chat.send_message(initial_context)
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