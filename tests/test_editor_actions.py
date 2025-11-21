"""
文本编辑命令单元测试模块
使用unittest框架实现全覆盖自动化测试
"""
import unittest
import sys
import os

# 添加项目根目录到路径（tests目录的父目录）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import File
import WorkSpace
import EditorActions


class TestEditorActionsBase(unittest.TestCase):
    """测试基类 - 提供通用的setUp和tearDown"""
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 清理环境
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        WorkSpace.WorkSpace.recent_files = []
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
        
        # 创建测试文件
        self.test_file_path = "test_file.txt"
        self.test_file = File.TextFile(self.test_file_path)
        File.FileList.all_files_path.add(self.test_file_path)
        File.FileList.all_files[self.test_file_path] = self.test_file
        WorkSpace.WorkSpace.current_workFile_path = self.test_file_path
        WorkSpace.WorkSpace.current_workFile_list[self.test_file_path] = self.test_file
        WorkSpace.WorkSpace.recent_files.append(self.test_file_path)
    
    def tearDown(self):
        """每个测试后的清理工作"""
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        WorkSpace.WorkSpace.recent_files = []
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()


class TestAppendCommand(TestEditorActionsBase):
    """测试AppendCommand - 追加文本命令"""
    
    def test_append_single_line(self):
        """测试追加单行文本"""
        cmd = EditorActions.AppendCommand()
        result = cmd.execute('append "Hello World"')
        
        self.assertTrue(result)
        self.assertEqual(len(self.test_file.content), 1)
        self.assertEqual(self.test_file.content[0], "Hello World")
        self.assertEqual(self.test_file.state, "modified")
    
    def test_append_multiple_lines(self):
        """测试追加多行文本"""
        cmd1 = EditorActions.AppendCommand()
        cmd2 = EditorActions.AppendCommand()
        cmd3 = EditorActions.AppendCommand()
        
        cmd1.execute('append "Line 1"')
        cmd2.execute('append "Line 2"')
        cmd3.execute('append "Line 3"')
        
        self.assertEqual(len(self.test_file.content), 3)
        self.assertEqual(self.test_file.content[0], "Line 1")
        self.assertEqual(self.test_file.content[1], "Line 2")
        self.assertEqual(self.test_file.content[2], "Line 3")
    
    def test_append_empty_string(self):
        """测试追加空字符串"""
        cmd = EditorActions.AppendCommand()
        result = cmd.execute('append ""')
        
        self.assertTrue(result)
        self.assertEqual(len(self.test_file.content), 1)
        self.assertEqual(self.test_file.content[0], "")
    
    def test_append_special_characters(self):
        """测试追加特殊字符"""
        cmd = EditorActions.AppendCommand()
        result = cmd.execute('append "!@#$%^&*()_+-=[]{}|;:,.<>?"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "!@#$%^&*()_+-=[]{}|;:,.<>?")
    
    def test_append_chinese_characters(self):
        """测试追加中文字符"""
        cmd = EditorActions.AppendCommand()
        result = cmd.execute('append "你好，世界！"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "你好，世界！")
    
    def test_append_without_quotes(self):
        """测试没有引号的追加命令（应该失败）"""
        cmd = EditorActions.AppendCommand()
        result = cmd.execute('append test')
        
        self.assertFalse(result)
    
    def test_append_command_history(self):
        """测试追加命令是否正确添加到历史记录"""
        cmd = EditorActions.AppendCommand()
        cmd.execute('append "Test"')
        
        self.assertEqual(len(self.test_file.command_history), 1)
        self.assertIsInstance(self.test_file.command_history[0], EditorActions.AppendCommand)
    
    def test_append_undo(self):
        """测试追加命令的撤销"""
        cmd = EditorActions.AppendCommand()
        cmd.execute('append "Test Line"')
        
        self.assertEqual(len(self.test_file.content), 1)
        
        self.test_file.undo()
        self.assertEqual(len(self.test_file.content), 0)
    
    def test_append_redo(self):
        """测试追加命令的重做"""
        cmd = EditorActions.AppendCommand()
        cmd.execute('append "Test Line"')
        self.test_file.undo()
        self.test_file.redo()
        
        self.assertEqual(len(self.test_file.content), 1)
        self.assertEqual(self.test_file.content[0], "Test Line")


class TestInsertCommand(TestEditorActionsBase):
    """测试InsertCommand - 插入文本命令"""
    
    def test_insert_in_empty_file_at_1_1(self):
        """测试在空文件的1:1位置插入"""
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:1 "First Line"')
        
        self.assertTrue(result)
        self.assertEqual(len(self.test_file.content), 1)
        self.assertEqual(self.test_file.content[0], "First Line")
    
    def test_insert_in_empty_file_at_invalid_position(self):
        """测试在空文件的非1:1位置插入（应该失败）"""
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:2 "Test"')
        
        self.assertFalse(result)
    
    def test_insert_at_beginning_of_line(self):
        """测试在行首插入"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:1 "Start "')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Start Hello World")
    
    def test_insert_in_middle_of_line(self):
        """测试在行中间插入"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:7 "Beautiful "')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hello Beautiful World")
    
    def test_insert_at_end_of_line(self):
        """测试在行尾插入"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:6 " World"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hello World")
    
    def test_insert_multiline_text(self):
        """测试插入多行文本"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:6 "\\nNew Line\\nAnother"')
        
        self.assertTrue(result)
        self.assertGreater(len(self.test_file.content), 1)
    
    def test_insert_invalid_line_number(self):
        """测试无效的行号"""
        self.test_file.content = ["Line 1"]
        
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 10:1 "Test"')
        
        self.assertFalse(result)
    
    def test_insert_invalid_column_number(self):
        """测试无效的列号"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.InsertCommand()
        result = cmd.execute('insert 1:100 "Test"')
        
        self.assertFalse(result)
    
    def test_insert_undo(self):
        """测试插入命令的撤销"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.InsertCommand()
        cmd.execute('insert 1:7 "Beautiful "')
        self.test_file.undo()
        
        self.assertEqual(self.test_file.content[0], "Hello World")
    
    def test_insert_redo(self):
        """测试插入命令的重做"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.InsertCommand()
        cmd.execute('insert 1:7 "Beautiful "')
        self.test_file.undo()
        self.test_file.redo()
        
        self.assertEqual(self.test_file.content[0], "Hello Beautiful World")


class TestDeleteCommand(TestEditorActionsBase):
    """测试DeleteCommand - 删除字符命令"""
    
    def test_delete_from_beginning(self):
        """测试从行首删除"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 1:1 6')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "World")
    
    def test_delete_from_middle(self):
        """测试从中间删除"""
        self.test_file.content = ["Hello Beautiful World"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 1:7 10')
        
        self.assertTrue(result)
        # 删除从第7位开始的10个字符 "Beautiful "，剩下 "Hello World"
        self.assertEqual(self.test_file.content[0], "Hello World")
    
    def test_delete_to_end_of_line(self):
        """测试删除到行尾"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 1:7 5')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hello ")
    
    def test_delete_entire_line_content(self):
        """测试删除整行内容"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 1:1 5')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "")
    
    def test_delete_length_exceeds_line(self):
        """测试删除长度超出行尾（应该失败）"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 1:1 100')
        
        self.assertFalse(result)
    
    def test_delete_invalid_line_number(self):
        """测试无效的行号"""
        self.test_file.content = ["Line 1"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 10:1 5')
        
        self.assertFalse(result)
    
    def test_delete_invalid_column_number(self):
        """测试无效的列号"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.DeleteCommand()
        result = cmd.execute('delete 1:100 5')
        
        self.assertFalse(result)
    
    def test_delete_undo(self):
        """测试删除命令的撤销"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.DeleteCommand()
        cmd.execute('delete 1:7 5')
        self.test_file.undo()
        
        self.assertEqual(self.test_file.content[0], "Hello World")
    
    def test_delete_redo(self):
        """测试删除命令的重做"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.DeleteCommand()
        cmd.execute('delete 1:7 5')
        self.test_file.undo()
        self.test_file.redo()
        
        self.assertEqual(self.test_file.content[0], "Hello ")


class TestReplaceCommand(TestEditorActionsBase):
    """测试ReplaceCommand - 替换字符命令"""
    
    def test_replace_at_beginning(self):
        """测试从行首替换"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 1:1 5 "Hi"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hi World")
    
    def test_replace_in_middle(self):
        """测试在中间替换"""
        self.test_file.content = ["fast fox"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 1:1 4 "slow"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "slow fox")
    
    def test_replace_with_longer_text(self):
        """测试用更长的文本替换"""
        self.test_file.content = ["Hi"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 1:1 2 "Hello World"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hello World")
    
    def test_replace_with_shorter_text(self):
        """测试用更短的文本替换"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 1:1 11 "Hi"')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hi")
    
    def test_replace_with_empty_string(self):
        """测试用空字符串替换（等同于删除）"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 1:7 5 ""')
        
        self.assertTrue(result)
        self.assertEqual(self.test_file.content[0], "Hello ")
    
    def test_replace_length_exceeds_line(self):
        """测试替换长度超出行尾（应该失败）"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 1:1 100 "Test"')
        
        self.assertFalse(result)
    
    def test_replace_invalid_position(self):
        """测试无效的位置"""
        self.test_file.content = ["Hello"]
        
        cmd = EditorActions.ReplaceCommand()
        result = cmd.execute('replace 10:1 5 "Test"')
        
        self.assertFalse(result)
    
    def test_replace_undo(self):
        """测试替换命令的撤销"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.ReplaceCommand()
        cmd.execute('replace 1:1 5 "Hi"')
        self.test_file.undo()
        
        self.assertEqual(self.test_file.content[0], "Hello World")
    
    def test_replace_redo(self):
        """测试替换命令的重做"""
        self.test_file.content = ["Hello World"]
        
        cmd = EditorActions.ReplaceCommand()
        cmd.execute('replace 1:1 5 "Hi"')
        self.test_file.undo()
        self.test_file.redo()
        
        self.assertEqual(self.test_file.content[0], "Hi World")


class TestShowCommand(TestEditorActionsBase):
    """测试ShowCommand - 显示内容命令"""
    
    def test_show_empty_file(self):
        """测试显示空文件"""
        cmd = EditorActions.ShowCommand()
        result = cmd.execute('show')
        
        self.assertFalse(result)
    
    def test_show_all_content(self):
        """测试显示全部内容"""
        self.test_file.content = ["Line 1", "Line 2", "Line 3"]
        
        cmd = EditorActions.ShowCommand()
        result = cmd.execute('show')
        
        self.assertFalse(result)  # show命令返回False（不进入历史栈）
    
    def test_show_range(self):
        """测试显示指定范围"""
        self.test_file.content = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        
        cmd = EditorActions.ShowCommand()
        result = cmd.execute('show 2:4')
        
        self.assertFalse(result)
    
    def test_show_invalid_range(self):
        """测试无效的范围"""
        self.test_file.content = ["Line 1", "Line 2"]
        
        cmd = EditorActions.ShowCommand()
        result = cmd.execute('show 5:10')
        
        self.assertFalse(result)
    
    def test_show_not_added_to_history(self):
        """测试show命令不添加到历史记录"""
        self.test_file.content = ["Line 1"]
        
        cmd = EditorActions.ShowCommand()
        cmd.execute('show')
        
        self.assertEqual(len(self.test_file.command_history), 0)
    
    def test_show_can_undo_returns_false(self):
        """测试show命令的can_undo返回False"""
        cmd = EditorActions.ShowCommand()
        self.assertFalse(cmd.can_undo())


class TestUndoRedoIntegration(TestEditorActionsBase):
    """测试Undo/Redo的集成功能"""
    
    def test_multiple_operations_undo(self):
        """测试多次操作后的撤销"""
        cmd1 = EditorActions.AppendCommand()
        cmd2 = EditorActions.AppendCommand()
        cmd3 = EditorActions.AppendCommand()
        
        cmd1.execute('append "Line 1"')
        cmd2.execute('append "Line 2"')
        cmd3.execute('append "Line 3"')
        
        self.assertEqual(len(self.test_file.content), 3)
        
        self.test_file.undo()
        self.assertEqual(len(self.test_file.content), 2)
        
        self.test_file.undo()
        self.assertEqual(len(self.test_file.content), 1)
        
        self.test_file.undo()
        self.assertEqual(len(self.test_file.content), 0)
    
    def test_multiple_undo_redo(self):
        """测试多次撤销和重做"""
        cmd1 = EditorActions.AppendCommand()
        cmd2 = EditorActions.AppendCommand()
        
        cmd1.execute('append "Line 1"')
        cmd2.execute('append "Line 2"')
        
        self.test_file.undo()
        self.test_file.undo()
        self.assertEqual(len(self.test_file.content), 0)
        
        self.test_file.redo()
        self.assertEqual(len(self.test_file.content), 1)
        self.assertEqual(self.test_file.content[0], "Line 1")
        
        self.test_file.redo()
        self.assertEqual(len(self.test_file.content), 2)
        self.assertEqual(self.test_file.content[1], "Line 2")
    
    def test_new_command_clears_redo_stack(self):
        """测试执行新命令清空redo栈"""
        cmd1 = EditorActions.AppendCommand()
        cmd2 = EditorActions.AppendCommand()
        cmd3 = EditorActions.AppendCommand()
        
        cmd1.execute('append "Line 1"')
        self.test_file.undo()
        
        self.assertEqual(len(self.test_file.redo_stack), 1)
        
        cmd2.execute('append "Line 2"')
        
        self.assertEqual(len(self.test_file.redo_stack), 0)
    
    def test_mixed_operations_undo_redo(self):
        """测试混合操作的撤销重做"""
        self.test_file.content = ["Hello World"]
        
        insert_cmd = EditorActions.InsertCommand()
        delete_cmd = EditorActions.DeleteCommand()
        replace_cmd = EditorActions.ReplaceCommand()
        
        insert_cmd.execute('insert 1:7 "Beautiful "')
        self.assertEqual(self.test_file.content[0], "Hello Beautiful World")
        
        delete_cmd.execute('delete 1:7 10')
        self.assertEqual(self.test_file.content[0], "Hello World")
        
        replace_cmd.execute('replace 1:1 5 "Hi"')
        self.assertEqual(self.test_file.content[0], "Hi World")
        
        # 撤销所有操作
        self.test_file.undo()
        self.assertEqual(self.test_file.content[0], "Hello World")
        
        self.test_file.undo()
        self.assertEqual(self.test_file.content[0], "Hello Beautiful World")
        
        self.test_file.undo()
        self.assertEqual(self.test_file.content[0], "Hello World")
        
        # 重做所有操作
        self.test_file.redo()
        self.assertEqual(self.test_file.content[0], "Hello Beautiful World")
        
        self.test_file.redo()
        self.assertEqual(self.test_file.content[0], "Hello World")
        
        self.test_file.redo()
        self.assertEqual(self.test_file.content[0], "Hi World")
    
    def test_undo_on_empty_history(self):
        """测试在空历史栈上撤销"""
        result = self.test_file.undo()
        self.assertFalse(result)
    
    def test_redo_on_empty_stack(self):
        """测试在空redo栈上重做"""
        result = self.test_file.redo()
        self.assertFalse(result)


class TestWorkSpaceUndoRedo(TestEditorActionsBase):
    """测试WorkSpace中的Undo/Redo命令"""
    
    def test_workspace_undo_command(self):
        """测试WorkSpace的undo命令"""
        append_cmd = EditorActions.AppendCommand()
        append_cmd.execute('append "Test"')
        
        undo_cmd = WorkSpace.UndoCommand()
        undo_cmd.execute('undo')
        
        self.assertEqual(len(self.test_file.content), 0)
    
    def test_workspace_redo_command(self):
        """测试WorkSpace的redo命令"""
        append_cmd = EditorActions.AppendCommand()
        append_cmd.execute('append "Test"')
        
        undo_cmd = WorkSpace.UndoCommand()
        undo_cmd.execute('undo')
        
        redo_cmd = WorkSpace.RedoCommand()
        redo_cmd.execute('redo')
        
        self.assertEqual(len(self.test_file.content), 1)
        self.assertEqual(self.test_file.content[0], "Test")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAppendCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestInsertCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestDeleteCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestReplaceCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestShowCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestUndoRedoIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkSpaceUndoRedo))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

