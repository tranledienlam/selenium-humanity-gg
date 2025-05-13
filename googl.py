#version browser_automation 04/04/2025
import argparse
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
    def _run(self):
        # Kiểm tra đăng nhập Google
        self.node.go_to('https://accounts.google.com/signin')

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.password = profile.get('password')

    def _run(self):
        '''Thực hiện đăng nhập tài khảon Google'''
        if not self.email:
            self.node.snapshot(f'Không tồn tại thông tin email trong data.txt')
        if not self.password:
            self.node.snapshot(f'Không tồn tại thông tin mật khẩu trong data.txt')

        self.node.go_to('https://accounts.google.com/signin')
        
        # Đợi và kiểm tra xem đã đăng nhập chưa bằng cách tìm avatar hoặc email hiển thị
        if self.node.find(By.CSS_SELECTOR, '[aria-label*="@gmail.com"]'):
            self.node.log('✅ Đã đăng nhập Google')
            return True
            
        # Nếu chưa đăng nhập, thực hiện đăng nhập
        self.node.log('⚠️ Chưa đăng nhập Google, đang thực hiện đăng nhập...')
        
        # Nhập email
        if not self.node.find_and_input(By.CSS_SELECTOR, 'input[type="email"]', self.email, None, 0.1):
            self.node.snapshot('Không tìm thấy ô nhập email')
            return
            
        # Click nút Next
        if not self.node.press_key('Enter'):
            self.node.snapshot('Không thể nhấn nút Enter')
            return
            
        # Đợi và nhập mật khẩu
        if not self.node.find_and_input(By.CSS_SELECTOR, 'input[type="password"]', self.password, None, 0.1):
            self.node.snapshot('Không tìm thấy ô nhập mật khẩu')
            return
            
        # Click nút Next
        if not self.node.press_key('Enter'):
            self.node.snapshot('Không thể nhấn nút Enter')
            return
        
        # Thỉnh thoảng nó sẽ hỏi đoạn này passkeys
        if self.node.find(By.XPATH, '//div[text()="With passkeys, your device will simply ask you for your Windows PIN or biometric and let Google know it\'s really you signing in"]', timeout=15):
            self.node.log('🔄 Đang thực hiện xác thực bằng passkey...')
            if not self.node.find_and_click(By.XPATH, '//span[text()="Not now"]'):
                self.node.snapshot('Không tìm thấy nút "Skip"')
                return
            self.node.find_and_click(By.XPATH, '//span[text()="Cancel"]')
        # Đợi và kiểm tra đăng nhập thành công
        if self.node.find(By.CSS_SELECTOR, '[aria-label*="@gmail.com"]'):
            self.node.log('✅ Đăng nhập Google thành công')
        else:
            self.node.snapshot('Không thể xác nhận đăng nhập thành công')
            return
        
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.get_data('profile_name', 'email', 'password')
    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=1,
        block_media=True,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
    )