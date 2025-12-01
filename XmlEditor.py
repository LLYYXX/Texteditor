"""
Lab2新增: XML编辑器模块
使用组合模式(Composite Pattern)表示XML树形结构
"""
import re
import WorkSpace


class XmlElement:
    """XML元素类 (组合模式)"""
    def __init__(self, tag, attributes=None, text=""):
        self.tag = tag
        self.attributes = attributes or {}
        self.text = text
        self.children = []
        self.parent = None
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def insert_before(self, new_child, target_child):
        if target_child in self.children:
            index = self.children.index(target_child)
            new_child.parent = self
            self.children.insert(index, new_child)
            return True
        return False
    
    def get_id(self):
        return self.attributes.get('id', '')
    
    def set_id(self, new_id):
        self.attributes['id'] = new_id
    
    def to_xml_lines(self, indent=0):
        lines = []
        indent_str = "    " * indent
        attrs_str = ""
        if self.attributes:
            attrs_str = " " + " ".join([f'{k}="{v}"' for k, v in self.attributes.items()])
        
        if self.children:
            lines.append(f"{indent_str}<{self.tag}{attrs_str}>")
            if self.text and self.text.strip():
                lines.append(f"{indent_str}    {self.text}")
            for child in self.children:
                lines.extend(child.to_xml_lines(indent + 1))
            lines.append(f"{indent_str}</{self.tag}>")
        else:
            if self.text:
                lines.append(f"{indent_str}<{self.tag}{attrs_str}>{self.text}</{self.tag}>")
            else:
                lines.append(f"{indent_str}<{self.tag}{attrs_str}></{self.tag}>")
        return lines
    
    def to_tree_lines(self, prefix="", is_last=True):
        lines = []
        connector = "└── " if is_last else "├── "
        attrs_str = ", ".join([f'{k}="{v}"' for k, v in self.attributes.items()])
        node_str = f"{self.tag} [{attrs_str}]"
        lines.append(prefix + connector + node_str)
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension
        if self.text and self.text.strip():
            text_connector = "└── " if not self.children else "├── "
            lines.append(new_prefix + text_connector + f'"{self.text}"')
        for i, child in enumerate(self.children):
            child_is_last = (i == len(self.children) - 1)
            lines.extend(child.to_tree_lines(new_prefix, child_is_last))
        return lines


def parse_xml(xml_string):
    """解析XML字符串"""
    lines = xml_string.strip().split('\n')
    has_log_comment = False
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    filtered_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('# log'):
            has_log_comment = True
        elif line.startswith('<?xml'):
            xml_declaration = line
        elif line:
            filtered_lines.append(line)
    xml_content = ' '.join(filtered_lines)
    element_map = {}
    root = _parse_element(xml_content, element_map)
    return root, element_map, xml_declaration, has_log_comment


def _parse_element(xml_str, element_map):
    """递归解析XML元素"""
    xml_str = xml_str.strip()
    tag_pattern = r'<(\w+)([^>]*)>'
    match = re.match(tag_pattern, xml_str)
    if not match:
        return None
    tag_name = match.group(1)
    attrs_str = match.group(2).strip()
    attributes = {}
    if attrs_str:
        attr_pattern = r'(\w+)="([^"]*)"'
        for attr_match in re.finditer(attr_pattern, attrs_str):
            attributes[attr_match.group(1)] = attr_match.group(2)
    element = XmlElement(tag_name, attributes)
    if 'id' in attributes:
        element_map[attributes['id']] = element
    end_tag = f'</{tag_name}>'
    end_tag_pos = xml_str.rfind(end_tag)
    if end_tag_pos == -1:
        return element
    start_pos = match.end()
    content = xml_str[start_pos:end_tag_pos].strip()
    if not content:
        return element
    if not content.startswith('<'):
        element.text = content
    else:
        _parse_children(content, element, element_map)
    return element


