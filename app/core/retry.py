import asyncio
import random
from typing import Callable, Any, Optional, Type
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions

def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt"""
    delay = config.base_delay * (config.exponential_base ** (attempt - 1))
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        # Add random jitter to prevent thundering herd
        jitter_range = delay * 0.1
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)

def retry_async(config: RetryConfig = None):
    """Decorator for async functions with retry logic"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {config.max_attempts} attempts",
                            exc_info=True
                        )
                        raise e
                    
                    delay = calculate_delay(attempt, config)
                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt}/{config.max_attempts}. "
                        f"Retrying in {delay:.2f} seconds. Error: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def retry_sync(config: RetryConfig = None):
    """Decorator for sync functions with retry logic"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {config.max_attempts} attempts",
                            exc_info=True
                        )
                        raise e
                    
                    delay = calculate_delay(attempt, config)
                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt}/{config.max_attempts}. "
                        f"Retrying in {delay:.2f} seconds. Error: {str(e)}"
                    )
                    
                    import time
                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

# Predefined retry configurations
LLM_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError, Exception)
)

VECTOR_DB_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    base_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError)
)

FILE_PROCESSING_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    base_delay=0.5,
    max_delay=5.0,
    exponential_base=2.0,
    jitter=False,
    retryable_exceptions=(IOError, OSError)
)