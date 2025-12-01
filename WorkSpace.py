import File
import CommonUtils
from datetime import datetime
import Memento
import Logging
import Statistics  # Lab2新增
import os  # Lab2新增

class WorkSpace():
    current_workFile_path = ""
    current_workFile_list = {}
    logOpen = False
    #这个用于lru
    recent_files = []
    
    # 集成 Logger 日志记录实例
    logger = Logging.Logger()
    
    # Lab2新增: 集成统计管理器
    statistics = Statistics.StatisticsManager() 
    
    @classmethod
    #只有在 load close 时才会更新
    def update_current_workFile_list(self):
        Memento.update(self.current_workFile_path,self.current_workFile_list)
    
    @classmethod
    def update_current_workFile_path(cls,filePath):
        # Lab2修改: 集成时长统计
        if cls.current_workFile_path:
            cls.statistics.stop_timing(cls.current_workFile_path)
        WorkSpace.current_workFile_path = filePath
        if filePath:
            cls.statistics.start_timing(filePath)
        Memento.update(cls.current_workFile_path,cls.current_workFile_list)

    @classmethod
    def recover(self):
        last_state = Memento.recover()
        if not last_state:
            return
        WorkSpace.current_workFile_path = last_state.get("current_workFile_path", "")

        WorkSpace.current_workFile_list.clear()
        File.FileList.all_files.clear()
        File.FileList.all_files_path.clear()
        WorkSpace.recent_files.clear()

        temp_files = {}

        # Lab2修改: 根据文件类型创建不同的文件对象
        for f in last_state.get("all_files", []):
            file_type = f.get("file_type", "text")
            if file_type == 'xml':
                tf = File.XmlFile(f["filePath"], content=f["content"])
            else:
                tf = File.TextFile(f["filePath"], content=f["content"])
            tf.state = f["state"]

            temp_files[f["filePath"]] = tf
            File.FileList.all_files[f["filePath"]] = tf
            File.FileList.all_files_path.add(f["filePath"])

        saved_list = last_state.get("current_workFile_list", {})
        current_file = None

        for filePath in saved_list.keys():
            if filePath in temp_files:
                WorkSpace.current_workFile_list[filePath] = temp_files[filePath]
                if filePath != WorkSpace.current_workFile_path:
                    WorkSpace.recent_files.append(filePath)
                else:
                    current_file = filePath

        #当前工作文件需要在最近列表最后
        if current_file:
            WorkSpace.recent_files.append(current_file)
        
        # Lab2新增: 如果有当前文件，开始计时
        if WorkSpace.current_workFile_path and WorkSpace.current_workFile_path in WorkSpace.current_workFile_list:
            WorkSpace.statistics.start_timing(WorkSpace.current_workFile_path)

class LoadCommand():
    def execute(self, command):
        if(len(command.split(" "))) != 2 :
            print("参数错误，应为：load <file>")
            return 
        filePath = command.split(" ")[1]
        if not CommonUtils.pathCheck(filePath):
            return 
        if filePath in WorkSpace.recent_files:
            print("当前文件已打开，请使用edit命令切换")
            return 
        curFile = None
        if(filePath not in File.FileList.all_files_path):
            # Lab2修改: 从文件系统加载时需要创建文件对象
            import os
            if os.path.exists(filePath):
                # 文件存在，从磁盘读取
                with open(filePath, 'r', encoding='utf-8') as f:
                    content = [line.rstrip('\n') for line in f.readlines()]
                # 根据扩展名创建相应类型的文件对象
                if filePath.endswith('.xml'):
                    curFile = File.XmlFile(filePath, content=content)
                else:
                    curFile = File.TextFile(filePath, content=content)
                File.FileList.all_files[filePath] = curFile
                File.FileList.all_files_path.add(filePath)
            else:
                # 文件不存在，创建新文件
                curFile = CommonUtils.create_newFile(filePath)
        else:
            curFile = File.FileList.all_files[filePath]
            print(f"加载文件成功")
        
        # Lab2新增: load命令应该重置文件的编辑时长
        WorkSpace.statistics.reset_timing(filePath)
        
        WorkSpace.current_workFile_list[filePath]=curFile    
        WorkSpace.update_current_workFile_path(filePath)
        # 更新recent_files列表
        if filePath in WorkSpace.recent_files:
            WorkSpace.recent_files.remove(filePath)
        WorkSpace.recent_files.append(filePath)
        WorkSpace.logger.log_command(filePath, f"load {filePath}")

     
