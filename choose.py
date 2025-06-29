import requests
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor

def load_course_data(course_files):
    """从文件加载选课信息"""
    return [
        {**json.load(open(file_path, 'r', encoding='utf-8')), 'file_path': file_path}
        for file_path in course_files
        if os.path.exists(file_path)
    ]

def send_course_request(course_data, cookies, headers):
    """发送选课请求并处理响应"""
    clazzId = course_data.get('clazzId', '')
    secretVal = course_data.get('secretVal', '')
    course_name = course_data.get('courseName', '未知课程')
    file_path = course_data.get('file_path', '')
    clazzType = course_data.get('clazzType', 'FANKC')  # 从课程信息中获取课程类型
    
    data = {
        'clazzType': clazzType,  # 使用课程类型
        'clazzId': clazzId,
        'secretVal': secretVal,
    }

    try:
        response = requests.post(
            'http://jwxk.ctgu.edu.cn/xsxk/elective/clazz/add',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )
        response_text = response.text
        res = response.json()
        flag = res['code']
        print(response_text)

        if flag == 500:
            print(f"{course_name} - {res.get('msg', '未知错误')}")
        elif flag == 401:
            print(f"{course_name} - {res.get('msg', '未知错误')}")
        elif flag == 200:
            print(f"{course_name} - {res.get('msg', '未知错误')}")
            # 选课成功后删除文件
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"已删除课程文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败: {str(e)}")
            return True
        else:
            print(f"{course_name} - 未知响应: {res}")
    except Exception as e:
        print(f"{course_name} - 请求失败: {str(e)}")
    
    return False

def task(course_data, cookies, headers, config):
    """执行单个课程的选课任务"""
    course_name = course_data.get('courseName', '未知课程')
    print(f"开始选课: {course_name}")
    
    # 获取预定时间和提前时间
    scheduled_time = config.get('scheduled_time')
    advance_time = config.get('advance_time', 30)
    
    while True:
        current_time = time.time()
        
        # 如果设置了预定时间
        if scheduled_time:
            # 提前开始阶段（预定时间前30秒）
            if current_time < scheduled_time - advance_time:
                # 还没到提前开始时间，等待
                wait_time = (scheduled_time - advance_time) - current_time
                print(f"等待提前开始: {wait_time:.1f}秒")
                time.sleep(wait_time)
                continue
                
            # 提前开始阶段（预定时间前30秒到预定时间）
            elif current_time < scheduled_time:
                # 使用1秒间隔
                interval = 1
                print(f"[提前开始] 间隔: {interval}秒")
                
            # 正式开始阶段
            else:
                # 使用配置的间隔
                interval = config['grab_interval']
                print(f"[正式开始] 间隔: {interval}秒")
        else:
            # 没有预定时间，使用配置的间隔
            interval = config['grab_interval']
        
        # 发送请求
        if send_course_request(course_data, cookies, headers):
            return True
        
        # 根据当前阶段等待
        time.sleep(interval)


def run_selected_courses(course_files, scheduled_time=None, config=None):
    # 处理 config 为 None 的情况
    if config is None:
        config = {
            'grab_interval': 1,
            'max_workers': 5
        }
    
    # 将预定时间添加到配置中
    config['scheduled_time'] = scheduled_time

    """运行选课任务，从文件加载选课信息"""
    # 如果有定时时间，等待到提前开始时间
    if scheduled_time:
        current_time = time.time()
        advance_start_time = scheduled_time - config.get('advance_time', 30)
        
        # 如果还没到提前开始时间
        if current_time < advance_start_time:
            wait_seconds = advance_start_time - current_time
            print(f"等待 {wait_seconds:.1f} 秒直到提前开始时间...")
            time.sleep(wait_seconds)
    
    course_list = load_course_data(course_files)
    
    if not course_list:
        print("没有可用的选课信息")
        return
    
    # 从登录信息加载cookies和headers
    try:
        with open('session_info.json', 'r', encoding='utf-8') as f:
            session_info = json.load(f)
    except Exception as e:
        print(f"加载登录信息失败: {str(e)}")
        return
    
    cookies = session_info.get('cookies', {})
    authorization = session_info.get('Authorization', '')
    
    # 构建请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Authorization': authorization,
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://jwxk.ctgu.edu.cn',
        'Referer': f'http://jwxk.ctgu.edu.cn/xsxk/elective/grablessons?batchId={session_info.get("batch_id", "")}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        'batchId': session_info.get('batch_id', ''),
    }
    
    print(f"开始选课，共{len(course_list)}个课程")
    print(f"使用配置: 抢课间隔={config['grab_interval']}秒, 并发数={config['max_workers']}")
    
    # 使用线程池并发选课
    with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        # 为每个课程提交任务
        futures = [executor.submit(task, course, cookies, headers, config) for course in course_list]
        
        # 等待所有任务完成
        for future in futures:
            future.result()
