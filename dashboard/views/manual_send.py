"""Manual audio send page."""
import streamlit as st
from pathlib import Path
from dashboard.api_client import BotAPIClient
from dashboard.config import DashboardConfig
from bot.config import BotConfigManager
from datetime import datetime


def show():
    """Display manual send page."""

    st.header("📤 Manual Send")

    config_manager = BotConfigManager(DashboardConfig.DATA_DIR)
    api_client = st.session_state.api_client
    bots = config_manager.get_bots()

    if not bots:
        st.warning("⚠️ No bots configured. Add bots in Configuration tab first.")
        return

    tabs = st.tabs(["Send Audio", "Send by Date", "Resend Latest"])

    with tabs[0]:
        st.subheader("Send Single Audio File")

        # Select bot
        bot_options = {f"{b['bot_token'][:20]}... → {b['chat_id']}": b for b in bots}
        selected_bot_key = st.selectbox(
            "Select Bot",
            options=list(bot_options.keys()),
            key="send_audio_bot"
        )
        selected_bot = bot_options[selected_bot_key]

        # File path input methods
        input_method = st.radio(
            "File Selection Method",
            ["Browse Files", "Enter Path Manually"],
            horizontal=True
        )

        if input_method == "Browse Files":
            # Get available audio files
            audio_files = _get_audio_files(DashboardConfig.DATA_DIR)

            if audio_files:
                selected_file = st.selectbox(
                    "Select Audio File",
                    options=audio_files,
                    format_func=lambda x: x.replace("/app/data/", "")
                )
                file_path = selected_file
            else:
                st.info("No audio files found. Upload files in File Management.")
                file_path = None
        else:
            file_path = st.text_input(
                "File Path",
                placeholder="/app/data/audio/sample.mp3",
                help="Enter full path to audio file"
            )

        if file_path and st.button("📤 Send Now", use_container_width=True):
            with st.spinner("Sending audio..."):
                success = api_client.send_audio(
                    selected_bot["bot_token"],
                    selected_bot["chat_id"],
                    file_path
                )

                if success:
                    st.success(f"✓ Audio sent successfully to chat {selected_bot['chat_id']}")
                else:
                    st.error("Failed to send audio. Check logs for details.")

    with tabs[1]:
        st.subheader("Send All Audio for Specific Date")

        st.markdown("""
        Send all enabled audio files scheduled for a specific date.
        """)

        # Select bot
        bot_options = {f"{b['bot_token'][:20]}... → {b['chat_id']}": b for b in bots}
        selected_bot_key = st.selectbox(
            "Select Bot",
            options=list(bot_options.keys()),
            key="send_date_bot"
        )
        selected_bot = bot_options[selected_bot_key]

        # Date picker
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now(),
            help="Choose date to send scheduled audio"
        )

        date_str = selected_date.strftime("%Y-%m-%d")

        # Preview entries for this date
        from bot.utils.excel_parser import ExcelParser
        parser = ExcelParser()
        entries = parser.get_entries_by_date(date_str)

        if entries:
            st.info(f"Found {len(entries)} enabled entries for {date_str}")

            with st.expander("📋 Preview Entries"):
                for entry in entries:
                    st.text(f"• {entry.track_name} (from {entry.path})")
        else:
            st.warning(f"No enabled entries found for {date_str}")

        if st.button("📤 Send All for Date", use_container_width=True):
            if entries:
                with st.spinner(f"Sending {len(entries)} audio files..."):
                    result = api_client.send_by_date(
                        selected_bot["bot_token"],
                        selected_bot["chat_id"],
                        date_str
                    )

                    if result:
                        success_count = result.get("success_count", 0)
                        st.success(f"✓ Sent {success_count}/{len(entries)} files successfully")
                    else:
                        st.error("Failed to send audio files")
            else:
                st.error("No entries to send for selected date")

    with tabs[2]:
        st.subheader("Resend Last Sent Audio")

        st.markdown("""
        Resend the last audio file sent by each bot.
        """)

        for bot in bots:
            with st.expander(
                f"🤖 Bot: {bot['bot_token'][:15]}... → Chat {bot['chat_id']}"
            ):
                # Get bot status
                status = api_client.get_bot_status(bot["bot_token"])

                if status:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Last Sent:** {status.get('last_sent_file', 'None')}")
                        st.markdown(f"**Last Run:** {status.get('last_run', 'Never')}")

                    with col2:
                        last_file = status.get('last_sent_file')

                        if last_file:
                            if st.button("🔄 Resend", key=f"resend_{bot['bot_token']}", use_container_width=True):
                                with st.spinner("Resending..."):
                                    success = api_client.resend_audio(
                                        bot['bot_token'],
                                        bot['chat_id'],
                                        last_file
                                    )

                                    if success:
                                        st.success("✓ Resent successfully!")
                                    else:
                                        st.error("Failed to resend")
                        else:
                            st.info("No previous send history")
                else:
                    st.error("Failed to get bot status")


def _get_audio_files(data_dir: Path) -> list:
    """Get list of all audio files."""
    audio_dir = data_dir / "audio"
    if not audio_dir.exists():
        return []

    files = []
    for ext in DashboardConfig.AUDIO_FORMATS:
        files.extend(audio_dir.rglob(f"*.{ext}"))

    return [str(f) for f in sorted(files)]
