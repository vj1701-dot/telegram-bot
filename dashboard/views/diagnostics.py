"""Bot diagnostics and monitoring page."""
import streamlit as st
from pathlib import Path
from dashboard.api_client import BotAPIClient
from dashboard.config import DashboardConfig


def show():
    """Display diagnostics page."""

    st.header("🔍 Diagnostics")

    api_client = st.session_state.api_client

    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh (5s)", value=False)

    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()

    st.markdown("---")

    # API Health check
    st.subheader("API Health")

    col1, col2 = st.columns(2)

    with col1:
        health = api_client.health_check()
        if health:
            st.success("✓ Bot API is Online")
        else:
            st.error("✗ Bot API is Offline")

    with col2:
        if st.button("🔍 Test Connection", use_container_width=True):
            with st.spinner("Testing..."):
                health = api_client.health_check()
                if health:
                    st.success("Connection successful!")
                else:
                    st.error("Connection failed!")

    st.markdown("---")

    # Bot Status
    st.subheader("Bot Status")

    statuses = api_client.get_all_bot_status()

    if statuses:
        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Bots", len(statuses))

        with col2:
            healthy_count = sum(1 for s in statuses if s.get("is_healthy", False))
            st.metric("Healthy", healthy_count)

        with col3:
            error_count = len(statuses) - healthy_count
            st.metric("Errors", error_count)

        st.markdown("---")

        # Individual bot status
        for idx, status in enumerate(statuses):
            is_healthy = status.get("is_healthy", False)
            status_icon = "🟢" if is_healthy else "🔴"

            with st.expander(
                f"{status_icon} Bot {idx + 1}: {status['bot_token'][:15]}...",
                expanded=not is_healthy
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Chat ID:** {status.get('chat_id', 'N/A')}")
                    st.markdown(f"**Status:** {'Healthy' if is_healthy else 'Error'}")
                    st.markdown(f"**Last Run:** {status.get('last_run', 'Never')}")

                with col2:
                    st.markdown(f"**Last Sent File:** {status.get('last_sent_file', 'None')}")

                    if status.get("last_error"):
                        st.error(f"**Error:** {status['last_error']}")
                    else:
                        st.success("**No Errors**")
    else:
        st.info("No bot status data available")

    st.markdown("---")

    # Scheduler Jobs
    st.subheader("Scheduler Jobs")

    jobs_data = api_client.get_scheduler_jobs()

    if jobs_data and "jobs" in jobs_data:
        if jobs_data["jobs"]:
            for job in jobs_data["jobs"]:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.text(f"📌 {job['id']}")

                    with col2:
                        st.text(f"{job['name']}")

                    with col3:
                        if job["next_run"]:
                            st.text(job["next_run"])
                        else:
                            st.text("Not scheduled")
        else:
            st.info("No active scheduler jobs")
    else:
        st.warning("Failed to retrieve scheduler jobs")

    st.markdown("---")

    # Logs
    st.subheader("Recent Logs")

    log_dir = DashboardConfig.DATA_DIR / "logs"

    if log_dir.exists():
        log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)

        if log_files:
            selected_log = st.selectbox(
                "Select Log File",
                [f.name for f in log_files]
            )

            log_file = log_dir / selected_log

            # Number of lines to show
            num_lines = st.slider("Number of lines", 10, 200, 50)

            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        logs = f.readlines()[-num_lines:]

                    st.code(''.join(logs), language="text")

                    # Download log button
                    with open(log_file, 'r') as f:
                        st.download_button(
                            label="📥 Download Full Log",
                            data=f.read(),
                            file_name=log_file.name,
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Failed to read log file: {e}")
        else:
            st.info("No log files found")
    else:
        st.info("Log directory not found")

    st.markdown("---")

    # System Info
    st.subheader("System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Data Directory:** {DashboardConfig.DATA_DIR}")
        st.markdown(f"**Bot API URL:** {DashboardConfig.BOT_API_URL}")

    with col2:
        # Check if schedule exists
        schedule_file = DashboardConfig.DATA_DIR / "schedule.xlsx"
        schedule_status = "✓ Found" if schedule_file.exists() else "✗ Not Found"
        st.markdown(f"**Schedule File:** {schedule_status}")

        # Check config file
        config_file = DashboardConfig.DATA_DIR / "config.json"
        config_status = "✓ Found" if config_file.exists() else "✗ Not Found"
        st.markdown(f"**Config File:** {config_status}")
