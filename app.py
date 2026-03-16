import streamlit as st
import yt_dlp
import os
import uuid
import tempfile
import re
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Free Social Media Video Downloader | Download HD Videos",
    page_icon="📥",
    layout="wide"
)

# --- CUSTOM CSS ---
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
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    <div class="header-container">
        <h1>📥 Social Media Video Downloader</h1>
        <p>Download Videos from YouTube, TikTok, Facebook, Instagram & More - 100% Free</p>
    </div>
    """, unsafe_allow_html=True)

# Custom progress handler
class ProgressHook:
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
        
    def hook(self, d):
        if d['status'] == 'downloading':
            # Extract percentage from string like "45.2%"
            if '_percent_str' in d:
                percent_str = d['_percent_str'].strip()
                # Remove color codes if present
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
                try:
                    percent = float(percent_str.replace('%', ''))
                    if self.progress_bar:
                        self.progress_bar.progress(percent / 100)
                    if self.status_text:
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        self.status_text.text(f"Downloading... {percent:.1f}% | Speed: {speed} | ETA: {eta}")
                except:
                    pass
                    
        elif d['status'] == 'finished':
            if self.progress_bar:
                self.progress_bar.progress(1.0)
            if self.status_text:
                self.status_text.text("✅ Download complete! Processing video...")

# --- MAIN INTERFACE ---
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    # Platform selection
    platform = st.selectbox(
        "Select Platform (Optional)",
        ["Auto Detect", "YouTube", "TikTok", "Instagram", "Facebook", "Twitter/X", "Other"]
    )
    
    url = st.text_input("", placeholder="Paste your video link here (YouTube, TikTok, Instagram, etc)...", key="url_input")
    
    if st.button("📥 Generate Download Link", use_container_width=True):
        if url:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
            
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            video_info_text = st.empty()
            
            # Initialize progress hook
            progress_hook = ProgressHook()
            progress_hook.progress_bar = progress_bar
            progress_hook.status_text = status_text
            
            with st.spinner("🔍 Analyzing video link..."):
                try:
                    # Comprehensive yt-dlp options
                    ydl_opts = {
                        'format': 'best[height<=1080][ext=mp4]/best[height<=1080]/best',  # Prefer 1080p MP4
                        'outtmpl': output_template,
                        'quiet': True,
                        'no_warnings': True,
                        'progress_hooks': [progress_hook.hook],
                        
                        # Headers to avoid 403
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        },
                        
                        # Extractor options
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['android', 'web', 'ios'],  # Multiple clients
                                'skip': ['dash', 'hls'],  # Skip problematic formats
                            },
                            'tiktok': {
                                'player_client': ['web', 'android'],
                            },
                            'instagram': {
                                'player_client': ['web'],
                            }
                        },
                        
                        # Retry configuration
                        'retries': 10,
                        'fragment_retries': 10,
                        'extractor_retries': 5,
                        'file_access_retries': 5,
                        
                        # Other options
                        'geo_bypass': True,
                        'nocheckcertificate': True,
                        'prefer_free_formats': True,
                        'verbose': False,  # Set to False to hide version numbers
                    }
                    
                    # First extract info
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Show extracting message
                        status_text.text("📋 Extracting video information...")
                        
                        # Extract info
                        info = ydl.extract_info(url, download=False)
                        
                        if info:
                            # Display video information
                            title = info.get('title', 'Unknown Title')
                            duration = info.get('duration', 0)
                            uploader = info.get('uploader', 'Unknown')
                            view_count = info.get('view_count', 0)
                            
                            # Format duration
                            if duration:
                                minutes = duration // 60
                                seconds = duration % 60
                                duration_str = f"{minutes}:{seconds:02d}"
                            else:
                                duration_str = "N/A"
                            
                            # Show video info in a nice box
                            video_info_text.markdown(f"""
                            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <h4>📹 Video Found!</h4>
                                <p><strong>Title:</strong> {title[:100]}{'...' if len(title) > 100 else ''}</p>
                                <p><strong>Channel/Uploader:</strong> {uploader}</p>
                                <p><strong>Duration:</strong> {duration_str} | <strong>Views:</strong> {view_count:,}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Now download
                            status_text.text("⏬ Starting download...")
                            
                            # Download the video
                            ydl.download([url])
                            
                            # Find the downloaded file
                            downloaded_files = list(Path(temp_dir).glob('*'))
                            if downloaded_files:
                                video_file = downloaded_files[0]
                                
                                # Check file size
                                file_size = os.path.getsize(video_file) / (1024 * 1024)  # MB
                                
                                if file_size > 0:
                                    st.markdown(f"""
                                    <div class="success-box">
                                        ✅ <strong>Success!</strong> Video ready for download<br>
                                        📊 Size: {file_size:.2f} MB | 📁 Format: MP4
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Read file for download
                                    with open(video_file, "rb") as file:
                                        st.download_button(
                                            label="💾 Download Video to Device",
                                            data=file,
                                            file_name=f"{title[:50]}.mp4",
                                            mime="video/mp4",
                                            use_container_width=True,
                                            key=f"download_{uuid.uuid4().hex[:8]}"
                                        )
                                    
                                    # Clean up
                                    os.remove(video_file)
                                    os.rmdir(temp_dir)
                                else:
                                    st.error("Downloaded file is empty. Please try again.")
                            else:
                                st.error("No file was downloaded. Please try again.")
                        else:
                            st.error("Could not extract video information. Please check the URL.")
                            
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    st.error(f"❌ Download Error: {error_msg[:200]}")
                    
                    # Provide helpful tips based on error
                    if "403" in error_msg:
                        st.info("💡 Tip: This video might be private or region-restricted. Try a different video or use a VPN.")
                    elif "copyright" in error_msg.lower():
                        st.info("💡 Tip: This video might be copyright protected and cannot be downloaded.")
                    elif "age" in error_msg.lower() or "18" in error_msg:
                        st.info("💡 Tip: This is an age-restricted video. Age verification might be required.")
                        
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {str(e)[:200]}")
                    
                finally:
                    # Clean up progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Clean up temp directory if it still exists
                    if os.path.exists(temp_dir):
                        try:
                            os.rmdir(temp_dir)
                        except:
                            pass
        else:
            st.warning("⚠️ Please paste a valid URL first!")

# Rest of your SEO content remains the same...
st.markdown("---")

# --- SEO CONTENT ---
st.write("## 🎯 Professional Social Media Video Downloader")
st.write("""""
Our advanced video downloader supports all major social media platforms. Whether you want to save YouTube videos for offline viewing, download TikTok trends, or keep Instagram reels, we've got you covered!
""")

# Features in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    ### ✨ Key Features
    - 🎥 **4K/HD Quality** - Download in original quality
    - 🔄 **Fast Processing** - 10x faster downloads
    - 🌐 **Multi-Platform** - YouTube, TikTok, Instagram, Facebook
    - 📱 **Mobile Friendly** - Works on all devices
    """)
    
