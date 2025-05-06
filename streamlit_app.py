import streamlit as st
import requests
import zipfile
import io
import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LifeCheck.Launcher")

# Config
ZIP_URL = "https://drive.google.com/file/d/1QWf72OVLmmUs3eaj2qBauSChpXzxL3lc/view?usp=share_link"
APP_FOLDER = "lifecheck"
MAIN_FILE = "main.py"

def download_and_extract_zip(url, extract_to="./"):
    """Download and extract zip file from Google Drive"""
    try:
        st.info("Downloading LifeCheck files...")
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Failed to download. Status code: {response.status_code}")
            return False
            
        # Extract the zip file
        st.info("Extracting files...")
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(extract_to)
        return True
    except Exception as e:
        st.error(f"Error downloading or extracting: {e}")
        return False

def main():
    st.set_page_config(
        page_title="LifeCheck - Health Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("LifeCheck - Health Assistant")
    
    # Check if the app folder exists
    if not os.path.exists(APP_FOLDER):
        st.warning("LifeCheck files not found. Downloading...")
        success = download_and_extract_zip(ZIP_URL)
        if not success:
            st.error("Failed to set up LifeCheck. Please try again.")
            return
        st.success("LifeCheck files downloaded successfully!")
        st.info("Starting LifeCheck app...")
        st.rerun()
    
    # Now that we have the files, import and run the main app
    try:
        # Add the lifecheck directory to the Python path
        if APP_FOLDER not in sys.path:
            sys.path.insert(0, APP_FOLDER)
        
        # Import the main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", os.path.join(APP_FOLDER, MAIN_FILE))
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Run the main function
        main_module.main()
    except Exception as e:
        st.error(f"Error running LifeCheck: {e}")
        logger.error(f"Error running app: {e}")

if __name__ == "__main__":
    main()
