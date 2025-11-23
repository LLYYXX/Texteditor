import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# 添加被测试模块的路径
sys.path.append('.')

# 导入被测试的类
from your_module import WorkSpace, LoadCommand, SaveCommand, InitCommand, CloseCommand, EditCommand, EditorListCommand, DirTreeCommand, UndoCommand, RedoCommand
import File
import CommonUtils
import Memento


class TestWorkSpace(unittest.TestCase):
    
    def setUp(self):
        """在每个测试前重置类变量"""
        WorkSpace.current_workFile_path = ""
        WorkSpace.current_workFile_list = {}
        WorkSpace.logOpen = False
        WorkSpace.recent_files = []
        File.FileList.all_files.clear()
        File.FileList.all_files_path.clear()
    
    def test_update_current_workFile_list(self):
        """测试更新当前工作文件列表"""
        with patch.object(Memento, 'update') as mock_update:
            WorkSpace.current_workFile_path = "/test/path"
            WorkSpace.current_workFile_list = {"file1": "content1"}
            
            WorkSpace.update_current_workFile_list()
            
            mock_update.assert_called_once_with("/test/path", {"file1": "content1"})
    
    def test_update_current_workFile_path(self):
        """测试更新当前工作文件路径"""
        with patch.object(Memento, 'update') as mock_update:
            WorkSpace.current_workFile_list = {"file1": "content1"}
            
            WorkSpace.update_current_workFile_path("/new/path")
            
            self.assertEqual(WorkSpace.current_workFile_path, "/new/path")
            mock_update.assert_called_once_with("/new/path", {"file1": "content1"})
    
    def test_recover_with_no_last_state(self):
        """测试恢复时没有保存的状态"""
        with patch.object(Memento, 'recover', return_value=None):
            WorkSpace.recover()
            
            self.assertEqual(WorkSpace.current_workFile_path, "")
            self.assertEqual(WorkSpace.current_workFile_list, {})
            self.assertEqual(WorkSpace.recent_files, [])
    
    def test_recover_with_last_state(self):
        """测试恢复时有保存的状态"""
        mock_state = {
            "current_workFile_path": "/current/file",
            "all_files": [
                {
                    "filePath": "/current/file",
                    "content": ["line1", "line2"],
                    "state": "normal"
                },
                {
                    "filePath": "/another/file",
                    "content": ["line3", "line4"],
                    "state": "modified"
                }
            ],
            "current_workFile_list": {
                "/current/file": {},
                "/another/file": {}
            }
        }
        
        with patch.object(Memento, 'recover', return_value=mock_state):
            WorkSpace.recover()
            
            self.assertEqual(WorkSpace.current_workFile_path, "/current/file")
            self.assertEqual(len(WorkSpace.current_workFile_list), 2)
            self.assertEqual(len(WorkSpace.recent_files), 2)
            self.assertIn("/current/file", WorkSpace.recent_files)
            self.assertIn("/another/file", WorkSpace.recent_files)


