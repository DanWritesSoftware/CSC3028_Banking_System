"""
Memory Manager Module

This module provides memory management utilities for tracking and optimizing memory usage.
It includes functionality for detecting memory leaks and managing object lifecycles.
"""

import gc
import logging
from typing import Dict, Any

import psutil

class MemoryManager:
    """A class for monitoring and managing memory usage in the application.
    
    Attributes:
        baseline (float): Initial memory usage in MB
        object_registry (Dict[str, Any]): Dictionary to track registered objects
    """

    def __init__(self):
        """Initialize the MemoryManager with baseline memory usage."""
        self.baseline = self._get_memory_usage()
        self.object_registry: Dict[str, Any] = {}

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB.
        
        Returns:
            float: Current memory usage in megabytes
        """
        return psutil.Process().memory_info().rss / (1024 * 1024)

    def check_for_leaks(self, threshold: float = 1.5) -> bool:
        """Check if memory usage exceeds threshold times baseline.
        
        Args:
            threshold (float): Multiplier for baseline memory usage
            
        Returns:
            bool: True if memory leak is detected
        """
        current = self._get_memory_usage()
        if current > self.baseline * threshold:
            logging.warning(
                "Memory leak detected! Current: %.2fMB, Baseline: %.2fMB",
                current,
                self.baseline
            )
            return True
        return False

    def register_object(self, name: str, obj: Any) -> None:
        """Track objects for memory management.
        
        Args:
            name (str): Identifier for the object
            obj (Any): The object to be tracked
        """
        self.object_registry[name] = obj

    def cleanup(self) -> None:
        """Force cleanup of registered objects and run garbage collection."""
        for name in list(self.object_registry.keys()):
            del self.object_registry[name]
        gc.collect()
