"""Excel schedule editor page."""
import streamlit as st
import pandas as pd
from pathlib import Path
from dashboard.config import DashboardConfig
from datetime import datetime
import openpyxl


def show():
    """Display schedule editor page."""

    st.header("📝 Schedule Editor")

    schedule_path = DashboardConfig.DATA_DIR / "schedule.xlsx"

    st.markdown("""
    Edit your audio schedule. The schedule determines which audio files are sent each day.

    **Required Columns:**
    - **Date**: YYYY-MM-DD format (e.g., 2024-01-15)
    - **Path**: Relative path from /data (e.g., audio/ or audio/subfolder/)
    - **Track Name**: Filename with extension (e.g., morning_brief.mp3)
    - **Enabled**: TRUE or FALSE
    """)

    if not schedule_path.exists():
        st.info("📋 schedule.xlsx not found. Creating template...")

        if st.button("Create Template Schedule"):
            _create_template(schedule_path)
            st.success("✓ Template created!")
            st.rerun()
        return

    # Load schedule
    try:
        df = pd.read_excel(schedule_path)

        st.subheader("Current Schedule")

        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Entries", len(df))
        with col2:
            enabled_count = len(df[df.get("Enabled", True) == True])
            st.metric("Enabled", enabled_count)
        with col3:
            unique_dates = df["Date"].nunique() if "Date" in df.columns else 0
            st.metric("Unique Dates", unique_dates)

        st.markdown("---")

        # Editable dataframe
        st.subheader("Edit Schedule")

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    format="YYYY-MM-DD",
                    help="Date to send audio"
                ),
                "Path": st.column_config.TextColumn(
                    "Path",
                    help="Relative path from /data"
                ),
                "Track Name": st.column_config.TextColumn(
                    "Track Name",
                    help="Filename with extension"
                ),
                "Enabled": st.column_config.CheckboxColumn(
                    "Enabled",
                    help="Enable/disable this entry"
                )
            }
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Schedule", use_container_width=True):
                try:
                    edited_df.to_excel(schedule_path, index=False)
                    st.success("✓ Schedule saved successfully!")
                except Exception as e:
                    st.error(f"Failed to save: {e}")

        with col2:
            if st.button("🔄 Reload", use_container_width=True):
                st.rerun()

        with col3:
            if st.button("📥 Download", use_container_width=True):
                # Provide download button
                with open(schedule_path, 'rb') as f:
                    st.download_button(
                        label="Download Excel",
                        data=f,
                        file_name="schedule.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        # Upload replacement schedule
        st.markdown("---")
        st.subheader("Upload Schedule")

        uploaded_file = st.file_uploader(
            "Replace schedule with uploaded file",
            type=["xlsx"],
            help="Upload a new schedule.xlsx file"
        )

        if uploaded_file:
            if st.button("📤 Upload and Replace"):
                try:
                    with open(schedule_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("✓ Schedule uploaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    except Exception as e:
        st.error(f"Failed to load schedule: {e}")
        st.info("Try creating a new template schedule.")


def _create_template(path: Path):
    """Create template schedule file."""
    wb = openpyxl.Workbook()
    ws = wb.active

    # Headers
    ws.append(["Date", "Path", "Track Name", "Enabled"])

    # Sample rows
    today = datetime.now().strftime("%Y-%m-%d")
    ws.append([today, "audio/", "sample_track.mp3", True])
    ws.append([today, "audio/", "morning_news.mp3", True])

    wb.save(path)
