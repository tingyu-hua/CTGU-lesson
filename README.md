# CTGU-lesson 项目

这是一个Python实现的课程管理系统，提供登录、课程选择、验证等功能。

## 功能特性

- 用户登录认证
- 课程列表展示
- 课程选择功能
- 验证功能
- 心跳检测保持连接

## 安装指南

1. 确保已安装Python 3.6+
2. 克隆本项目：
   ```bash
   git clone https://github.com/your-repo/sanxailesson.git
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用说明

1. 在config.yaml中填写相关信息，目前密码是直接输入加密后的密码，需要自行查看，方法如下
2. 运行主程序：
   ```bash
   python main.py
   ```
3. 按照提示输入目录下的验证码
4. 使用菜单选择所需功能

## 项目结构

```
sanxailesson/
├── main.py          # 主程序入口
├── login.py         # 登录模块
├── function.py      # 功能模块
├── lesson.py        # 课程模块
├── list.py          # 列表模块
├── veri_choose.py   # 验证选择模块
├── veri_list.py     # 验证列表模块
├── heartbeat.py     # 心跳检测模块
├── choose.py        # 选择模块
├── requirements.txt # 依赖文件
└── README.md        # 项目说明
```

## 注意事项

1. 请确保配置文件(config.yml)已正确设置
2. 保持网络连接正常使用所有功能
3. 目前线程太多可能产生拥挤，导致无法抢课