class SaveCommand():
    def execute(self, command):
        args = command.split(" ")
        if len(args) == 1:
            # save 当前文件
            filePath = WorkSpace.current_workFile_path
            self.save_single_file(filePath)
        elif len(args) == 2:
            param = args[1]
            if param == "all":
                # save 所有文件
                self.save_all_files()
            else:
                # save 指定文件
                filePath = param
                if not CommonUtils.pathCheck(filePath):
                    print("参数错误")
                    return
                if filePath not in [f.filePath for f in WorkSpace.current_workFile_list.values()]:
                    print("该文件不在当前工作区中")
                    return
                self.save_single_file(filePath)
                WorkSpace.logger.log_command(filePath, f"save {filePath}")
        else:
            print("参数错误，应为：save [file|all]")
            return

    def save_single_file(self, file_path):
        """保存单个文件"""
        # 检查是否有活动文件
        if not WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return

        # 获取要保存的文件
        file_to_save = WorkSpace.current_workFile_list.get(file_path)
        if not file_to_save:
            print("文件不存在")
            return

        # 写入文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Lab2修改: 区分TextFile和XmlFile
                if hasattr(file_to_save, 'content'):
                    # TextFile
                    for line in file_to_save.content:
                        f.write(line + '\n')
                else:
                    # XmlFile
                    lines = file_to_save.serialize()
                    for line in lines:
                        f.write(line + '\n')
            # 更新文件状态
            file_to_save.state = "normal"
            print(f"保存文件 {file_path} 成功")
        except Exception as e:
            print(f"保存文件失败: {e}")

    def save_all_files(self):
        """保存所有已打开的文件"""
        if not WorkSpace.current_workFile_list:
            print("没有打开的文件")
            return
            
        for file_path, file_obj in WorkSpace.current_workFile_list.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in file_obj.content:
                        f.write(line + '\n')
                # 更新文件状态
                file_obj.state = "normal"
                print(f"保存文件 {file_path} 成功")
            except Exception as e:
                print(f"保存文件 {file_path} 失败: {e}")
        
        print("所有文件保存完成")
        
               

class InitCommand():
    # Lab2修改: 支持创建XML文件
    def execute(self, command):
        args = command.split(" ")
        if len(args) < 2:
            print("参数错误，应为：init <text|xml> [with-log]")
            return
        file_type = args[1]
        withLog = False
        if len(args) == 3:
            if args[2] == "with-log":
                withLog = True
            else:
                print("参数错误")
                return
        elif len(args) > 3:
            print("参数错误")
            return
        if file_type not in ['text', 'xml']:
            print("参数错误，文件类型必须是 text 或 xml")
            return
        import random, string
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        filePath = f"untitled_{rand_suffix}.{'txt' if file_type == 'text' else 'xml'}"
        curFile = CommonUtils.create_newFile(filePath, withLog=withLog, file_type=file_type)
        if not curFile:
            return
        curFile.state = "modified"
        WorkSpace.current_workFile_list[filePath]=curFile
        WorkSpace.update_current_workFile_path(filePath)
        if filePath in WorkSpace.recent_files:
            WorkSpace.recent_files.remove(filePath)
        WorkSpace.recent_files.append(filePath)
        print(f"初始化{file_type}文件成功: {filePath}")
        if withLog:
            WorkSpace.logger.enable_logging(filePath)
            WorkSpace.logger.log_command(filePath, f"init {file_type} with-log")
        else:
            WorkSpace.logger.log_command(filePath, f"init {file_type}")

