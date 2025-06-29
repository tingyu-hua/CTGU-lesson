from heartbeat import keep_session_alive
from login import login  
from function import (
    load_config,
    select_batch,
    view_and_manage_saved_courses,
    run_course_selection,
    get_existing_courses,
    start_session_verification,
    save_session_info,
    course_selection_loop
)

def main():
    # 1. 加载配置文件
    config = load_config()
    print("\n已加载配置:")
    print(f"  学号: {config['username']}")
    print(f"  抢课间隔: {config['grab_interval']}秒")
    print(f"  并发数: {config['max_workers']}")
    print(f"  校区: {config['campus']}")
    
    # 2. 自动登录
    print("正在登录系统...")
    session_info = login(config)
    if not session_info:
        print("登录失败，请检查网络连接或验证码")
        return
    
    # 启动保活线程
    keep_session_alive(session_info, interval=300)
    
    # 3. 选择批次
    batch_list = session_info.get('batch_list', [])
    batch_id = select_batch(batch_list)
    if not batch_id:
        print("未选择批次，程序结束")
        return

    # 保存会话信息
    session_info = save_session_info(session_info, batch_id)
    
    # 启动会话验证线程
    start_session_verification()

    # 4. 获取已保存的课程
    selected_courses = get_existing_courses()

    # 主菜单
    while True:
        print("\n===== 主菜单 =====")
        print("1. 直接开始抢课（使用已保存的课程）")
        print("2. 进入选课循环（选择新课程）")
        print("3. 查看/管理已保存的课程") 
        print("4. 退出程序")  
        
        choice = input("请选择操作: ").strip()
        
        if choice == "1":  # 直接开始抢课
            if not selected_courses:
                print("没有已保存的课程信息，请先选择课程")
                continue
                
            selected_courses, continue_selection = run_course_selection(selected_courses, config)
            if continue_selection:
                continue
        
        elif choice == "2":  # 进入选课循环
            selected_courses = course_selection_loop(
                session_info, batch_id, config, selected_courses
            )
        
        elif choice == "3":  # 查看/管理已保存的课程
            selected_courses = view_and_manage_saved_courses(selected_courses)

        elif choice == "4":  # 退出程序
            print("\n程序结束")
            break
            
        else:
            print("无效的选择，请重新输入")

if __name__ == "__main__":
    main()
