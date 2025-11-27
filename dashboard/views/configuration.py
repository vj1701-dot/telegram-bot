"""Bot configuration management page."""
import streamlit as st
from pathlib import Path
from bot.config import BotConfigManager
from dashboard.config import DashboardConfig
from dashboard.api_client import BotAPIClient


def show():
    """Display configuration page."""

    st.header("⚙️ Bot Configuration")

    tabs = st.tabs(["Add Bot", "Manage Bots", "Global Settings"])

    config_manager = BotConfigManager(DashboardConfig.DATA_DIR)
    api_client = st.session_state.api_client

    with tabs[0]:
        st.subheader("Add New Bot")

        with st.form("add_bot_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                bot_token = st.text_input(
                    "Bot Token",
                    type="password",
                    help="Get this from @BotFather on Telegram"
                )

            with col2:
                chat_id = st.text_input(
                    "Chat ID",
                    help="Chat ID where messages will be sent"
                )

            scheduler_time = st.time_input(
                "Default Scheduler Time",
                help="Daily time to send scheduled audio"
            )

            submitted = st.form_submit_button("➕ Add Bot", use_container_width=True, type="primary")

            if submitted:
                if bot_token and chat_id:
                    # Test connection first
                    with st.spinner("Testing bot connection..."):
                        if api_client.test_connection(bot_token):
                            if config_manager.add_bot(
                                bot_token,
                                chat_id,
                                f"{scheduler_time.hour:02d}:{scheduler_time.minute:02d}"
                            ):
                                st.success("✓ Bot added successfully!")

                                # Reload config in bot
                                api_client.reload_config()
                                st.rerun()
                            else:
                                st.error("Bot token already exists!")
                        else:
                            st.error("Failed to connect to Telegram. Check your bot token.")
                else:
                    st.error("Please fill in all fields")

    with tabs[1]:
        st.subheader("Manage Bots")

        bots = config_manager.get_bots()

        if not bots:
            st.info("No bots configured yet. Add your first bot above.")
        else:
            for idx, bot in enumerate(bots):
                with st.expander(
                    f"🤖 Bot {idx + 1}: {bot['bot_token'][:15]}... (Chat: {bot['chat_id']})"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_chat_id = st.text_input(
                            "Chat ID",
                            value=bot["chat_id"],
                            key=f"chat_{bot['bot_token']}"
                        )

                    with col2:
                        enabled = st.checkbox(
                            "Enabled",
                            value=bot.get("enabled", True),
                            key=f"enabled_{bot['bot_token']}"
                        )

                    time_parts = bot["scheduler_time"].split(":")
                    new_time = st.time_input(
                        "Scheduler Time",
                        value=(int(time_parts[0]), int(time_parts[1])),
                        key=f"time_{bot['bot_token']}"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("💾 Update", key=f"update_{bot['bot_token']}", use_container_width=True):
                            config_manager.update_bot(
                                bot['bot_token'],
                                chat_id=new_chat_id,
                                enabled=enabled,
                                scheduler_time=f"{new_time.hour:02d}:{new_time.minute:02d}"
                            )
                            api_client.reload_config()
                            st.success("Bot updated!")
                            st.rerun()

                    with col2:
                        if st.button("🔍 Test", key=f"test_{bot['bot_token']}", use_container_width=True):
                            if api_client.test_connection(bot['bot_token']):
                                st.success("Connection OK!")
                            else:
                                st.error("Connection failed!")

                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{bot['bot_token']}", use_container_width=True):
                            config_manager.delete_bot(bot['bot_token'])
                            api_client.reload_config()
                            st.success("Bot deleted!")
                            st.rerun()

    with tabs[2]:
        st.subheader("Global Settings")

        current_tz = config_manager.data.get("global_timezone", "UTC")
        current_subfolder = config_manager.data.get("default_upload_subfolder", "")

        # Load timezones
        tz_file = Path("/app/north_america_timezones.txt")
        if tz_file.exists():
            with open(tz_file, 'r') as f:
                timezones = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        else:
            timezones = ["UTC"]

        timezone = st.selectbox(
            "Global Timezone",
            timezones,
            index=timezones.index(current_tz) if current_tz in timezones else 0,
            help="Timezone for scheduler"
        )

        default_subfolder = st.text_input(
            "Default Upload Subfolder",
            value=current_subfolder,
            help="Default folder for uploaded audio files"
        )

        if st.button("💾 Save Global Settings", use_container_width=True):
            config_manager.data["global_timezone"] = timezone
            config_manager.data["default_upload_subfolder"] = default_subfolder
            config_manager.save()
            api_client.reload_config()
            st.success("✓ Global settings saved!")
