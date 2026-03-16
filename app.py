import customtkinter as ctk
import yt_dlp
from tkinter import messagebox
import threading
import os

# Theme settings
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class SocialDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My Social Downloader")
        self.geometry("800x500")
        self.resizable(False, False)
        self.configure(fg_color="#F8F9FA")

        # --- BLUE HEADER SECTION ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#5856D6", height=200, corner_radius=0)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.title_label = ctk.CTkLabel(self.header_frame, text="Download Videos from Social Media", 
                                        font=("Arial Bold", 32), text_color="white")
        self.title_label.pack(pady=(50, 5))

        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Fast, Free, and Easy to Use", 
                                           font=("Arial", 16), text_color="#E0E0E0")
        self.subtitle_label.pack()

        # --- INPUT SECTION (The White Box Fix) ---
        # Error fix: pady ki jagah 'place' use kiya hai taake overlap bhi ho aur error bhi na aaye
        self.input_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10, 
                                       border_width=1, border_color="#E0E0E0", width=650, height=90)
        self.input_card.place(relx=0.5, rely=0.4, anchor="center") 
        self.input_card.pack_propagate(False)

        self.url_entry = ctk.CTkEntry(self.input_card, placeholder_text="Paste video link here...", 
                                      width=480, height=45, fg_color="#F1F3F4", border_width=0, text_color="black")
        self.url_entry.place(relx=0.03, rely=0.5, anchor="w")

        self.download_btn = ctk.CTkButton(self.input_card, text="⬇ Download", command=self.start_download_thread,
                                          fg_color="#5856D6", hover_color="#4644B2", width=120, height=45, font=("Arial Bold", 14))
        self.download_btn.place(relx=0.97, rely=0.5, anchor="e")

        # --- LOWER ICONS / STATUS ---
        self.status_label = ctk.CTkLabel(self, text="Supported: YouTube, TikTok, FB, Instagram, Twitter", 
                                         text_color="gray", font=("Arial", 12))
        self.status_label.place(relx=0.5, rely=0.6, anchor="center")

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Bahi, link to paste karein!")
            return
        
        self.download_btn.configure(state="disabled", text="Working...")
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        try:
            # Desktop path configuration
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': f'{desktop_path}/%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Success", "Video Download ho chuki hai!\nFile aapke Desktop par save hai.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Ye link nahi chal raha: {str(e)}")
        
        finally:
            self.download_btn.configure(state="normal", text="⬇ Download")
            self.url_entry.delete(0, 'end')

if __name__ == "__main__":
    app = SocialDownloader()
    app.mainloop()
