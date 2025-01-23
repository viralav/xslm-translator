import os
import asyncio
import tempfile
import streamlit as st

from utils.row_ds import CancellationToken
from utils.handler import translate_file, translate_folder

import os
import sys

# Ensure the script can access the utils folder
if getattr(sys, 'frozen', False):
    # If the app is packaged, get the path of the executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running normally, get the current directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASE_DIR, 'utils'))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def main():
    

    # Disable the Streamlit hamburger menu and footer for a cleaner look
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Excel Translator (macOS-Friendly)")
    st.write("Translate Excel files while streaming logs.")

    option = st.radio("Select Option", ("Single File", "Folder"))

    src_language_options = {
        "auto": "Auto Detect",
        "de": "German",
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "zh-CN": "Chinese (Simplified)",
        "ru": "Russian"
    }

    desc_language_options = {
        "en": "English",
        "de": "German",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "zh-CN": "Chinese (Simplified)",
        "ru": "Russian"
    }

    src_lang = st.selectbox("Source Language", list(src_language_options.keys()), format_func=lambda x: src_language_options[x])
    dest_lang = st.selectbox("Destination Language", list(desc_language_options.keys()), format_func=lambda x: desc_language_options[x])

    log_queue = asyncio.Queue()

    if option == "Single File":
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsm", "xlsx"])

        if uploaded_file:
            st.write("Uploaded file:", uploaded_file.name)

            if st.button("Translate File"):
                try:
                    temp_input_file = os.path.join(TEMP_DIR, uploaded_file.name)
                    with open(temp_input_file, "wb") as f:
                        f.write(uploaded_file.read())

                    cancellation_token = CancellationToken()
                    progress_bar = st.progress(0)

                    # Run the translation synchronously
                    translated_file_path = asyncio.run(
                        translate_file(temp_input_file, src_lang, dest_lang, cancellation_token, log_queue, progress_bar)
                    )

                    # Display logs
                    while not log_queue.empty():
                        log_message = log_queue.get_nowait()
                        st.info(log_message)

                    if translated_file_path:
                        st.success("Translation completed. Download your file below:")
                        with open(translated_file_path, "rb") as f:
                            st.download_button(
                                "Download Translated File",
                                f,
                                file_name=os.path.basename(translated_file_path),
                            )

                except Exception as e:
                    st.error(f"An error occurred: {e}")

    else:
        
        folder_path = st.text_input("Enter folder path containing Excel files")

        if st.button("Translate Folder"):
            try:
                cancellation_token = CancellationToken()
                progress_bar = st.progress(0)

                async def process_folder():
                    await translate_folder(folder_path, src_lang, dest_lang, cancellation_token, log_queue, progress_bar)
                    st.success("Translation of all files in the folder completed.")

                asyncio.run(process_folder())

                while not log_queue.empty():
                    log_message = log_queue.get_nowait()
                    st.info(log_message)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    import streamlit as st  # Import streamlit within the main block
    st.set_page_config(page_title="Excel Translator", layout="centered")

    main()  # Call your main function as before

    # Launch the Streamlit app
    st.write("Streamlit app started.") 
    st.balloons()  # Add a visual cue