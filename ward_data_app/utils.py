"""
General utility module.

This script provides a set of reusable helper functions, such as
formatting database cursor results and safely handling
dates and times.
"""
import logging
import datetime
import re
import unicodedata
from .logging_config import setup_logger

logger = setup_logger(__name__, log_to_file=True, log_level=logging.DEBUG)


def dictfetchall(cursor):
    """
    Return all rows from a database cursor as a list of dictionaries.

    Args:
        cursor: The executed cursor object.

    Returns:
        list[dict]: A list of dictionaries, where each represents a row.
    """
    try:
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error in dictfetchall: {e}", exc_info=True)
        return []


def dictfetchone(cursor):
    """
    Return a single row from a cursor as a dictionary, or None if no rows are left.

    Args:
        cursor: The executed cursor object.

    Returns:
        dict or None: A dictionary representing the row, or None.
    """
    try:
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None
    except Exception as e:
        logger.error(f"Error in dictfetchone: {e}", exc_info=True)
        return None


def format_hour(hour_seconds):
    """
    Converts a total number of seconds since midnight to an HH:MM string format.

    Args:
        hour_seconds (int | None): The total number of seconds.

    Returns:
        str: The formatted time as "HH:MM", or "00:00" for invalid input.
    """
    if hour_seconds is None:
        return "00:00"
    try:
        total_seconds = int(hour_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}"
    except (ValueError, TypeError):
        logger.warning(f"Invalid hour format received: {hour_seconds}")
        return "00:00"


def safe_strftime(date_obj, fmt='%d-%m-%Y'):
    """
    Safely formats a date or datetime object to a string.

    Args:
        date_obj (datetime.date | datetime.datetime | None): The object to format.
        fmt (str): The desired string format.

    Returns:
        str or None: The formatted date, or None if the input is invalid.
    """
    if isinstance(date_obj, (datetime.date, datetime.datetime)):
        try:
            return date_obj.strftime(fmt)
        except ValueError:
            logger.warning(f"Error formatting date/datetime: {date_obj} with format {fmt}")
            return None
    # Return None if not a valid date/datetime object
    return None

def slugify(value):
    """
    Normalizes a string, removes non-alphanumeric characters,
    converts spaces to underscores, and limits length.
    Used for creating safe filenames.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().upper()
    value = re.sub(r'[-\s]+', '_', value)
    return value[:50]