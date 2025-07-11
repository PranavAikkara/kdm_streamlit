"""
Logging Configuration for KDM Student Onboarding System
=======================================================

This module configures logging for the KDM system to track agent activity,
API requests, document processing, and system events. Logs are saved to
the 'log' folder with filename 'kdm.log'.

Main Purpose: Track which agent is active and monitor system behavior.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Optional


class AgentActivityLogger:
    """Custom logger specifically for tracking agent activity."""
    
    def __init__(self, name: str = "kdm_system"):
        self.logger = logging.getLogger(name)
        self.current_agent = None
        self.session_context = {}
    
    def set_active_agent(self, agent_name: str, session_id: str = None, user_id: str = None):
        """Set the currently active agent."""
        self.current_agent = agent_name
        self.session_context = {
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(
            f"AGENT_ACTIVATED: {agent_name}",
            extra={
                "agent_name": agent_name,
                "session_id": session_id,
                "user_id": user_id,
                "event_type": "agent_activation"
            }
        )
    
    def log_agent_response(self, agent_name: str, message: str, response: str, 
                          processing_time: float = None):
        """Log agent response with context."""
        self.logger.info(
            f"AGENT_RESPONSE: {agent_name} responded",
            extra={
                "agent_name": agent_name,
                "message_length": len(message),
                "response_length": len(response),
                "processing_time": processing_time,
                "event_type": "agent_response",
                **self.session_context
            }
        )
    
    def log_agent_handoff(self, from_agent: str, to_agent: str, reason: str = None):
        """Log when control is handed off between agents."""
        self.logger.info(
            f"AGENT_HANDOFF: {from_agent} → {to_agent}",
            extra={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason,
                "event_type": "agent_handoff",
                **self.session_context
            }
        )
        
        # Update current agent
        self.current_agent = to_agent
    
    def log_document_processing(self, filename: str, file_type: str, 
                               processing_agent: str = None):
        """Log document processing activity."""
        self.logger.info(
            f"DOCUMENT_PROCESSED: {filename}",
            extra={
                "filename": filename,
                "file_type": file_type,
                "processing_agent": processing_agent or self.current_agent,
                "event_type": "document_processing",
                **self.session_context
            }
        )
    
    def log_api_request(self, endpoint: str, method: str, status_code: int = None):
        """Log API requests."""
        self.logger.info(
            f"API_REQUEST: {method} {endpoint}",
            extra={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "event_type": "api_request",
                **self.session_context
            }
        )
    
    def log_error(self, error_message: str, agent_name: str = None, 
                  error_type: str = None):
        """Log errors with agent context."""
        self.logger.error(
            f"ERROR: {error_message}",
            extra={
                "error_message": error_message,
                "agent_name": agent_name or self.current_agent,
                "error_type": error_type,
                "event_type": "error",
                **self.session_context
            }
        )


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if available
        if hasattr(record, 'agent_name'):
            log_entry["agent_name"] = record.agent_name
        
        if hasattr(record, 'event_type'):
            log_entry["event_type"] = record.event_type
        
        if hasattr(record, 'session_id'):
            log_entry["session_id"] = record.session_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # Add any other extra attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 'funcName',
                          'created', 'msecs', 'relativeCreated', 'thread',
                          'threadName', 'processName', 'process', 'getMessage',
                          'message', 'agent_name', 'event_type', 'session_id', 'user_id']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO", max_file_size: int = 10 * 1024 * 1024, 
                  backup_count: int = 5) -> AgentActivityLogger:
    """
    Set up logging configuration for the KDM system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_file_size: Maximum size of log file in bytes (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        
    Returns:
        AgentActivityLogger instance for tracking agent activity
    """
    
    # Create log directory if it doesn't exist
    log_dir = Path("log")
    log_dir.mkdir(exist_ok=True)
    
    # Log file path
    log_file = log_dir / "kdm.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    # JSON formatter for file logs (structured)
    json_formatter = JSONFormatter()
    file_handler.setFormatter(json_formatter)
    
    # Simple formatter for console logs (human-readable)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create and configure agent activity logger
    agent_logger = AgentActivityLogger("kdm_agents")
    
    # Log system startup
    agent_logger.logger.info(
        "KDM Logging System Initialized",
        extra={
            "log_file": str(log_file),
            "log_level": log_level,
            "max_file_size": max_file_size,
            "backup_count": backup_count,
            "event_type": "system_startup"
        }
    )
    
    return agent_logger


def get_agent_logger() -> AgentActivityLogger:
    """Get the configured agent activity logger."""
    return AgentActivityLogger("kdm_agents")


# Configure specific loggers for different components
def configure_component_loggers():
    """Configure loggers for specific system components."""
    
    # FastAPI/Routes logger
    routes_logger = logging.getLogger("kdm_routes")
    routes_logger.setLevel(logging.INFO)
    
    # Streamlit/App logger  
    app_logger = logging.getLogger("kdm_app")
    app_logger.setLevel(logging.INFO)
    
    # Document processing logger
    docs_logger = logging.getLogger("kdm_documents")
    docs_logger.setLevel(logging.INFO)
    
    # Agent logger
    agent_logger = logging.getLogger("kdm_agents")
    agent_logger.setLevel(logging.INFO)
    
    return {
        "routes": routes_logger,
        "app": app_logger,
        "documents": docs_logger,
        "agents": agent_logger
    }


# Agent name constants for consistency
class AgentNames:
    """Constants for agent names to ensure consistency across logging."""
    ORCHESTRATOR = "orchestrator"
    DOCUMENT_DIGITISER = "document_digitiser"
    ELIGIBILITY_CHECKER = "eligibility_checker"
    PROGRAM_RECOMMENDER = "program_recommender"
    FEE_CALCULATOR = "fee_calculator"
    REGISTRATION_MANAGER = "registration_manager"
    SMART_FAQ = "smart_faq"
    STUDENT_PROFILER = "student_profiler"


# Usage example and initialization
if __name__ == "__main__":
    # Initialize logging
    agent_logger = setup_logging(log_level="INFO")
    
    # Example usage
    agent_logger.set_active_agent(
        AgentNames.ORCHESTRATOR, 
        session_id="session-12345", 
        user_id="user-67890"
    )
    
    agent_logger.log_agent_response(
        AgentNames.ORCHESTRATOR,
        "Hello, I need help with programs",
        "I can help you find the perfect program!",
        processing_time=0.5
    )
    
    agent_logger.log_agent_handoff(
        AgentNames.ORCHESTRATOR,
        AgentNames.PROGRAM_RECOMMENDER,
        "User requesting program information"
    )
    
    agent_logger.log_document_processing(
        "transcript.pdf",
        "pdf",
        AgentNames.DOCUMENT_DIGITISER
    )
    
    print("Logging test completed. Check log/kdm.log for output.") 