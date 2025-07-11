"""
User Data Management Tool for KDM Student Onboarding System

This tool manages user data storage in a single JSON file with concurrent access handling
and data completeness tracking. All agents use this tool to update and retrieve user information.
"""

import json
import os
import time
import platform
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Platform-specific imports for file locking
if platform.system() == "Windows":
    import msvcrt
else:
    import fcntl

# User data storage file
USER_DATA_FILE = "user_data.json"
USER_DATA_LOCK_FILE = "user_data.lock"

# Required user data schema - what needs to be collected for complete application
REQUIRED_USER_DATA = {
    "personal_info": {
        "full_name": None,
        "phone_number": None,  # Primary identifier
        "email": None,
        "date_of_birth": None,
        "address": None
    },
    "academic_background": {
        "highest_qualification": None,
        "institution": None,
        "graduation_year": None,
        "percentage_cgpa": None,
        "field_of_study": None
    },
    "program_preferences": {
        "interested_programs": [],
        "preferred_start_date": None,
        "study_mode": None,  # full-time/part-time/online
        "budget_range": None
    },
    "eligibility_status": {
        "programs_eligible_for": [],
        "documents_verified": False,
        "eligibility_checked": False
    },
    "application_status": {
        "current_stage": "data_collection",  # data_collection, eligibility_check, program_selection, fee_calculation, registration
        "documents_submitted": [],
        "payment_status": "pending"
    }
}