with col2:
    st.markdown("""
    ### 📝 How to Use
    1. **Copy** video URL from any platform
    2. **Paste** in the box above
    3. **Click** Generate Download Link
    4. **Save** video to your device
    """)
    
with col3:
    st.markdown("""
    ### 🔒 Privacy First
    - No registration required
    - No tracking or cookies
    - Videos deleted after download
    - 100% free & secure
    """)

# FAQ Section
st.write("### ❓ Frequently Asked Questions")
with st.expander("Why am I getting a 403 Forbidden error?"):
    st.write("""
    A 403 error usually occurs when:
    - The video is private or unlisted
    - The platform has blocked our downloader temporarily
    - The video is region-restricted in your country
    
    **Solutions:**
    - Try a different video
    - Use a VPN if the video is region-restricted
    - Wait a few minutes and try again
    """)

with st.expander("Which platforms are supported?"):
    st.write("""
    We support downloading from:
    - **YouTube** (videos, shorts, playlists)
    - **TikTok** (videos, sounds)
    - **Instagram** (reels, posts, stories)
    - **Facebook** (videos, reels)
    - **Twitter/X** (videos)
    - **Reddit** (videos)
    - And many more...
    """)

with st.expander("What video quality can I download?"):
    st.write("""
    The downloader automatically selects the best available quality up to 1080p. 
    For YouTube videos, you can get up to 4K quality depending on what's available.
    """)

with st.expander("Is this tool really free?"):
    st.write("""
    Yes! Our downloader is completely free with no hidden charges. 
    We don't even require you to create an account. Just paste and download!
    """)

# Footer
st.markdown("""
<div style='text-align: center; color: grey; padding: 20px; margin-top: 50px;'>
    <hr>
    <p>© 2026 One Pilot Tools | Built with ❤️ by Abdul Hameed Mughal (Bahi)</p>
    <p style='font-size: 12px;'>For personal use only. Respect content creators' rights.</p>
</div>
""", unsafe_allow_html=True)
