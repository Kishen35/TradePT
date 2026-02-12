
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatSession:
    """A chat session with history."""
    session_id: str
    user_id: int
    messages: List[ChatMessage] = field(default_factory=list)
    user_context: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session."""
        self.messages.append(ChatMessage(role=role, content=content))

    def get_history_text(self, max_messages: int = 10) -> str:
        """Get formatted conversation history."""
        recent = self.messages[-max_messages:]
        return "\n".join(
            f"{m.role.capitalize()}: {m.content}"
            for m in recent
        )

    def get_messages_for_api(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get messages formatted for API call."""
        recent = self.messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]

