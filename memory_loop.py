import asyncio
import hashlib
import json
import time
import logging
from memory_store import ConversationMemory
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class MemoryExtractor:
    def __init__(self):
        # last_conversation_hash is no longer needed with the new logic
        self.saved_message_count = 0  # Tracks how many messages have been saved.

    def _serialize_for_hash(self, obj):
        """
        Recursively converts Pydantic objects or nested data into serializable dicts.
        This is necessary for consistency.
        """
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_hash(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_hash(item) for item in obj]
        else:
            return obj  # primitive types

    async def run(self, session):
        """
        The main loop that checks for and saves new conversations.
        """
        memory = ConversationMemory("Gaurav_22")

        while True:
            # Check for new messages every 1 second
            await asyncio.sleep(1)

            # Assuming the conversation history is a list of message objects
            # within the session object. Adjust 'session.chat_history' if needed.
            current_chat_history = session
            
            # This is the core logic: Compare the current count with the saved count.
            if len(current_chat_history) > self.saved_message_count:
                logging.info(f"{len(current_chat_history) - self.saved_message_count} new message(s) detected. Saving...")
                
                # Get a "slice" of the new messages that haven't been saved yet.
                new_messages = current_chat_history[self.saved_message_count:]
                
                for message in new_messages:
                    # Serialize the single message for saving
                    serialized_message = self._serialize_for_hash(message)
                    conversation_wrapper = {
                        "messages": [serialized_message],
                        "timestamp": time.time()
                    }
                    
                    success = memory.save_conversation(conversation_wrapper)
                    
                    if success:
                        logging.info(f"Saved new message with ID: {message.id}")
                    else:
                        logging.error(f"Failed to save message with ID: {message.id}")
                
                # After successfully saving all new messages, update the counter.
                self.saved_message_count = len(current_chat_history)
            
            else:
                pass
