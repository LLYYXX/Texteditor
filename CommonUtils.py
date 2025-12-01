import os
import File

rootpath = os.getcwd()

def pathCheck(path: str):
    base = os.path.basename(path)
    if '.' not in base:
        print("文件名必须包含扩展名（例如 .txt 或 .log）")
        return False

    _, ext = os.path.splitext(base)
    # Lab2修改: 支持.xml文件
    if ext.lower() not in ['.txt', '.log', '.xml']:
        print("仅支持 .txt, .xml 和 .log 文件")
        return False

    full_path = os.path.abspath(os.path.join(rootpath, path))

    if not full_path.startswith(rootpath):
        print("禁止越出根目录")
        return False
    dir_path = os.path.dirname(full_path)
    if not os.path.exists(dir_path):
        print("目录不存在，请先创建目录")
        return False

    return True

# 新建文件，包括load和init
# Lab2修改: 支持创建XML文件
def create_newFile(filePath, withLog=False, file_type='text'):
    if not pathCheck(filePath):
        return
    if filePath in File.FileList.all_files_path:
        print("文件已存在")
        return
    File.FileList.all_files_path.add(filePath)
    
    # Lab2新增: 根据文件类型或扩展名创建对应对象
    if file_type == 'xml' or filePath.endswith('.xml'):
        newFile = File.XmlFile(filePath, withLog=withLog)
    else:
        newFile = File.TextFile(filePath, withLog=withLog)
    
    File.FileList.all_files[newFile.filePath] = newFile
    return newFile
