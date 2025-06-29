import json
import os

def load_and_parse_json(filename):
    """加载并解析JSON文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"解析JSON文件时出错: {e}")
        return None

def extract_courses(data):
    """递归提取所有包含课程信息的对象"""
    courses = []
    
    # 处理字典类型
    if isinstance(data, dict):
        # 检查是否是课程对象（包含tcList字段或XGXKLB字段）
        if "tcList" in data or ("XGXKLB" in data and data["XGXKLB"] == "素质拓展选修课"):
            courses.append(data)
        # 递归检查所有值
        for value in data.values():
            courses.extend(extract_courses(value))
    
    # 处理列表类型
    elif isinstance(data, list):
        for item in data:
            courses.extend(extract_courses(item))
            
    return courses

def display_class_info(class_info):
    """显示班级的指定信息"""
    # 对于素质拓展选修课，班级信息在顶层对象中
    if "XGXKLB" in class_info and class_info["XGXKLB"] == "素质拓展选修课":
        info = {
            "课程名": class_info.get("KCM", "未知"),
            "老师名字": class_info.get("SKJS", "未知"),
            "班级号": class_info.get("KXH", "未知"),
            "教室及时间": class_info.get("teachingPlace", "未知"),
            "总人数": class_info.get("KRL", "未知"),
            "已选人数": class_info.get("YXRS", "未知"),
            #"课程代码": class_info.get("JXBID", "未知"),
            #"密钥": class_info.get("secretVal", "未知")
        }
    else:
        # 普通课程的班级信息
        info = {
            "课程名": class_info.get("KCM", "未知"),
            "老师名字": class_info.get("SKJS", "未知"),
            "班级号": class_info.get("KXH", "未知"),
            "教室及时间": class_info.get("teachingPlace", "未知"),
            "总人数": class_info.get("KRL", "未知"),
            "已选人数": class_info.get("YXRS", "未知"),
            #"课程代码": class_info.get("JXBID", "未知"),
            #"密钥": class_info.get("secretVal", "未知")
        }
    
    # 打印格式化信息
    for key, value in info.items():
        print(f"    {key}: {value}")

def save_selected_course(course_info, class_info, class_type):
    """保存选择的课程信息到文件"""
    # 对于素质拓展选修课，班级信息在顶层对象中
    if "XGXKLB" in course_info and course_info["XGXKLB"] == "素质拓展选修课":
        selected_data = {
            "clazzId": course_info.get("JXBID", ""),
            "secretVal": course_info.get("secretVal", ""),
            "courseName": course_info.get("KCM", ""),
            "teacher": course_info.get("SKJS", ""),
            "clazzType": class_type
        }
    else:
        # 普通课程的班级信息
        selected_data = {
            "clazzId": class_info.get("JXBID", ""),
            "secretVal": class_info.get("secretVal", ""),
            "courseName": course_info.get("KCM", ""),
            "teacher": class_info.get("SKJS", ""),
            "clazzType": class_type
        }
    
    # 创建保存目录
    save_dir = "selected_courses"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 生成文件名
    filename = f"{selected_data['clazzId']}.json"
    filepath = os.path.join(save_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(selected_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存选课信息到: {filepath}")
    return filepath

def display_course_list(class_type):
    """显示课程列表并让用户选择"""
    filename = "save.json"
    json_data = load_and_parse_json(filename)
    
    if json_data is None:
        return None
    
    # 提取所有课程
    courses = extract_courses(json_data)
    
    if not courses:
        print("未找到任何课程信息")
        return None
    
    # 课程选择循环
    while True:
        # 显示课程列表
        print("\n课程列表:")
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course.get('KCM', '未知课程名')}")
        
        # 用户选择课程
        selected_course = None
        while selected_course is None:
            try:
                choice = input("\n输入课程序号查看班级信息 (q退出): ")
                if choice.lower() == 'q':
                    return None
                    
                index = int(choice) - 1
                if 0 <= index < len(courses):
                    selected_course = courses[index]
                else:
                    print("序号无效，请重新输入")
            except ValueError:
                print("请输入有效数字或q退出")
        
        # 显示所选课程的班级
        print(f"\n课程名称: {selected_course.get('KCM')}")
        print(f"课程代码: {selected_course.get('KCH')}")
        print(f"开课单位: {selected_course.get('KKDW')}")
        
        # 对于素质拓展选修课，只有一个班级（即课程本身）
        if "XGXKLB" in selected_course and selected_course["XGXKLB"] == "素质拓展选修课":
            print("\n班级信息:")
            display_class_info(selected_course)
            
            # 返回选择的课程和班级信息
            return {
                'course': selected_course,
                'class_info': selected_course,  # 班级信息就是课程本身
                'save_path': save_selected_course(selected_course, selected_course, class_type)
            }
        
        # 普通课程有多个班级
        print("\n班级列表:")
        for i, class_info in enumerate(selected_course['tcList'], 1):
            print(f"  班级 {i}:")
            display_class_info(class_info)
        
        # 班级选择循环
        selected_class = None
        while selected_class is None:
            try:
                class_choice = input("\n输入班级序号选择班级 (b返回课程列表, q退出): ")
                if class_choice.lower() == 'q':
                    return None
                if class_choice.lower() == 'b':
                    # 返回课程列表，重新选择课程
                    selected_class = 'back'  # 设置特殊值表示返回
                    break
                    
                class_index = int(class_choice) - 1
                if 0 <= class_index < len(selected_course['tcList']):
                    selected_class = selected_course['tcList'][class_index]
                else:
                    print("班级序号无效，请重新输入")
            except ValueError:
                print("请输入有效数字、b返回或q退出")
        
        # 如果用户选择了返回，则继续课程选择循环
        if selected_class == 'back':
            continue
        
        # 返回选择的课程和班级信息
        return {
            'course': selected_course,
            'class_info': selected_class,
            'save_path': save_selected_course(selected_course, selected_class, class_type)
        }

def main():
    display_course_list()

if __name__ == "__main__":
    main()