def _parse_children(content, parent, element_map):
    """解析子元素"""
    i = 0
    while i < len(content):
        if content[i] == '<' and i+1 < len(content) and content[i+1] != '/':
            tag_match = re.match(r'<(\w+)', content[i:])
            if tag_match:
                tag_name = tag_match.group(1)
                end_tag = f'</{tag_name}>'
                tag_count = 0
                j = i
                while j < len(content):
                    if content[j:j+len(f'<{tag_name}')].startswith(f'<{tag_name}'):
                        if j == i or content[j:j+len(f'<{tag_name}')+1] in [f'<{tag_name} ', f'<{tag_name}>']:
                            tag_count += 1
                    if content[j:j+len(end_tag)] == end_tag:
                        tag_count -= 1
                        if tag_count == 0:
                            child_xml = content[i:j+len(end_tag)]
                            child = _parse_element(child_xml, element_map)
                            if child:
                                parent.add_child(child)
                            i = j + len(end_tag)
                            break
                    j += 1
                else:
                    break
            else:
                i += 1
        else:
            if content[i:i+2] != '</':
                text_end = content.find('<', i)
                if text_end == -1:
                    text_end = len(content)
                text = content[i:text_end].strip()
                if text and not parent.text:
                    parent.text = text
                i = text_end
            else:
                i += 1


# ==================== Lab2新增: XML编辑命令 ====================

# Lab2新增: 装饰器模式 - 自动标记文件修改状态
class ModifiedStateDecorator:
    """
    文件状态装饰器 (Decorator Pattern)
    自动标记文件修改状态，避免在每个命令中手动设置
    """
    def __init__(self, command):
        """
        :param command: 被装饰的命令对象
        """
        self._command = command
    
    def execute(self, command_str):
        """
        装饰后的execute方法：执行命令后自动标记文件为已修改
        """
        # 执行原始命令
        result = self._command.execute(command_str)
        
        # 如果命令执行成功，自动标记文件状态为modified
        if result and hasattr(self._command, 'file') and self._command.file:
            self._command.file.state = "modified"
        
        return result
    
    def undo(self):
        """委托给被装饰的命令"""
        return self._command.undo()
    
    def redo(self):
        """委托给被装饰的命令"""
        return self._command.redo()
    
    def can_undo(self):
        """委托给被装饰的命令"""
        return self._command.can_undo()
    
    def __getattr__(self, name):
        """转发其他属性访问到被装饰的命令"""
        return getattr(self._command, name)


class XmlEditCommand:
    """XML编辑命令基类"""
    def execute(self, command):
        raise NotImplementedError
    def undo(self):
        raise NotImplementedError
    def redo(self):
        raise NotImplementedError
    def can_undo(self):
        return True


class InsertBeforeCommand(XmlEditCommand):
    """insert-before命令"""
    def __init__(self):
        self.file = None
        self.new_element = None
        self.target_element = None
        self.parent_element = None
    
    def execute(self, command):
        parts = command.split('"')
        text = parts[1] if len(parts) >= 2 else ""
        args = parts[0].strip().split()
        if len(args) < 4:
            print("参数错误，应为：insert-before <tag> <newId> <targetId> [\"text\"]")
            return False
        tag, new_id, target_id = args[1], args[2], args[3]
        if not WorkSpace.WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return False
        self.file = WorkSpace.WorkSpace.current_workFile_list.get(WorkSpace.WorkSpace.current_workFile_path)
        if not self.file or self.file.file_type != 'xml':
            print("当前文件不是XML文件")
            return False
        if new_id in self.file.element_map:
            print(f"元素ID已存在: {new_id}")
            return False
        if target_id not in self.file.element_map:
            print(f"目标元素不存在: {target_id}")
            return False
        self.target_element = self.file.element_map[target_id]
        if self.target_element == self.file.root:
            print("不能在根元素前插入元素")
            return False
        self.parent_element = self.target_element.parent
        if not self.parent_element:
            print("目标元素没有父元素")
            return False
        self.new_element = XmlElement(tag, {'id': new_id}, text)
        self.parent_element.insert_before(self.new_element, self.target_element)
        self.file.element_map[new_id] = self.new_element
        # Lab2修改: 移除手动设置state，由装饰器自动处理
        # self.file.state = "modified"
        print(f"成功在元素 {target_id} 前插入新元素 {new_id}")
        WorkSpace.WorkSpace.logger.log_command(self.file.filePath, f'insert-before {tag} {new_id} {target_id} "{text}"')
        self.file.add_to_history(self)
        return True
    
    def undo(self):
        if self.file and self.new_element and self.parent_element:
            self.parent_element.remove_child(self.new_element)
            del self.file.element_map[self.new_element.get_id()]
            print("撤销插入操作成功")
    
    def redo(self):
        if self.file and self.new_element and self.parent_element and self.target_element:
            self.parent_element.insert_before(self.new_element, self.target_element)
            self.file.element_map[self.new_element.get_id()] = self.new_element
            print("重做插入操作成功")


