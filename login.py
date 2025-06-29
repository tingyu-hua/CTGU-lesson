import requests
import base64
import os

# 登录URL和验证码URL
login_url = 'http://jwxk.ctgu.edu.cn/xsxk/auth/login'
captcha_url = 'http://jwxk.ctgu.edu.cn/xsxk/auth/captcha'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
}

def get_captcha():
    """获取验证码图片和uuid"""
    try:
        # 发送POST请求获取验证码
        response = requests.post(captcha_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析JSON响应
        captcha_data = response.json()
        if captcha_data['code'] != 200:
            print("获取验证码失败:", captcha_data['msg'])
            return None, None
            
        # 提取base64编码的图片和uuid
        img_base64 = captcha_data['data']['captcha'].split(',')[1]  # 去掉"data:image/png;base64,"
        uuid = captcha_data['data']['uuid']
        
        # 解码base64图片
        img_data = base64.b64decode(img_base64)
        
        # 保存图片到当前目录
        save_path = os.path.join(os.getcwd(), 'captcha.jpg')
        with open(save_path, 'wb') as f:
            f.write(img_data)
            
        print(f"验证码图片已保存到: {save_path}")
        
        # 显示图片（可选）
        '''img = Image.open(BytesIO(img_data))
        img.show()'''
        
        return img_data, uuid
        
    except Exception as e:
        print(f"获取验证码时发生错误: {str(e)}")
        return None, None

def login(config):
    """登录函数"""
    # 获取验证码
    img_data, uuid = get_captcha()
    if not img_data:
        return
        
    # 让用户输入验证码
    captcha = input("请输入验证码图片中的字符: ")
    
    # 使用配置中的学号和密码
    data = {
        'loginname': config['username'],  # 使用配置中的学号
        'password': config['password'],  # 使用配置中的密码
        'captcha': captcha,
        'uuid': uuid
    }
    
    print(f"使用学号: {data['loginname']} 进行登录")  # 调试信息
    
    # 提交登录请求
    try:
        resp = requests.post(login_url, headers=headers, data=data)
        print("登录结果:", resp.status_code)
        
        # 检查登录是否成功
        if resp.status_code == 200:
            login_data = resp.json()
            if login_data.get('code') == 200:
                print("登录成功!")
                student_info = login_data.get('data', {}).get('student', {})
                batch_list = student_info.get('electiveBatchList', [])
                
                # 返回cookies、token和批次列表
                return {
                    'cookies': resp.cookies.get_dict(),
                    'token': login_data.get('data', {}).get('token', ''),
                    'Authorization': f"Bearer {login_data.get('data', {}).get('token', '')}",
                    'batch_list': batch_list  # 添加批次列表
                }
            else:
                print("登录失败:", login_data.get('msg', '未知错误'))
                return None
    except Exception as e:
        print(f"登录时发生错误: {str(e)}")
        return None
    
if __name__ == "__main__":
    # 测试时需要加载配置
    import yaml
    config = yaml.safe_load(open("config.yaml", "r", encoding="utf-8"))
    login(config)