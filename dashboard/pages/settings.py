"""Settings and preferences page."""
import streamlit as st
from pathlib import Path
from dashboard.config import DashboardConfig
from bot.config import BotConfigManager


def show():
    """Display settings page."""

    st.header("🎨 Settings")

    config_manager = BotConfigManager(DashboardConfig.DATA_DIR)

    tabs = st.tabs(["Theme", "Timezone", "Preferences", "About"])

    with tabs[0]:
        st.subheader("Theme Settings")

        theme = st.radio(
            "Select Theme",
            ["light", "dark"],
            index=0 if config_manager.data.get("theme", "light") == "light" else 1,
            help="Choose dashboard theme"
        )

        if st.button("💾 Apply Theme", use_container_width=True):
            config_manager.data["theme"] = theme
            config_manager.save()
            st.success(f"✓ Theme set to {theme}!")
            st.info("Note: Theme changes require a Streamlit restart to take full effect")

    with tabs[1]:
        st.subheader("Timezone Settings")

        st.markdown("""
        The global timezone affects when scheduled jobs run.
        All scheduler times use this timezone.
        """)

        # Load all North America timezones
        tz_file = Path("/app/north_america_timezones.txt")
        if tz_file.exists():
            with open(tz_file, 'r') as f:
                timezones = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        else:
            timezones = ["UTC"]

        current_tz = config_manager.data.get("global_timezone", "UTC")

        selected_tz = st.selectbox(
            "Select Timezone",
            timezones,
            index=timezones.index(current_tz) if current_tz in timezones else 0,
            help="Timezone for scheduler"
        )

        if st.button("💾 Update Timezone", use_container_width=True):
            config_manager.data["global_timezone"] = selected_tz
            config_manager.save()

            # Reload bot config
            api_client = st.session_state.api_client
            if api_client.reload_config():
                st.success(f"✓ Timezone updated to {selected_tz}!")
                st.info("Scheduler has been reloaded with new timezone")
            else:
                st.error("Failed to reload scheduler")

    with tabs[2]:
        st.subheader("Preferences")

        # Default upload folder
        default_subfolder = st.text_input(
            "Default Upload Subfolder",
            value=config_manager.data.get("default_upload_subfolder", ""),
            placeholder="e.g., audio/ or audio/news/",
            help="Default folder for file uploads"
        )

        # Refresh interval
        st.markdown("**Dashboard Settings**")
        refresh_interval = st.slider(
            "Diagnostics Auto-Refresh Interval (seconds)",
            min_value=5,
            max_value=60,
            value=DashboardConfig.REFRESH_INTERVAL,
            step=5
        )

        if st.button("💾 Save Preferences", use_container_width=True):
            config_manager.data["default_upload_subfolder"] = default_subfolder
            config_manager.data["refresh_interval"] = refresh_interval
            config_manager.save()
            st.success("✓ Preferences saved!")

    with tabs[3]:
        st.subheader("About Telegram Audio Bot")

        st.markdown("""
        ### Telegram Audio Bot Dashboard
        **Version:** 1.0.0
        **Status:** Production Ready

        ---

        #### Features
        - ✓ Multi-bot support (multiple tokens & chat IDs)
        - ✓ Automatic MP3 → OGG OPUS conversion
        - ✓ Daily scheduler with timezone support
        - ✓ Excel-based schedule management
        - ✓ Manual send/resend capabilities
        - ✓ Real-time diagnostics and monitoring
        - ✓ File upload and verification

        #### Technology Stack
        - **Backend:** Python 3.9+, FastAPI, APScheduler
        - **Bot:** python-telegram-bot (async)
        - **Dashboard:** Streamlit
        - **Audio:** FFmpeg, pydub
        - **Data:** Excel (openpyxl), JSON

        #### Architecture
        - **Bot Container:** Telegram bot + scheduler + API
        - **Dashboard Container:** Streamlit web interface
        - **Shared Volume:** `/data` for configuration and audio

        ---

        #### Support
        For issues or questions, check the logs in the Diagnostics tab.

        #### Configuration Files
        - **config.json** - Bot configurations
        - **bot_state.json** - Runtime state
        - **schedule.xlsx** - Audio schedule
        - **.env** - Environment variables

        """)

        # System info
        st.markdown("---")
        st.markdown("### System Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Data Directory:** `{DashboardConfig.DATA_DIR}`")
            st.markdown(f"**Bot API URL:** `{DashboardConfig.BOT_API_URL}`")

        with col2:
            import platform
            st.markdown(f"**Platform:** {platform.system()}")
            st.markdown(f"**Python:** {platform.python_version()}")
