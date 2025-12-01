"""
Lab2新增: 日志增强功能单元测试
测试命令过滤功能
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Logging
import File
import WorkSpace


class TestLoggerCommandFiltering(unittest.TestCase):
    """测试日志命令过滤功能（Lab2新增）"""
    
    def setUp(self):
        """准备测试环境"""
        self.logger = Logging.Logger()
        
        # 清理环境
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
        
        # 清理可能存在的测试日志文件
        test_log = ".test_filter.txt.log"
        if os.path.exists(test_log):
            os.remove(test_log)
    
    def tearDown(self):
        """清理测试环境"""
        test_log = ".test_filter.txt.log"
        if os.path.exists(test_log):
            os.remove(test_log)
    
    def test_parse_log_config_no_filter(self):
        """测试解析不带过滤的日志配置"""
        # 创建只有 # log 的文件
        test_file = File.TextFile("test_filter.txt", content=["# log"])
        File.FileList.all_files["test_filter.txt"] = test_file
        
        self.logger.enable_logging("test_filter.txt")
        
        # 应该没有排除的命令
        self.assertNotIn("test_filter.txt", self.logger._excluded_commands)
    
    def test_parse_log_config_with_filter(self):
        """测试解析带过滤的日志配置"""
        # 创建带过滤配置的文件
        test_file = File.TextFile("test_filter.txt", content=["# log -e append -e delete"])
        File.FileList.all_files["test_filter.txt"] = test_file
        
        self.logger.enable_logging("test_filter.txt")
        
        # 应该有排除的命令
        self.assertIn("test_filter.txt", self.logger._excluded_commands)
        self.assertIn("append", self.logger._excluded_commands["test_filter.txt"])
        self.assertIn("delete", self.logger._excluded_commands["test_filter.txt"])
    
    def test_log_command_without_filter(self):
        """测试不过滤时正常记录日志"""
        test_file = File.TextFile("test_filter.txt", content=["# log"])
        File.FileList.all_files["test_filter.txt"] = test_file
        
        self.logger.enable_logging("test_filter.txt")
        self.logger.log_command("test_filter.txt", "append \"test\"")
        
        # 验证日志已写入
        log_content = self.logger.show_log("test_filter.txt")
        self.assertIn("append", log_content)
    
    def test_log_command_with_filter(self):
        """测试过滤特定命令"""
        test_file = File.TextFile("test_filter.txt", content=["# log -e append"])
        File.FileList.all_files["test_filter.txt"] = test_file
        
        self.logger.enable_logging("test_filter.txt")
        
        # 记录被过滤的命令
        self.logger.log_command("test_filter.txt", "append \"test\"")
        
        # 记录未被过滤的命令
        self.logger.log_command("test_filter.txt", "insert 1:1 \"test\"")
        
        # 验证日志内容
        log_content = self.logger.show_log("test_filter.txt")
        
        # append应该被过滤，不在日志中
        self.assertNotIn("append", log_content)
        
        # insert应该在日志中
        self.assertIn("insert", log_content)
    
    def test_multiple_filters(self):
        """测试多个命令过滤"""
        test_file = File.TextFile("test_filter.txt", content=["# log -e append -e delete -e replace"])
        File.FileList.all_files["test_filter.txt"] = test_file
        
        self.logger.enable_logging("test_filter.txt")
        
        # 验证所有过滤命令都被记录
        excluded = self.logger._excluded_commands["test_filter.txt"]
        self.assertIn("append", excluded)
        self.assertIn("delete", excluded)
        self.assertIn("replace", excluded)
    
    def test_filter_only_affects_target_file(self):
        """测试过滤只影响目标文件"""
        # 创建两个文件，一个有过滤，一个没有
        file1 = File.TextFile("file1.txt", content=["# log -e append"])
        file2 = File.TextFile("file2.txt", content=["# log"])
        
        File.FileList.all_files["file1.txt"] = file1
        File.FileList.all_files["file2.txt"] = file2
        
        self.logger.enable_logging("file1.txt")
        self.logger.enable_logging("file2.txt")
        
        # file1的append应该被过滤
        self.logger.log_command("file1.txt", "append \"test1\"")
        
        # file2的append不应该被过滤
        self.logger.log_command("file2.txt", "append \"test2\"")
        
        # 验证
        log1 = self.logger.show_log("file1.txt")
        log2 = self.logger.show_log("file2.txt")
        
        self.assertNotIn("append", log1)  # file1过滤了append
        self.assertIn("append", log2)     # file2没有过滤


class TestLoggerDisableWithFilter(unittest.TestCase):
    """测试禁用日志时清除过滤配置"""
    
    def setUp(self):
        """准备测试环境"""
        self.logger = Logging.Logger()
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
    
    def tearDown(self):
        """清理测试环境"""
        test_log = ".test.txt.log"
        if os.path.exists(test_log):
            os.remove(test_log)
    
    def test_disable_logging_clears_filter(self):
        """测试禁用日志时清除过滤配置"""
        test_file = File.TextFile("test.txt", content=["# log -e append"])
        File.FileList.all_files["test.txt"] = test_file
        
        self.logger.enable_logging("test.txt")
        
        # 验证过滤配置存在
        self.assertIn("test.txt", self.logger._excluded_commands)
        
        # 禁用日志
        self.logger.disable_logging("test.txt")
        
        # 验证过滤配置被清除
        self.assertNotIn("test.txt", self.logger._excluded_commands)


class TestLogConfigParsing(unittest.TestCase):
    """测试日志配置解析"""
    
    def setUp(self):
        """准备测试环境"""
        self.logger = Logging.Logger()
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
    
    def test_parse_simple_log(self):
        """测试解析简单的# log"""
        test_file = File.TextFile("test.txt", content=["# log"])
        File.FileList.all_files["test.txt"] = test_file
        
        self.logger._parse_log_config("test.txt")
        
        # 不应该有排除命令
        self.assertNotIn("test.txt", self.logger._excluded_commands)
    
    def test_parse_log_with_single_exclude(self):
        """测试解析带单个排除命令的配置"""
        test_file = File.TextFile("test.txt", content=["# log -e append"])
        File.FileList.all_files["test.txt"] = test_file
        
        self.logger._parse_log_config("test.txt")
        
        # 应该有一个排除命令
        self.assertIn("test.txt", self.logger._excluded_commands)
        self.assertEqual(len(self.logger._excluded_commands["test.txt"]), 1)
        self.assertIn("append", self.logger._excluded_commands["test.txt"])
    
    def test_parse_log_with_multiple_excludes(self):
        """测试解析带多个排除命令的配置"""
        test_file = File.TextFile("test.txt", content=["# log -e append -e delete -e insert"])
        File.FileList.all_files["test.txt"] = test_file
        
        self.logger._parse_log_config("test.txt")
        
        # 应该有三个排除命令
        excluded = self.logger._excluded_commands["test.txt"]
        self.assertEqual(len(excluded), 3)
        self.assertIn("append", excluded)
        self.assertIn("delete", excluded)
        self.assertIn("insert", excluded)
    
    def test_parse_xml_file_with_log_config(self):
        """测试解析XML文件的日志配置"""
        # XML文件的日志配置在序列化后的第一行
        test_file = File.XmlFile("test.xml", withLog=True)
        # 手动添加过滤配置（模拟用户编辑）
        test_file.has_log_comment = True
        
        # 创建一个带过滤的内容
        test_file_with_filter = File.TextFile("test2.xml", content=[
            "# log -e append-child -e delete"
        ])
        File.FileList.all_files["test2.xml"] = test_file_with_filter
        
        self.logger._parse_log_config("test2.xml")
        
        # 验证XML命令也可以被过滤
        excluded = self.logger._excluded_commands.get("test2.xml", set())
        self.assertIn("append-child", excluded)
        self.assertIn("delete", excluded)


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLoggerCommandFiltering))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLoggerDisableWithFilter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogConfigParsing))
    
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

