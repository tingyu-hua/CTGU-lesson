import list  # 导入list模块以使用其功能
import json

def verify_session():
    """验证会话是否有效"""
    print("[会话验证] 开始验证会话状态...")
    
    try:
        # 加载会话信息
        with open('session_info.json', 'r', encoding='utf-8') as f:
            session_info = json.load(f)
        
        # 获取批次ID（如果不存在则使用空字符串）
        batch_id = session_info.get('batch_id', '')
        
        # 使用专门的会话验证函数
        is_valid = list.verify_session(session_info, batch_id=batch_id)

        if is_valid:
            print("[会话验证] 会话有效")
            return True
        else:
            print("[会话验证] 会话无效或已过期")
            return False
            
    except Exception as e:
        print(f"[会话验证] 发生错误: {str(e)}")
        return False
