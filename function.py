import os
import time
import json
import yaml
import threading
from datetime import datetime
from choose import run_selected_courses
import veri_list

def load_config():
    """加载配置文件"""
    config_path = "config.yaml"
    default_config = {
        "username": "",
        "password": "",
        "grab_interval": 1,
        "max_workers": 5,
        "campus": "01"
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                # 确保所有配置项都存在
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        else:
            # 创建默认配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f)
            print(f"已创建默认配置文件: {config_path}")
            return default_config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}，使用默认配置")
        return default_config

def select_batch(batch_list):
    """让用户选择批次"""
    if not batch_list:
        print("没有可用的选课批次")
        return None
    
    print("\n请选择选课批次:")
    for i, batch in enumerate(batch_list, 1):
        print(f"{i}. {batch['name']} (开始时间: {batch['beginTime']} 结束时间: {batch['endTime']})")
    
    try:
        choice = int(input("请输入批次编号: "))
        if 1 <= choice <= len(batch_list):
            selected_batch = batch_list[choice-1]
            print(f"已选择: {selected_batch['name']}")
            return selected_batch['code']
        else:
            print("编号无效，请重新输入")
            return None
    except ValueError:
        print("输入无效，请输入数字")
        return None

# 课程类型映射
CLASS_TYPE_MAP = {
    '1': ('FANKC', '方案内课程'),
    '2': ('CXKC', '重修课程'),
    '3': ('TYKC', '分级课程'),
    '4': ('XGKC', '素质拓展选修课'),
    '5': ('FXKC', '辅修课程'),
    '6': ('ALLKC', '全校课程')
}

def get_existing_courses():
    """获取已保存的课程文件"""
    selected_courses = []
    save_dir = "selected_courses"
    if os.path.exists(save_dir):
        existing_files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith('.json')]
        selected_courses.extend(existing_files)
        print(f"已加载{len(existing_files)}个之前保存的课程信息文件")
    return selected_courses

def start_session_verification():
    """启动会话验证线程"""
    def session_verification_loop():
        time.sleep(30)
        while True:
            veri_list.verify_session()
            time.sleep(180)  # 每3分钟验证一次
    
    verification_thread = threading.Thread(target=session_verification_loop, daemon=True)
    verification_thread.start()
    print("会话验证线程已启动")
    return verification_thread

def save_session_info(session_info, batch_id):
    """保存会话信息到文件"""
    session_info['batch_id'] = batch_id
    with open('session_info.json', 'w', encoding='utf-8') as f:
        json.dump(session_info, f, ensure_ascii=False, indent=2)
    print("会话信息已保存到session_info.json")
    return session_info

def course_selection_loop(session_info, batch_id, config, selected_courses):
    """选课循环逻辑"""
    # 在函数内部导入，避免循环导入问题
    from list import get_course_list
    from lesson import display_course_list
    
    while True:
        # 选择课程类型
        class_type = select_class_type()
        
        # 获取课程列表并保存到save.json
        print("\n正在获取课程列表...")
        if not get_course_list(session_info, batch_id=batch_id, campus=config['campus'], class_type=class_type):
            print("获取课程列表失败")
            break
        
        # 显示课程列表并让用户选择
        selection = display_course_list(class_type)
        
        if not selection:
            print("未选择课程，返回主菜单")
            break
        
        # 处理选择的课程
        course = selection['course']
        class_info = selection['class_info']
        save_path = selection['save_path']

        # 添加到已选课程列表
        if save_path not in selected_courses:
            selected_courses.append(save_path)
        else:
            print(f"课程文件 {save_path} 已经在选课列表中")
        
        print(f"\n已选择课程: {course.get('KCM', '未知课程名')} ({course.get('KCH', '未知代码')})")
        print(f"班级信息:")
        print(f"  老师: {class_info.get('SKJS', '未知')}")
        print(f"  时间地点: {class_info.get('teachingPlace', '未知')}")
        print(f"  总人数: {class_info.get('KRL', '未知')}, 已选人数: {class_info.get('YXRS', '未知')}")
        
        # 询问下一步操作
        action = input("\n输入'a'添加更多课程，'r'刷新课程列表，'s'开始选课，其他键返回主菜单: ").lower()
        if action == 'a':
            continue  # 继续添加课程
        elif action == 'r':
            continue  # 刷新课程列表
        elif action != 's':
            break  # 返回主菜单
        
        # 开始选课
        if not selected_courses:
            print("没有选择任何课程")
            continue
        
        selected_courses, continue_selection = run_course_selection(selected_courses, config)
        if continue_selection:
            continue
        else:
            break
    
    return selected_courses

def select_class_type():
    """让用户选择课程类型"""
    print("\n请选择课程类型:")
    for key, value in CLASS_TYPE_MAP.items():
        print(f"{key}. {value[1]}")
    
    while True:
        choice = input("请输入课程类型编号: ").strip()
        if choice in CLASS_TYPE_MAP:
            class_type, class_name = CLASS_TYPE_MAP[choice]
            print(f"已选择: {class_name}")
            return class_type
        else:
            print("输入无效，请重新输入")

