"""
Main Streamlit application entry point.
Manages pages and global state.
"""
import streamlit as st
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.config import DashboardConfig
from dashboard.api_client import BotAPIClient

# Configure page
st.set_page_config(
    page_title="Telegram Audio Bot Dashboard",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize session state
if "api_client" not in st.session_state:
    st.session_state.api_client = BotAPIClient()

if "config_dir" not in st.session_state:
    st.session_state.config_dir = DashboardConfig.DATA_DIR

# Sidebar branding
with st.sidebar:
    st.title("🎙️ Telegram Audio Bot")
    st.markdown("---")

    # API Health Check
    api_healthy = st.session_state.api_client.health_check()
    if api_healthy:
        st.success("✓ Bot API Connected")
    else:
        st.error("✗ Bot API Offline")

    st.markdown("---")

# Main navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    [
        "🏠 Home",
        "⚙️ Configuration",
        "📅 Scheduler",
        "📝 Schedule Editor",
        "📁 File Management",
        "📤 Manual Send",
        "🔍 Diagnostics",
        "🎨 Settings"
    ]
)

# Page routing
if page == "🏠 Home":
    st.title("Welcome to Telegram Audio Bot Dashboard")

    st.markdown("""
    ## Features

    - **Configuration**: Manage multiple bot tokens and chat IDs
    - **Scheduler**: Set daily send times for each bot
    - **Schedule Editor**: Edit Excel schedule file
    - **File Management**: Upload and verify audio files
    - **Manual Send**: Trigger audio sends manually
    - **Diagnostics**: Monitor bot health and logs
    - **Settings**: Customize timezone and theme

    ### Quick Start

    1. Go to **Configuration** to add your first bot
    2. Upload audio files in **File Management**
    3. Create your schedule in **Schedule Editor**
    4. Set send time in **Scheduler**
    5. Monitor status in **Diagnostics**

    ### System Status
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Bot API", "Online" if api_healthy else "Offline")

    with col2:
        # Get bot count
        from bot.config import BotConfigManager
        config_mgr = BotConfigManager(DashboardConfig.DATA_DIR)
        bot_count = len(config_mgr.get_bots())
        st.metric("Active Bots", bot_count)

    with col3:
        # Get schedule file status
        schedule_file = DashboardConfig.DATA_DIR / "schedule.xlsx"
        st.metric("Schedule", "Ready" if schedule_file.exists() else "Not Found")

elif page == "⚙️ Configuration":
    from dashboard.views import configuration
    configuration.show()

elif page == "📅 Scheduler":
    from dashboard.views import scheduler
    scheduler.show()

elif page == "📝 Schedule Editor":
    from dashboard.views import schedule_editor
    schedule_editor.show()

elif page == "📁 File Management":
    from dashboard.views import file_management
    file_management.show()

elif page == "📤 Manual Send":
    from dashboard.views import manual_send
    manual_send.show()

elif page == "🔍 Diagnostics":
    from dashboard.views import diagnostics
    diagnostics.show()

elif page == "🎨 Settings":
    from dashboard.views import settings
    settings.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.0.0")
st.sidebar.markdown("**Status:** Production Ready")
