"""
Lab2新增: 拼写检查单元测试
测试适配器模式的应用
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import SpellChecker
import File
import WorkSpace


class TestSpellCheckInterface(unittest.TestCase):
    """测试拼写检查接口"""
    
    def test_interface_definition(self):
        """测试接口定义"""
        # 接口应该定义check_text方法
        self.assertTrue(hasattr(SpellChecker.SpellCheckInterface, 'check_text'))


class TestMockSpellChecker(unittest.TestCase):
    """测试Mock拼写检查器（适配器模式）"""
    
    def setUp(self):
        """准备测试环境"""
        self.checker = SpellChecker.MockSpellChecker()
    
    def test_check_known_error(self):
        """测试检查已知错误"""
        errors = self.checker.check_text("I recieve your message")
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['word'], 'recieve')
        self.assertIn('receive', errors[0]['suggestions'])
    
    def test_check_multiple_errors(self):
        """测试检查多个错误"""
        errors = self.checker.check_text("This occured and was seperate")
        
        self.assertEqual(len(errors), 2)
        words = [e['word'] for e in errors]
        self.assertIn('occured', words)
        self.assertIn('seperate', words)
    
    def test_check_correct_text(self):
        """测试检查正确的文本"""
        errors = self.checker.check_text("This is correct text")
        
        self.assertEqual(len(errors), 0)
    
    def test_check_empty_text(self):
        """测试检查空文本"""
        errors = self.checker.check_text("")
        
        self.assertEqual(len(errors), 0)


class TestPySpellCheckerAdapter(unittest.TestCase):
    """测试PySpellChecker适配器"""
    
    def setUp(self):
        """准备测试环境"""
        self.adapter = SpellChecker.PySpellCheckerAdapter()
    
    def test_adapter_creation(self):
        """测试适配器创建"""
        # 适配器应该实现SpellCheckInterface
        self.assertIsInstance(self.adapter, SpellChecker.SpellCheckInterface)
    
    def test_check_text_interface(self):
        """测试check_text接口"""
        # 即使库未安装，check_text方法也应该存在
        self.assertTrue(hasattr(self.adapter, 'check_text'))
        
        # 调用应该返回列表（可能为空）
        result = self.adapter.check_text("test")
        self.assertIsInstance(result, list)


class TestSpellCheckService(unittest.TestCase):
    """测试拼写检查服务"""
    
    def setUp(self):
        """准备测试环境"""
        # 使用Mock检查器以确保测试稳定
        mock_checker = SpellChecker.MockSpellChecker()
        self.service = SpellChecker.SpellCheckService(mock_checker)
        
        # 准备WorkSpace环境
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
    
    def test_check_text_file(self):
        """测试检查文本文件"""
        # 创建包含拼写错误的文本文件
        test_file = File.TextFile("test.txt", content=[
            "# log",
            "I recieve your message",
            "This occured yesterday"
        ])
        
        # 捕获输出
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.service.check_text_file(test_file)
        
        output = f.getvalue()
        
        # 验证输出包含错误信息
        self.assertIn("recieve", output)
        self.assertIn("receive", output)
        self.assertIn("occured", output)
        self.assertIn("occurred", output)
    
    def test_check_xml_file(self):
        """测试检查XML文件"""
        # 创建包含拼写错误的XML文件
        test_file = File.XmlFile("test.xml")
        
        # 添加包含拼写错误的元素
        import XmlEditor
        title = XmlEditor.XmlElement('title', {'id': 'title1'}, 'Itallian Food')
        author = XmlEditor.XmlElement('author', {'id': 'author1'}, 'Rowlling')
        test_file.root.add_child(title)
        test_file.root.add_child(author)
        test_file.element_map['title1'] = title
        test_file.element_map['author1'] = author
        
        # 捕获输出
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.service.check_xml_file(test_file)
        
        output = f.getvalue()
        
        # 验证输出包含错误信息
        self.assertIn("Itallian", output)
        self.assertIn("Italian", output)
        self.assertIn("Rowlling", output)
        self.assertIn("Rowling", output)
    
    def test_check_file_with_no_errors(self):
        """测试检查没有错误的文件"""
        test_file = File.TextFile("test.txt", content=["This is correct text"])
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.service.check_text_file(test_file)
        
        output = f.getvalue()
        
        self.assertIn("未发现拼写错误", output)


class TestSpellCheckCommand(unittest.TestCase):
    """测试spell-check命令"""
    
    def setUp(self):
        """准备测试环境"""
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
        
        # 使用Mock服务
        mock_checker = SpellChecker.MockSpellChecker()
        service = SpellChecker.SpellCheckService(mock_checker)
        self.cmd = SpellChecker.SpellCheckCommand(service)
    
    def test_check_current_file(self):
        """测试检查当前文件"""
        test_file = File.TextFile("test.txt", content=["I recieve your message"])
        WorkSpace.WorkSpace.current_workFile_path = "test.txt"
        WorkSpace.WorkSpace.current_workFile_list["test.txt"] = test_file
        
        result = self.cmd.execute("spell-check")
        
        # spell-check命令不应进入历史栈
        self.assertFalse(result)
        self.assertFalse(self.cmd.can_undo())
    
    def test_check_specified_file(self):
        """测试检查指定文件"""
        test_file = File.TextFile("other.txt", content=["I recieve your message"])
        WorkSpace.WorkSpace.current_workFile_list["other.txt"] = test_file
        
        result = self.cmd.execute("spell-check other.txt")
        
        self.assertFalse(result)
    
    def test_check_nonexistent_file(self):
        """测试检查不存在的文件"""
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = self.cmd.execute("spell-check nonexistent.txt")
        
        output = f.getvalue()
        
        self.assertFalse(result)
        self.assertIn("未打开", output)
    
    def test_check_without_active_file(self):
        """测试没有活动文件时检查"""
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = self.cmd.execute("spell-check")
        
        output = f.getvalue()
        
        self.assertFalse(result)
        self.assertIn("没有打开的文件", output)


class TestAdapterPattern(unittest.TestCase):
    """测试适配器模式的正确应用"""
    
    def test_multiple_adapters_same_interface(self):
        """测试多个适配器实现相同接口"""
        mock = SpellChecker.MockSpellChecker()
        py_adapter = SpellChecker.PySpellCheckerAdapter()
        
        # 两个适配器都应该实现相同的接口
        self.assertTrue(isinstance(mock, SpellChecker.SpellCheckInterface))
        self.assertTrue(isinstance(py_adapter, SpellChecker.SpellCheckInterface))
        
        # 都应该有check_text方法
        self.assertTrue(hasattr(mock, 'check_text'))
        self.assertTrue(hasattr(py_adapter, 'check_text'))
    
    def test_service_accepts_any_adapter(self):
        """测试服务可以接受任何适配器"""
        mock = SpellChecker.MockSpellChecker()
        service1 = SpellChecker.SpellCheckService(mock)
        
        py_adapter = SpellChecker.PySpellCheckerAdapter()
        service2 = SpellChecker.SpellCheckService(py_adapter)
        
        # 两个服务都应该正常工作
        self.assertIsNotNone(service1.spell_checker)
        self.assertIsNotNone(service2.spell_checker)


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSpellCheckInterface))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMockSpellChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPySpellCheckerAdapter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSpellCheckService))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSpellCheckCommand))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAdapterPattern))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print(f"\n{'='*70}")
    print(f"测试完成: 运行 {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"{'='*70}")

