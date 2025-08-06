import uuid
import time
import random
import string
from typing import Optional

class Player:
    def __init__(self, username: Optional[str] = None):
        self.uuid = str(uuid.uuid4())
        self.timestamp = int(time.time())
        self.username = username or f"guest-{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
        self.choice = None
        self.websocket = None
    
    def to_dict(self):
        return {
            "uuid": self.uuid,
            "username": self.username,
            "choice": self.choice,
            "timestamp": self.timestamp
        }
