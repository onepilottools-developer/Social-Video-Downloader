import streamlit as st
import yt_dlp
import os
import uuid
import tempfile
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Free Social Media Video Downloader | Download HD Videos",
    page_icon="📥",
    layout="wide"
)

# --- CUSTOM CSS (White UI Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .header-container {
        background-color: #5856D6;
        padding: 50px;
        text-align: center;
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #5856D6;
        color: white;
        width: 100%;
        border-radius: 5px;
        height: 50px;
        font-weight: bold;
    }
    h2, h3 { color: #333333; }
    </style>
    <div class="header-container">
        <h1>Social Media Video Downloader</h1>
        <p>Download Videos from YouTube, TikTok, Facebook & Instagram for Free</p>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN TOOL INTERFACE ---
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    url = st.text_input("", placeholder="Paste your video link here...", key="url_input")
    
    if st.button("📥 Generate Download Link"):
        if url:
            # Create unique filename in temp directory
            temp_dir = tempfile.mkdtemp()
            unique_filename = os.path.join(temp_dir, f"video_{uuid.uuid4().hex[:8]}.mp4")
            
            with st.spinner("🚀 Fetching video data... Please wait..."):
                try:
                    # Comprehensive yt-dlp options to fix 403 Forbidden
                    ydl_opts = {
                        'format': 'best[ext=mp4]/best',  # Prefer MP4 format
                        'outtmpl': unique_filename,
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': False,
                        'force_generic_extractor': False,
                        
                        # Add comprehensive headers to avoid 403
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Sec-Fetch-Mode': 'navigate',
                        },
                        
                        # Additional options for better compatibility
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['android', 'web'],  # Try multiple clients
                                'skip': ['hls', 'dash'],  # Skip problematic formats
                            }
                        },
                        
                        # Retry and timeout settings
                        'retries': 10,
                        'fragment_retries': 10,
                        'file_access_retries': 5,
                        'extractor_retries': 5,
                        'socket_timeout': 30,
                        
                        # Cookies handling (optional, but can help)
                        'cookiefile': None,  # Add path to cookies.txt if needed
                        
                        # Geo-bypass if needed
                        'geo_bypass': True,
                        
                        # Other useful options
                        'nocheckcertificate': True,
                        'prefer_free_formats': True,
                    }
                    
                    # Try to extract info first without downloading
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # First try to extract info to verify the URL
                        info = ydl.extract_info(url, download=False)
                        
                        if info:
                            # If info extraction successful, proceed with download
                            st.info(f"📹 Video Found: {info.get('title', 'Unknown Title')}")
                            
                            # Now download the video
                            ydl.download([url])
                            
                            if os.path.exists(unique_filename):
                                file_size = os.path.getsize(unique_filename) / (1024 * 1024)  # Size in MB
                                
                                with open(unique_filename, "rb") as file:
                                    st.success(f"✅ Video ready! Size: {file_size:.2f} MB")
                                    st.download_button(
                                        label="💾 Save Video to Device",
                                        data=file,
                                        file_name=f"{info.get('title', 'video')[:50]}.mp4",
                                        mime="video/mp4",
                                        key=f"btn_{uuid.uuid4().hex[:8]}"
                                    )
                                
                                # Cleanup
                                os.remove(unique_filename)
                                os.rmdir(temp_dir)
                            else:
                                st.error("File not found after download. Please try again.")
                        else:
                            st.error("Could not extract video information. Try another link.")
                            
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    if "403" in error_msg:
                        st.error("❌ Access Forbidden (403). Trying alternative method...")
                        # Fallback method
                        try:
                            # Try with different settings
                            fallback_opts = {
                                'format': 'worst',  # Try worst quality first
                                'outtmpl': unique_filename,
                                'quiet': True,
                                'http_headers': {
                                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                                },
                                'force_generic_extractor': True,  # Force generic extractor
                            }
                            
                            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                                ydl.download([url])
                                
                            if os.path.exists(unique_filename):
                                with open(unique_filename, "rb") as file:
                                    st.success("✅ Video downloaded with alternative method!")
                                    st.download_button(
                                        label="💾 Save Video",
                                        data=file,
                                        file_name=f"video_{uuid.uuid4().hex[:8]}.mp4",
                                        mime="video/mp4"
                                    )
                                os.remove(unique_filename)
                                os.rmdir(temp_dir)
                        except Exception as fallback_error:
                            st.error(f"Both methods failed. Error: {fallback_error}")
                    else:
                        st.error(f"Download Error: {error_msg}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}. Try another link or check your internet.")
                    
                finally:
                    # Cleanup temp directory if it exists and is empty
                    if os.path.exists(temp_dir):
                        try:
                            os.rmdir(temp_dir)
                        except:
                            pass
        else:
            st.warning("Bahi, please paste a valid URL first!")

st.markdown("---")

# Rest of your code remains the same...
# --- SEO ARTICLE SECTION (2000+ Words for AdSense & Rank Math) ---
st.write("## Comprehensive Guide to Social Media Video Downloader")
st.write("""
In today's digital age, social media platforms like YouTube, Instagram, and TikTok have become our primary source of entertainment and information. 
However, these platforms often don't provide an official way to download videos directly to your gallery. 
Our **Social Media Video Downloader** is a professional-grade tool designed to solve this problem efficiently.
""")

# --- FEATURES TABLE ---
st.write("### Key Features of Our Downloader")
features_data = {
    "Feature": ["High Quality", "Multi-Platform", "Fast Speed", "Safe & Secure", "Unlimited Downloads"],
    "Description": ["Download videos in HD, 1080p, and 4K resolution.", "Supports YouTube, FB, IG, and Twitter.", "Advanced servers ensure 10x faster processing.", "No malware, no tracking, 100% privacy.", "Use the tool as many times as you want."]
}
st.table(features_data)

st.write("### How to Use the Video Downloader (Step-by-Step Guide)")
st.write("""
1.  **Copy the Link:** Go to the social media app and copy the video URL.
2.  **Paste the Link:** Open our tool and paste the link in the input box above.
3.  **Process:** Click on the 'Generate Download Link' button.
4.  **Save:** Once the video is processed, click 'Save Video to Device'.
""")

# --- INTERNAL & EXTERNAL LINKS ---
st.markdown("""
* **External Resource:** [Check Official YT-DLP Documentation](https://github.com/yt-dlp/yt-dlp)
* **Internal Tool:** [Check our PDF Manager Tools](https://onepilottools.com)
""")

# --- FAQ SECTION ---
st.write("### Frequently Asked Questions (FAQs)")
with st.expander("Is this tool free to use?"):
    st.write("Yes, our downloader is 100% free and requires no registration.")
with st.expander("Can I download YouTube Shorts?"):
    st.write("Absolutely! Simply paste the Shorts link and it will download in MP4 format.")
with st.expander("Is it legal to download videos?"):
    st.write("Downloading videos for personal use and offline viewing is generally acceptable, but please respect the creator's copyright.")

# --- FOOTER ---
st.markdown("""
<div style='text-align: center; color: grey; padding: 20px;'>
    © 2026 One Pilot Tools | Built by Abdul Hameed Mughal (Bahi)
</div>
""", unsafe_allow_html=True)
