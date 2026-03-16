import streamlit as st
import yt_dlp
import os
import uuid
import tempfile
import re
import subprocess
import sys
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px;
        text-align: center;
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 100%;
        border-radius: 5px;
        height: 50px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    h2, h3 { color: #333333; }
    .success-box {
        padding: 20px;
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #155724;
        border-radius: 10px;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 10px 0;
    }
    </style>
    <div class="header-container">
        <h1>📥 Advanced Video Downloader 2.0</h1>
        <p>Bypass 403 Errors | Download from YouTube, TikTok, Instagram & More</p>
    </div>
    """, unsafe_allow_html=True)

# Check and update yt-dlp
def check_ytdlp_version():
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "yt-dlp"], 
                              capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    except:
        return "Unknown"

# Update yt-dlp to latest version
def update_ytdlp():
    try:
        st.info("🔄 Checking for yt-dlp updates...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                      capture_output=True)
        return True
    except:
        return False

# Custom progress handler
class ProgressHook:
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
        
    def hook(self, d):
        if d['status'] == 'downloading':
            if '_percent_str' in d:
                percent_str = d['_percent_str'].strip()
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
                try:
                    percent = float(percent_str.replace('%', ''))
                    if self.progress_bar:
                        self.progress_bar.progress(percent / 100)
                    if self.status_text:
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        downloaded = d.get('downloaded_bytes', 0) / (1024 * 1024)
                        total = d.get('total_bytes', 0) / (1024 * 1024) if d.get('total_bytes') else 0
                        
                        if total > 0:
                            status = f"📥 Downloading... {percent:.1f}% | {downloaded:.1f}MB/{total:.1f}MB | Speed: {speed} | ETA: {eta}"
                        else:
                            status = f"📥 Downloading... {percent:.1f}% | Speed: {speed} | ETA: {eta}"
                        
                        self.status_text.text(status)
                except:
                    pass
        elif d['status'] == 'finished':
            if self.progress_bar:
                self.progress_bar.progress(1.0)
            if self.status_text:
                self.status_text.text("✅ Download complete! Processing video...")

# Try different download methods
def try_download_with_methods(url, temp_dir, progress_hook):
    methods = [
        {
            'name': 'Method 1: Android Client',
            'opts': {
                'format': 'best[height<=720]',  # Lower quality for Android
                'extractor_args': {'youtube': {'player_client': ['android']}},
                'http_headers': {'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 13) gzip'}
            }
        },
        {
            'name': 'Method 2: Web Client',
            'opts': {
                'format': 'best[height<=1080][ext=mp4]/best',
                'extractor_args': {'youtube': {'player_client': ['web']}},
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            }
        },
        {
            'name': 'Method 3: iOS Client',
            'opts': {
                'format': 'best[height<=720]',
                'extractor_args': {'youtube': {'player_client': ['ios']}},
                'http_headers': {'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone; iOS 17.0; gzip)'}
            }
        },
        {
            'name': 'Method 4: TV Client',
            'opts': {
                'format': 'best[height<=1080]',
                'extractor_args': {'youtube': {'player_client': ['tv']}},
                'http_headers': {'User-Agent': 'Mozilla/5.0 (PlayStation; PlayStation 5/2.26) AppleWebKit/605.1.15'}
            }
        },
        {
            'name': 'Method 5: Generic Extractor',
            'opts': {
                'format': 'worst',  # Try worst quality as last resort
                'force_generic_extractor': True,
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            }
        }
    ]
    
    for method in methods:
        st.info(f"🔄 Trying {method['name']}...")
        
        # Base options
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook.hook],
            'retries': 5,
            'fragment_retries': 5,
            'geo_bypass': True,
            'nocheckcertificate': True,
            **method['opts']
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Try to extract info first
                info = ydl.extract_info(url, download=False)
                if info:
                    st.success(f"✅ {method['name']} successful! Downloading...")
                    ydl.download([url])
                    
                    # Find downloaded file
                    downloaded_files = list(Path(temp_dir).glob('*'))
                    if downloaded_files:
                        return downloaded_files[0], info
        except Exception as e:
            st.warning(f"⚠️ {method['name']} failed: {str(e)[:100]}")
            continue
    
    return None, None

# --- MAIN INTERFACE ---
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    # Show yt-dlp version
    yt_version = check_ytdlp_version()
    st.caption(f"📦 yt-dlp version: {yt_version}")
    
    # Update button
    if st.button("🔄 Update Downloader Engine", use_container_width=True):
        if update_ytdlp():
            st.success("✅ yt-dlp updated successfully! Please refresh the page.")
        else:
            st.error("❌ Update failed. Please check your internet.")
    
    st.markdown("---")
    
    # URL input with example
    url = st.text_input("", placeholder="Paste your video link here (YouTube, TikTok, Instagram, etc)...", key="url_input")
    
    # Advanced options expander
    with st.expander("⚙️ Advanced Options (For 403 Errors)"):
        col_a, col_b = st.columns(2)
        with col_a:
            use_cookies = st.checkbox("Use cookies (if available)", value=False)
            quality = st.selectbox("Preferred Quality", ["Best Available", "1080p", "720p", "480p", "360p"])
        with col_b:
            bypass_geo = st.checkbox("Bypass Geo-restrictions", value=True)
            audio_only = st.checkbox("Audio Only (MP3)", value=False)
    
    if st.button("📥 Generate Download Link", use_container_width=True):
        if url:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            video_info_text = st.empty()
            
            # Initialize progress hook
            progress_hook = ProgressHook()
            progress_hook.progress_bar = progress_bar
            progress_hook.status_text = status_text
            
            # Show info box
            st.markdown("""
            <div class="info-box">
                <strong>🔄 Trying multiple methods to bypass 403 error...</strong><br>
                This might take a few moments. Please wait.
            </div>
            """, unsafe_allow_html=True)
            
            # Try different methods
            video_file, info = try_download_with_methods(url, temp_dir, progress_hook)
            
            if video_file and info:
                # Success!
                title = info.get('title', 'Video')
                uploader = info.get('uploader', 'Unknown')
                duration = info.get('duration', 0)
                
                # Format duration
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "N/A"
                
                # File size
                file_size = os.path.getsize(video_file) / (1024 * 1024)
                
                # Show success message with animation
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ Download Successful!</h3>
                    <p><strong>📹 Title:</strong> {title[:100]}{'...' if len(title) > 100 else ''}</p>
                    <p><strong>👤 Channel:</strong> {uploader}</p>
                    <p><strong>⏱️ Duration:</strong> {duration_str} | <strong>📊 Size:</strong> {file_size:.2f} MB</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Read file for download
                with open(video_file, "rb") as file:
                    st.download_button(
                        label="💾 Download Video Now",
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
                # All methods failed
                st.error("❌ All download methods failed. This video cannot be downloaded.")
                
                # Show troubleshooting tips
                st.markdown("""
                ### 🔧 Troubleshooting Tips:
                1. **Try a different video** - Some videos are heavily protected
                2. **Use a VPN** - Change your country/region
                3. **Update the tool** - Click the "Update Downloader Engine" button above
                4. **Check if video is:** 
                   - Private/Unlisted
                   - Age-restricted (18+)
                   - Removed by uploader
                   - Region-blocked in your country
                
                ### ✅ Videos that usually work:
                - Public YouTube videos
                - YouTube Shorts
                - TikTok videos
                - Instagram Reels
                - Facebook public videos
                """)
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
        else:
            st.warning("⚠️ Please paste a valid URL first!")

# Rest of your SEO content...
st.markdown("---")
st.write("## 🎯 Professional Video Downloader - Bypass 403 Errors")

# Features
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    ### 🚀 Advanced Features
    - **5 Different Download Methods**
    - Automatic 403 Bypass
    - Multiple Client Emulation
    - Cookie Support
    """)
    
