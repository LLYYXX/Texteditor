
class FileList():
    all_files_path = set()
    all_files = {}

class TextFile():
    def __init__(self, filePath,content=None,withLog=False):
        self.fileName = filePath.split("/")[-1]
        self.filePath = filePath
        self.content = content or []
        self.state = "normal"
        self.file_type = 'text'  # Lab2新增
        if withLog:
            self.content.append("# log")

        # 命令历史栈（用于undo/redo）
        self.command_history = []  # 已执行的命令
        self.redo_stack = []  # 已撤销的命令（用于redo）
    
    def add_to_history(self, command):
        """添加命令到历史记录"""
        if command.can_undo():
            self.command_history.append(command)
            # 执行新命令后，清空redo栈
            self.redo_stack.clear()
    
    def undo(self):
        """撤销最后一个命令"""
        if not self.command_history:
            print("没有可撤销的操作")
            return False
        
        command = self.command_history.pop()
        command.undo()
        self.redo_stack.append(command)
        
        # 如果撤销后没有修改，更新状态
        if not self.command_history:
            self.state = "normal"
        
        return True
    
    def redo(self):
        """重做最后一个撤销的命令"""
        if not self.redo_stack:
            print("没有可重做的操作")
            return False
        
        command = self.redo_stack.pop()
        command.redo()
        self.command_history.append(command)
        self.state = "modified"
        
        return True

class LogFile():
    def __init__(self,content=None):
        self.content = content or []


# ==================== Lab2新增: XmlFile类 ====================
class XmlFile():
    """XML文件类 (Lab2新增)"""
    def __init__(self, filePath, content=None, withLog=False):
        self.fileName = filePath.split("/")[-1]
        self.filePath = filePath
        self.state = "normal"
        self.file_type = 'xml'
        self.root = None
        self.element_map = {}
        self.command_history = []
        self.redo_stack = []
        
        if content:
            self.parse_from_lines(content)
        else:
            self._init_empty_xml(withLog)
    
    def _init_empty_xml(self, withLog):
        from XmlEditor import XmlElement
        self.xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
        self.has_log_comment = withLog
        self.root = XmlElement('root', {'id': 'root'})
        self.element_map['root'] = self.root
    
    def parse_from_lines(self, lines):
        from XmlEditor import parse_xml
        xml_string = '\n'.join(lines)
        self.root, self.element_map, self.xml_declaration, self.has_log_comment = parse_xml(xml_string)
    
    def serialize(self):
        lines = []
        if self.has_log_comment:
            lines.append("# log")
        lines.append(self.xml_declaration)
        if self.root:
            lines.extend(self.root.to_xml_lines())
        return lines
    
    def add_to_history(self, command):
        if command.can_undo():
            self.command_history.append(command)
            self.redo_stack.clear()
    
    def undo(self):
        if not self.command_history:
            print("没有可撤销的操作")
            return False
        command = self.command_history.pop()
        command.undo()
        self.redo_stack.append(command)
        if not self.command_history:
            self.state = "normal"
        return True
    
    def redo(self):
        if not self.redo_stack:
            print("没有可重做的操作")
            return False
        command = self.redo_stack.pop()
        command.redo()
        self.command_history.append(command)
        self.state = "modified"
        return True
    