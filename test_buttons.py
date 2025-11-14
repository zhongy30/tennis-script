#!/usr/bin/env python3
"""
按钮点击测试脚本
测试 book 和 confirm 按钮的点击成功率
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
try:
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
import time
from datetime import datetime


def setup_driver(use_existing_browser=True):
    """设置 Edge WebDriver"""
    edge_options = Options()
    
    if use_existing_browser:
        edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        print("正在连接到已打开的 Edge 浏览器...")
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    service = Service(EdgeChromiumDriverManager().install())
                    driver = webdriver.Edge(service=service, options=edge_options)
                except:
                    driver = webdriver.Edge(options=edge_options)
            else:
                driver = webdriver.Edge(options=edge_options)
            
            print("✅ 已连接到现有浏览器")
            return driver
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("\n请确保已使用以下命令启动 Edge：")
            print('"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug"')
            raise
    else:
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                service = Service(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=edge_options)
            except:
                driver = webdriver.Edge(options=edge_options)
        else:
            driver = webdriver.Edge(options=edge_options)
        
        driver.maximize_window()
        return driver


def find_and_click_book_button(driver):
    """查找并点击 book 按钮"""
    print("\n" + "-"*60)
    print("测试 Book 按钮")
    print("-"*60)
    
    selectors = [
        "//button[contains(text(), 'Book')]",
        "//button[contains(text(), 'book')]",
        "button[class*='book']",
        "button[id*='book']",
        "button[type='submit']",
        "input[type='submit'][value*='Book']",
    ]
    
    for selector in selectors:
        try:
            if selector.startswith("//"):
                button = driver.find_element(By.XPATH, selector)
            else:
                button = driver.find_element(By.CSS_SELECTOR, selector)
            
            if button.is_displayed() and button.is_enabled():
                button_text = button.text.strip() or button.get_attribute("value") or "预订按钮"
                button_id = button.get_attribute("id") or "无ID"
                button_class = button.get_attribute("class") or "无class"
                location = button.location
                size = button.size
                
                print(f"✅ 找到 Book 按钮")
                print(f"   文本: {button_text}")
                print(f"   ID: {button_id}")
                print(f"   Class: {button_class}")
                print(f"   选择器: {selector}")
                print(f"   位置: x={location['x']}, y={location['y']}")
                print(f"   大小: width={size['width']}, height={size['height']}")
                print(f"   正在点击...")
                
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)
                print("✅ 已点击 Book 按钮")
                return True, selector
        except Exception as e:
            print(f"   选择器 {selector} 失败: {str(e)[:50]}")
            continue
    
    print("❌ 未找到 Book 按钮")
    return False, None


def find_and_click_confirm_button(driver):
    """查找并点击 confirm 按钮"""
    print("\n" + "-"*60)
    print("测试 Confirm 按钮")
    print("-"*60)
    
    time.sleep(0.5)  # 等待弹出窗口出现
    
    confirm_selectors = [
        "//button[contains(text(), 'Confirm')]",
        "//button[contains(text(), 'confirm')]",
        "//button[contains(text(), '确认')]",
        "//button[contains(text(), 'OK')]",
        "//button[contains(text(), 'Yes')]",
        "button[class*='confirm']",
        "button[id*='confirm']",
        ".confirm-button",
        "#confirm",
    ]
    
    for selector in confirm_selectors:
        try:
            if selector.startswith("//"):
                button = driver.find_element(By.XPATH, selector)
            else:
                button = driver.find_element(By.CSS_SELECTOR, selector)
            
            if button.is_displayed() and button.is_enabled():
                button_text = button.text.strip() or "按钮"
                button_id = button.get_attribute("id") or "无ID"
                button_class = button.get_attribute("class") or "无class"
                location = button.location
                size = button.size
                
                print(f"✅ 找到 Confirm 按钮")
                print(f"   文本: {button_text}")
                print(f"   ID: {button_id}")
                print(f"   Class: {button_class}")
                print(f"   选择器: {selector}")
                print(f"   位置: x={location['x']}, y={location['y']}")
                print(f"   大小: width={size['width']}, height={size['height']}")
                print(f"   正在点击...")
                
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)
                print("✅ 已点击 Confirm 按钮")
                return True, selector
        except Exception as e:
            print(f"   选择器 {selector} 失败: {str(e)[:50]}")
            continue
    
    # 尝试查找所有弹出窗口
    print("⚠️  未找到 Confirm 按钮，尝试查找弹出窗口...")
    try:
        dialogs = driver.find_elements(By.CSS_SELECTOR, 
            "div[role='dialog'], .modal, .popup, [class*='dialog'], [class*='modal']")
        
        if dialogs:
            print(f"   找到 {len(dialogs)} 个可能的弹出窗口")
            for i, dialog in enumerate(dialogs, 1):
                if dialog.is_displayed():
                    print(f"   弹出窗口 {i}:")
                    buttons = dialog.find_elements(By.TAG_NAME, "button")
                    print(f"     找到 {len(buttons)} 个按钮")
                    for btn in buttons:
                        if btn.is_displayed():
                            btn_text = btn.text.strip() or "按钮"
                            print(f"       - {btn_text}")
    except:
        pass
    
    print("❌ 未找到 Confirm 按钮")
    return False, None


def run_single_test(driver, test_number):
    """运行单次测试"""
    print(f"\n{'='*60}")
    print(f"测试 #{test_number}")
    print(f"{'='*60}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试 Book 按钮
    book_success, book_selector = find_and_click_book_button(driver)
    
    if not book_success:
        return {
            'test_number': test_number,
            'book_success': False,
            'book_selector': None,
            'confirm_success': False,
            'confirm_selector': None,
            'timestamp': datetime.now()
        }
    
    # 测试 Confirm 按钮
    confirm_success, confirm_selector = find_and_click_confirm_button(driver)
    
    return {
        'test_number': test_number,
        'book_success': book_success,
        'book_selector': book_selector,
        'confirm_success': confirm_success,
        'confirm_selector': confirm_selector,
        'timestamp': datetime.now()
    }


def print_statistics(results):
    """打印统计信息"""
    print("\n" + "="*60)
    print("测试统计")
    print("="*60)
    
    total_tests = len(results)
    book_successes = sum(1 for r in results if r['book_success'])
    confirm_successes = sum(1 for r in results if r['book_success'] and r['confirm_success'])
    
    book_rate = (book_successes / total_tests * 100) if total_tests > 0 else 0
    confirm_rate = (confirm_successes / book_successes * 100) if book_successes > 0 else 0
    overall_rate = (confirm_successes / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n总测试次数: {total_tests}")
    print(f"\nBook 按钮:")
    print(f"  成功: {book_successes}/{total_tests}")
    print(f"  成功率: {book_rate:.1f}%")
    
    print(f"\nConfirm 按钮 (在 Book 成功的前提下):")
    print(f"  成功: {confirm_successes}/{book_successes}")
    print(f"  成功率: {confirm_rate:.1f}%")
    
    print(f"\n整体成功率 (Book + Confirm):")
    print(f"  成功: {confirm_successes}/{total_tests}")
    print(f"  成功率: {overall_rate:.1f}%")
    
    # 显示最成功的选择器
    if book_successes > 0:
        book_selectors = {}
        for r in results:
            if r['book_success'] and r['book_selector']:
                selector = r['book_selector']
                book_selectors[selector] = book_selectors.get(selector, 0) + 1
        
        if book_selectors:
            best_book_selector = max(book_selectors.items(), key=lambda x: x[1])
            print(f"\n最成功的 Book 选择器: {best_book_selector[0]} ({best_book_selector[1]} 次)")
    
    if confirm_successes > 0:
        confirm_selectors = {}
        for r in results:
            if r['confirm_success'] and r['confirm_selector']:
                selector = r['confirm_selector']
                confirm_selectors[selector] = confirm_selectors.get(selector, 0) + 1
        
        if confirm_selectors:
            best_confirm_selector = max(confirm_selectors.items(), key=lambda x: x[1])
            print(f"最成功的 Confirm 选择器: {best_confirm_selector[0]} ({best_confirm_selector[1]} 次)")
    
    # 显示详细结果
    print(f"\n详细结果:")
    print("-"*60)
    for r in results:
        status = "✅" if (r['book_success'] and r['confirm_success']) else ("⚠️" if r['book_success'] else "❌")
        print(f"{status} 测试 #{r['test_number']}: Book={r['book_success']}, Confirm={r['confirm_success']}")


def main():
    """主函数"""
    # ========== 配置参数 ==========
    USE_EXISTING_BROWSER = True  # 使用已打开的浏览器
    NUM_TESTS = 10  # 测试次数
    TEST_INTERVAL = 2  # 每次测试间隔（秒）
    
    print("="*60)
    print("按钮点击测试脚本")
    print("="*60)
    print(f"\n将运行 {NUM_TESTS} 次测试")
    print(f"每次测试间隔 {TEST_INTERVAL} 秒")
    print("\n请确保：")
    print("1. 已在浏览器中登录并打开预订页面")
    print("2. 已选择好要预订的日期")
    print("3. 页面已准备好（可以手动选择一些时间段）")
    print("\n脚本立即开始...")
    print("="*60)
    
    driver = None
    results = []
    
    try:
        driver = setup_driver(use_existing_browser=USE_EXISTING_BROWSER)
        
        # 显示当前页面信息
        current_url = driver.current_url
        print(f"\n当前页面: {current_url}")
        print(f"页面标题: {driver.title}\n")
        
        # 运行多次测试
        for i in range(1, NUM_TESTS + 1):
            result = run_single_test(driver, i)
            results.append(result)
            
            if i < NUM_TESTS:
                print(f"\n等待 {TEST_INTERVAL} 秒后进行下一次测试...")
                time.sleep(TEST_INTERVAL)
        
        # 打印统计信息
        print_statistics(results)
        
        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        print("\n浏览器将保持打开...")
        
    except KeyboardInterrupt:
        print("\n\n用户取消")
        if results:
            print_statistics(results)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if results:
            print_statistics(results)
    # 不关闭浏览器


if __name__ == "__main__":
    main()

