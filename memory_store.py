import json
import os
from datetime import datetime
from typing import List, Dict, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationMemory:
    """Handles persistent conversation memory for users"""
    
    def __init__(self, user_id: str, storage_path: str = "conversations"):
        self.user_id = user_id
        self.storage_path = storage_path
        self.memory_file = os.path.join(storage_path, f"{user_id}_memory.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        logger.info(f"ConversationMemory initialized for user: {user_id}")
        logger.info(f"Memory file path: {os.path.abspath(self.memory_file)}")   
    
    def load_memory(self) -> List[Dict]:
        """Load all past conversations for this user"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} conversations from memory for user {self.user_id}")
                    return data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading memory file: {e}")
                return []
        else:
            logger.info(f"No existing memory file found for user {self.user_id}")
            return []
    
    def _conversation_exists(self, new_conversation: Dict, existing_conversations: List[Dict]) -> bool:
        """Check if a conversation already exists in memory"""
        new_conv_data = new_conversation.get('model_dump', lambda: new_conversation)()
        new_timestamp = new_conv_data.get('timestamp')
        new_messages = new_conv_data.get('messages', [])
        
        for existing_conv in existing_conversations:
            existing_timestamp = existing_conv.get('timestamp')
            existing_messages = existing_conv.get('messages', [])
            
            # Compare by timestamp and message count
            if (existing_timestamp == new_timestamp and 
                len(existing_messages) == len(new_messages)):
                return True
        
        return False
    
    def save_conversation(self, conversation: Union[Dict, object]) -> bool:
        """Save a conversation to memory - returns True if successful"""
        logger.info(f"save_conversation called for user {self.user_id}")
        
        try:
            memory = self.load_memory()
            
            # Convert conversation to dict if it's an object with model_dump method
            if hasattr(conversation, 'model_dump'):
                conversation_dict = conversation.model_dump()
            else:
                conversation_dict = conversation
            
            # Add timestamp if not present
            if 'timestamp' not in conversation_dict:
                conversation_dict['timestamp'] = datetime.now().isoformat()
            
            # Check if this conversation already exists
            if self._conversation_exists(conversation_dict, memory):
                logger.info("Conversation already exists in memory, skipping save")
                return True
            
            # If this is an update to the last conversation, replace it instead of adding
            if memory and self._is_conversation_update(conversation_dict, memory[-1]):
                logger.info("Updating last conversation instead of adding new one")
                memory[-1] = conversation_dict
            else:
                # Add new conversation
                memory.append(conversation_dict)
            
            # Save to file
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved conversation for user {self.user_id}")
            logger.info(f"File saved at: {os.path.abspath(self.memory_file)}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False
    
    def _is_conversation_update(self, new_conv: Dict, last_conv: Dict) -> bool:
        """Check if new conversation is an update to the last one"""
        # Simple heuristic: if timestamps are close and new conversation has more messages
        try:
            new_timestamp = datetime.fromisoformat(new_conv.get('timestamp', ''))
            last_timestamp = datetime.fromisoformat(last_conv.get('timestamp', ''))
            
            time_diff = abs((new_timestamp - last_timestamp).total_seconds())
            new_msg_count = len(new_conv.get('messages', []))
            last_msg_count = len(last_conv.get('messages', []))
            
            # If within 5 minutes and has more messages, consider it an update
            return time_diff < 300 and new_msg_count > last_msg_count
            
        except Exception:
            return False
    
    def get_recent_context(self, max_messages: int = 30) -> List[Dict]:
        """Get recent conversation context for the agent"""
        memory = self.load_memory()
        all_messages = []
        
        # Flatten all conversations into a single message list
        for conversation in memory:
            if "messages" in conversation:
                all_messages.extend(conversation["messages"])
        
        # Return the most recent messages
        recent_messages = all_messages[-max_messages:] if all_messages else []
        logger.info(f"Retrieved {len(recent_messages)} recent messages for user {self.user_id}")
        return recent_messages
    
    def get_conversation_count(self) -> int:
        """Get total number of saved conversations"""
        memory = self.load_memory()
        return len(memory)
    
    def clear_duplicates(self) -> int:
        """Remove duplicate conversations and return count of removed duplicates"""
        memory = self.load_memory()
        unique_conversations = []
        removed_count = 0
        
        for conv in memory:
            if not self._conversation_exists(conv, unique_conversations):
                unique_conversations.append(conv)
            else:
                removed_count += 1
        
        if removed_count > 0:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(unique_conversations, f, indent=2, ensure_ascii=False)
            logger.info(f"Removed {removed_count} duplicate conversations")
        
        return removed_count