class TestLoadCommand(unittest.TestCase):
    
    def setUp(self):
        WorkSpace.current_workFile_path = ""
        WorkSpace.current_workFile_list = {}
        WorkSpace.recent_files = []
        File.FileList.all_files.clear()
        File.FileList.all_files_path.clear()
    
    def test_load_command_invalid_args(self):
        """测试load命令参数错误"""
        command = LoadCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("load")
            mock_print.assert_called_with("参数错误，应为：load <file>")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_load_command_path_check_failed(self, mock_pathCheck):
        """测试load命令路径检查失败"""
        mock_pathCheck.return_value = False
        command = LoadCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("load /invalid/path")
            mock_pathCheck.assert_called_once_with("/invalid/path")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_load_command_file_already_open(self, mock_pathCheck):
        """测试load命令文件已打开"""
        mock_pathCheck.return_value = True
        WorkSpace.recent_files = ["/existing/file"]
        command = LoadCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("load /existing/file")
            mock_print.assert_called_with("当前文件已打开，请使用edit命令切换")
    
    @patch.object(CommonUtils, 'pathCheck')
    @patch.object(CommonUtils, 'create_newFile')
    def test_load_command_new_file(self, mock_create_newFile, mock_pathCheck):
        """测试load命令加载新文件"""
        mock_pathCheck.return_value = True
        mock_file = MagicMock()
        mock_create_newFile.return_value = mock_file
        command = LoadCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("load /new/file")
            
            mock_create_newFile.assert_called_once_with("/new/file")
            self.assertIn("/new/file", WorkSpace.current_workFile_list)
            self.assertEqual(WorkSpace.current_workFile_list["/new/file"], mock_file)
            self.assertEqual(WorkSpace.current_workFile_path, "/new/file")
            self.assertIn("/new/file", WorkSpace.recent_files)
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_load_command_existing_file(self, mock_pathCheck):
        """测试load命令加载已存在文件"""
        mock_pathCheck.return_value = True
        mock_file = MagicMock()
        File.FileList.all_files_path.add("/existing/file")
        File.FileList.all_files["/existing/file"] = mock_file
        command = LoadCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("load /existing/file")
            
            self.assertIn("/existing/file", WorkSpace.current_workFile_list)
            mock_print.assert_called_with("加载文件成功")


class TestSaveCommand(unittest.TestCase):
    
    def setUp(self):
        WorkSpace.current_workFile_path = "/current/file"
        WorkSpace.current_workFile_list = {}
        WorkSpace.recent_files = ["/current/file"]
    
    def test_save_command_no_args(self):
        """测试save命令无参数"""
        command = SaveCommand()
        
        with patch.object(SaveCommand, 'save_single_file') as mock_save:
            command.execute("save")
            mock_save.assert_called_once_with("/current/file")
    
    def test_save_command_all(self):
        """测试save all命令"""
        command = SaveCommand()
        
        with patch.object(SaveCommand, 'save_all_files') as mock_save_all:
            command.execute("save all")
            mock_save_all.assert_called_once()
    
    def test_save_command_specific_file(self):
        """测试save指定文件命令"""
        mock_file = MagicMock()
        mock_file.filePath = "/specific/file"
        WorkSpace.current_workFile_list["/specific/file"] = mock_file
        command = SaveCommand()
        
        with patch.object(CommonUtils, 'pathCheck', return_value=True):
            with patch.object(SaveCommand, 'save_single_file') as mock_save:
                command.execute("save /specific/file")
                mock_save.assert_called_once_with("/specific/file")
    
    def test_save_command_invalid_args(self):
        """测试save命令参数错误"""
        command = SaveCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("save too many args")
            mock_print.assert_called_with("参数错误，应为：save [file|all]")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_single_file_success(self, mock_file):
        """测试保存单个文件成功"""
        mock_text_file = MagicMock()
        mock_text_file.content = ["line1", "line2", "line3"]
        mock_text_file.state = "modified"
        WorkSpace.current_workFile_list["/test/file"] = mock_text_file
        command = SaveCommand()
        
        with patch('builtins.print') as mock_print:
            command.save_single_file("/test/file")
            
            mock_file.assert_called_once_with("/test/file", 'w', encoding='utf-8')
            mock_file().write.assert_any_call("line1\n")
            mock_file().write.assert_any_call("line2\n")
            mock_file().write.assert_any_call("line3\n")
            self.assertEqual(mock_text_file.state, "normal")
            mock_print.assert_called_with("保存文件 /test/file 成功")
    
    def test_save_single_file_no_current_file(self):
        """测试保存单个文件时没有当前文件"""
        WorkSpace.current_workFile_path = ""
        command = SaveCommand()
        
        with patch('builtins.print') as mock_print:
            command.save_single_file("/test/file")
            mock_print.assert_called_with("没有打开的文件")
    
    def test_save_single_file_not_in_list(self):
        """测试保存不在工作列表中的文件"""
        command = SaveCommand()
        
        with patch('builtins.print') as mock_print:
            command.save_single_file("/nonexistent/file")
            mock_print.assert_called_with("文件不存在")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_all_files(self, mock_file):
        """测试保存所有文件"""
        mock_file1 = MagicMock()
        mock_file1.content = ["content1"]
        mock_file1.state = "modified"
        
        mock_file2 = MagicMock()
        mock_file2.content = ["content2"]
        mock_file2.state = "modified"
        
        WorkSpace.current_workFile_list = {
            "/file1": mock_file1,
            "/file2": mock_file2
        }
        command = SaveCommand()
        
        with patch('builtins.print') as mock_print:
            command.save_all_files()
            
            self.assertEqual(mock_file1.state, "normal")
            self.assertEqual(mock_file2.state, "normal")
            self.assertEqual(mock_print.call_count, 3)  # 2个成功消息 + 1个完成消息


