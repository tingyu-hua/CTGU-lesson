import requests
import json
import os

def verify_session():
    """验证当前会话是否有效，尝试进行一次选课测试"""
    print("\n[会话验证] 开始验证会话状态...")
    
    try:
        # 加载会话信息
        with open('session_info.json', 'r', encoding='utf-8') as f:
            session_info = json.load(f)
    except Exception as e:
        print(f"[会话验证] 加载会话信息失败: {str(e)}")
        return False
    
    cookies = session_info.get('cookies', {})
    authorization = session_info.get('Authorization', '')
    batch_id = session_info.get('batch_id', '')
    
    # 构建请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Authorization': authorization,
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://jwxk.ctgu.edu.cn',
        'Referer': f'http://jwxk.ctgu.edu.cn/xsxk/elective/grablessons?batchId={batch_id}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
        'batchId': batch_id,
    }
    
    # 尝试加载一个真实课程ID
    real_course_id = None
    real_secret_val = None
    
    # 检查selected_courses目录
    save_dir = "selected_courses"
    if os.path.exists(save_dir) and os.listdir(save_dir):
        try:
            # 获取第一个课程文件
            course_file = os.path.join(save_dir, os.listdir(save_dir)[0])
            with open(course_file, 'r', encoding='utf-8') as f:
                course_data = json.load(f)
                real_course_id = course_data.get('clazzId')
                real_secret_val = course_data.get('secretVal')
        except:
            pass

    # 使用一个课程ID进行验证
    test_data = {
        'clazzType': 'FANKC',
        'clazzId': real_course_id,
        'secretVal': real_secret_val,
        'batchId': batch_id,
        'campus': '01',
    }
    
    try:
        print(f"[会话验证] 发送测试请求...")
        response = requests.post(
            'http://jwxk.ctgu.edu.cn/xsxk/elective/clazz/add',
            cookies=cookies,
            headers=headers,
            data=test_data,
            verify=False,
        )
        
        # 打印完整响应
        print(f"[会话验证] 响应状态码: {response.status_code}")
        #print(f"[会话验证] 响应头: {response.headers}")
        print(f"[会话验证] 响应内容: {response.text}")
        
        # 尝试解析JSON响应
        try:
            res = response.json()
            print(f"[会话验证] JSON解析结果: {res}")
            
            # 检查会话是否过期
            if response.status_code == 401 or res.get('code') == 401:
                print("[会话验证]  会话已过期")
                return False
            elif res.get('code') == 500 and "参数校验不通过" in res.get('msg', ''):
                print("[会话验证] 会话未知(参数校验失败)")
                return False
            else:
                print("[会话验证] 会话有效")
                return True
        except json.JSONDecodeError:
            print("[会话验证] ⚠️ 响应不是有效的JSON格式")
            return False
            
    except Exception as e:
        print(f"[会话验证] 请求失败: {str(e)}")
        return False

if __name__ == "__main__":
    verify_session()