with col2:
    st.markdown("""
    ### 📱 Supported Platforms
    - YouTube (All formats)
    - YouTube Shorts
    - TikTok
    - Instagram
    - Facebook
    - Twitter/X
    """)
    
with col3:
    st.markdown("""
    ### 💡 Pro Tips
    - Update regularly
    - Use VPN for blocked videos
    - Try different qualities
    - Clear browser cache
    """)

# FAQ
with st.expander("Why do I get 403 Forbidden error?"):
    st.write("""
    YouTube and other platforms actively block downloaders. Our tool uses multiple methods to bypass this:
    
    1. **Different clients** (Android, iOS, Web, TV)
    2. **Updated user agents**
    3. **Multiple extractors**
    4. **Geo-bypass techniques**
    
    If one method fails, it automatically tries the next one!
    """)

with st.expander("Which videos are hardest to download?"):
    st.write("""
    These videos often fail:
    - **Music videos** (record label restrictions)
    - **Age-restricted content** (18+)
    - **Live streams** (must be finished)
    - **Premium content** (YouTube Premium only)
    - **Recently uploaded** (may need time)
    """)

# Footer
st.markdown("""
<div style='text-align: center; color: grey; padding: 20px; margin-top: 50px;'>
    <hr>
    <p>© 2026 One Pilot Tools | Built by Abdul Hameed Mughal (Bahi)</p>
    <p style='font-size: 12px;'>For educational purposes only. Respect copyright laws.</p>
</div>
""", unsafe_allow_html=True)
