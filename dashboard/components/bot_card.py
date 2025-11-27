"""Reusable bot configuration card component."""
import streamlit as st
from typing import Dict, Optional


def bot_card(bot_config: Dict, status: Optional[Dict] = None):
    """
    Display bot configuration card.

    Args:
        bot_config: Bot configuration dict
        status: Optional bot status dict
    """
    with st.container():
        # Header
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"**Bot Token:** {bot_config['bot_token'][:15]}...")

        with col2:
            st.markdown(f"**Chat ID:** {bot_config['chat_id']}")

        with col3:
            enabled = bot_config.get("enabled", True)
            if enabled:
                st.success("Enabled")
            else:
                st.error("Disabled")

        # Status info
        if status:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"📅 **Last Run:** {status.get('last_run', 'Never')}")

            with col2:
                st.markdown(f"📄 **Last File:** {status.get('last_sent_file', 'None')}")

            if status.get("last_error"):
                st.error(f"⚠️ Error: {status['last_error']}")

        # Scheduler info
        st.markdown(f"⏰ **Schedule Time:** {bot_config.get('scheduler_time', 'Not set')}")


def bot_status_badge(is_healthy: bool) -> str:
    """Return status badge emoji."""
    return "🟢" if is_healthy else "🔴"
