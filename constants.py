"""
Application-wide constants.

This module defines constants used throughout the application
to avoid magic numbers and improve maintainability.
"""

# Time-related constants (in seconds)
DEFAULT_TIME_LIMIT_SECONDS = 600  # 10 minutes default
CLOCK_SKEW_TOLERANCE_SECONDS = 5  # Maximum acceptable time difference
SECONDS_PER_MINUTE = 60

# Timer warning thresholds (in seconds)
TIMER_DANGER_THRESHOLD = 60  # Red warning when <= 60 seconds
TIMER_WARNING_THRESHOLD = 180  # Yellow warning when <= 180 seconds

# Clock skew detection threshold (in seconds)
CLOCK_SKEW_LOG_THRESHOLD = 2  # Log warning if skew > 2 seconds

# UI constants
SEPARATOR_WIDTH = 80  # Width of separator lines in console output
