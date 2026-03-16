import streamlit as st
import yt_dlp
import os
import uuid
import tempfile
import re
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Free Social Media Video Downloader | Bypass 403",
    page_icon="📥",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        text-align: center;
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 100%;
        border-radius: 8px;
        height: 55px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .success-box {
        padding: 20px;
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #155724;
        border-radius: 10px;
        margin: 10px 0;
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
        <h1>📥 Ultimate Video Downloader</h1>
        <p>Bypass 403 Errors | Download YouTube, TikTok, Instagram & More easily!</p>
    </div>
    """, unsafe_allow_html=True)

# Format YouTube Shorts URL (Shorts URL aksar masla karti hain, isliye usko Watch URL mein badalna zaroori hai)
def format_url(url):
    if "youtube.com/shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

# Custom progress handler
class ProgressHook:
    def __init__(self, progress_bar, status_text):
        self.progress_bar = progress_bar
        self.status_text = status_text
        
    def hook(self, d):
        if d['status'] == 'downloading':
            if '_percent_str' in d:
                percent_str = d['_percent_str'].strip()
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
                try:
                    percent = float(percent_str.replace('%', ''))
                    self.progress_bar.progress(percent / 100)
                    
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    status = f"📥 Downloading... {percent:.1f}% | Speed: {speed} | ETA: {eta}"
                    self.status_text.text(status)
                except:
                    pass
        elif d['status'] == 'finished':
            self.progress_bar.progress(1.0)
            self.status_text.text("✅ Download complete! Finalizing file...")

# Try different download methods
def try_download(url, temp_dir, progress_hook, audio_only=False, use_cookies=False):
    # Determine format
    if audio_only:
        format_str = 'bestaudio/best'
        postprocessors = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    else:
        format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        postprocessors = []

    # API Bypass Methods (YouTube ko lagega ke mobile app se request aa rahi hai)
    methods = [
        {'name': 'Method 1 (Android Client)', 'opts': {'extractor_args': {'youtube': {'player_client': ['android', 'web']}}}},
        {'name': 'Method 2 (iOS Client)', 'opts': {'extractor_args': {'youtube': {'player_client': ['ios']}}}},
        {'name': 'Method 3 (TV Client)', 'opts': {'extractor_args': {'youtube': {'player_client': ['tv']}}}},
        {'name': 'Method 4 (Safe Web)', 'opts': {'extractor_args': {'youtube': {'player_skip': ['webpage']}}}}
    ]

    for method in methods:
        st.info(f"🔄 Trying {method['name']} to bypass security...")
        
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': format_str,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'progress_hooks': [progress_hook.hook],
            'postprocessors': postprocessors,
            **method['opts']
        }

        # Agar github par cookies.txt file majood ho
        if use_cookies and os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Direct download, do not extract info first to avoid early bans
                ydl.download([url])
                
                # Check if file was created in temp folder
                downloaded_files = list(Path(temp_dir).glob('*'))
                if downloaded_files:
                    st.success(f"✅ {method['name']} successful!")
                    return downloaded_files[0]
        except Exception as e:
            st.warning(f"⚠️ {method['name']} failed. Retrying next method...")
            continue
            
    return None

# --- MAIN INTERFACE ---
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    st.markdown("### Paste your video link below:")
    url_input = st.text_input("", placeholder="e.g., https://www.youtube.com/watch?v=...", label_visibility="collapsed")
    
    with st.expander("⚙️ Settings (For Blocked Videos)"):
        col_a, col_b = st.columns(2)
        with col_a:
            audio_only = st.checkbox("🎵 Download Audio Only (MP3)", value=False)
        with col_b:
            use_cookies = st.checkbox("🍪 Use Cookies (Bypass Strict 403)", value=True)

    if st.button("🚀 Download Video", use_container_width=True):
        if url_input:
            fixed_url = format_url(url_input)
            temp_dir = tempfile.mkdtemp()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            hook = ProgressHook(progress_bar, status_text)
            
            st.markdown("""
            <div class="info-box">
                <strong>⏳ Connecting to servers...</strong><br>
                Please wait, large videos may take a minute to process.
            </div>
            """, unsafe_allow_html=True)
            
            # Start download process
            downloaded_file = try_download(fixed_url, temp_dir, hook, audio_only, use_cookies)
            
            if downloaded_file:
                file_size = os.path.getsize(downloaded_file) / (1024 * 1024)
                file_name = os.path.basename(downloaded_file)
                
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 Ready to Save!</h3>
                    <p><strong>📄 File:</strong> {file_name}</p>
                    <p><strong>📊 Size:</strong> {file_size:.2f} MB</p>
                </div>
                """, unsafe_allow_html=True)
                
                with open(downloaded_file, "rb") as file:
                    mime_type = "audio/mpeg" if audio_only else "video/mp4"
                    st.download_button(
                        label="💾 Click Here to Save to Your Device",
                        data=file,
                        file_name=file_name,
                        mime=mime_type,
                        use_container_width=True,
                        key=f"download_{uuid.uuid4().hex[:8]}"
                    )
                
                # Cleanup (will not delete until python session ends, safe for streamlit)
            else:
                st.error("❌ All bypass methods failed! YouTube has strictly blocked this cloud IP.")
                st.info("💡 Tip: Try downloading a different video, or read the 'How to fix 100%' guide below.")
            
            # Reset UI
            progress_bar.empty()
            status_text.empty()
        else:
            st.warning("⚠️ Lalki, pehle link toh paste karo!")

st.markdown("---")
st.markdown("""
### 🛡️ Why do some videos fail?
Sometimes, platforms like YouTube block Cloud Servers (like the one this app runs on). This code uses 4 different "Bypass Methods" (Android/iOS spoofing) to trick YouTube. 

**🔥 HOW TO FIX 100% (For Admin / Developer):**
If you want this app to NEVER fail for your friends, do this:
1. Install **"Get cookies.txt LOCALLY"** extension on your Chrome browser.
2. Go to YouTube, click the extension, and click **Export**.
3. A file named `cookies.txt` will download. 
4. Upload this `cookies.txt` file to your GitHub repository where this `app.py` is saved.
5. That's it! The app will automatically read the cookies and YouTube will think a real human is downloading.
""")
