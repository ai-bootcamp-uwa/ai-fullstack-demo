"""Storage layer for chat persistence."""

from .base import ChatStorage
from .file_storage import FileBasedChatStorage

__all__ = [
    "ChatStorage",
    "FileBasedChatStorage"
] 