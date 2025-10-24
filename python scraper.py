import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re

# --- CẤU HÌNH (BẠN CHỈNH SỬA 2 PHẦN NÀY) ---

# 1. Dán CÁC URL trang web tham khảo của bạn vào danh sách (list) này
TARGET_URLS = [
    "https://vhttdl.nghean.gov.vn/tin-tuc-su-kien/ban-yen-hoa-xa-my-ly-vua-duoc-cong-nhan-la-diem-du-lich-cap-tinh-933574",
    "https://baonghean.vn/kham-pha-ve-dep-du-lich-cong-dong-ban-yen-hoa-ky-son-10264904.html",
]

# 2. Đặt tên thư mục GỐC (nơi sẽ chứa các thư mục con)
BASE_OUTPUT_FOLDER = "scraped_assets"

# ---------------------------------------------

def sanitize_filename(filename):
    """
    Làm sạch tên file/folder để tránh các ký tự không hợp lệ.
    """
    # Xóa http/https, www, và dấu / ở cuối
    clean_name = re.sub(r'^https?://(www\.)?|/$', '', filename)
    # Thay thế các ký tự không an toàn bằng dấu gạch dưới
    clean_name = re.sub(r'[\\/:*?"<>|.]+', '_', clean_name)
    return clean_name

def scrape_website(url, specific_folder):
    """
    Pipeline chính: Fetch, parse text, và download ảnh cho MỘT URL.
    """
    print(f"\n--- Dang chay URL: {url} ---")
    
    # Tạo thư mục con cho ảnh
    images_folder = os.path.join(specific_folder, "images")
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"Da tao thu muc: {images_folder}")

    try:
        # Bước 1: Fetch Page HTML
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Báo lỗi nếu status code không phải 200
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Bước 2: Parse Content & Save Text
        print(f"Dang lay noi dung text...")
        text_content = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'li', 'span']):
            text = element.get_text(strip=True)
            if text:
                text_content.append(text)
        
        text_file_path = os.path.join(specific_folder, "content.txt")
        # QUAN TRỌNG: Vẫn lưu file text là UTF-8 (có dấu)
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(text_content))
        print(f"Da luu content vao: {text_file_path}")

        # Bước 3: Parse Images & Download
        print(f"Dang tim va tai hinh anh...")
        images = soup.find_all('img')
        image_count = 0
        
        for img in images:
            img_src = img.get('src')
            if not img_src:
                continue # Bỏ qua nếu tag <img> không có 'src'

            img_url = urljoin(url, img_src)
            img_name = os.path.basename(urlparse(img_url).path)
            
          
            img_name = f"image_{image_count:03d}.png" # Đặt tên tạm
            
            # Làm sạch tên file một lần nữa
            img_path = os.path.join(images_folder, img_name)
            
            try:
                img_response = requests.get(img_url, headers=headers, stream=True)
                img_response.raise_for_status()
                
                with open(img_path, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
                print(f"  -> Da tai: {img_name}")
                image_count += 1
            except Exception as e:
                print(f"  -> Loi khi tai {img_url}: {e}") # Bỏ qua nếu 1 ảnh lỗi

        print(f"--- Hoan thanh URL: {url} ---")
        print(f"Da tai {image_count} hinh anh vao thu muc: {images_folder}")
        
    except requests.exceptions.RequestException as e:
        print(f"LOI NGHIEM TRONG: Khong a truy cap URL {url}. {e}")

# --- CHẠY SCRIPT ---
if __name__ == "__main__":
    print("Bat dau pipeline crawl da-website...")
    
    # Tạo thư mục gốc (base folder) nếu nó chưa tồn tại
    if not os.path.exists(BASE_OUTPUT_FOLDER):
        os.makedirs(BASE_OUTPUT_FOLDER)
        print(f"Da tao thu muc goc: {BASE_OUTPUT_FOLDER}")
        
    # Lặp qua từng URL trong danh sách
    for url in TARGET_URLS:
        # Tạo một tên thư mục con an toàn từ URL
        # Ví dụ: "https.://vtv.vn/demo" -> "vtv_vn_demo"
        safe_folder_name = sanitize_filename(url)
        
        # Tạo đường dẫn thư mục cụ thể cho URL này
        specific_folder = os.path.join(BASE_OUTPUT_FOLDER, safe_folder_name)
        
        # Gọi hàm scrape cho URL đó
        scrape_website(url, specific_folder)

    print("\n--- HOAN THANH TOAN BO ---")