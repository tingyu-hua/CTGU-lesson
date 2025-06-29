import threading
import time
import requests
from datetime import datetime, timedelta

def keep_session_alive(session_info, interval=300):
    """
    保活函数：定期发送心跳请求维持会话
    :param session_info: 会话信息字典(包含cookies和Authorization)
    :param interval: 心跳间隔(秒),默认5分钟
    """
    # 记录开始时间
    start_time = datetime.now()
    
    def heartbeat_loop():
        nonlocal start_time
        while True:
            try:
                # 检查会话信息是否存在
                if not session_info:
                    time.sleep(interval)
                    continue
                
                # 计算在线时长
                current_time = datetime.now()
                online_duration = current_time - start_time
                hours, remainder = divmod(online_duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # 发送心跳请求
                resp = requests.post(
                    "http://jwxk.ctgu.edu.cn/xsxk/web/now",
                    cookies=session_info.get('cookies', {}),
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": "http://jwxk.ctgu.edu.cn/xsxk/profile/index.html",
                        "Authorization": session_info.get('Authorization', '')
                    }
                )
                
                # 检查响应状态
                if resp.status_code == 401:  # 会话过期
                    print("会话已过期，需要重新登录")
                    break
                
                # 解析响应数据
                data = resp.json()
                if data.get("code") == 200:
                    print(f"[{current_time.strftime('%H:%M:%S')}] 保活成功 | "
                          f"在线时长: {hours:02d}:{minutes:02d}:{seconds:02d} | "
                          f"服务器时间: {data['data']['currentTime']} | "
                          f"在线人数: {data['data']['onlineCount']}")
                else:
                    print(f"保活异常: {data.get('msg')}")
                    
            except Exception as e:
                print(f"now请求失败: {e}")
            
            # 等待下一次心跳
            time.sleep(interval)
    
    # 启动心跳线程
    thread = threading.Thread(target=heartbeat_loop, daemon=True)
    thread.start()
    print(f"保活线程已启动，每隔{interval}秒发送一次心跳")
    print(f"会话开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
