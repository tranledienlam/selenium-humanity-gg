import argparse
import time
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility
from googl import Auto as Google_auto, Setup as Google_setup

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.google_setup = Google_setup(node, profile)
        
    def _run(self):
        self.google_setup._run()

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.google_auto = Google_auto(node, profile)
        self.node = node
        self.profile_name = profile.get('profile_name')
    
    def is_login(self):
        answer = self.node.ask_ai(prompt="Đã đăng nhập chưa? chỉ trả lời 0 hoặc 1, 0 - Chưa đăng nhập, 1 - đã đăng nhập, 1 - nếu trang đang load, 2 - Nếu trang có xuất hiện popup ")
        is_login = False
        
        if answer is None:
            if self.node.find(By.XPATH, '//span[text()="Balance"]') or self.node.find(By.XPATH, '//h2[text()="Welcome to Humanity Protocol"]'):
                self.node.log("Đã đăng nhập tài khoản humanity")
                if self.node.find(By.XPATH, '//h2[text()="Welcome to Humanity Protocol"]', timeout=20):
                    self.node.find_and_click(By.CSS_SELECTOR, 'button[aria-label="Close"]')

                is_login = True
            else:
                self.node.log("Chưa đăng nhập tài khoản humanity")
                is_login = False
        elif "0" in answer:
            is_login = False
            self.node.log("Chưa đăng nhập tài khoản humanity")
        elif "1" in answer:
            is_login = True
            self.node.log("Đã đăng nhập tài khoản humanity")
        elif "2" in answer:
            is_login = True
            self.node.find_and_click(By.CSS_SELECTOR, 'button[aria-label="Close"]')
        else:
            self.node.snapshot(f"AI đã trả lời: {answer}")
        
        return is_login
    
    def claim(self):
        xpath_btn = '//div[div[div[h3[text()="Daily Rewards"]]]]/button'
        time_out = 60 + time.time()
        while time.time() < time_out:
            js = f'''
                const result = document.evaluate('{xpath_btn}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                const button = result.singleNodeValue;
                if (button) {{
                    return button.innerText.trim().toLowerCase();
                }} else {{
                    return null;
                }};
            '''
            text_btn = self.driver.execute_script(js)
            if text_btn:
                lowered = text_btn.strip().lower()
                if lowered == "Claim".lower():
                    self.node.find_and_click(By.XPATH, xpath_btn)
                elif lowered == "Until Next Claim".lower():
                    return True
                elif lowered == "Loading...".lower():
                    Utility.wait_time(5)
            else:
                return False
            
        return False
            
    def _run(self):
        self.google_auto._run()
        self.node.go_to('https://testnet.humanity.org/login?ref=tranlamvpn')
        
        # Đăng nhập
        if not self.is_login():
            self.node.find_and_click(By.CSS_SELECTOR, "a[href*='oauth/google']")
            Utility.wait_time(10)
            if not self.is_login():
                self.node.snapshot(f'login thất bại')

        if self.claim():
            self.node.snapshot(f'Đã nhận thưởng thành công')
        else:
            self.node.snapshot(f'Nhận thưởng thất bại')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    
    profiles = Utility.get_data('profile_name', 'email', 'password')
    if not profiles:
        print("Thực hiện fake data")
        # Fake profile data khi file data.txt rỗng hoặc không tồn tại
        profiles = Utility.fake_data('profile_name', 30)
        browser_manager.run_fake_data(
            profiles=profiles,
            max_concurrent_profiles=8,
            block_media=True,
            headless=args.headless,
            disable_gpu=args.disable_gpu,
        )
    else:
        browser_manager.run_terminal(
            profiles=profiles,
            max_concurrent_profiles=4,
            block_media=True,
            auto=args.auto,
            headless=args.headless,
            disable_gpu=args.disable_gpu,
        )