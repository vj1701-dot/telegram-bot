"""Reusable timezone selector component."""
import streamlit as st
from pathlib import Path
from typing import List


def timezone_selector(current_tz: str = "UTC", key: str = "timezone") -> str:
    """
    Display timezone selector component.

    Args:
        current_tz: Currently selected timezone
        key: Unique key for the component

    Returns:
        Selected timezone
    """
    # Load timezones
    tz_file = Path("/app/north_america_timezones.txt")
    if tz_file.exists():
        with open(tz_file, 'r') as f:
            timezones = [line.strip() for line in f
                        if line.strip() and not line.startswith("#")]
    else:
        timezones = ["UTC"]

    selected_tz = st.selectbox(
        "Timezone",
        timezones,
        index=timezones.index(current_tz) if current_tz in timezones else 0,
        key=key,
        help="Select timezone for scheduling"
    )

    return selected_tz


def get_all_timezones() -> List[str]:
    """Get list of all available timezones."""
    tz_file = Path("/app/north_america_timezones.txt")
    if tz_file.exists():
        with open(tz_file, 'r') as f:
            return [line.strip() for line in f
                   if line.strip() and not line.startswith("#")]
    return ["UTC"]