class AppendChildCommand(XmlEditCommand):
    """append-child命令"""
    def __init__(self):
        self.file = None
        self.new_element = None
        self.parent_element = None
    
    def execute(self, command):
        parts = command.split('"')
        text = parts[1] if len(parts) >= 2 else ""
        args = parts[0].strip().split()
        if len(args) < 4:
            print("参数错误，应为：append-child <tag> <newId> <parentId> [\"text\"]")
            return False
        tag, new_id, parent_id = args[1], args[2], args[3]
        if not WorkSpace.WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return False
        self.file = WorkSpace.WorkSpace.current_workFile_list.get(WorkSpace.WorkSpace.current_workFile_path)
        if not self.file or self.file.file_type != 'xml':
            print("当前文件不是XML文件")
            return False
        if new_id in self.file.element_map:
            print(f"元素ID已存在: {new_id}")
            return False
        if parent_id not in self.file.element_map:
            print(f"父元素不存在: {parent_id}")
            return False
        self.parent_element = self.file.element_map[parent_id]
        self.new_element = XmlElement(tag, {'id': new_id}, text)
        self.parent_element.add_child(self.new_element)
        self.file.element_map[new_id] = self.new_element
        # Lab2修改: 移除手动设置state，由装饰器自动处理
        # self.file.state = "modified"
        print(f"成功为元素 {parent_id} 添加子元素 {new_id}")
        WorkSpace.WorkSpace.logger.log_command(self.file.filePath, f'append-child {tag} {new_id} {parent_id} "{text}"')
        self.file.add_to_history(self)
        return True
    
    def undo(self):
        if self.file and self.new_element and self.parent_element:
            self.parent_element.remove_child(self.new_element)
            del self.file.element_map[self.new_element.get_id()]
            print("撤销追加操作成功")
    
    def redo(self):
        if self.file and self.new_element and self.parent_element:
            self.parent_element.add_child(self.new_element)
            self.file.element_map[self.new_element.get_id()] = self.new_element
            print("重做追加操作成功")


class EditIdCommand(XmlEditCommand):
    """edit-id命令"""
    def __init__(self):
        self.file = None
        self.element = None
        self.old_id = ""
        self.new_id = ""
    
    def execute(self, command):
        args = command.split()
        if len(args) != 3:
            print("参数错误，应为：edit-id <oldId> <newId>")
            return False
        self.old_id, self.new_id = args[1], args[2]
        if not WorkSpace.WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return False
        self.file = WorkSpace.WorkSpace.current_workFile_list.get(WorkSpace.WorkSpace.current_workFile_path)
        if not self.file or self.file.file_type != 'xml':
            print("当前文件不是XML文件")
            return False
        if self.old_id not in self.file.element_map:
            print(f"元素不存在: {self.old_id}")
            return False
        if self.new_id in self.file.element_map:
            print(f"目标ID已存在: {self.new_id}")
            return False
        self.element = self.file.element_map[self.old_id]
        if self.element == self.file.root:
            print("警告: 不建议修改根元素ID，但操作将继续")
        self.element.set_id(self.new_id)
        del self.file.element_map[self.old_id]
        self.file.element_map[self.new_id] = self.element
        # Lab2修改: 移除手动设置state，由装饰器自动处理
        # self.file.state = "modified"
        print(f"成功将元素ID从 {self.old_id} 修改为 {self.new_id}")
        WorkSpace.WorkSpace.logger.log_command(self.file.filePath, f'edit-id {self.old_id} {self.new_id}')
        self.file.add_to_history(self)
        return True
    
    def undo(self):
        if self.file and self.element:
            self.element.set_id(self.old_id)
            del self.file.element_map[self.new_id]
            self.file.element_map[self.old_id] = self.element
            print("撤销ID修改操作成功")
    
    def redo(self):
        if self.file and self.element:
            self.element.set_id(self.new_id)
            del self.file.element_map[self.old_id]
            self.file.element_map[self.new_id] = self.element
            print("重做ID修改操作成功")


