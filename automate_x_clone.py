import json
import time
import requests
from datetime import datetime
from DrissionPage import ChromiumPage

# Cấu hình API và URL
API_BASE_URL = "http://127.0.0.1:8000/api"
FRONTEND_URL = "http://localhost:5173"

def fetch_cookies_from_db(username):
    """Lấy cookies và localStorage của user từ cơ sở dữ liệu qua API"""
    try:
        url = f"{API_BASE_URL}/auth/cookies/{username}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"[-] Không tìm thấy dữ liệu cookies cho user '{username}' trong DB.")
            return None
        else:
            print(f"[-] Lỗi API khi lấy cookies: {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Lỗi kết nối tới API: {e}")
        return None

def save_cookies_to_db(username, cookies, local_storage):
    """Lưu cookies và localStorage của user vào cơ sở dữ liệu qua API"""
    try:
        url = f"{API_BASE_URL}/auth/cookies"
        data = {
            "username": username,
            "cookies": json.dumps(cookies),
            "local_storage": local_storage
        }
        response = requests.post(url, json=data)
        if response.status_code in (200, 201):
            print(f"[+] Đã lưu cookies của '{username}' vào database thành công!")
            return True
        else:
            print(f"[-] Không thể lưu cookies qua API: {response.text}")
            return False
    except Exception as e:
        print(f"[-] Lỗi lưu cookies: {e}")
        return False

