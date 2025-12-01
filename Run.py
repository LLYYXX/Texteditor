import WorkSpace
import Memento
import EditorActions
import Logging
import XmlEditor  # Lab2新增
import SpellChecker  # Lab2新增

class CommandFactory:
    def __init__(self):
        self.commands = {
            # 工作区命令
            "load": WorkSpace.LoadCommand(),
            "save": WorkSpace.SaveCommand(),
            "init": WorkSpace.InitCommand(),
            "close": WorkSpace.CloseCommand(),
            "edit": WorkSpace.EditCommand(),
            "editor-list": WorkSpace.EditorListCommand(),
            "dir-tree": WorkSpace.DirTreeCommand(),
            "undo": WorkSpace.UndoCommand(),
            "redo": WorkSpace.RedoCommand(),

            # 文本编辑命令
            "append": EditorActions.AppendCommand(),
            "insert": EditorActions.InsertCommand(),
            "delete": EditorActions.DeleteCommand(),
            "replace": EditorActions.ReplaceCommand(),
            "show": EditorActions.ShowCommand(),

            # Lab2新增: XML编辑命令（使用装饰器模式自动标记文件修改状态）
            "insert-before": XmlEditor.ModifiedStateDecorator(XmlEditor.InsertBeforeCommand()),
            "append-child": XmlEditor.ModifiedStateDecorator(XmlEditor.AppendChildCommand()),
            "edit-id": XmlEditor.ModifiedStateDecorator(XmlEditor.EditIdCommand()),
            "edit-text": XmlEditor.ModifiedStateDecorator(XmlEditor.EditTextCommand()),
            "xml-tree": XmlEditor.XmlTreeCommand(),  # 查询命令不需要装饰器

            # Lab2新增: 拼写检查命令
            "spell-check": SpellChecker.SpellCheckCommand(),

            # 日志命令
            "log-on": Logging.LogOnCommand(),
            "log-off": Logging.LogOffCommand(),
            "log-show": Logging.LogShowCommand(),
        }
        # Lab2新增: XML delete命令（使用装饰器）
        self.xml_delete_command = XmlEditor.ModifiedStateDecorator(XmlEditor.DeleteElementCommand())

    def isValid(self, operator):
        return operator in self.commands or operator == "delete"

    def getCommand(self, operator):
        # Lab2修改: delete命令根据文件类型选择
        if operator == "delete":
            return self._get_delete_command()
        return self.commands.get(operator)
    
    def _get_delete_command(self):
        """智能选择delete命令"""
        if WorkSpace.WorkSpace.current_workFile_path:
            current_file = WorkSpace.WorkSpace.current_workFile_list.get(
                WorkSpace.WorkSpace.current_workFile_path
            )
            if current_file and hasattr(current_file, 'file_type') and current_file.file_type == 'xml':
                return self.xml_delete_command
        if "delete" not in self.commands:
            self.commands["delete"] = EditorActions.DeleteCommand()
        return self.commands["delete"]
    
if __name__ == "__main__":
    print("=" * 50)
    print("Lab2: 多文本编辑器")
    print("支持文本文件(.txt)和XML文件(.xml)")
    print("输入 'help' 查看命令帮助，'exit' 退出程序")
    print("=" * 50)
    
    cf=CommandFactory()
    last_state = Memento.recover()
    WorkSpace.WorkSpace.recover()
    
    while True:
        try:
            command = input("> ").strip()
            if not command:
                continue
            
            if(command == "exit"):
                # Lab2修改: 退出前停止所有文件的计时
                for filepath in WorkSpace.WorkSpace.current_workFile_list.keys():
                    WorkSpace.WorkSpace.statistics.stop_timing(filepath)
                Memento.update(WorkSpace.WorkSpace.current_workFile_path,WorkSpace.WorkSpace.current_workFile_list)
                print("工作区状态已保存，再见！")
                break
            
            # Lab2新增: help命令
            if command == "help":
                print("\n常用命令:")
                print("  init <text|xml> [with-log] - 创建新文件")
                print("  load <file>                - 加载文件")
                print("  save [file|all]            - 保存文件")
                print("  editor-list                - 查看文件列表(含编辑时长)")
                print("  xml-tree                   - 显示XML树")
                print("  spell-check                - 拼写检查")
                print("  help                       - 显示帮助")
                print("  exit                       - 退出程序\n")
                continue
            
            #调试用
            if(command == "curpath"):
                print(WorkSpace.WorkSpace.current_workFile_path)
                continue
            if(command == "curlist"):
                print(WorkSpace.WorkSpace.current_workFile_list)
                continue
            
            operator = command.split(" ")[0]
            if(not cf.isValid(operator)):
                print("不支持的操作，输入 'help' 查看帮助")
                continue
            cf.getCommand(operator).execute(command)
        
        except KeyboardInterrupt:
            print("\n使用 'exit' 命令退出程序")
        except Exception as e:
            print(f"执行命令时发生错误: {e}")
            import traceback
            traceback.print_exc()
        

