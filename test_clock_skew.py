"""
Test clock skew detection functionality.
"""

import time

from session_helpers import get_server_timestamp, validate_client_timestamp


def test_valid_timestamp():
    """Test that a current timestamp is valid."""
    current_time = time.time()
    assert validate_client_timestamp(current_time) is True
    print("✓ Valid timestamp test passed")


def test_future_timestamp_within_tolerance():
    """Test that a slightly future timestamp (within tolerance) is valid."""
    future_time = time.time() + 3  # 3 seconds in the future
    assert validate_client_timestamp(future_time) is True
    print("✓ Future timestamp within tolerance test passed")


def test_past_timestamp_within_tolerance():
    """Test that a slightly past timestamp (within tolerance) is valid."""
    past_time = time.time() - 4  # 4 seconds in the past
    assert validate_client_timestamp(past_time) is True
    print("✓ Past timestamp within tolerance test passed")


def test_future_timestamp_beyond_tolerance():
    """Test that a future timestamp beyond tolerance is invalid."""
    future_time = time.time() + 10  # 10 seconds in the future (beyond 5s tolerance)
    assert validate_client_timestamp(future_time) is False
    print("✓ Future timestamp beyond tolerance test passed")


def test_past_timestamp_beyond_tolerance():
    """Test that a past timestamp beyond tolerance is invalid."""
    past_time = time.time() - 10  # 10 seconds in the past (beyond 5s tolerance)
    assert validate_client_timestamp(past_time) is False
    print("✓ Past timestamp beyond tolerance test passed")


def test_none_timestamp():
    """Test that None timestamp is invalid."""
    assert validate_client_timestamp(None) is False
    print("✓ None timestamp test passed")


def test_custom_tolerance():
    """Test custom tolerance parameter."""
    past_time = time.time() - 8  # 8 seconds in the past
    assert validate_client_timestamp(past_time, tolerance_seconds=10) is True
    assert validate_client_timestamp(past_time, tolerance_seconds=5) is False
    print("✓ Custom tolerance test passed")


def test_server_timestamp():
    """Test that server timestamp is a valid float."""
    timestamp = get_server_timestamp()
    assert isinstance(timestamp, float)
    assert timestamp > 0
    print("✓ Server timestamp test passed")


if __name__ == "__main__":
    print("Running clock skew detection tests...\n")

    test_valid_timestamp()
    test_future_timestamp_within_tolerance()
    test_past_timestamp_within_tolerance()
    test_future_timestamp_beyond_tolerance()
    test_past_timestamp_beyond_tolerance()
    test_none_timestamp()
    test_custom_tolerance()
    test_server_timestamp()

    print("\n✓ All clock skew detection tests passed!")
