import requests
import json

def get_course_list(session_info, batch_id=None, campus='01', class_type='FANKC'):
    """获取所有课程列表并保存到save.json"""
    if not batch_id:
        print("错误:未提供批次ID")
        return False

    print("\n正在获取课程列表...")
    print(f"使用批次ID: {batch_id}")
    print(f"校区: {campus}")
    print(f"课程类型: {class_type}")
    
    # 使用Session保持会话
    session = requests.Session()
    session.cookies.update(session_info.get('cookies', {}))
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Authorization': session_info.get('Authorization', ''),
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://jwxk.ctgu.edu.cn',
        'Referer': f'http://jwxk.ctgu.edu.cn/xsxk/elective/grablessons?batchId={batch_id}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    }

    # 初始化变量
    all_courses = []
    page_number = 1
    page_size = 100  # 每页获取100条记录
    total_pages = 1
    
    try:
        # 首先获取第一页以确定总页数
        print(f"\n获取第1页数据...")
        json_data = {
            'teachingClassType': class_type,  # 使用传入的课程类型
            'pageNumber': page_number,
            'pageSize': page_size,
            'orderBy': '',
            'campus': campus,
        }
        
        response = session.post(
            'http://jwxk.ctgu.edu.cn/xsxk/elective/clazz/list',  
            headers=headers,
            json=json_data,
            verify=False,  
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                course_data = data.get('data', {})
                rows = course_data.get('rows', [])
                total = course_data.get('total', 0)
                total_pages = (total + page_size - 1) // page_size  # 计算总页数
                
                print(f"总课程数: {total}, 总页数: {total_pages}")
                
                # 添加第一页课程
                all_courses.extend(rows)
                
                # 获取剩余页面的数据
                for page in range(2, total_pages + 1):
                    print(f"获取第{page}页数据...")
                    json_data['pageNumber'] = page
                    
                    response = session.post(
                        'http://jwxk.ctgu.edu.cn/xsxk/elective/clazz/list',  
                        headers=headers,
                        json=json_data,
                        verify=False,  
                    )
                    
                    if response.status_code == 200:
                        page_data = response.json()
                        if page_data.get('code') == 200:
                            page_courses = page_data.get('data', {}).get('rows', [])
                            all_courses.extend(page_courses)
                        else:
                            print(f"获取第{page}页失败: {page_data.get('msg', '未知错误')}")
                    else:
                        print(f"获取第{page}页失败，状态码: {response.status_code}")
                
                # 构建最终数据结构
                final_data = {
                    'code': 200,
                    'msg': '成功',
                    'data': {
                        'pageNumber': 1,
                        'pageSize': total,
                        'rows': all_courses,
                        'total': total
                    }
                }
                
                # 保存所有课程数据到save.json
                with open('save.json', 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, ensure_ascii=False, indent=2)
                print(f"成功获取 {len(all_courses)} 门课程，已保存到save.json")
                
                # 根据实际响应结构调整数据
                for course in all_courses:
                    # 确保每个课程都有classList字段
                    if 'classList' not in course:
                        course['classList'] = []
                
                return True
            else:
                print(f"获取课程列表失败: {data.get('msg', '未知错误')}")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"获取课程列表时发生错误: {str(e)}")
        return False

def verify_session(session_info, batch_id='', campus='01'):
    """验证会话是否有效（专用于会话验证）"""
    try:
        # 使用Session保持会话
        session = requests.Session()
        session.cookies.update(session_info.get('cookies', {}))
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Authorization': session_info.get('Authorization', ''),
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'http://jwxk.ctgu.edu.cn',
            'Referer': f'http://jwxk.ctgu.edu.cn/xsxk/elective/grablessons?batchId={batch_id}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        }

        # 最小化的请求参数 - 仅用于验证会话
        json_data = {
            'teachingClassType': 'FANKC',
            'pageNumber': 1,
            'pageSize': 1,  # 仅请求1条记录
            'orderBy': '',
            'campus': campus,
        }

        response = session.post(
            'http://jwxk.ctgu.edu.cn/xsxk/elective/clazz/list',  
            headers=headers,
            json=json_data,
            verify=False,  
        )
        #print(f"[会话验证] 响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                return True
            elif data.get('code') == 500 and "本轮次选课暂未开始" in data.get('msg', ''):
                return True  # 选课未开始但会话有效
        return False
            
    except Exception:
        return False