class EditTextCommand(XmlEditCommand):
    """edit-text命令"""
    def __init__(self):
        self.file = None
        self.element = None
        self.old_text = ""
        self.new_text = ""
    
    def execute(self, command):
        parts = command.split('"')
        self.new_text = parts[1] if len(parts) >= 2 else ""
        args = parts[0].strip().split()
        if len(args) < 2:
            print("参数错误，应为：edit-text <elementId> [\"text\"]")
            return False
        element_id = args[1]
        if not WorkSpace.WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return False
        self.file = WorkSpace.WorkSpace.current_workFile_list.get(WorkSpace.WorkSpace.current_workFile_path)
        if not self.file or self.file.file_type != 'xml':
            print("当前文件不是XML文件")
            return False
        if element_id not in self.file.element_map:
            print(f"元素不存在: {element_id}")
            return False
        self.element = self.file.element_map[element_id]
        self.old_text = self.element.text
        self.element.text = self.new_text
        # Lab2修改: 移除手动设置state，由装饰器自动处理
        # self.file.state = "modified"
        print(f"成功修改元素 {element_id} 的文本内容")
        WorkSpace.WorkSpace.logger.log_command(self.file.filePath, f'edit-text {element_id} "{self.new_text}"')
        self.file.add_to_history(self)
        return True
    
    def undo(self):
        if self.file and self.element:
            self.element.text = self.old_text
            print("撤销文本修改操作成功")
    
    def redo(self):
        if self.file and self.element:
            self.element.text = self.new_text
            print("重做文本修改操作成功")


class DeleteElementCommand(XmlEditCommand):
    """delete命令"""
    def __init__(self):
        self.file = None
        self.element = None
        self.parent_element = None
        self.element_index = -1
    
    def execute(self, command):
        args = command.split()
        if len(args) != 2:
            print("参数错误，应为：delete <elementId>")
            return False
        element_id = args[1]
        if not WorkSpace.WorkSpace.current_workFile_path:
            print("没有打开的文件")
            return False
        self.file = WorkSpace.WorkSpace.current_workFile_list.get(WorkSpace.WorkSpace.current_workFile_path)
        if not self.file or self.file.file_type != 'xml':
            print("当前文件不是XML文件")
            return False
        if element_id not in self.file.element_map:
            print(f"元素不存在: {element_id}")
            return False
        self.element = self.file.element_map[element_id]
        if self.element == self.file.root:
            print("不能删除根元素")
            return False
        self.parent_element = self.element.parent
        if not self.parent_element:
            print("元素没有父元素")
            return False
        self.element_index = self.parent_element.children.index(self.element)
        self.parent_element.remove_child(self.element)
        self._remove_from_map(self.element)
        # Lab2修改: 移除手动设置state，由装饰器自动处理
        # self.file.state = "modified"
        print(f"成功删除元素 {element_id}")
        WorkSpace.WorkSpace.logger.log_command(self.file.filePath, f'delete {element_id}')
        self.file.add_to_history(self)
        return True
    
    def _remove_from_map(self, element):
        element_id = element.get_id()
        if element_id in self.file.element_map:
            del self.file.element_map[element_id]
        for child in element.children:
            self._remove_from_map(child)
    
    def _add_to_map(self, element):
        element_id = element.get_id()
        if element_id:
            self.file.element_map[element_id] = element
        for child in element.children:
            self._add_to_map(child)
    
    def undo(self):
        if self.file and self.element and self.parent_element:
            self.element.parent = self.parent_element
            self.parent_element.children.insert(self.element_index, self.element)
            self._add_to_map(self.element)
            print("撤销删除操作成功")
    
    def redo(self):
        if self.file and self.element and self.parent_element:
            self.parent_element.remove_child(self.element)
            self._remove_from_map(self.element)
            print("重做删除操作成功")


class XmlTreeCommand(XmlEditCommand):
    """xml-tree命令"""
    def execute(self, command):
        args = command.split()
        if len(args) == 1:
            if not WorkSpace.WorkSpace.current_workFile_path:
                print("没有打开的文件")
                return False
            file_path = WorkSpace.WorkSpace.current_workFile_path
        elif len(args) == 2:
            file_path = args[1]
        else:
            print("参数错误，应为：xml-tree [file]")
            return False
        file = WorkSpace.WorkSpace.current_workFile_list.get(file_path)
        if not file:
            print(f"文件未打开: {file_path}")
            return False
        if file.file_type != 'xml':
            print("该文件不是XML文件")
            return False
        if not file.root:
            print("(空XML)")
            return False
        lines = file.root.to_tree_lines(prefix="", is_last=True)
        for line in lines:
            if lines.index(line) == 0:
                print(line[4:])
            else:
                print(line)
        return False
    
    def can_undo(self):
        return False