class TestInitCommand(unittest.TestCase):
    
    def setUp(self):
        WorkSpace.current_workFile_path = ""
        WorkSpace.current_workFile_list = {}
        WorkSpace.recent_files = []
        File.FileList.all_files.clear()
        File.FileList.all_files_path.clear()
    
    def test_init_command_invalid_args(self):
        """测试init命令参数错误"""
        command = InitCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("init")
            mock_print.assert_called_with("参数错误")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_init_command_path_check_failed(self, mock_pathCheck):
        """测试init命令路径检查失败"""
        mock_pathCheck.return_value = False
        command = InitCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("init /invalid/path")
            mock_print.assert_called_with("参数错误")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_init_command_file_exists(self, mock_pathCheck):
        """测试init命令文件已存在"""
        mock_pathCheck.return_value = True
        File.FileList.all_files_path.add("/existing/file")
        command = InitCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("init /existing/file")
            mock_print.assert_called_with("文件已存在")
    
    @patch.object(CommonUtils, 'pathCheck')
    @patch.object(CommonUtils, 'create_newFile')
    def test_init_command_success(self, mock_create_newFile, mock_pathCheck):
        """测试init命令成功"""
        mock_pathCheck.return_value = True
        mock_file = MagicMock()
        mock_create_newFile.return_value = mock_file
        command = InitCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("init /new/file")
            
            mock_create_newFile.assert_called_once_with("/new/file", False)
            self.assertIn("/new/file", WorkSpace.current_workFile_list)
            self.assertEqual(WorkSpace.current_workFile_path, "/new/file")
            self.assertIn("/new/file", WorkSpace.recent_files)
            mock_print.assert_called_with("初始化文件成功")
    
    @patch.object(CommonUtils, 'pathCheck')
    @patch.object(CommonUtils, 'create_newFile')
    def test_init_command_with_log(self, mock_create_newFile, mock_pathCheck):
        """测试init命令带日志"""
        mock_pathCheck.return_value = True
        mock_file = MagicMock()
        mock_create_newFile.return_value = mock_file
        command = InitCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("init /new/file with-log")
            
            mock_create_newFile.assert_called_once_with("/new/file", True)
            mock_print.assert_called_with("初始化文件成功")


