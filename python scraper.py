import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

TARGET_URL = "https://dangcongsan.vn/" 


OUTPUT_FOLDER = "scraped_assets"
# ---------------------------------------------

def scrape_website(url, folder):
    """
    Pipeline chính: Fetch, parse text, và download ảnh.
    """
    print(f"Pipeline đang chạy... Bắt đầu crawl trang: {url}")
    
    # Tạo thư mục chính và thư mục con cho ảnh
    images_folder = os.path.join(folder, "images")
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"Đã tạo thư mục: {images_folder}")

    try:
        # Bước 1: Fetch Page HTML
        # (Giả lập làm trình duyệt để tránh bị chặn 403)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Báo lỗi nếu status code không phải 200
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Bước 2: Parse Content & Save Text
        # Lấy tất cả nội dung văn bản có ý nghĩa
        print("Đang lấy nội dung text...")
        text_content = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'li', 'span']):
            text = element.get_text(strip=True)
            if text:
                text_content.append(text)
        
        text_file_path = os.path.join(folder, "content.txt")
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(text_content))
        print(f"Đã lưu nội dung text vào: {text_file_path}")

        # Bước 3: Parse Images & Download
        print("Đang tìm và tải hình ảnh...")
        images = soup.find_all('img')
        image_count = 0
        
        for img in images:
            img_src = img.get('src')
            if not img_src:
                continue # Bỏ qua nếu tag <img> không có 'src'

            # Chuyển URL tương đối (ví dụ: /images/pic.jpg) -> URL tuyệt đối
            img_url = urljoin(url, img_src)
            
            # Lấy tên file từ URL (đảm bảo tên file sạch)
            img_name = os.path.basename(urlparse(img_url).path)
            if not img_name or '.' not in img_name:
                 img_name = f"image_{image_count:03d}.png" # Đặt tên tạm

            img_path = os.path.join(images_folder, img_name)
            
            try:
                # Tải ảnh (dùng stream=True để xử lý file lớn)
                img_response = requests.get(img_url, headers=headers, stream=True)
                img_response.raise_for_status()
                
                with open(img_path, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
                print(f"  -> Đã tải: {img_name}")
                image_count += 1
            except Exception as e:
                print(f"  -> Lỗi khi tải {img_url}: {e}") # Bỏ qua nếu 1 ảnh lỗi

        print(f"\n--- HOÀN THÀNH ---")
        print(f"Đã lưu nội dung vào: {text_file_path}")
        print(f"Đã tải {image_count} hình ảnh vào thư mục: {images_folder}")
        
    except requests.exceptions.RequestException as e:
        print(f"LỖI NGHIÊM TRỌNG: Không thể truy cập URL. {e}")

# --- CHẠY SCRIPT ---
if __name__ == "__main__":
    scrape_website(TARGET_URL, OUTPUT_FOLDER)