def main():
    print("====================================================")
    print("   HỆ THỐNG TỰ ĐỘNG HÓA X CLONE - DRISSIONPAGE      ")
    print("====================================================")
    
    username = input("Nhập username cần chạy tự động: ").strip()
    password = input("Nhập password (dùng để đăng nhập nếu chưa có cookie): ").strip()
    
    if not username or not password:
        print("[-] Username và Password không được để trống!")
        return

    # 1. Truy vấn cookies từ database
    print(f"\n[*] Đang kiểm tra cookies của '{username}' trong database...")
    session_data = fetch_cookies_from_db(username)
    
    page = ChromiumPage()
    logged_in = False

    try:
        if session_data:
            print("[+] Tìm thấy cookies! Tiến hành tự động đăng nhập...")
            
            # Truy cập trang trước để khởi tạo origin của domain
            page.get(FRONTEND_URL)
            time.sleep(1)
            
            # Nạp localStorage
            ls_data = json.loads(session_data["local_storage"])
            for key, val in ls_data.items():
                # Sử dụng json.dumps để định dạng chuỗi an toàn
                page.run_js(f"localStorage.setItem({json.dumps(key)}, {json.dumps(val)});")
                
            # Nạp Cookies (nếu có lưu)
            if session_data.get("cookies"):
                try:
                    # Nếu cookies lưu ở định dạng chuỗi cookie thô hoặc danh sách json
                    cookies_list = json.loads(session_data["cookies"])
                    if isinstance(cookies_list, list):
                        for cookie in cookies_list:
                            page.set.cookies(cookie)
                except Exception:
                    pass
            
            # Tải lại trang để áp dụng session và bỏ qua Login
            page.refresh()
            time.sleep(2)
            
            # Xác nhận xem có nút Textarea đăng bài không để đảm bảo đã đăng nhập thành công
            if page.ele("tag:textarea"):
                print("[+] Đăng nhập bằng Cookies thành công!")
                logged_in = True
            else:
                print("[-] Cookies đã hết hạn hoặc không còn hiệu lực. Đang đăng nhập lại bằng mật khẩu...")

        if not logged_in:
            # Thực hiện đăng nhập bằng form thông thường
            print("[*] Đang điều hướng tới trang đăng nhập...")
            page.get(f"{FRONTEND_URL}/login")
            time.sleep(1.5)
            
            # Điền thông tin đăng nhập
            print(f"[*] Điền thông tin đăng nhập cho user: {username}")
            page.ele("#identity").input(username)
            page.ele("#password").input(password)
            
            # Click Đăng nhập
            login_btn = page.ele("text=Đăng nhập") or page.ele("tag:button")
            login_btn.click()
            
            print("[*] Đang đợi đăng nhập hoàn tất...")
            # Đợi cho tới khi xuất hiện ô soạn thảo bài viết của Trang Chủ
            page.wait.ele_displayed("tag:textarea", timeout=10)
            
            if page.ele("tag:textarea"):
                print("[+] Đăng nhập thành công!")
                logged_in = True
                
                # Trích xuất và sao lưu cookies/localStorage
                print("[*] Đang lưu trữ session cookies vào database...")
                cookies = page.cookies()
                # Lấy dữ liệu localStorage dạng chuỗi JSON
                local_storage = page.run_js("return JSON.stringify(localStorage);")
                save_cookies_to_db(username, cookies, local_storage)
            else:
                print("[-] Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin credentials.")
                return

        # 2. Thực hiện Quy trình Tự động hóa
        tweets_posted = 0
        tweets_liked = 0
        
        print("\n================== BẮT ĐẦU AUTOMATION ==================")
        
        while tweets_posted < 2 or tweets_liked < 3:
            # A. Tự động đăng bài viết (Target: 2 bài)
            if tweets_posted < 2:
                print(f"\n[*] Tiến hành viết bài đăng số {tweets_posted + 1}...")
                textarea = page.ele("tag:textarea")
                tweet_content = f"Bài đăng tự động số {tweets_posted + 1} gửi từ DrissionPage lúc {datetime.now().strftime('%H:%M:%S')}!"
                textarea.input(tweet_content)
                time.sleep(0.5)
                
                post_btn = page.ele("text=Đăng")
                post_btn.click()
                print(f"[+] Đã gửi yêu cầu đăng bài số {tweets_posted + 1}.")
                
                time.sleep(2)  # Đợi API hoàn thành
                tweets_posted += 1
                print(f"[+] Bài viết thành công. Đếm bài đăng: {tweets_posted}/2")
                
            # B. Tự động thả tim bài viết trên Newfeed (Target: 3 bài)
            if tweets_liked < 3:
                print(f"\n[*] Đang quét các bài đăng trên Newsfeed để thả tim...")
                
                # Quét tất cả các phần tử có chứa biểu tượng ❤️
                heart_spans = page.eles("text:❤️")
                like_clicked_this_loop = False
                
                for span in heart_spans:
                    # Like button là phần tử cha của span chứa ❤️
                    parent_btn = span.parent()
                    btn_class = parent_btn.attr("class") or ""
                    
                    # Nếu nút chưa được like (chứa text-gray-500 thay vì text-red-500)
                    if "text-red-500" not in btn_class:
                        print(f"[*] Thả tim bài viết chưa tương tác...")
                        # Cuộn tới phần tử để nhấp chuột an toàn
                        parent_btn.scroll.to_see()
                        time.sleep(0.5)
                        parent_btn.click()
                        
                        tweets_liked += 1
                        print(f"[+] Thả tim thành công. Đếm thả tim: {tweets_liked}/3")
                        like_clicked_this_loop = True
                        time.sleep(1.5)  # Đợi Snappy UI cập nhật
                        
                        if tweets_liked == 3:
                            break
                
                if not like_clicked_this_loop and tweets_liked < 3:
                    print("[-] Không quét thêm được bài đăng mới chưa thả tim. Đang cuộn xuống để tải thêm...")
                    page.scroll.down(600)
                    time.sleep(2)

        print("\n================== HOÀN THÀNH AUTOMATION ==================")
        print(f"[+] Đã hoàn thành mục tiêu: Đăng {tweets_posted}/2 bài viết và Thả tim {tweets_liked}/3 bài viết.")
        print("[*] Chương trình sẽ dừng lại sau 5 giây...")
        time.sleep(5)

    except Exception as ex:
        print(f"\n[-] Đã xảy ra lỗi trong quá trình tự động hóa: {ex}")
    finally:
        print("[*] Đang đóng trình duyệt...")
        page.quit()

if __name__ == "__main__":
    main()
