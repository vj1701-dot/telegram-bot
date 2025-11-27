"""File upload and management page."""
import streamlit as st
import os
from pathlib import Path
from dashboard.config import DashboardConfig
from bot.utils.file_validator import FileValidator


def show():
    """Display file management page."""

    st.header("📁 File Management")

    tabs = st.tabs(["Upload Files", "Verify Files", "Browse Files"])

    data_dir = DashboardConfig.DATA_DIR
    validator = FileValidator()

    with tabs[0]:
        st.subheader("Upload Audio Files")

        # Get subfolders
        subfolders = _get_subfolders(data_dir)

        target_folder = st.selectbox(
            "Target Folder",
            options=["audio/"] + subfolders,
            help="Select destination folder"
        )

        # Create new subfolder option
        with st.expander("➕ Create New Subfolder"):
            new_folder = st.text_input("Subfolder Name", placeholder="e.g., news")
            if st.button("Create Folder"):
                if new_folder:
                    folder_path = data_dir / "audio" / new_folder
                    folder_path.mkdir(parents=True, exist_ok=True)
                    st.success(f"✓ Created folder: {new_folder}")
                    st.rerun()

        uploaded_files = st.file_uploader(
            "Choose audio files",
            type=DashboardConfig.AUDIO_FORMATS,
            accept_multiple_files=True,
            help=f"Supported formats: {', '.join(DashboardConfig.AUDIO_FORMATS)}"
        )

        if uploaded_files:
            st.info(f"Selected {len(uploaded_files)} file(s)")

            for file in uploaded_files:
                size_mb = len(file.getvalue()) / (1024 * 1024)
                st.text(f"📄 {file.name} ({size_mb:.2f} MB)")

            if st.button("📤 Upload Files", use_container_width=True):
                progress_bar = st.progress(0)
                uploaded_count = 0

                for idx, file in enumerate(uploaded_files):
                    save_path = data_dir / target_folder / file.name

                    save_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(save_path, 'wb') as f:
                        f.write(file.getbuffer())

                    uploaded_count += 1
                    progress_bar.progress((idx + 1) / len(uploaded_files))

                st.success(f"✓ Uploaded {uploaded_count} file(s) to {target_folder}")

    with tabs[1]:
        st.subheader("Verify Schedule Files")

        st.markdown("""
        Check if all audio files referenced in schedule.xlsx exist.
        """)

        if st.button("🔍 Verify All Files", use_container_width=True):
            with st.spinner("Verifying files..."):
                results = validator.verify_schedule_files()

                if results:
                    valid_count = sum(1 for v in results.values() if v)
                    total_count = len(results)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Valid Files", valid_count)
                    with col2:
                        st.metric("Missing Files", total_count - valid_count)

                    st.markdown("---")

                    # Show results
                    for file_path, exists in results.items():
                        if exists:
                            st.success(f"✓ {file_path}")
                        else:
                            st.error(f"✗ {file_path} - NOT FOUND")
                else:
                    st.info("No schedule entries found to verify")

    with tabs[2]:
        st.subheader("Browse Audio Files")

        # File browser
        audio_dir = data_dir / "audio"
        if not audio_dir.exists():
            st.info("No audio directory found. Upload files to create it.")
            return

        files = list(audio_dir.rglob("*.*"))
        audio_files = [f for f in files if f.suffix.lower() in [f".{ext}" for ext in DashboardConfig.AUDIO_FORMATS]]

        if audio_files:
            st.metric("Total Audio Files", len(audio_files))

            # Group by folder
            folders = {}
            for file in audio_files:
                rel_path = file.relative_to(data_dir)
                folder = str(rel_path.parent)

                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(file)

            # Display by folder
            for folder, files in sorted(folders.items()):
                with st.expander(f"📂 {folder} ({len(files)} files)"):
                    for file in sorted(files):
                        size_mb = file.stat().st_size / (1024 * 1024)
                        rel_path = file.relative_to(data_dir)

                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.text(f"🎵 {file.name}")
                        with col2:
                            st.text(f"{size_mb:.2f} MB")
                        with col3:
                            if st.button("🗑️", key=f"delete_{file}", help="Delete file"):
                                file.unlink()
                                st.success(f"Deleted {file.name}")
                                st.rerun()
        else:
            st.info("No audio files found. Upload files in the Upload tab.")


def _get_subfolders(data_dir: Path) -> list:
    """Get list of subfolders in audio directory."""
    try:
        audio_dir = data_dir / "audio"
        if not audio_dir.exists():
            return []

        subfolders = []
        for item in audio_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                rel_path = item.relative_to(data_dir)
                subfolders.append(str(rel_path) + "/")

        return sorted(subfolders)
    except:
        return []
