import streamlit as st
import requests
import zipfile
import io
import os
import sys
import logging
import re
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LifeCheck.Launcher")

# Config - Google Drive file ID for Archive.zip
FILE_ID = "1QWf72OVLmmUs3eaj2qBauSChpXzxL3lc"  # Fixed: removed "/view"
APP_FOLDER = "lifecheck"
MAIN_FILE = "main.py"

def download_file_from_google_drive(file_id, destination):
    """
    Download a file from Google Drive, handling large files correctly
    """
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        
        # Check if the response is valid
        if response.status_code != 200:
            st.error(f"Error response: Status code {response.status_code}")
            return False
            
        content_type = response.headers.get('content-type', '')
        st.info(f"Response content type: {content_type}")
        
        if 'text/html' in content_type and 'drive.google.com' in response.text:
            st.error("Received HTML instead of file data. File may not be accessible.")
            return False
            
        # Save the file
        total_size = 0
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    total_size += len(chunk)
        
        st.info(f"Downloaded {total_size} bytes")
        
        # Verify file was created and has content
        if os.path.exists(destination) and os.path.getsize(destination) > 0:
            return True
        else:
            st.error("Downloaded file is empty or doesn't exist")
            return False

    # Direct download link with export=download
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    st.info(f"Downloading file ID: {file_id}")
    
    # First attempt with the uc?export=download URL
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        st.info(f"Received confirmation token: {token}")
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    success = save_response_content(response, destination)
    
    # If the first method failed, try alternate URL format
    if not success:
        st.warning("First download method failed, trying alternate method...")
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = session.get(direct_url, stream=True)
        success = save_response_content(response, destination)
        
    return success

def extract_zip(zip_path, extract_to="./"):
    """Extract zip file to the specified directory"""
    try:
        # First verify the file exists and is a zip
        if not os.path.exists(zip_path):
            st.error(f"Zip file does not exist: {zip_path}")
            return False
            
        file_size = os.path.getsize(zip_path)
        st.info(f"Zip file size: {file_size} bytes")
        
        if file_size == 0:
            st.error("Zip file is empty (0 bytes)")
            return False
            
        # Check if file is actually a zip
        with open(zip_path, 'rb') as f:
            header = f.read(4)
            # Zip files start with PK\x03\x04
            if header != b'PK\x03\x04':
                st.error(f"File is not a valid zip file (wrong header): {header}")
                return False
        
        st.info("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_to)
        st.success("Extraction complete")
        return True
    except zipfile.BadZipFile as e:
        st.error(f"Bad zip file: {e}")
        return False
    except Exception as e:
        st.error(f"Error extracting: {e}")
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
        
        # Create temporary zip file path
        temp_zip = "temp_archive.zip"
        
        # Remove existing file if it exists
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        
        # Download the zip file from Google Drive
        success = download_file_from_google_drive(FILE_ID, temp_zip)
        
        if not success:
            st.error("Failed to download the zip file.")
            return
            
        # Extract the zip file
        success = extract_zip(temp_zip)
        
        # Keep the file for debugging - comment this out later
        # if os.path.exists(temp_zip):
        #     os.remove(temp_zip)
            
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
