#!/usr/bin/env python3
"""
Standalone script to validate questions data.

This script validates the questions.json file against the schema
and performs additional semantic checks.

Usage:
    python validate_questions.py
"""

import logging
import sys
from pathlib import Path

from constants import SEPARATOR_WIDTH
from question_validator import (
    QuestionValidationError,
    get_validation_summary,
    validate_questions_file,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main validation function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Get file paths
    base_dir = Path(__file__).parent
    questions_file = base_dir / "data" / "questions.json"
    schema_file = base_dir / "data" / "questions_schema.json"

    separator = "=" * SEPARATOR_WIDTH
    logger.info(separator)
    logger.info("Questions Data Validation")
    logger.info(separator)
    logger.info("Questions file: %s", questions_file)
    logger.info("Schema file: %s", schema_file)
    logger.info("")

    try:
        # Validate questions
        logger.info("Validating questions...")
        questions = validate_questions_file(questions_file, schema_file, strict=True)

        # Get summary
        summary = get_validation_summary(questions)

        logger.info("✓ Validation successful!")
        logger.info("")
        logger.info("Summary:")
        logger.info("  Total questions: %d", summary["total_questions"])
        logger.info("  Categories: %d", summary["category_count"])
        logger.info("")
        logger.info("Questions per category:")
        for category, count in sorted(summary["categories"].items()):
            logger.info("  %s: %d", category, count)

        logger.info("")
        logger.info(separator)
        logger.info("All checks passed!")
        logger.info(separator)
        return 0

    except QuestionValidationError as e:
        logger.error("✗ Validation failed!")
        logger.error("")
        logger.error("%s", str(e))
        logger.error("")
        logger.error(separator)
        logger.error("Please fix the errors above and try again.")
        logger.error(separator)
        return 1

    except FileNotFoundError as e:
        logger.error("✗ File not found error!")
        logger.error("")
        logger.error("Error: %s", e)
        logger.error("Please ensure both questions.json and questions_schema.json exist.")
        logger.error("")
        logger.error(separator)
        return 1

    except (ValueError, TypeError) as e:
        logger.error("✗ Data format error!")
        logger.error("")
        logger.error("Error: %s", e)
        logger.error("Please check the JSON file format and data types.")
        logger.error("")
        logger.error(separator)
        return 1

    except OSError as e:
        logger.error("✗ File I/O error!")
        logger.error("")
        logger.error("Error: %s", e)
        logger.error("")
        logger.error(separator)
        return 1


if __name__ == "__main__":
    sys.exit(main())
