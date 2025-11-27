"""Reusable file explorer component."""
import streamlit as st
from pathlib import Path
from typing import List, Optional
from dashboard.config import DashboardConfig


def file_explorer(root_dir: Path, file_extensions: Optional[List[str]] = None) -> Optional[str]:
    """
    Display file explorer component.

    Args:
        root_dir: Root directory to explore
        file_extensions: List of file extensions to filter (e.g., ['.mp3', '.ogg'])

    Returns:
        Selected file path or None
    """
    if not root_dir.exists():
        st.warning(f"Directory not found: {root_dir}")
        return None

    # Get all files
    if file_extensions:
        files = []
        for ext in file_extensions:
            files.extend(root_dir.rglob(f"*{ext}"))
    else:
        files = list(root_dir.rglob("*.*"))

    if not files:
        st.info("No files found in directory")
        return None

    # Group by folder
    folders = {}
    for file in files:
        rel_path = file.relative_to(root_dir)
        folder = str(rel_path.parent)

        if folder not in folders:
            folders[folder] = []
        folders[folder].append(file)

    # Display files grouped by folder
    selected_file = None

    for folder, folder_files in sorted(folders.items()):
        with st.expander(f"📂 {folder} ({len(folder_files)} files)"):
            for file in sorted(folder_files):
                size_mb = file.stat().st_size / (1024 * 1024)

                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.text(f"📄 {file.name}")

                with col2:
                    st.text(f"{size_mb:.2f} MB")

                with col3:
                    if st.button("Select", key=f"select_{file}"):
                        selected_file = str(file)

    return selected_file


def list_audio_files(root_dir: Path = None) -> List[str]:
    """
    Get list of all audio files.

    Args:
        root_dir: Root directory (defaults to DATA_DIR/audio)

    Returns:
        List of audio file paths
    """
    if root_dir is None:
        root_dir = DashboardConfig.DATA_DIR / "audio"

    if not root_dir.exists():
        return []

    files = []
    for ext in DashboardConfig.AUDIO_FORMATS:
        files.extend(root_dir.rglob(f"*.{ext}"))

    return [str(f) for f in sorted(files)]