class TestCloseCommand(unittest.TestCase):
    
    def setUp(self):
        WorkSpace.current_workFile_path = "/current/file"
        WorkSpace.recent_files = ["/file1", "/current/file", "/file2"]
        
        mock_file = MagicMock()
        mock_file.filePath = "/current/file"
        mock_file.state = "normal"
        WorkSpace.current_workFile_list = {
            "/current/file": mock_file,
            "/file1": MagicMock(),
            "/file2": MagicMock()
        }
    
    def test_close_command_no_args(self):
        """测试close命令无参数"""
        command = CloseCommand()
        
        with patch('builtins.input', return_value='n'):
            with patch('builtins.print') as mock_print:
                command.execute("close")
                
                self.assertNotIn("/current/file", WorkSpace.current_workFile_list)
                self.assertNotIn("/current/file", WorkSpace.recent_files)
                self.assertEqual(WorkSpace.current_workFile_path, "/file2")
                mock_print.assert_called_with("关闭文件成功")
    
    def test_close_command_specific_file(self):
        """测试close命令指定文件"""
        command = CloseCommand()
        
        with patch.object(CommonUtils, 'pathCheck', return_value=True):
            with patch('builtins.input', return_value='n'):
                with patch('builtins.print') as mock_print:
                    command.execute("close /file1")
                    
                    self.assertNotIn("/file1", WorkSpace.current_workFile_list)
                    self.assertNotIn("/file1", WorkSpace.recent_files)
                    mock_print.assert_called_with("关闭文件成功")
    
    def test_close_command_modified_file_save(self):
        """测试关闭已修改文件并保存"""
        mock_file = MagicMock()
        mock_file.filePath = "/current/file"
        mock_file.state = "modified"
        WorkSpace.current_workFile_list["/current/file"] = mock_file
        command = CloseCommand()
        
        with patch('builtins.input', return_value='y'):
            with patch.object(SaveCommand, 'execute') as mock_save:
                with patch('builtins.print') as mock_print:
                    command.execute("close")
                    
                    mock_save.assert_called_once_with("save /current/file")
                    self.assertNotIn("/current/file", WorkSpace.current_workFile_list)
                    mock_print.assert_called_with("关闭文件成功")
    
    def test_close_command_modified_file_dont_save(self):
        """测试关闭已修改文件不保存"""
        mock_file = MagicMock()
        mock_file.filePath = "/current/file"
        mock_file.state = "modified"
        WorkSpace.current_workFile_list["/current/file"] = mock_file
        command = CloseCommand()
        
        with patch('builtins.input', return_value='n'):
            with patch('builtins.print') as mock_print:
                command.execute("close")
                
                self.assertNotIn("/current/file", WorkSpace.current_workFile_list)
                mock_print.assert_called_with("关闭文件成功")
    
    def test_close_command_invalid_input(self):
        """测试关闭文件时输入无效参数"""
        mock_file = MagicMock()
        mock_file.filePath = "/current/file"
        mock_file.state = "modified"
        WorkSpace.current_workFile_list["/current/file"] = mock_file
        command = CloseCommand()
        
        with patch('builtins.input', return_value='invalid'):
            with patch('builtins.print') as mock_print:
                command.execute("close")
                
                mock_print.assert_called_with("参数错误")
                # 文件应该没有被关闭
                self.assertIn("/current/file", WorkSpace.current_workFile_list)


class TestEditCommand(unittest.TestCase):
    
    def setUp(self):
        WorkSpace.current_workFile_path = "/old/file"
        WorkSpace.recent_files = ["/old/file"]
        
        mock_file = MagicMock()
        mock_file.filePath = "/new/file"
        WorkSpace.current_workFile_list = {
            "/old/file": MagicMock(),
            "/new/file": mock_file
        }
    
    def test_edit_command_invalid_args(self):
        """测试edit命令参数错误"""
        command = EditCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("edit")
            mock_print.assert_called_with("参数错误，应为：edit <file>")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_edit_command_path_check_failed(self, mock_pathCheck):
        """测试edit命令路径检查失败"""
        mock_pathCheck.return_value = False
        command = EditCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("edit /invalid/path")
            mock_print.assert_called_with("参数错误")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_edit_command_file_not_in_workspace(self, mock_pathCheck):
        """测试edit命令文件不在工作区"""
        mock_pathCheck.return_value = True
        command = EditCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("edit /nonexistent/file")
            mock_print.assert_called_with("该文件不在当前工作区中")
    
    @patch.object(CommonUtils, 'pathCheck')
    def test_edit_command_success(self, mock_pathCheck):
        """测试edit命令成功"""
        mock_pathCheck.return_value = True
        command = EditCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("edit /new/file")
            
            self.assertEqual(WorkSpace.current_workFile_path, "/new/file")
            self.assertEqual(WorkSpace.recent_files, ["/new/file"])
            mock_print.assert_called_with("切换到文件/new/file成功")


