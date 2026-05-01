import os
import requests
import time # Hız sınırı için

DISCORD_WEBHOOK_URL = "WEBHOOK_URL_BURAYA"

def upload_file_to_discord(file_path):
    try:
        # Dosya boyutu kontrolü (Discord sınırı genelde 25MB)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 24:
            print(f"⏩ {os.path.basename(file_path)} çok büyük, atlanıyor ({file_size:.2f}MB)")
            return

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(DISCORD_WEBHOOK_URL, files=files)

        if response.status_code == 429: # Çok fazla istek (Rate Limit)
            wait_time = response.json().get('retry_after', 5)
            print(f"⏳ Hız sınırına takıldı. {wait_time} saniye bekleniyor...")
            time.sleep(wait_time)
            upload_file_to_discord(file_path) # Tekrar dene
        elif 200 <= response.status_code <= 204:
            print(f"✅ {os.path.basename(file_path)} gönderildi.")
        else:
            print(f"❌ Hata: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Hata: {e}")

# ... find_images_in_gallery fonksiyonu aynı kalabilir ...

if __name__ == "__main__":
    images = find_images_in_gallery()
    if images:
        for image in images:
            upload_file_to_discord(image)
            time.sleep(0.5) # Discord'u yormamak için yarım saniye bekle
