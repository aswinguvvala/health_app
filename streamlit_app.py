import streamlit as st
import os
import sys
import importlib.util
import gdown
import pandas as pd
import pickle
import json

# App title and initial setup
st.set_page_config(page_title="LifeCheck", layout="wide")

# Google Drive folder IDs - replace these with your actual folder/file IDs
DRIVE_IDS = {
    'code_folder': "14uxP8K7fY9yulzAU0G6Mkoz-CPsWX1ZH",
    'models_folder': "17A0Lnu0Fn-wXZ_5nssM9OJ5CsoQi8olq",
    'data_folder': "14uxP8K7fY9yulzAU0G6Mkoz-CPsWX1ZH",
    'req_txt': "1sMEed9yNgLXvo_JwB1uyo6hXXRZVwzew/view"
}

# Create necessary directories
os.makedirs("code", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("plots", exist_ok=True)

def download_folder(folder_id, output_path):
    """Download a folder from Google Drive"""
    try:
        st.write(f"Downloading {output_path}...")
        gdown.download_folder(
            id=folder_id,
            output=output_path,
            quiet=False
        )
        return True
    except Exception as e:
        st.error(f"Error downloading {output_path}: {e}")
        return False

def download_file(file_id, output_path):
    """Download a single file from Google Drive"""
    try:
        st.write(f"Downloading {output_path}...")
        gdown.download(
            id=file_id,
            output=output_path,
            quiet=False
        )
        return True
    except Exception as e:
        st.error(f"Error downloading {output_path}: {e}")
        return False

def download_and_setup():
    """Download all project files from Google Drive and set up the environment"""
    st.write("Setting up LifeCheck application...")
    
    # Create a progress bar
    progress = st.progress(0)
    
    # Step 1: Download the code folder
    if not download_folder(DRIVE_IDS['code_folder'], "code"):
        return False
    progress.progress(25)
    
    # Step 2: Download the data folder
    if not download_folder(DRIVE_IDS['data_folder'], "data"):
        return False
    progress.progress(50)
    
    # Step 3: Download the models folder
    if not download_folder(DRIVE_IDS['models_folder'], "models"):
        return False
    progress.progress(75)
    
    # Step 4: Download the plots folder
    if not download_folder(DRIVE_IDS['plots_folder'], "plots"):
        return False
    
    # Step 5: Download requirements.txt
    if not download_file(DRIVE_IDS['req_txt'], "requirements.txt"):
        return False
    progress.progress(100)
    
    # Step 6: Add code directory to Python path so we can import modules
    code_dir = "./code"
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    
    st.success("Setup complete!")
    return True

# Check if we've already set up
if 'setup_complete' not in st.session_state:
    with st.spinner("Setting up application..."):
        if download_and_setup():
            st.session_state['setup_complete'] = True
            st.experimental_rerun()  # Rerun the app now that setup is complete
        else:
            st.error("Setup failed. Please check the console for errors.")

# Once setup is complete, import and run the main app
if st.session_state.get('setup_complete', False):
    try:
        # Import main.py dynamically
        spec = importlib.util.spec_from_file_location("main", "./code/main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Run the main function from main.py
        main_module.main()
    except Exception as e:
        st.error(f"Error running LifeCheck application: {e}")
        st.error("Check the console for more details or refresh the page.")
        st.exception(e)
