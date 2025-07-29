import os
import sys
import shutil
import xml.etree.ElementTree as ET

def get_base_dir():
    # 如果是打包后的 exe，用 exe 所在目录
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # 普通脚本，用脚本所在目录
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

    shutil.copytree(template_dir, target_dir)

    old_name = os.path.basename(template_dir)

    idea_dir = os.path.join(target_dir, ".idea")
    name_file = os.path.join(idea_dir, ".name")
    if os.path.exists(name_file):
        with open(name_file, "w", encoding="utf-8") as f:
            f.write(project_name)

    for file in os.listdir(idea_dir):
        if file.endswith(".iml") and old_name in file:
            old_path = os.path.join(idea_dir, file)
            new_file = file.replace(old_name, project_name)
            new_path = os.path.join(idea_dir, new_file)
            os.rename(old_path, new_path)

    replace_in_xml(os.path.join(idea_dir, "workspace.xml"), old_name, project_name)
    replace_in_xml(os.path.join(idea_dir, "misc.xml"), old_name, project_name)

    print(f"Project '{project_name}' created at: {target_dir}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    else:
        project_name = input("Enter new project name: ").strip()

    if project_name:
        create_project(project_name)
