"""Scheduler configuration page."""
import streamlit as st
from pathlib import Path
from bot.config import BotConfigManager
from dashboard.config import DashboardConfig
from dashboard.api_client import BotAPIClient


def show():
    """Display scheduler page."""

    st.header("📅 Scheduler Configuration")

    config_manager = BotConfigManager(DashboardConfig.DATA_DIR)
    api_client = st.session_state.api_client
    bots = config_manager.get_bots()

    if not bots:
        st.warning("⚠️ No bots configured. Add bots in Configuration tab first.")
        return

    st.markdown("""
    Set the daily time when scheduled audio files will be sent.
    All times use the global timezone setting from Configuration.
    """)

    st.markdown("---")

    # Get scheduler jobs
    jobs_data = api_client.get_scheduler_jobs()

    # Display current timezone
    current_tz = config_manager.data.get("global_timezone", "UTC")
    st.info(f"🌍 Current Timezone: **{current_tz}**")

    st.subheader("Bot Schedule Times")

    for idx, bot in enumerate(bots):
        with st.expander(
            f"🤖 Bot {idx + 1}: {bot['bot_token'][:15]}... → Chat {bot['chat_id']}",
            expanded=True
        ):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                current_time = bot["scheduler_time"].split(":")
                new_time = st.time_input(
                    "Schedule Time",
                    value=(int(current_time[0]), int(current_time[1])),
                    key=f"sched_{bot['bot_token']}",
                    help="Daily time to send scheduled audio"
                )

            with col2:
                enabled = bot.get("enabled", True)
                status = "🟢 Enabled" if enabled else "🔴 Disabled"
                st.markdown(f"**Status:** {status}")

                if jobs_data and "jobs" in jobs_data:
                    job_id = f"schedule_{bot['bot_token'][:20]}"
                    matching_job = next((j for j in jobs_data["jobs"] if j["id"] == job_id), None)
                    if matching_job and matching_job["next_run"]:
                        st.markdown(f"**Next Run:** {matching_job['next_run']}")
                    else:
                        st.markdown("**Next Run:** Not scheduled")

            with col3:
                if st.button("💾 Update", key=f"update_sched_{bot['bot_token']}", use_container_width=True):
                    config_manager.update_bot(
                        bot['bot_token'],
                        scheduler_time=f"{new_time.hour:02d}:{new_time.minute:02d}"
                    )

                    # Reload scheduler
                    if api_client.reload_config():
                        st.success("✓ Schedule updated!")
                        st.rerun()
                    else:
                        st.error("Failed to reload config")

    st.markdown("---")

    # Reload all schedules button
    if st.button("🔄 Reload All Schedules", use_container_width=True):
        with st.spinner("Reloading schedules..."):
            if api_client.reload_config():
                st.success("✓ All schedules reloaded successfully!")
                st.rerun()
            else:
                st.error("Failed to reload schedules")

    # Display all scheduled jobs
    if jobs_data and "jobs" in jobs_data:
        st.markdown("---")
        st.subheader("Active Scheduler Jobs")

        if jobs_data["jobs"]:
            for job in jobs_data["jobs"]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"📌 {job['name']}")
                with col2:
                    if job["next_run"]:
                        st.text(job["next_run"])
        else:
            st.info("No active scheduler jobs")