class TestEditorListCommand(unittest.TestCase):
    
    def test_editor_list_command(self):
        """测试editor-list命令"""
        mock_file1 = MagicMock()
        mock_file1.filePath = "/file1"
        mock_file2 = MagicMock()
        mock_file2.filePath = "/file2"
        WorkSpace.current_workFile_list = {
            "/file1": mock_file1,
            "/file2": mock_file2
        }
        command = EditorListCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("editor-list")
            
            self.assertEqual(mock_print.call_count, 2)
            mock_print.assert_any_call("/file1")
            mock_print.assert_any_call("/file2")
    
    def test_editor_list_command_invalid_args(self):
        """测试editor-list命令参数错误"""
        command = EditorListCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("editor-list extra")
            mock_print.assert_called_with("参数错误，应为：editor-list")


class TestDirTreeCommand(unittest.TestCase):
    
    def setUp(self):
        File.FileList.all_files_path.clear()
    
    def test_dir_tree_command_empty(self):
        """测试dir-tree命令空目录"""
        command = DirTreeCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("dir-tree")
            mock_print.assert_called_with("(空)")
    
    def test_dir_tree_command_with_files(self):
        """测试dir-tree命令有文件"""
        File.FileList.all_files_path.update([
            "root/file1.txt",
            "root/dir1/file2.txt",
            "root/dir1/subdir/file3.txt",
            "root/dir2/file4.txt"
        ])
        command = DirTreeCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("dir-tree")
            
            # 验证至少打印了一些内容
            self.assertGreater(mock_print.call_count, 0)
    
    def test_dir_tree_command_invalid_args(self):
        """测试dir-tree命令参数错误"""
        command = DirTreeCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("dir-tree extra")
            mock_print.assert_called_with("参数错误，应为：dir-tree")


class TestUndoCommand(unittest.TestCase):
    
    def test_undo_command_no_current_file(self):
        """测试undo命令没有当前文件"""
        WorkSpace.current_workFile_path = ""
        command = UndoCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("undo")
            mock_print.assert_called_with("没有打开的文件")
    
    def test_undo_command_file_not_in_list(self):
        """测试undo命令文件不在列表中"""
        WorkSpace.current_workFile_path = "/nonexistent/file"
        command = UndoCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("undo")
            mock_print.assert_called_with("当前文件不存在")
    
    def test_undo_command_success(self):
        """测试undo命令成功"""
        mock_file = MagicMock()
        WorkSpace.current_workFile_path = "/current/file"
        WorkSpace.current_workFile_list["/current/file"] = mock_file
        command = UndoCommand()
        
        command.execute("undo")
        
        mock_file.undo.assert_called_once()
    
    def test_undo_command_invalid_args(self):
        """测试undo命令参数错误"""
        command = UndoCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("undo extra")
            mock_print.assert_called_with("参数错误，应为：undo")


class TestRedoCommand(unittest.TestCase):
    
    def test_redo_command_no_current_file(self):
        """测试redo命令没有当前文件"""
        WorkSpace.current_workFile_path = ""
        command = RedoCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("redo")
            mock_print.assert_called_with("没有打开的文件")
    
    def test_redo_command_file_not_in_list(self):
        """测试redo命令文件不在列表中"""
        WorkSpace.current_workFile_path = "/nonexistent/file"
        command = RedoCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("redo")
            mock_print.assert_called_with("当前文件不存在")
    
    def test_redo_command_success(self):
        """测试redo命令成功"""
        mock_file = MagicMock()
        WorkSpace.current_workFile_path = "/current/file"
        WorkSpace.current_workFile_list["/current/file"] = mock_file
        command = RedoCommand()
        
        command.execute("redo")
        
        mock_file.redo.assert_called_once()
    
    def test_redo_command_invalid_args(self):
        """测试redo命令参数错误"""
        command = RedoCommand()
        
        with patch('builtins.print') as mock_print:
            command.execute("redo extra")
            mock_print.assert_called_with("参数错误，应为：redo")


if __name__ == '__main__':
    unittest.main()