def parse_scheduled_time(input_str):
    """解析用户输入的定时时间"""
    try:
        # 尝试解析为时间戳
        if input_str.isdigit():
            timestamp = float(input_str)
            if timestamp > time.time():
                return timestamp
            else:
                print("时间戳不能是过去时间")
                return None
        
        # 尝试解析为日期极时间字符串
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%H:%M:%S",
            "%H:%M"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(input_str, fmt)
                # 如果只提供了时间，使用今天的日期
                if fmt in ["%H:%M:%S", "%H:%M"]:
                    now = datetime.now()
                    dt = dt.replace(year=now.year, month=now.month, day=now.day)
                
                # 转换为时间戳
                timestamp = dt.timestamp()
                if timestamp > time.time():
                    return timestamp
                else:
                    print("指定的时间不能是过去时间")
                    return None
            except ValueError:
                continue
        
        print("无法识别的时间格式")
        return None
    except Exception as e:
        print(f"解析时间失败: {str(e)}")
        return None

def view_and_manage_saved_courses(selected_courses):
    """查看和管理已保存的课程"""
    if not selected_courses:
        print("没有已保存的课程")
        return selected_courses
    
    print("\n已保存的课程:")
    for i, course_file in enumerate(selected_courses, 1):
        try:
            with open(course_file, 'r', encoding='utf-8') as f:
                course_data = json.load(f)
                course_name = course_data.get('courseName', '未知课程')
                teacher = course_data.get('teacher', '未知老师')
                clazz_type = course_data.get('clazzType', '未知类型')
                
                # 获取课程类型名称
                type_name = next((v[1] for k, v in CLASS_TYPE_MAP.items() if v[0] == clazz_type), clazz_type)
                
                print(f"{i}. {course_name} - {teacher} ({type_name})")
        except Exception:
            print(f"{i}. 无法读取课程文件: {course_file}")
    
    print("\n操作:")
    print("d. 删除课程")
    print("b. 返回主菜单")
    
    action = input("请选择操作: ").lower()
    
    if action != 'd':
        return selected_courses
    
    try:
        choice = input("请输入要删除的课程编号 (多个用逗号分隔) 或 'a' 删除所有: ")
        if choice.lower() == 'a':
            # 删除所有课程
            for course_file in selected_courses:
                try:
                    os.remove(course_file)
                    print(f"已删除: {os.path.basename(course_file)}")
                except Exception:
                    print(f"删除失败: {os.path.basename(course_file)}")
            print("所有课程已删除")
            return []  # 返回空列表
        
        # 删除选定的课程
        indices = [int(idx.strip()) - 1 for idx in choice.split(',') if idx.strip().isdigit()]
        to_remove = []
        
        for idx in indices:
            if 0 <= idx < len(selected_courses):
                course_file = selected_courses[idx]
                try:
                    os.remove(course_file)
                    print(f"已删除: {os.path.basename(course_file)}")
                    to_remove.append(course_file)
                except Exception:
                    print(f"删除失败: {os.path.basename(course_file)}")
        
        # 从列表中移除已删除的课程
        remaining_courses = [c for c in selected_courses if c not in to_remove]
        print(f"已删除 {len(to_remove)} 门课程")
        return remaining_courses
    except Exception as e:
        print(f"操作失败: {str(e)}")
        return selected_courses

def update_course_list_after_selection(selected_courses):
    """选课后更新课程列表"""
    remaining_courses = []
    for course_file in selected_courses:
        if os.path.exists(course_file):
            remaining_courses.append(course_file)
        else:
            print(f"课程文件 {course_file} 已被删除，表示抢课成功")
    
    # 更新选课列表为未成功的课程
    selected_courses = remaining_courses
    
    # 如果还有未成功的课程，询问是否继续
    if selected_courses:
        continue_action = input("\n还有未成功的课程, 输入'c'继续尝试，其他键返回主菜单: ").lower()
        if continue_action == 'c':
            return selected_courses, True
    else:
        print("\n所有课程都已成功抢到！")
    
    return selected_courses, False

def run_course_selection(selected_courses, config):
    """运行选课流程"""
    # 询问是否定时抢课
    schedule_input = input("\n是否定时抢课?(输入时间或直接回车立即开始): ").strip()
    scheduled_time = None
    advance_time = config.get('advance_time', 30)  # 获取提前时间
    
    if schedule_input:
        scheduled_time = parse_scheduled_time(schedule_input)
        if scheduled_time:
            current_time = time.time()
            
            # 计算提前开始时间
            advance_start_time = scheduled_time - advance_time
            
            # 如果提前开始时间还没到
            if current_time < advance_start_time:
                wait_time = advance_start_time - current_time
                print(f"将在 {datetime.fromtimestamp(advance_start_time).strftime('%Y-%m-%d %H:%M:%S')} 提前开始抢课")
                print(f"距离提前开始还有: {wait_time:.0f} 秒")
                time.sleep(wait_time)
            
            # 如果已经过了提前开始时间但还没到抢课时间
            elif current_time < scheduled_time:
                print(f"已过提前开始时间，将在 {datetime.fromtimestamp(scheduled_time).strftime('%Y-%m-%d %H:%M:%S')} 开始正式抢课")
                print(f"距离正式开始还有: {scheduled_time - current_time:.0f} 秒")
            
            # 如果已经过了抢课时间
            else:
                print("已经过了抢课时间，将立即开始抢课")
        else:
            print("时间格式无效，将立即开始抢课")
    
    # 创建抢课专用配置
    grab_config = {
        'grab_interval': config['grab_interval'],  # 使用配置中的间隔
        'max_workers': config['max_workers'],
        'advance_time': advance_time,  # 传递提前时间
        'scheduled_time': scheduled_time  # 传递预定时间
    }
    
    print("\n开始自动选课...")
    run_selected_courses(selected_courses, scheduled_time, grab_config)
    
    # 更新课程列表
    return update_course_list_after_selection(selected_courses)

