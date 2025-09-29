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

    async def run(self, session, max_iterations=100):
        """
        Save conversation messages periodically.
        Args:
            session: The conversation session/history
            max_iterations: Maximum number of iterations to prevent infinite loop
        """
        memory = ConversationMemory("Prash_22")
        iteration_count = 0

        try:
            while iteration_count < max_iterations:
                # Check for new messages every 2 seconds (reduced frequency)
                await asyncio.sleep(2)
                iteration_count += 1

                # Handle different session types
                if hasattr(session, '__iter__') and not isinstance(session, (str, dict)):
                    current_chat_history = list(session)
                elif isinstance(session, list):
                    current_chat_history = session
                else:
                    logging.warning(f"Unexpected session type: {type(session)}")
                    current_chat_history = []
                
                # This is the core logic: Compare the current count with the saved count.
                if len(current_chat_history) > self.saved_message_count:
                    new_message_count = len(current_chat_history) - self.saved_message_count
                    logging.info(f"{new_message_count} new message(s) detected. Saving...")
                    
                    # Get a "slice" of the new messages that haven't been saved yet.
                    new_messages = current_chat_history[self.saved_message_count:]
                    
                    for i, message in enumerate(new_messages):
                        try:
                            # Serialize the single message for saving
                            serialized_message = self._serialize_for_hash(message)
                            conversation_wrapper = {
                                "messages": [serialized_message],
                                "timestamp": time.time(),
                                "message_index": self.saved_message_count + i
                            }
                            
                            success = memory.save_conversation(conversation_wrapper)
                            
                            if success:
                                # Check if message has ID attribute, handle gracefully if not
                                message_id = getattr(message, 'id', f'message_{self.saved_message_count + i}')
                                logging.info(f"Saved new message with ID: {message_id}")
                            else:
                                message_id = getattr(message, 'id', f'message_{self.saved_message_count + i}')
                                logging.error(f"Failed to save message with ID: {message_id}")
                        
                        except Exception as e:
                            logging.error(f"Error processing message {i}: {e}")
                            continue
                    
                    # After successfully saving all new messages, update the counter.
                    self.saved_message_count = len(current_chat_history)
                
                # Break if no new messages for a while (optional optimization)
                elif iteration_count > 10 and len(current_chat_history) == self.saved_message_count:
                    logging.info("No new messages detected for a while, pausing memory extractor")
                    break
        
        except Exception as e:
            logging.error(f"Error in memory extraction loop: {e}")
        
        finally:
            logging.info(f"Memory extractor finished after {iteration_count} iterations")
