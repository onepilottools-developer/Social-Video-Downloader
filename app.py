import streamlit as st
import yt_dlp
import os
import uuid  # Har video ko alag naam dene ke liye

# Page Settings
st.set_page_config(page_title="My Social Downloader", page_icon="📥", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .header-container {
        background-color: #5856D6;
        padding: 60px;
        text-align: center;
        color: white;
        margin: -50px -50px 20px -50px;
    }
    </style>
    <div class="header-container">
        <h1>Download Videos from Social Media</h1>
        <p>Fast, Free, and Easy to Use</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    url = st.text_input("", placeholder="Paste video link here...", key="url_input")
    
    if st.button("📥 Download"):
        if url:
            # Har dafa naya unique filename banayega
            unique_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            
            with st.spinner("Processing video..."):
                try:
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': unique_filename,
                        'quiet': True,
                        'noplaylist': True
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    # File ko read karke download button dikhana
                    if os.path.exists(unique_filename):
                        with open(unique_filename, "rb") as file:
                            st.download_button(
                                label="✅ Click to Save Video",
                                data=file,
                                file_name=unique_filename,
                                mime="video/mp4",
                                key=unique_filename # Key zaroori hai refresh ke liye
                            )
                        st.success("Mubarak ho! Video ready hai.")
                        # File server se delete kar dein taake space full na ho
                        os.remove(unique_filename)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Pehle link paste karein bahi!")
