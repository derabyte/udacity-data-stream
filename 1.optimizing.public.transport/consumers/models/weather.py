"""Contains functionality related to Weather"""
import logging
import json

logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        logger.info("STATUS: Commence weather message processing")

        weather_message = json.loads(message.value())
        try:
            self.temperature = weather_message.get('temperature')
            self.status = weather_message.get('status')
        except Exception as e:
            logger.error(f'ERROR: Unable to process weather message {e}')
