"""
Retry handler module for the RAG ingestion pipeline.
Handles network errors and API rate limiting with exponential backoff.
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Any
import requests
from requests.exceptions import RequestException


logger = logging.getLogger(__name__)


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (RequestException, ConnectionError)
):
    """
    Decorator to retry a function on specific exceptions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e

                    logger.warning(f"Attempt {retries} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None  # This should not be reached due to the exception above
        return wrapper
    return decorator


class RetryHandler:
    """
    A class to handle retry logic for network operations.
    """

    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with retry logic.

        Args:
            operation: The function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the operation if successful

        Raises:
            The last exception if all retries fail
        """
        retries = 0
        delay = self.initial_delay

        while retries < self.max_retries:
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries >= self.max_retries:
                    logger.error(f"Operation failed after {self.max_retries} retries: {str(e)}")
                    raise e

                logger.warning(f"Attempt {retries} failed: {str(e)}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= self.backoff_factor

        # This should not be reached
        raise RuntimeError("Retry logic error: reached end of retry loop without exception")


# Example usage
if __name__ == "__main__":
    # Example of how to use the retry decorator
    @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0)
    def example_network_call(url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text