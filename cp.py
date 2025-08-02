import os
import sys
import shutil
import xml.etree.ElementTree as ET

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def replace_in_xml(file_path, old_name, new_name):
    if not os.path.exists(file_path):
        return
    tree = ET.parse(file_path)
    root = tree.getroot()
    changed = False
    for elem in root.iter():
        if elem.text and old_name in elem.text:
            elem.text = elem.text.replace(old_name, new_name)
            changed = True
        if elem.attrib:
            for k, v in elem.attrib.items():
                if old_name in v:
                    elem.attrib[k] = v.replace(old_name, new_name)
                    changed = True
    if changed:
        tree.write(file_path, encoding="UTF-8", xml_declaration=True)

def create_project(project_name):
    base_dir = get_base_dir()
    template_dir = os.path.join(base_dir, "1-Template")
    target_dir = os.path.join(base_dir, project_name)

    if not os.path.exists(template_dir):
        print(f"Error: template directory not found at {template_dir}")
        input("Press Enter to exit...")
        return
    if os.path.exists(target_dir):
        print(f"Error: target project '{project_name}' already exists!")
        input("Press Enter to exit...")
        return

    # 复制模板目录
    shutil.copytree(template_dir, target_dir)

    old_name = os.path.basename(template_dir)

    # 修改 .idea 配置
    idea_dir = os.path.join(target_dir, ".idea")
    name_file = os.path.join(idea_dir, ".name")
    if os.path.exists(name_file):
        with open(name_file, "w", encoding="utf-8") as f:
            f.write(project_name)

    # 重命名 .iml 文件
    for file in os.listdir(idea_dir):
        if file.endswith(".iml") and old_name in file:
            old_path = os.path.join(idea_dir, file)
            new_file = file.replace(old_name, project_name)
            new_path = os.path.join(idea_dir, new_file)
            os.rename(old_path, new_path)

    # 替换 .idea 配置文件中的旧项目名
    replace_in_xml(os.path.join(idea_dir, "workspace.xml"), old_name, project_name)
    replace_in_xml(os.path.join(idea_dir, "misc.xml"), old_name, project_name)
    replace_in_xml(os.path.join(idea_dir, "modules.xml"), old_name, project_name)

    # 替换所有 .iml 文件中的内容
    for file in os.listdir(idea_dir):
        if file.endswith(".iml"):
            replace_in_xml(os.path.join(idea_dir, file), old_name, project_name)

    print(f"Project '{project_name}' created at: {target_dir}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    else:
        project_name = input("Enter new project name: ").strip()

    if project_name:
        create_project(project_name)
