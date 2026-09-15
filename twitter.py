"""Compatibility import: X/Twitter publishing now goes through Buffer."""
from buffer_client import send_tweet

__all__ = ["send_tweet"]
