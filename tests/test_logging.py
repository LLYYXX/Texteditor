import unittest
import os
import shutil
import sys
import time
from datetime import datetime

# 将项目根目录加入路径，确保能导入 src 模块
# 假设当前文件在 tests/ 目录下，向上两级找到项目根目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import WorkSpace
import Logging
import File

class TestLoggingSystem(unittest.TestCase):

    def setUp(self):
        """每个测试开始前的初始化"""
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_env")
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # 1. 重置 WorkSpace 全局状态
        WorkSpace.WorkSpace.current_workFile_list = {}
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.recent_files = []
        
        # 2. 重置 File.FileList 全局状态
        File.FileList.all_files = {}
        File.FileList.all_files_path = set()
        
        # 3. 重置 Logger (创建一个新的实例替换旧的)
        WorkSpace.WorkSpace.logger = Logging.Logger()
        
        # 4. 准备测试文件路径
        self.filename = "test_doc.txt"
        self.filepath = os.path.join(self.test_dir, self.filename)
        self.log_filepath = os.path.join(self.test_dir, ".test_doc.txt.log")
        
        # 5. 在磁盘创建物理文件
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write("Initial content\n")

        # 6. 注册文件到系统 (模拟 load 后的状态)
        self.file_obj = File.TextFile(self.filepath)
        self.file_obj.content = ["Initial content"]

        File.FileList.all_files[self.filepath] = self.file_obj
        File.FileList.all_files_path.add(self.filepath)
        
        # 7. 设置为当前活动文件
        WorkSpace.WorkSpace.current_workFile_list[self.filepath] = self.file_obj
        WorkSpace.WorkSpace.current_workFile_path = self.filepath

    def tearDown(self):
        """每个测试结束后的清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # ==================== 核心功能测试 ====================

    def test_filename_generation(self):
        """测试日志文件名生成规则"""
        logger = WorkSpace.WorkSpace.logger
        # Windows 路径测试
        path = r"d:\data\my_file.txt"
        log_path = logger._get_log_filename(path)
        self.assertTrue(log_path.endswith(".my_file.txt.log"))

    def test_enable_logging_creates_file(self):
        """测试启用日志是否创建文件并写入 Session Header"""
        logger = WorkSpace.WorkSpace.logger
        logger.enable_logging(self.filepath)
        
        self.assertTrue(os.path.exists(self.log_filepath), "日志文件未创建")
        
        with open(self.log_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("session start at", content)

    def test_log_command_writing(self):
        """测试命令写入功能"""
        logger = WorkSpace.WorkSpace.logger
        logger.enable_logging(self.filepath)
        
        cmd = 'append "Hello World"'
        logger.log_command(self.filepath, cmd)
        
        with open(self.log_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 应该有两行：Session Header 和 Command
            self.assertTrue(len(lines) >= 2)
            self.assertIn(cmd, lines[-1])
            # 验证包含时间戳 (简单检查是否以数字开头)
            self.assertTrue(lines[-1][0].isdigit())

    # ==================== 命令类测试 ====================

    def test_log_on_command_current_file(self):
        """测试 log-on (无参数，针对当前文件)"""
        cmd = Logging.LogOnCommand()
        cmd.execute("log-on")
        
        self.assertTrue(WorkSpace.WorkSpace.logger.is_logging_enabled(self.filepath))
        self.assertTrue(os.path.exists(self.log_filepath))

    def test_log_on_command_specific_file(self):
        """测试 log-on "path" (指定文件)"""
        # 创建另一个文件
        other_filename = "other.txt"
        other_path = os.path.join(self.test_dir, other_filename)
        other_log_path = os.path.join(self.test_dir, ".other.txt.log")
        
        # 注册到系统
        File.FileList.all_files_path.add(other_path)
        
        cmd = Logging.LogOnCommand()
        cmd.execute(f'log-on {other_path}')
        
        self.assertTrue(WorkSpace.WorkSpace.logger.is_logging_enabled(other_path))
        # 确保当前文件没有被错误开启
        # (注意：setUp里默认是关闭的，除非显式开启)
        self.assertFalse(WorkSpace.WorkSpace.logger.is_logging_enabled(self.filepath))

    def test_log_off_command(self):
        """测试 log-off"""
        # 先开启
        WorkSpace.WorkSpace.logger.enable_logging(self.filepath)
        self.assertTrue(WorkSpace.WorkSpace.logger.is_logging_enabled(self.filepath))
        
        # 执行关闭命令
        cmd = Logging.LogOffCommand()
        cmd.execute("log-off")
        
        self.assertFalse(WorkSpace.WorkSpace.logger.is_logging_enabled(self.filepath))
        
        # 验证关闭后不再写入
        WorkSpace.WorkSpace.logger.log_command(self.filepath, "should_not_appear")
        with open(self.log_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertNotIn("should_not_appear", content)

    def test_log_show_command(self):
        """测试 log-show 读取内容"""
        logger = WorkSpace.WorkSpace.logger
        logger.enable_logging(self.filepath)
        logger.log_command(self.filepath, "test_cmd")
        
        # 直接测试 show_log 方法的返回值
        content = logger.show_log(self.filepath)
        self.assertIn("session start at", content)
        self.assertIn("test_cmd", content)

    def test_log_on_invalid_file(self):
        """测试 log-on 一个不存在的文件"""
        # 捕获 stdout 输出
        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd = Logging.LogOnCommand()
        cmd.execute('log-on "non_existent_file.txt"')
        
        sys.stdout = sys.__stdout__ # 恢复 stdout
        self.assertIn("当前文件不存在", captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()