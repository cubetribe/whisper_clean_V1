"""
Event system for the Whisper Transcription Tool.
"""

import logging
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
import asyncio

from .logging_setup import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    """Types of events that can be published."""
    TRANSCRIPTION_STARTED = auto()
    TRANSCRIPTION_COMPLETED = auto()
    TRANSCRIPTION_FAILED = auto()
    EXTRACTION_STARTED = auto()
    EXTRACTION_COMPLETED = auto()
    EXTRACTION_FAILED = auto()
    PHONE_PROCESSING_STARTED = auto()
    PHONE_PROCESSING_COMPLETED = auto()
    PHONE_PROCESSING_FAILED = auto()
    MODEL_DOWNLOAD_STARTED = auto()
    MODEL_DOWNLOAD_COMPLETED = auto()
    MODEL_DOWNLOAD_FAILED = auto()
    PROGRESS_UPDATE = auto()
    CUSTOM = auto()  # For custom events like chunking


class Event:
    """Event object containing event type and data."""
    
    def __init__(self, event_type: EventType, data: Optional[Dict[str, Any]] = None):
        """
        Initialize an event.
        
        Args:
            event_type: Type of the event
            data: Event data
        """
        self.event_type = event_type
        self.data = data or {}
    
    def __str__(self) -> str:
        return f"Event({self.event_type.name}, {self.data})"


class EventBus:
    """Event bus for publishing and subscribing to events."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one event bus exists."""
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance
    
    def __init__(self):
        """Initialize the event bus."""
        # Already initialized in __new__
        pass
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        
        self._subscribers[event_type].add(callback)
        logger.debug(f"Subscribed to {event_type.name}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from {event_type.name}")
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        if event.event_type not in self._subscribers or not self._subscribers[event.event_type]:
            logger.debug(f"No subscribers for event type {event.event_type}, not publishing.")
            return
        
        logger.debug(f"Publishing {event}")
        
        loop = asyncio.get_event_loop() # Get the current event loop
        # Create a copy of the list in case a handler modifies the subscription list during iteration
        handlers = list(self._subscribers[event.event_type])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # If the handler is an async function, schedule it as a task
                    logger.debug(f"Scheduling async handler {handler.__name__} for event {event.event_type}")
                    loop.create_task(handler(event))
                else:
                    # If it's a regular function, call it directly
                    logger.debug(f"Calling sync handler {handler.__name__} for event {event.event_type}")
                    handler(event)
            except Exception as e:
                # Log the exception but continue notifying other handlers
                logger.error(f"Error executing handler {handler.__name__} for event {event.event_type}: {e}", exc_info=True)
    
    def get_subscribers(self, event_type: EventType) -> Set[Callable[[Event], None]]:
        """
        Get all subscribers for an event type.
        
        Args:
            event_type: Type of event
            
        Returns:
            Set of subscriber callbacks
        """
        return self._subscribers.get(event_type, set())


# Global event bus instance
event_bus = EventBus()


def subscribe(event_type: EventType, callback: Callable[[Event], None]) -> None:
    """
    Subscribe to an event type.
    
    Args:
        event_type: Type of event to subscribe to
        callback: Function to call when event is published
    """
    event_bus.subscribe(event_type, callback)


def unsubscribe(event_type: EventType, callback: Callable[[Event], None]) -> None:
    """
    Unsubscribe from an event type.
    
    Args:
        event_type: Type of event to unsubscribe from
        callback: Function to remove from subscribers
    """
    event_bus.unsubscribe(event_type, callback)


def publish(event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Publish an event.
    
    Args:
        event_type: Type of event to publish
        data: Event data
    """
    event = Event(event_type, data)
    event_bus.publish(event)
