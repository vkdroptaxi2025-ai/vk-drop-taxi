# Phase 2 & 3: Driver Operations & Smart Dispatch Algorithm
# This file contains all the business logic for the intelligent taxi dispatch system

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
import math

# ==================== PHASE 2 & 3 MODELS ====================

class DriverDutyStatus(BaseModel):
    duty_on: bool
    go_home_mode: bool = False
    home_location: Optional[dict] = None  # {latitude, longitude, address}

class DriverStatusEnum(str, Enum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    WAITING = "waiting"
    OFFLINE = "offline"
    GOING_HOME = "going_home"

class AssignmentMode(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"

# ==================== SMART MATCHING LOGIC ====================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in KM using Haversine formula"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)

def is_driver_moving_towards(driver_loc: dict, pickup_loc: dict, drop_loc: dict) -> bool:
    """Check if driver's current/end location is moving towards pickup"""
    # If driver is closer to pickup than drop, they're moving towards pickup
    dist_to_pickup = calculate_distance(
        driver_loc['latitude'], driver_loc['longitude'],
        pickup_loc['latitude'], pickup_loc['longitude']
    )
    
    dist_to_drop = calculate_distance(
        driver_loc['latitude'], driver_loc['longitude'],
        drop_loc['latitude'], drop_loc['longitude']
    )
    
    return dist_to_pickup < dist_to_drop

def calculate_matching_score(driver: dict, booking: dict) -> float:
    """
    Calculate matching score for driver-booking pair
    Score based on:
    - Distance to pickup (40%)
    - Driver seniority/total trips (30%)
    - Continuous trips count (20%)
    - Time availability (10%)
    
    Returns: Score between 0-100 (higher is better)
    """
    score = 0
    
    # 1. Distance score (40 points max)
    driver_location = driver.get('current_location') or driver.get('last_trip_end_location')
    if driver_location:
        distance = calculate_distance(
            driver_location['latitude'], driver_location['longitude'],
            booking['pickup']['latitude'], booking['pickup']['longitude']
        )
        
        # Within 5km: 40 points, 10km: 30 points, 20km: 20 points, 40km: 10 points
        if distance <= 5:
            score += 40
        elif distance <= 10:
            score += 30
        elif distance <= 20:
            score += 20
        elif distance <= 40:
            score += 10
        else:
            score += 0  # Too far
    
    # 2. Seniority score (30 points max)
    total_trips = driver.get('total_trips', 0)
    if total_trips >= 500:
        score += 30
    elif total_trips >= 100:
        score += 25
    elif total_trips >= 50:
        score += 20
    elif total_trips >= 10:
        score += 15
    else:
        score += 10
    
    # 3. Continuous trips score (20 points max)
    continuous_trips = driver.get('continuous_trips_count', 0)
    if continuous_trips == 0:
        score += 20  # Priority to drivers who haven't had trips yet
    elif continuous_trips == 1:
        score += 15  # Need one more for 2-trip rule
    else:
        score += 5  # Already completed 2 trips
    
    # 4. Time availability score (10 points max)
    last_trip_time = driver.get('last_trip_end_time')
    if last_trip_time:
        time_diff = datetime.utcnow() - datetime.fromisoformat(last_trip_time.replace('Z', '+00:00'))
        if time_diff.total_seconds() / 3600 < 0.5:  # Less than 30 min
            score += 10
        elif time_diff.total_seconds() / 3600 < 1:  # Less than 1 hour
            score += 7
        else:
            score += 3
    else:
        score += 10  # Fresh driver
    
    return round(score, 2)

# ==================== DRIVER ELIGIBILITY CHECKS ====================

async def check_driver_eligibility(driver: dict, wallet_balance: float) -> dict:
    """
    Check if driver is eligible to receive bookings
    Returns: {eligible: bool, reason: str}
    """
    # Check approval status
    if driver.get('approval_status') != 'approved':
        return {
            'eligible': False,
            'reason': 'Driver not approved yet'
        }
    
    # Check wallet balance (minimum ₹1000)
    if wallet_balance < 1000:
        return {
            'eligible': False,
            'reason': 'Wallet balance below ₹1000. Please recharge.'
        }
    
    # Check duty status
    if not driver.get('duty_on'):
        return {
            'eligible': False,
            'reason': 'Driver is off duty'
        }
    
    # Check online status
    if not driver.get('is_online'):
        return {
            'eligible': False,
            'reason': 'Driver is offline'
        }
    
    # Check document expiry
    expiry_data = driver.get('document_expiry', {})
    today = datetime.now().date()
    
    for doc_type, expiry_str in expiry_data.items():
        try:
            expiry_date = datetime.fromisoformat(expiry_str).date()
            if expiry_date < today:
                return {
                    'eligible': False,
                    'reason': f'{doc_type.replace("_", " ").title()} has expired'
                }
        except:
            pass
    
    # Check if driver is already on a trip
    if driver.get('driver_status') == 'on_trip':
        return {
            'eligible': False,
            'reason': 'Driver is currently on a trip'
        }
    
    return {
        'eligible': True,
        'reason': 'Driver is eligible'
    }

# ==================== GO HOME FEATURE ====================

def is_trip_towards_home(pickup: dict, drop: dict, home: dict, threshold_km: float = 20) -> bool:
    """
    Check if trip drop location is towards driver's home
    Returns True if drop is closer to home than pickup
    """
    if not home:
        return False
    
    pickup_to_home = calculate_distance(
        pickup['latitude'], pickup['longitude'],
        home['latitude'], home['longitude']
    )
    
    drop_to_home = calculate_distance(
        drop['latitude'], drop['longitude'],
        home['latitude'], home['longitude']
    )
    
    # Drop should be significantly closer to home (at least threshold_km closer)
    return (pickup_to_home - drop_to_home) >= threshold_km

# ==================== QUEUE MANAGEMENT ====================

def calculate_queue_priority(driver: dict) -> int:
    """
    Calculate queue priority for driver
    Priority rules:
    1. Drivers who completed 2 trips (continuous_trips_count >= 2)
    2. Senior drivers (total_trips)
    3. Waiting time
    
    Returns: Priority score (higher = higher priority)
    """
    priority = 0
    
    # Rule 1: Completed 2 trips (1000 points)
    if driver.get('continuous_trips_count', 0) >= 2:
        priority += 1000
    
    # Rule 2: Seniority (up to 500 points)
    total_trips = driver.get('total_trips', 0)
    priority += min(total_trips, 500)
    
    # Rule 3: Waiting time (up to 100 points)
    # Assuming queue_entry_time exists
    queue_time = driver.get('queue_entry_time')
    if queue_time:
        wait_minutes = (datetime.utcnow() - datetime.fromisoformat(queue_time.replace('Z', '+00:00'))).total_seconds() / 60
        priority += min(int(wait_minutes), 100)
    
    return priority

# ==================== 2-TRIP CONTINUITY RULE ====================

async def check_and_update_trip_continuity(db, driver_id: str, booking_status: str):
    """
    Manage 2-trip continuity rule
    - Increment continuous_trips_count when booking is accepted
    - Move to queue after 2 trips
    - Reset when driver completes queue cycle
    """
    driver = await db.drivers.find_one({'driver_id': driver_id})
    if not driver:
        return
    
    continuous_trips = driver.get('continuous_trips_count', 0)
    
    if booking_status == 'accepted':
        # Increment continuous trips
        new_count = continuous_trips + 1
        
        update_data = {
            'continuous_trips_count': new_count
        }
        
        # After 2 trips, move to queue
        if new_count >= 2:
            update_data['in_queue'] = True
            update_data['queue_entry_time'] = datetime.utcnow().isoformat()
            update_data['driver_status'] = 'waiting'
        
        await db.drivers.update_one(
            {'driver_id': driver_id},
            {'$set': update_data}
        )
    
    elif booking_status == 'completed':
        # Update last trip end location and time
        await db.drivers.update_one(
            {'driver_id': driver_id},
            {'$set': {
                'last_trip_end_time': datetime.utcnow().isoformat(),
                'driver_status': 'available'
            }}
        )

# ==================== TIME-BASED ASSIGNMENT ====================

def can_driver_reach_in_time(driver: dict, pickup: dict, buffer_hours: float = 1.0) -> bool:
    """
    Check if driver can reach pickup within buffer time
    Assumes average speed of 30 km/h in city
    """
    driver_location = driver.get('current_location') or driver.get('last_trip_end_location')
    if not driver_location:
        return False
    
    distance = calculate_distance(
        driver_location['latitude'], driver_location['longitude'],
        pickup['latitude'], pickup['longitude']
    )
    
    # Assuming 30 km/h average speed
    time_needed_hours = distance / 30
    
    return time_needed_hours <= buffer_hours

# Export all functions for use in main server
__all__ = [
    'calculate_distance',
    'calculate_matching_score',
    'check_driver_eligibility',
    'is_trip_towards_home',
    'calculate_queue_priority',
    'check_and_update_trip_continuity',
    'can_driver_reach_in_time',
    'is_driver_moving_towards',
]
