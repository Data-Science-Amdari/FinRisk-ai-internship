"""
Velocity Rules Engine for Fraud Detection
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class VelocityRuleEngine:
    """
    Velocity-based rule engine for fraud detection
    """
    
    def __init__(self):
        """Initialize the velocity rule engine"""
        self.rules = {
            'amount_threshold': 10000,
            'frequency_threshold': 10,
            'time_window_hours': 24,
            'location_mismatch_weight': 0.8,
            'device_fingerprint_weight': 0.6,
            'velocity_amount_threshold': 5000,
            'velocity_frequency_threshold': 5,
            'velocity_time_window_hours': 1
        }
        
        # In-memory storage for velocity tracking (in production, use Redis/database)
        self.velocity_cache = {}
    
    def evaluate_rules(self, transaction_data: Dict[str, Any]) -> float:
        """
        Evaluate velocity rules for a transaction
        
        Args:
            transaction_data: Dictionary containing transaction data
            
        Returns:
            Velocity score between 0 and 1
        """
        try:
            customer_id = transaction_data.get('customer_id', '')
            amount = transaction_data.get('amount', 0)
            location = transaction_data.get('location', '')
            device_id = transaction_data.get('device_id', '')
            timestamp = transaction_data.get('timestamp', datetime.now())
            
            # Convert timestamp to datetime if it's a string
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Initialize velocity score
            velocity_score = 0.0
            rule_violations = []
            
            # Rule 1: High amount threshold
            if amount > self.rules['amount_threshold']:
                velocity_score += 0.3
                rule_violations.append(f"Amount {amount} exceeds threshold {self.rules['amount_threshold']}")
            
            # Rule 2: Frequency check
            frequency_score = self._check_frequency(customer_id, timestamp)
            if frequency_score > 0:
                velocity_score += frequency_score * 0.2
                rule_violations.append(f"High transaction frequency detected")
            
            # Rule 3: Location velocity
            location_score = self._check_location_velocity(customer_id, location, timestamp)
            if location_score > 0:
                velocity_score += location_score * self.rules['location_mismatch_weight']
                rule_violations.append(f"Location velocity violation")
            
            # Rule 4: Device velocity
            device_score = self._check_device_velocity(customer_id, device_id, timestamp)
            if device_score > 0:
                velocity_score += device_score * self.rules['device_fingerprint_weight']
                rule_violations.append(f"Device velocity violation")
            
            # Rule 5: Amount velocity
            amount_velocity_score = self._check_amount_velocity(customer_id, amount, timestamp)
            if amount_velocity_score > 0:
                velocity_score += amount_velocity_score * 0.3
                rule_violations.append(f"Amount velocity violation")
            
            # Update velocity cache
            self._update_velocity_cache(customer_id, transaction_data, timestamp)
            
            # Log rule violations
            if rule_violations:
                logger.info(
                    "Velocity rule violations detected",
                    customer_id=customer_id,
                    violations=rule_violations,
                    velocity_score=velocity_score
                )
            
            return min(velocity_score, 1.0)
            
        except Exception as e:
            logger.error("Error evaluating velocity rules", error=str(e), exc_info=True)
            return 0.0
    
    def _check_frequency(self, customer_id: str, timestamp: datetime) -> float:
        """
        Check transaction frequency for a customer
        
        Args:
            customer_id: Customer identifier
            timestamp: Current transaction timestamp
            
        Returns:
            Frequency score between 0 and 1
        """
        if not customer_id:
            return 0.0
        
        # Get recent transactions for this customer
        recent_transactions = self._get_recent_transactions(
            customer_id, 
            timestamp, 
            self.rules['time_window_hours']
        )
        
        if len(recent_transactions) > self.rules['frequency_threshold']:
            # Calculate frequency score based on how much over threshold
            excess = len(recent_transactions) - self.rules['frequency_threshold']
            return min(excess / self.rules['frequency_threshold'], 1.0)
        
        return 0.0
    
    def _check_location_velocity(self, customer_id: str, location: str, timestamp: datetime) -> float:
        """
        Check location velocity for a customer
        
        Args:
            customer_id: Customer identifier
            location: Current transaction location
            timestamp: Current transaction timestamp
            
        Returns:
            Location velocity score between 0 and 1
        """
        if not customer_id or not location:
            return 0.0
        
        # Get recent transactions for this customer
        recent_transactions = self._get_recent_transactions(
            customer_id, 
            timestamp, 
            self.rules['velocity_time_window_hours']
        )
        
        if len(recent_transactions) < 2:
            return 0.0
        
        # Check for location changes
        locations = [t.get('location', '') for t in recent_transactions]
        unique_locations = set(locations)
        
        if len(unique_locations) > 2:
            # Multiple location changes in short time
            return 0.8
        elif len(unique_locations) == 2 and location not in locations[:-1]:
            # New location in recent transactions
            return 0.6
        
        return 0.0
    
    def _check_device_velocity(self, customer_id: str, device_id: str, timestamp: datetime) -> float:
        """
        Check device velocity for a customer
        
        Args:
            customer_id: Customer identifier
            device_id: Current device identifier
            timestamp: Current transaction timestamp
            
        Returns:
            Device velocity score between 0 and 1
        """
        if not customer_id or not device_id:
            return 0.0
        
        # Get recent transactions for this customer
        recent_transactions = self._get_recent_transactions(
            customer_id, 
            timestamp, 
            self.rules['velocity_time_window_hours']
        )
        
        if len(recent_transactions) < 2:
            return 0.0
        
        # Check for device changes
        devices = [t.get('device_id', '') for t in recent_transactions]
        unique_devices = set(devices)
        
        if len(unique_devices) > 2:
            # Multiple device changes in short time
            return 0.9
        elif len(unique_devices) == 2 and device_id not in devices[:-1]:
            # New device in recent transactions
            return 0.7
        
        return 0.0
    
    def _check_amount_velocity(self, customer_id: str, amount: float, timestamp: datetime) -> float:
        """
        Check amount velocity for a customer
        
        Args:
            customer_id: Customer identifier
            amount: Current transaction amount
            timestamp: Current transaction timestamp
            
        Returns:
            Amount velocity score between 0 and 1
        """
        if not customer_id:
            return 0.0
        
        # Get recent transactions for this customer
        recent_transactions = self._get_recent_transactions(
            customer_id, 
            timestamp, 
            self.rules['velocity_time_window_hours']
        )
        
        if len(recent_transactions) < 2:
            return 0.0
        
        # Calculate total amount in recent transactions
        recent_amounts = [t.get('amount', 0) for t in recent_transactions]
        total_recent_amount = sum(recent_amounts)
        
        if total_recent_amount > self.rules['velocity_amount_threshold']:
            # High total amount in short time
            excess = total_recent_amount - self.rules['velocity_amount_threshold']
            return min(excess / self.rules['velocity_amount_threshold'], 1.0)
        
        return 0.0
    
    def _get_recent_transactions(self, customer_id: str, timestamp: datetime, hours: int) -> List[Dict[str, Any]]:
        """
        Get recent transactions for a customer
        
        Args:
            customer_id: Customer identifier
            timestamp: Current timestamp
            hours: Time window in hours
            
        Returns:
            List of recent transactions
        """
        if customer_id not in self.velocity_cache:
            return []
        
        cutoff_time = timestamp - timedelta(hours=hours)
        recent_transactions = []
        
        for transaction in self.velocity_cache[customer_id]:
            if transaction.get('timestamp', timestamp) >= cutoff_time:
                recent_transactions.append(transaction)
        
        return recent_transactions
    
    def _update_velocity_cache(self, customer_id: str, transaction_data: Dict[str, Any], timestamp: datetime):
        """
        Update velocity cache with new transaction
        
        Args:
            customer_id: Customer identifier
            transaction_data: Transaction data
            timestamp: Transaction timestamp
        """
        if not customer_id:
            return
        
        if customer_id not in self.velocity_cache:
            self.velocity_cache[customer_id] = []
        
        # Add transaction to cache
        transaction_record = {
            'timestamp': timestamp,
            'amount': transaction_data.get('amount', 0),
            'location': transaction_data.get('location', ''),
            'device_id': transaction_data.get('device_id', ''),
            'transaction_id': transaction_data.get('transaction_id', '')
        }
        
        self.velocity_cache[customer_id].append(transaction_record)
        
        # Keep only recent transactions (last 7 days)
        cutoff_time = timestamp - timedelta(days=7)
        self.velocity_cache[customer_id] = [
            t for t in self.velocity_cache[customer_id] 
            if t.get('timestamp', timestamp) >= cutoff_time
        ]
    
    def update_rules(self, new_rules: Dict[str, Any]):
        """
        Update velocity rules
        
        Args:
            new_rules: Dictionary containing new rule values
        """
        self.rules.update(new_rules)
        logger.info("Velocity rules updated", new_rules=new_rules)
    
    def get_rules(self) -> Dict[str, Any]:
        """
        Get current velocity rules
        
        Returns:
            Dictionary containing current rules
        """
        return self.rules.copy()
    
    def clear_cache(self, customer_id: str = None):
        """
        Clear velocity cache
        
        Args:
            customer_id: Specific customer ID to clear, or None to clear all
        """
        if customer_id:
            if customer_id in self.velocity_cache:
                del self.velocity_cache[customer_id]
                logger.info("Cleared velocity cache for customer", customer_id=customer_id)
        else:
            self.velocity_cache.clear()
            logger.info("Cleared all velocity cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get velocity cache statistics
        
        Returns:
            Dictionary containing cache statistics
        """
        total_customers = len(self.velocity_cache)
        total_transactions = sum(len(transactions) for transactions in self.velocity_cache.values())
        
        return {
            'total_customers': total_customers,
            'total_transactions': total_transactions,
            'avg_transactions_per_customer': total_transactions / max(total_customers, 1)
        }
