"""
Redis client for caching and session management.
"""

import redis
import json
from typing import Optional, Any, Dict
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client for caching and session management."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self.logger = logger
        
        try:
            self.client = redis.from_url(self.redis_url)
            # Test connection
            self.client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None
    
    def cache_credit_decision(self, customer_id: str, decision_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache credit decision for a customer."""
        if not self.client:
            return False
        
        try:
            key = f"credit_decision:{customer_id}"
            self.client.setex(key, ttl, json.dumps(decision_data))
            self.logger.debug(f"Credit decision cached for customer: {customer_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error caching credit decision: {str(e)}")
            return False
    
    def get_cached_credit_decision(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get cached credit decision for a customer."""
        if not self.client:
            return None
        
        try:
            key = f"credit_decision:{customer_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached credit decision: {str(e)}")
            return None
    
    def cache_fraud_decision(self, transaction_id: str, decision_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache fraud decision for a transaction."""
        if not self.client:
            return False
        
        try:
            key = f"fraud_decision:{transaction_id}"
            self.client.setex(key, ttl, json.dumps(decision_data))
            self.logger.debug(f"Fraud decision cached for transaction: {transaction_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error caching fraud decision: {str(e)}")
            return False
    
    def get_cached_fraud_decision(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get cached fraud decision for a transaction."""
        if not self.client:
            return None
        
        try:
            key = f"fraud_decision:{transaction_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached fraud decision: {str(e)}")
            return None
    
    def increment_counter(self, key: str, ttl: int = 86400) -> Optional[int]:
        """Increment a counter with TTL."""
        if not self.client:
            return None
        
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl)
            result = pipe.execute()
            return result[0]
        except Exception as e:
            self.logger.error(f"Error incrementing counter: {str(e)}")
            return None
    
    def get_counter(self, key: str) -> Optional[int]:
        """Get counter value."""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            return int(value) if value else 0
        except Exception as e:
            self.logger.error(f"Error getting counter: {str(e)}")
            return None