class CloseCommand():
    def execute(self, command):
        args = command.split(" ")
        if len(args) == 1:
            filePath = WorkSpace.current_workFile_path
        elif len(args) == 2:
            filePath = args[1]
            if not CommonUtils.pathCheck(filePath):
                print("参数错误")
                return
            if filePath not in [f.filePath for f in WorkSpace.current_workFile_list.values()]:
                print("该文件不在当前工作区中")
                return
        else:
            print("参数错误")
            return
        curFile = WorkSpace.current_workFile_list[filePath]
        if(curFile.state=="modified"):
            op=input("文件已修改，是否保存文件？(y/n)")
            if(op == "y"):
                #这里调save 的操作
                SaveCommand().execute(f"save {filePath}")
            elif(op == "n"):
                #n 就直接关闭
                del WorkSpace.current_workFile_list[filePath]
                WorkSpace.recent_files.remove(filePath)
                if(filePath == WorkSpace.current_workFile_path and WorkSpace.recent_files):
                    WorkSpace.update_current_workFile_path(WorkSpace.recent_files[-1])
                else:
                    WorkSpace.update_current_workFile_path("")
            else:
                print("参数错误")
        else:
            del WorkSpace.current_workFile_list[filePath]
            WorkSpace.recent_files.remove(filePath)
            if(filePath == WorkSpace.current_workFile_path and WorkSpace.recent_files):
                WorkSpace.update_current_workFile_path(WorkSpace.recent_files[-1])
            else:
                WorkSpace.update_current_workFile_path("")
        WorkSpace.update_current_workFile_list()
        print("关闭文件成功")
        WorkSpace.logger.log_command(filePath, f"close {filePath}")


class EditCommand():
    def execute(self, command):
        if(len(command.split(" "))) != 2 :
            print("参数错误，应为：edit <file>")
            return
        filePath = command.split(" ")[1]
        if not CommonUtils.pathCheck(filePath):
                print("参数错误")
                return
        if filePath not in [f.filePath for f in WorkSpace.current_workFile_list.values()]:
            print("该文件不在当前工作区中")
            return
        
        WorkSpace.update_current_workFile_path(filePath)
        #把当前文件放到recent的最后
        if filePath in WorkSpace.recent_files:
            WorkSpace.recent_files.remove(filePath)
        WorkSpace.recent_files.append(filePath)
        print(f"切换到文件{filePath}成功")
        WorkSpace.logger.log_command(filePath, f"edit {filePath}")

class EditorListCommand():
    # Lab2修改: 显示编辑时长
    def execute(self, command):
        if(len(command.split(" "))) != 1 :
            print("参数错误，应为：editor-list")
            return
        if not WorkSpace.current_workFile_list:
            print("(没有打开的文件)")
            return
        time_decorator = Statistics.TimeDecorator(WorkSpace.statistics)
        for f in WorkSpace.current_workFile_list.values():
            is_active = (f.filePath == WorkSpace.current_workFile_path)
            is_modified = (f.state == "modified")
            decorated_name = time_decorator.decorate_with_status(
                f.filePath, is_active, is_modified
            )
            print(decorated_name)

class DirTreeCommand():
    def execute(self, command):
        if len(command.split(" ")) != 1:
            print("参数错误，应为：dir-tree")
            return

        paths = list(File.FileList.all_files_path)
        if not paths:
            print("(空)")
            return
        tree = {}

        for filePath in paths:
            parts = filePath.split("/")
            cur = tree
            for p in parts:
                if p not in cur:
                    cur[p] = {}
                cur = cur[p]

        def print_tree(node, indent=""):
            keys = list(node.keys())
            total = len(keys)
            for i, key in enumerate(keys):
                is_last = (i == total - 1)
                prefix = "└── " if is_last else "├── "
                print(indent + prefix + key)

                # 如果还有下级目录，继续打印
                next_indent = indent + ("    " if is_last else "│   ")
                print_tree(node[key], next_indent)

        print_tree(tree)

class UndoCommand():
    def execute(self, command):
        if len(command.split()) != 1:
            print("参数错误，应为：undo")
            return
        
        # 检查是否有活动文件
        if not WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return
        
        # 获取当前文件
        current_file = WorkSpace.current_workFile_list.get(WorkSpace.current_workFile_path)
        if not current_file:
            print("当前文件不存在")
            return
        
        # 执行撤销
        current_file.undo()
        WorkSpace.logger.log_command(current_file, f"undo {current_file}")

class RedoCommand():
    def execute(self, command):
        if len(command.split()) != 1:
            print("参数错误，应为：redo")
            return
        
        # 检查是否有活动文件
        if not WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return
        
        # 获取当前文件
        current_file = WorkSpace.current_workFile_list.get(WorkSpace.current_workFile_path)
        if not current_file:
            print("当前文件不存在")
            return
        
        # 执行重做
        current_file.redo()
        WorkSpace.logger.log_command(current_file, f"redo {current_file}")