class UserDataManager:
    """Manages user data with concurrent access and completeness tracking."""
    
    def __init__(self):
        self.data_file = USER_DATA_FILE
        self.lock_file = USER_DATA_LOCK_FILE
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self):
        """Ensure the user data file exists."""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _acquire_lock(self, timeout: int = 5) -> Optional[object]:
        """Acquire file lock with timeout (cross-platform)."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                lock_file = open(self.lock_file, 'w')
                
                if platform.system() == "Windows":
                    # Windows file locking using msvcrt
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    # Unix/Linux file locking using fcntl
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                return lock_file
            except (IOError, OSError):
                if 'lock_file' in locals():
                    lock_file.close()
                time.sleep(0.1)
        return None
    
    def _release_lock(self, lock_file):
        """Release file lock (cross-platform)."""
        if lock_file:
            try:
                if platform.system() == "Windows":
                    # Windows file unlocking
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    # Unix/Linux file unlocking
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except (IOError, OSError):
                pass  # Best effort release
            
            lock_file.close()
            try:
                os.remove(self.lock_file)
            except OSError:
                pass  # Lock file might already be removed
    
    def _load_data(self) -> Dict[str, Any]:
        """Load user data from file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data: Dict[str, Any]):
        """Save user data to file."""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_user(self, phone_number: str) -> Dict[str, Any]:
        """Initialize a new user with the required data structure."""
        user_data = {}
        
        # Deep copy the required structure
        def deep_copy_structure(obj):
            if isinstance(obj, dict):
                return {k: deep_copy_structure(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return []
            else:
                return obj
        
        user_data = deep_copy_structure(REQUIRED_USER_DATA)
        
        # Set the phone number as it's the primary identifier
        user_data["personal_info"]["phone_number"] = phone_number
        
        # Add metadata
        user_data["_metadata"] = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "version": 1,
            "last_updated_by": "system"
        }
        
        return user_data
    
    def _calculate_completeness(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data completeness score and identify missing fields."""
        def check_completeness(required, actual, path=""):
            total_fields = 0
            completed_fields = 0
            missing_fields = []
            
            for key, value in required.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, dict):
                    if key in actual and isinstance(actual[key], dict):
                        sub_total, sub_completed, sub_missing = check_completeness(
                            value, actual[key], current_path
                        )
                        total_fields += sub_total
                        completed_fields += sub_completed
                        missing_fields.extend(sub_missing)
                    else:
                        # Entire section missing
                        sub_total, _, sub_missing = check_completeness(value, {}, current_path)
                        total_fields += sub_total
                        missing_fields.extend(sub_missing)
                elif isinstance(value, list):
                    total_fields += 1
                    if key in actual and actual[key] and len(actual[key]) > 0:
                        completed_fields += 1
                    else:
                        missing_fields.append(current_path)
                else:
                    total_fields += 1
                    if key in actual and actual[key] is not None and actual[key] != "":
                        completed_fields += 1
                    else:
                        missing_fields.append(current_path)
            
            return total_fields, completed_fields, missing_fields
        
        # Calculate completeness excluding metadata
        user_data_copy = {k: v for k, v in user_data.items() if not k.startswith('_')}
        total, completed, missing = check_completeness(REQUIRED_USER_DATA, user_data_copy)
        
        completeness_score = completed / total if total > 0 else 0
        
        return {
            "completeness_score": round(completeness_score, 2),
            "total_fields": total,
            "completed_fields": completed,
            "missing_fields": missing
        }
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set a value in nested dictionary using dot notation."""
        keys = field_path.split('.')
        current = data
        
        # Navigate to the parent of the target field
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def update_user_data(
        self, 
        phone_number: str, 
        field_path: str, 
        value: Any, 
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Update user data for a specific field.
        
        Args:
            phone_number: User's phone number (primary identifier)
            field_path: Dot notation path to the field (e.g., "personal_info.full_name")
            value: Value to set
            agent_id: ID of the agent making the update
            
        Returns:
            Dict with update status and completeness information
        """
        # Acquire file lock
        lock_file = self._acquire_lock()
        if not lock_file:
            return {
                "success": False,
                "error": "Could not acquire file lock",
                "completeness_score": 0,
                "missing_fields": []
            }
        
        try:
            # Load current data
            all_data = self._load_data()
            
            # Initialize user if not exists
            if phone_number not in all_data:
                all_data[phone_number] = self._initialize_user(phone_number)
            
            user_data = all_data[phone_number]
            
            # Update the specific field
            self._set_nested_value(user_data, field_path, value)
            
            # Update metadata
            user_data["_metadata"]["last_updated"] = datetime.now().isoformat()
            user_data["_metadata"]["last_updated_by"] = agent_id
            user_data["_metadata"]["version"] += 1
            
            # Save data
            self._save_data(all_data)
            
            # Calculate completeness
            completeness_info = self._calculate_completeness(user_data)
            
            return {
                "success": True,
                "user_exists": True,
                **completeness_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "completeness_score": 0,
                "missing_fields": []
            }
        finally:
            self._release_lock(lock_file)
    
    def get_user_data(self, phone_number: str) -> Dict[str, Any]:
        """
        Get complete user data.
        
        Args:
            phone_number: User's phone number
            
        Returns:
            Dict with user data and completeness information
        """
        lock_file = self._acquire_lock()
        if not lock_file:
            return {
                "success": False,
                "error": "Could not acquire file lock",
                "user_data": None
            }
        
        try:
            all_data = self._load_data()
            
            if phone_number not in all_data:
                return {
                    "success": True,
                    "user_exists": False,
                    "user_data": None,
                    "completeness_score": 0,
                    "missing_fields": list(REQUIRED_USER_DATA.keys())
                }
            
            user_data = all_data[phone_number]
            completeness_info = self._calculate_completeness(user_data)
            
            return {
                "success": True,
                "user_exists": True,
                "user_data": user_data,
                **completeness_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_data": None
            }
        finally:
            self._release_lock(lock_file)


# Global instance
_user_data_manager = UserDataManager()


# ADK-compatible functions for agents
def update_user_data(phone_number: str, field_path: str, value: str, agent_id: str) -> str:
    """
    Update user data for a specific field.
    
    This tool should be used whenever an agent collects or updates user information.
    It handles concurrent access and tracks data completeness automatically.
    
    Args:
        phone_number: User's phone number (primary identifier)  
        field_path: Dot notation path to field (e.g., "personal_info.full_name", "academic_background.highest_qualification")
        value: Value to set for the field
        agent_id: Your agent identifier for tracking
        
    Returns:
        JSON string with update status and completeness information
    """
    result = _user_data_manager.update_user_data(phone_number, field_path, value, agent_id)
    return json.dumps(result)


def get_user_data(phone_number: str) -> str:
    """
    Retrieve complete user data and completeness status.
    
    Use this to check what information is already collected and what's missing
    before deciding on next steps or routing to other agents.
    
    Args:
        phone_number: User's phone number (primary identifier)
        
    Returns:
        JSON string with user data and completeness information
    """
    result = _user_data_manager.get_user_data(phone_number)
    return json.dumps(result)


def get_required_data_schema() -> str:
    """
    Get the complete schema of required user data.
    
    Use this to understand what information needs to be collected for a complete application.
    
    Returns:
        JSON string with the required data structure
    """
    return json.dumps(REQUIRED_USER_DATA, indent=2) 