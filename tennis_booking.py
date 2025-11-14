#!/usr/bin/env python3
"""
网球场快速预订脚本
在已登录的预订页面上快速选择时间段并点击预订按钮
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


def setup_driver(use_existing_browser=True):
    """
    设置 Edge WebDriver
    
    Args:
        use_existing_browser: 是否使用已打开的浏览器（True）或打开新浏览器（False）
    """
    edge_options = Options()
    
    if use_existing_browser:
        # 连接到已存在的 Edge 浏览器
        # 使用远程调试端口连接到已打开的浏览器
        edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        print("正在连接到已打开的 Edge 浏览器...")
        
        try:
            # 不需要启动新的浏览器，直接连接
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
            print("\n" + "="*60)
            print("解决方案：")
            print("="*60)
            print("\n1. 首先关闭所有 Edge 浏览器窗口")
            print("2. 使用以下命令启动 Edge（远程调试模式）：")
            print("\n   macOS:")
            print('   "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug"')
            print("\n   或者运行启动脚本：")
            print("   ./start_edge.sh")
            print("\n3. 在启动的浏览器中登录并打开预订页面")
            print("4. 然后再次运行此脚本")
            print("\n" + "="*60)
            raise
    else:
        # 打开新的浏览器窗口
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


def is_time_in_range(time_slot, start_hour=12, end_hour=18):
    """
    检查时间段是否在指定范围内（12:00pm - 6:00pm）
    
    Args:
        time_slot: 时间段字符串，如 "3:00pm - 4:00pm" 或 "3:00pm"
        start_hour: 开始小时（24小时制），默认12（12:00pm）
        end_hour: 结束小时（24小时制），默认18（6:00pm）
    
    Returns:
        True 如果在范围内，False 如果不在
    """
    try:
        # 提取时间段中的小时
        time_lower = time_slot.lower()
        
        # 提取所有时间（如 "3:00pm", "4:00pm"）
        import re
        time_pattern = r'(\d{1,2}):\d{2}\s*(am|pm)'
        times = re.findall(time_pattern, time_lower)
        
        if not times:
            return False
        
        # 检查是否有任何时间在范围内
        for hour_str, period in times:
            hour = int(hour_str)
            
            # 转换为24小时制
            if period == 'pm' and hour != 12:
                hour_24 = hour + 12
            elif period == 'am' and hour == 12:
                hour_24 = 0
            else:
                hour_24 = hour
            
            # 检查是否在范围内（12:00pm - 6:00pm，即12-18点）
            if start_hour <= hour_24 < end_hour:
                return True
        
        return False
    except:
        return False


def find_available_slots(driver, time_range_start=14, time_range_end=21):
    """
    查找所有可用的时间段（2:00pm - 9:00pm）
    只查找真正包含时间信息的元素，排除球场号、预订标签等
    
    Args:
        driver: WebDriver 实例
        time_range_start: 开始小时（24小时制），默认14（2:00pm）
        time_range_end: 结束小时（24小时制），默认21（9:00pm）
    
    Returns:
        可用时间段列表
    """
    print(f"正在查找可用时间段（2:00pm - 9:00pm）...")
    time.sleep(2)  # 增加等待时间，确保页面完全加载
    
    available_slots = []
    
    # 策略1: 查找包含时间信息的可点击元素
    print("策略1: 查找包含时间信息的可点击元素...")
    try:
        # 查找表格中的所有单元格和可点击元素
        all_cells = driver.find_elements(By.CSS_SELECTOR, "td, button, div[role='button'], a[role='button']")
        print(f"  找到 {len(all_cells)} 个可能的元素")
        
        for cell in all_cells:
            try:
                if not cell.is_displayed():
                    continue
                
                # 获取元素信息
                text = cell.text.strip()
                classes = cell.get_attribute("class") or ""
                onclick = cell.get_attribute("onclick")
                data_time = cell.get_attribute("data-time")
                title = cell.get_attribute("title")
                
                # 排除明显不可用的元素
                if any(keyword in classes.lower() for keyword in ["unavailable", "booked", "reserved", "disabled"]):
                    continue
                
                # 排除纯数字（球场号）
                if text.isdigit():
                    continue
                
                # 排除包含"reserved"的文本
                if text and "reserved" in text.lower():
                    continue
                
                # 必须包含时间信息（包含冒号或am/pm）
                time_slot = data_time or title or text or ""
                has_time = time_slot and (":" in time_slot or "am" in time_slot.lower() or "pm" in time_slot.lower())
                
                # 必须有时间信息才考虑
                if has_time:
                    # 检查时间范围（12:00pm - 6:00pm）
                    if is_time_in_range(time_slot, time_range_start, time_range_end):
                        # 检查是否可点击
                        is_clickable = cell.is_enabled() and (onclick or cell.tag_name in ['button', 'a'])
                        if is_clickable or cell.tag_name == 'td':  # td可能通过onclick点击
                            available_slots.append((cell, time_slot))
                            if len(available_slots) <= 10:  # 只打印前几个用于调试
                                print(f"  找到: {time_slot[:50]}")
            except:
                continue
    except Exception as e:
        print(f"  策略1失败: {e}")
    
    # 策略2: 如果策略1没找到，尝试更具体的选择器
    if not available_slots:
        print("策略2: 使用特定选择器查找时间段...")
        selectors = [
            "td[onclick][data-time]",  # 有onclick和data-time的td
            "td[onclick]",  # 有onclick的td
            "button[data-time]",  # 有data-time的button
            "[data-time]",  # 任何有data-time的元素
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  选择器 {selector}: 找到 {len(elements)} 个元素")
                for elem in elements:
                    if elem.is_displayed():
                        text = elem.text.strip()
                        time_slot = elem.get_attribute("data-time") or text
                        
                        # 排除纯数字和reserved
                        if time_slot and not time_slot.isdigit() and "reserved" not in time_slot.lower():
                            # 必须包含时间信息
                            if ":" in time_slot or "am" in time_slot.lower() or "pm" in time_slot.lower():
                                # 检查时间范围
                                if is_time_in_range(time_slot, time_range_start, time_range_end):
                                    available_slots.append((elem, time_slot))
                                    if len(available_slots) <= 5:
                                        print(f"    找到: {time_slot[:50]}")
            except Exception as e:
                print(f"  选择器 {selector} 失败: {e}")
                continue
    
    # 策略3: 调试模式 - 如果还是没找到，显示所有可点击的元素供调试
    if not available_slots:
        print("\n⚠️  策略3: 未找到时间段，显示所有可点击元素进行调试...")
        try:
            clickable_elements = driver.find_elements(By.CSS_SELECTOR, "td[onclick], button[onclick]")
            print(f"  找到 {len(clickable_elements)} 个可点击元素")
            
            for i, elem in enumerate(clickable_elements[:20], 1):  # 只显示前20个
                if elem.is_displayed():
                    text = elem.text.strip()
                    classes = elem.get_attribute("class") or ""
                    data_time = elem.get_attribute("data-time") or ""
                    title = elem.get_attribute("title") or ""
                    onclick = elem.get_attribute("onclick") or ""
                    
                    print(f"\n  元素 {i}:")
                    print(f"    标签: {elem.tag_name}")
                    print(f"    文本: {text[:50] if text else '(无)'}")
                    print(f"    Class: {classes[:50] if classes else '(无)'}")
                    print(f"    data-time: {data_time[:50] if data_time else '(无)'}")
                    print(f"    title: {title[:50] if title else '(无)'}")
                    print(f"    onclick: {onclick[:80] if onclick else '(无)'}")
        except Exception as e:
            print(f"  调试信息获取失败: {e}")
    
    # 去重（基于元素对象）
    unique_slots = []
    seen_elements = set()
    for elem, slot in available_slots:
        elem_id = id(elem)  # 使用元素的内存地址作为唯一标识
        if elem_id not in seen_elements:
            seen_elements.add(elem_id)
            unique_slots.append((elem, slot))
    
    available_slots = unique_slots
    
    print(f"\n找到 {len(available_slots)} 个可用时间段（2:00pm - 9:00pm）")
    if available_slots:
        print("可用时间段列表（前10个）：")
        for i, (_, slot) in enumerate(available_slots[:10], 1):
            print(f"  {i}. {slot[:60]}")
        if len(available_slots) > 10:
            print(f"  ... 还有 {len(available_slots) - 10} 个时间段")
    else:
        print("\n" + "="*60)
        print("⚠️  未找到任何可用时间段")
        print("="*60)
        print("可能的原因：")
        print("1. 当前日期没有可用时间段")
        print("2. 所有时间段都已被预订")
        print("3. 需要在网页上先选择日期")
        print("4. 页面结构与脚本不匹配")
        print("\n建议：")
        print("- 检查网页上是否显示可用时间段")
        print("- 尝试在网页上手动选择一个时间段，看看元素结构")
        print("- 查看上方的调试信息，了解页面上的实际元素")
        print("="*60)
    
    return available_slots


def is_button_clickable(button):
    """
    检查按钮是否可以点击（绿色空心圆圈）
    
    Args:
        button: 按钮元素
    
    Returns:
        True 如果可以点击（绿色空心圆圈），False 如果不可点击（灰色）
    """
    try:
        # 检查按钮是否被禁用
        if not button.is_enabled():
            return False
        
        # 获取按钮的样式信息
        classes = button.get_attribute("class") or ""
        style = button.get_attribute("style") or ""
        
        # 检查是否有灰色/禁用相关的 class
        if any(keyword in classes.lower() for keyword in ["disabled", "gray", "grey", "unavailable", "inactive"]):
            return False
        
        # 检查背景色（灰色通常表示不可用）
        if "gray" in style.lower() or "grey" in style.lower():
            return False
        
        # 检查是否有绿色相关的 class（绿色空心圆圈）
        if any(keyword in classes.lower() for keyword in ["green", "available", "circle", "hollow"]):
            return True
        
        # 检查背景色是否为绿色
        if "green" in style.lower():
            return True
        
        # 如果按钮可见且可点击，且没有灰色标识，假设可以点击
        # 但需要进一步检查是否已经是选中状态（绿色正方形）
        # 如果已经是绿色正方形（selected），不应该再次点击
        if any(keyword in classes.lower() for keyword in ["selected", "active", "square"]):
            # 检查是否是绿色正方形（已选中状态）
            if "green" in classes.lower() or "green" in style.lower():
                return False  # 已经是选中状态，不需要再点击
        
        # 默认：如果按钮可见且可点击，尝试点击
        return True
    except:
        return False


def click_court_number_buttons(driver, court_numbers=[6, 7, 8, 9, 10], target_court=None, stop_on_first=True):
    """
    点击时间段上的球场号按钮（6-10），只点击绿色空心圆圈的按钮
    如果找到可点击的按钮，立即停止搜索
    
    Args:
        driver: WebDriver 实例
        court_numbers: 要选择的球场号列表，默认 [6, 7, 8, 9, 10]
        target_court: 目标球场号（如果指定，只点击这个球场号）
        stop_on_first: 找到第一个可点击的按钮后立即停止，默认True
    
    Returns:
        成功点击的球场号，如果没有则返回None
    """
    print("\n正在查找可点击的球场号按钮（6-10，绿色空心圆圈）...")
    time.sleep(0.5)  # 增加等待时间，确保按钮出现
    
    courts_to_check = [target_court] if target_court else court_numbers
    
    # 策略1: 先找到所有包含数字的按钮
    print("查找所有数字按钮...")
    all_buttons = []
    try:
        # 查找所有按钮
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.is_displayed():
                text = btn.text.strip()
                # 检查是否是数字按钮（6-10）
                if text.isdigit():
                    num = int(text)
                    if num in courts_to_check:
                        all_buttons.append((num, btn))
    except Exception as e:
        print(f"  查找按钮时出错: {e}")
    
    # 如果没找到，尝试其他选择器
    if not all_buttons:
        print("尝试使用选择器查找...")
        for court_num in courts_to_check:
            if court_num is None:
                continue
            selectors = [
                f"//button[text()='{court_num}']",
                f"//button[contains(text(), '{court_num}')]",
                f"button[data-court='{court_num}']",
                f"button[data-court-number='{court_num}']",
            ]
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        button = driver.find_element(By.XPATH, selector)
                    else:
                        button = driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        all_buttons.append((court_num, button))
                        break
                except:
                    continue
    
    print(f"找到 {len(all_buttons)} 个可能的球场号按钮")
    
    # 检查每个按钮是否可以点击，找到第一个可点击的就立即返回
    for court_num, button in all_buttons:
        try:
            button_text = button.text.strip()
            button_class = button.get_attribute("class") or ""
            style = button.get_attribute("style") or ""
            
            print(f"\n检查球场 {court_num} 按钮:")
            print(f"  文本: {button_text}")
            print(f"  Class: {button_class[:80]}")
            print(f"  Style: {style[:80] if style else '无'}")
            print(f"  可点击: {button.is_enabled()}")
            
            # 检查按钮状态
            if is_button_clickable(button):
                location = button.location
                size = button.size
                print(f"  ✅ 找到可点击的按钮（绿色空心圆圈）")
                print(f"  位置: x={location['x']}, y={location['y']}")
                print(f"  大小: width={size['width']}, height={size['height']}")
                print(f"  正在点击...")
                
                driver.execute_script("arguments[0].click();", button)
                print(f"  ✅ 已点击球场 {court_num} 按钮（应变为绿色正方形）")
                time.sleep(0.3)  # 等待状态变化
                
                # 找到可点击的按钮后立即返回
                if stop_on_first:
                    print(f"\n✅ 找到可点击按钮，立即停止搜索")
                    return court_num
            else:
                print(f"  ⚠️  不可点击（灰色或已选中）")
        except Exception as e:
            print(f"  处理按钮时出错: {e}")
            continue
    
    print(f"\n⚠️  未找到可点击的球场号按钮")
    return None


def format_time_slot(time_slot):
    """
    格式化时间段显示
    
    Args:
        time_slot: 时间段字符串
    
    Returns:
        格式化后的时间段字符串
    """
    # 如果已经是标准格式，直接返回
    if "-" in time_slot:
        return time_slot.strip()
    
    # 如果只有开始时间，尝试构造完整时间段
    # 例如 "3:00pm" -> "3:00pm - 4:00pm"
    try:
        import re
        match = re.search(r'(\d{1,2}):\d{2}\s*(am|pm)', time_slot.lower())
        if match:
            hour_str, period = match.groups()
            hour = int(hour_str)
            
            # 计算下一个小时
            if period == 'pm' and hour != 12:
                next_hour = hour + 1
                if next_hour > 12:
                    next_hour = next_hour - 12
                    next_period = 'pm'
                else:
                    next_period = 'pm'
            elif period == 'am':
                next_hour = hour + 1
                if next_hour >= 12:
                    next_hour = next_hour - 12 if next_hour > 12 else 12
                    next_period = 'pm'
                else:
                    next_period = 'am'
            else:  # 12pm
                next_hour = 1
                next_period = 'pm'
            
            return f"{time_slot.strip()} - {next_hour}:00{next_period}"
    except:
        pass
    
    return time_slot.strip()


def find_consecutive_slots(available_slots, num_consecutive=2):
    """
    查找连续的时间段
    
    Args:
        available_slots: 可用时间段列表 [(element, time_slot), ...]
        num_consecutive: 需要的连续时间段数量
    
    Returns:
        连续时间段列表，如果找到；否则返回None
    """
    import re
    
    # 提取时间段的小时信息
    def extract_hour(time_slot):
        match = re.search(r'(\d{1,2}):\d{2}\s*(am|pm)', time_slot.lower())
        if match:
            hour_str, period = match.groups()
            hour = int(hour_str)
            # 转换为24小时制
            if period == 'pm' and hour != 12:
                return hour + 12
            elif period == 'am' and hour == 12:
                return 0
            return hour
        return None
    
    # 为每个时间段提取小时
    slots_with_hours = []
    for elem, slot in available_slots:
        hour = extract_hour(slot)
        if hour is not None:
            slots_with_hours.append((elem, slot, hour))
    
    # 按小时排序
    slots_with_hours.sort(key=lambda x: x[2])
    
    # 查找连续的时间段
    for i in range(len(slots_with_hours) - num_consecutive + 1):
        consecutive = [slots_with_hours[i]]
        for j in range(i + 1, len(slots_with_hours)):
            if slots_with_hours[j][2] == consecutive[-1][2] + 1:
                consecutive.append(slots_with_hours[j])
                if len(consecutive) == num_consecutive:
                    # 找到连续时间段
                    return [(elem, slot) for elem, slot, _ in consecutive]
            else:
                break
    
    return None


def select_slots(driver, num_slots, preferred_times=None):
    """
    选择指定数量的时间段，每个时间段为1小时，在2:00pm - 9:00pm之间
    优先选择连续的时间段，如果没有连续的，则降级为选择1个时间段
    
    Args:
        driver: WebDriver 实例
        num_slots: 要预订的时间段数量（每个时间段是1小时）
        preferred_times: 首选时间段列表
    
    Returns:
        (成功, 实际选择的数量)
    """
    # 只查找2:00pm - 9:00pm之间的时间段
    available_slots = find_available_slots(driver, time_range_start=14, time_range_end=21)
    
    if len(available_slots) == 0:
        print(f"错误: 没有可用时间段")
        return False, 0
    
    # 优先查找连续时间段
    target_slots = []
    actual_num_slots = num_slots
    
    if num_slots >= 2:
        print(f"\n优先查找 {num_slots} 个连续时间段...")
        consecutive_slots = find_consecutive_slots(available_slots, num_slots)
        
        if consecutive_slots:
            print(f"✅ 找到 {num_slots} 个连续时间段！")
            target_slots = consecutive_slots
        else:
            print(f"⚠️  未找到 {num_slots} 个连续时间段，降级为选择 1 个时间段")
            actual_num_slots = 1
            target_slots = available_slots[:1]  # 只选择第一个
    else:
        target_slots = available_slots
        
    if len(target_slots) < actual_num_slots:
        print(f"错误: 可用时间段 ({len(target_slots)}) 少于所需数量 ({actual_num_slots})")
        return False, 0
    
    selected_count = 0
    selected_court = None  # 记录第一个选择的球场号
    selected_time_slots = []  # 记录所有选择的时间段
    
    print(f"\n{'='*60}")
    print(f"开始选择 {actual_num_slots} 个时间段")
    print(f"{'='*60}")
    
    # 遍历目标时间段并选择
    for elem, time_slot in target_slots:
        if selected_count >= actual_num_slots:
            break
        
        try:
            formatted_slot = format_time_slot(time_slot)
            print(f"\n正在选择时间段 {selected_count + 1}/{actual_num_slots}: {formatted_slot}")
            
            # 点击时间段（1小时）
            driver.execute_script("arguments[0].click();", elem)
            time.sleep(0.3)  # 等待按钮出现
            
            # 点击球场号按钮，如果已选择过球场号，使用相同的
            if selected_court:
                print(f"使用已选择的球场号: {selected_court}")
                clicked_court = click_court_number_buttons(driver, court_numbers=[6, 7, 8, 9, 10], target_court=selected_court, stop_on_first=True)
            else:
                clicked_court = click_court_number_buttons(driver, court_numbers=[6, 7, 8, 9, 10], stop_on_first=True)
                if clicked_court:
                    selected_court = clicked_court
                    print(f"\n📌 已选择球场号: {selected_court}，后续将选择相同的球场号")
            
            if clicked_court:
                selected_count += 1
                selected_time_slots.append((formatted_slot, clicked_court))
                print(f"✅ 已成功选择时间段 {selected_count}/{actual_num_slots}: {formatted_slot} (球场 {clicked_court})")
            else:
                print(f"⚠️  时间段 {formatted_slot} 已选择，但未找到可点击的球场号按钮")
        except Exception as e:
            print(f"选择时间段失败: {e}")
            continue
    
    # 显示所有选择的时间段
    if selected_time_slots:
        print(f"\n{'='*60}")
        print(f"已成功选择 {len(selected_time_slots)} 个时间段：")
        print(f"{'='*60}")
        for i, (slot, court) in enumerate(selected_time_slots, 1):
            print(f"  {i}. {slot} - 球场 {court}")
        print(f"{'='*60}")
    
    # 只要选择了至少1个时间段就算成功
    if selected_count >= actual_num_slots:
        print(f"\n✅ 成功选择了 {selected_count} 个时间段！")
        return True, selected_count
    else:
        print(f"\n❌ 只选择了 {selected_count}/{actual_num_slots} 个时间段，未达到要求")
        return False, selected_count


def is_blue_button_with_arrow(button):
    """
    检查按钮是否是蓝色长方形且包含箭头
    
    Args:
        button: 按钮元素
    
    Returns:
        True 如果是蓝色长方形且包含箭头
    """
    try:
        classes = button.get_attribute("class") or ""
        style = button.get_attribute("style") or ""
        text = button.text.strip() or ""
        inner_html = button.get_attribute("innerHTML") or ""
        
        # 排除球场号按钮（纯数字）
        if text.isdigit():
            return False
        
        # 排除disabled按钮
        if "disabled" in classes.lower():
            return False
        
        # 检查是否是蓝色
        is_blue = (
            "blue" in classes.lower() or
            "blue" in style.lower() or
            "rgb(0, 0, 255)" in style.lower() or
            "rgb(0,123,255)" in style.lower() or
            "#0066ff" in style.lower() or
            "#007bff" in style.lower() or
            "background-color: blue" in style.lower()
        )
        
        # 检查是否包含箭头
        has_arrow = (
            "arrow" in text.lower() or
            "arrow" in classes.lower() or
            "→" in text or
            ">" in text or
            "arrow" in inner_html.lower() or
            "→" in inner_html or
            ">" in inner_html or
            "▶" in text or
            "▶" in inner_html
        )
        
        # 检查是否是长方形（宽度明显大于高度，或者高度明显大于宽度）
        size = button.size
        is_rectangle = size['width'] > 50 and size['height'] > 20  # 长方形特征
        
        return is_blue and (has_arrow or is_rectangle)
    except:
        return False


def click_book_button(driver, test_mode=False):
    """
    点击预订按钮（蓝色长方形，带箭头，在列表右下角）
    
    Args:
        driver: WebDriver 实例
        test_mode: 测试模式，即使没有选择时间段也尝试点击
    
    Returns:
        是否成功点击预订按钮
    """
    print("\n" + "="*60)
    print("正在查找Book按钮（蓝色长方形，带箭头，右下角）...")
    print("="*60)
    
    # 策略1: 先找到所有可能的按钮
    all_buttons = []
    
    # 尝试多种选择器
    selectors = [
        "//button[contains(text(), 'Book')]",
        "//button[contains(text(), 'book')]",
        "button[class*='book']",
        "button[id*='book']",
        "button[type='submit']",
        "input[type='submit'][value*='Book']",
        "button",  # 所有按钮
        "a[role='button']",  # 链接样式的按钮
    ]
    
    for selector in selectors:
        try:
            if selector.startswith("//"):
                buttons = driver.find_elements(By.XPATH, selector)
            else:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    # 排除纯数字的按钮（球场号）
                    text = button.text.strip()
                    if not text.isdigit():
                        all_buttons.append(button)
        except Exception as e:
            if test_mode:
                print(f"   选择器 {selector} 失败: {str(e)[:50]}")
            continue
    
    if not all_buttons:
        if test_mode:
            print("⚠️  未找到任何按钮（测试模式：这是正常的）")
        else:
            print("❌ 未找到任何非数字按钮")
        return False
    
    print(f"找到 {len(all_buttons)} 个可能的按钮（已排除纯数字按钮）")
    
    # 策略2: 筛选蓝色长方形且带箭头的按钮
    blue_arrow_buttons = []
    for button in all_buttons:
        try:
            if is_blue_button_with_arrow(button):
                blue_arrow_buttons.append(button)
                button_text = button.text.strip() or button.get_attribute("value") or ""
                print(f"  找到蓝色箭头按钮: {button_text[:30]}")
        except:
            continue
    
    # 如果找到蓝色箭头按钮，优先使用
    if blue_arrow_buttons:
        print(f"\n找到 {len(blue_arrow_buttons)} 个蓝色箭头按钮")
        buttons_to_check = blue_arrow_buttons
    else:
        print("\n未找到明确的蓝色箭头按钮，查找包含'book'文本的按钮")
        # 尝试查找包含book文本的按钮
        book_text_buttons = []
        for button in all_buttons:
            text = button.text.strip().lower()
            classes = (button.get_attribute("class") or "").lower()
            button_id = (button.get_attribute("id") or "").lower()
            if "book" in text or "book" in classes or "book" in button_id:
                book_text_buttons.append(button)
                print(f"  找到包含'book'的按钮: {button.text.strip()[:30]}")
        
        if book_text_buttons:
            buttons_to_check = book_text_buttons
        else:
            print("\n未找到任何相关按钮")
            return False
    
    # 找到最右下角的按钮（y坐标最大，如果y相同则x最大）
    target_button = None
    max_y = -1
    max_x = -1
    
    for button in buttons_to_check:
        try:
            location = button.location
            y = location['y']
            x = location['x']
            
            # 选择最右下角的（y最大，如果y相同则x最大）
            if y > max_y or (y == max_y and x > max_x):
                max_y = y
                max_x = x
                target_button = button
        except:
            continue
    
    if target_button:
        try:
            button_text = target_button.text.strip() or target_button.get_attribute("value") or "预订按钮"
            button_id = target_button.get_attribute("id") or "无ID"
            button_class = target_button.get_attribute("class") or "无class"
            style = target_button.get_attribute("style") or "无"
            location = target_button.location
            size = target_button.size
            
            print(f"\n✅ 找到Book按钮")
            print(f"   文本: {button_text}")
            print(f"   ID: {button_id}")
            print(f"   Class: {button_class[:80]}")
            print(f"   Style: {style[:100] if style != '无' else '无'}")
            print(f"   位置: x={location['x']}, y={location['y']}")
            print(f"   大小: width={size['width']}, height={size['height']}")
            print(f"   正在点击...")
            
            # 滚动到按钮可见
            driver.execute_script("arguments[0].scrollIntoView(true);", target_button)
            time.sleep(0.2)
            
            # 点击按钮
            driver.execute_script("arguments[0].click();", target_button)
            time.sleep(0.5)
            print("✅ 已点击Book按钮")
            return True
        except Exception as e:
            print(f"❌ 点击Book按钮失败: {e}")
            return False
    else:
        print("❌ 未找到可点击的Book按钮")
        return False


def handle_confirmation_dialog(driver, click_confirm=True):
    """
    处理确认/取消弹出窗口
    
    Args:
        driver: WebDriver 实例
        click_confirm: True 点击确认，False 点击取消
    
    Returns:
        是否成功处理弹出窗口
    """
    print("\n正在查找确认/取消弹出窗口...")
    time.sleep(0.5)  # 等待弹出窗口出现
    
    # 尝试多种选择器查找确认和取消按钮
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
    
    cancel_selectors = [
        "//button[contains(text(), 'Cancel')]",
        "//button[contains(text(), 'cancel')]",
        "//button[contains(text(), '取消')]",
        "//button[contains(text(), 'No')]",
        "button[class*='cancel']",
        "button[id*='cancel']",
        ".cancel-button",
        "#cancel",
    ]
    
    target_selectors = confirm_selectors if click_confirm else cancel_selectors
    action_name = "确认" if click_confirm else "取消"
    
    for selector in target_selectors:
        try:
            if selector.startswith("//"):
                button = driver.find_element(By.XPATH, selector)
            else:
                button = driver.find_element(By.CSS_SELECTOR, selector)
            
            if button.is_displayed() and button.is_enabled():
                button_text = button.text.strip() or "按钮"
                button_id = button.get_attribute("id") or "无ID"
                button_class = button.get_attribute("class") or "无class"
                
                print(f"✅ 找到{action_name}按钮")
                print(f"   文本: {button_text}")
                print(f"   ID: {button_id}")
                print(f"   Class: {button_class}")
                print(f"   选择器: {selector}")
                
                # 获取按钮位置信息
                location = button.location
                size = button.size
                print(f"   位置: x={location['x']}, y={location['y']}")
                print(f"   大小: width={size['width']}, height={size['height']}")
                print(f"   正在点击{action_name}按钮...")
                
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)
                print(f"✅ 已点击{action_name}按钮")
                return True
        except Exception as e:
            print(f"   选择器 {selector} 失败: {str(e)[:50]}")
            continue
    
    # 如果找不到特定按钮，尝试查找所有可能的弹出窗口按钮
    print(f"⚠️  未找到{action_name}按钮，尝试查找所有弹出窗口按钮...")
    try:
        # 查找所有可能的弹出窗口
        dialogs = driver.find_elements(By.CSS_SELECTOR, 
            "div[role='dialog'], .modal, .popup, [class*='dialog'], [class*='modal']")
        
        if dialogs:
            print(f"   找到 {len(dialogs)} 个可能的弹出窗口")
            for i, dialog in enumerate(dialogs, 1):
                if dialog.is_displayed():
                    print(f"   弹出窗口 {i}:")
                    print(f"     可见: 是")
                    # 在弹出窗口中查找按钮
                    buttons = dialog.find_elements(By.TAG_NAME, "button")
                    print(f"     找到 {len(buttons)} 个按钮")
                    for btn in buttons:
                        if btn.is_displayed():
                            btn_text = btn.text.strip() or "按钮"
                            print(f"       - {btn_text}")
    except:
        pass
    
    print(f"❌ 未找到{action_name}按钮")
    return False


def main():
    """主函数"""
    # ========== 配置参数 ==========
    NUM_SLOTS = 2  # 要预订的时间段数量
    PREFERRED_TIMES = ["3:00pm", "4:00pm", "5:00pm", "6:00pm", "7:00pm"]  # 首选时间段
    USE_EXISTING_BROWSER = True  # 使用已打开的浏览器（True）或打开新浏览器（False）
    MAX_RETRIES = 5  # 最大重试次数
    RETRY_INTERVAL = 1  # 重试间隔（秒）
    TEST_MODE = True  # 测试模式：即使没有选择时间段也尝试点击book按钮
    CLICK_CONFIRM = True  # 在弹出窗口中点击确认（True）或取消（False）
    
    print("="*60)
    print("网球场快速预订脚本")
    print("="*60)
    
    if USE_EXISTING_BROWSER:
        print("\n⚠️  使用已打开的浏览器模式")
        print("\n请确保：")
        print("1. 已使用远程调试模式启动 Edge 浏览器（见下方命令）")
        print("2. 已在浏览器中手动登录到预订网站")
        print("3. 当前页面是预订页面（包含时间段表格）")
        print("4. 已选择好要预订的日期")
        print("\n启动 Edge 的命令：")
        print('   "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222')
        print("\n或者（如果 Edge 在 PATH 中）：")
        print("   msedge --remote-debugging-port=9222")
    else:
        print("\n请确保：")
        print("1. 已在浏览器中手动登录到预订网站")
        print("2. 当前页面是预订页面（包含时间段表格）")
        print("3. 已选择好要预订的日期")
    
    print(f"\n将尝试 {MAX_RETRIES} 次，每次间隔 {RETRY_INTERVAL} 秒")
    print("脚本立即开始运行...")
    print("（按 Ctrl+C 可取消）")
    print("="*60)
    
    driver = None
    try:
        driver = setup_driver(use_existing_browser=USE_EXISTING_BROWSER)
        
        # 显示当前页面信息
        current_url = driver.current_url
        print(f"\n当前页面: {current_url}")
        print(f"页面标题: {driver.title}\n")
        
        # 重试循环
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n{'='*60}")
            print(f"尝试 {attempt}/{MAX_RETRIES}")
            print(f"{'='*60}\n")
            
            # 选择时间段（优先选择连续时间段，否则降级为1个）
            slots_selected, actual_selected = select_slots(driver, NUM_SLOTS, PREFERRED_TIMES)
            
            if not slots_selected:
                print(f"\n⚠️  尝试 {attempt}: 未能选择足够的时间段")
                if attempt < MAX_RETRIES:
                    print(f"等待 {RETRY_INTERVAL} 秒后重试...")
                    time.sleep(RETRY_INTERVAL)
                    continue
                else:
                    print(f"\n❌ 已尝试 {MAX_RETRIES} 次，均未能选择足够的时间段")
                    print("浏览器将保持打开，你可以手动检查或稍后再试")
                    return
            
            # 只有当成功选择了时间段后，才点击Book按钮
            print(f"\n{'='*60}")
            print(f"✅ 已选择 {actual_selected} 个时间段，现在点击Book按钮")
            print(f"{'='*60}")
            
            book_clicked = click_book_button(driver, test_mode=False)
            
            if not book_clicked:
                print(f"\n⚠️  尝试 {attempt}: 未找到Book按钮")
                if attempt < MAX_RETRIES:
                    print(f"等待 {RETRY_INTERVAL} 秒后重试...")
                    time.sleep(RETRY_INTERVAL)
                    continue
                else:
                    print(f"\n❌ 已尝试 {MAX_RETRIES} 次，均未找到Book按钮")
                    print("浏览器将保持打开，你可以手动检查或稍后再试")
                    return
            
            # 处理确认/取消弹出窗口
            print("\n" + "-"*60)
            print("处理弹出窗口...")
            print("-"*60)
            action = "确认" if CLICK_CONFIRM else "取消"
            confirmation_handled = handle_confirmation_dialog(driver, click_confirm=CLICK_CONFIRM)
            
            if confirmation_handled:
                print(f"\n✅ 已成功点击{action}按钮")
            else:
                print(f"\n⚠️  未找到弹出窗口或{action}按钮（可能已经自动处理）")
            
            # 成功
            print("\n" + "="*60)
            print("✅ 预订流程完成！")
            print("="*60)
            print("\n浏览器将保持打开以便查看结果...")
            print("（可以手动关闭浏览器）")
            return
        
    except KeyboardInterrupt:
        print("\n\n用户取消")
        print("浏览器将保持打开")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("浏览器将保持打开")
    # 注意：不再自动关闭浏览器


if __name__ == "__main__":
    main()

