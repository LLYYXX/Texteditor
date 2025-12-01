"""
Lab2新增: 编辑时长统计单元测试
测试观察者模式和装饰器模式的应用
"""
import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Statistics


class TestStatisticsManager(unittest.TestCase):
    """测试统计管理器（观察者模式）"""
    
    def setUp(self):
        """准备测试环境"""
        self.stats = Statistics.StatisticsManager()
    
    def test_start_timing(self):
        """测试开始计时"""
        self.stats.start_timing("test.txt")
        
        # 验证计时已开始
        time.sleep(0.1)  # 等待一小段时间
        elapsed = self.stats.get_editing_time("test.txt")
        self.assertGreater(elapsed, 0)
        self.assertLess(elapsed, 1)  # 应该小于1秒
    
    def test_stop_timing(self):
        """测试停止计时"""
        self.stats.start_timing("test.txt")
        time.sleep(0.1)
        self.stats.stop_timing("test.txt")
        
        # 停止后时长不应再增加
        time1 = self.stats.get_editing_time("test.txt")
        time.sleep(0.1)
        time2 = self.stats.get_editing_time("test.txt")
        
        self.assertAlmostEqual(time1, time2, delta=0.01)
    
    def test_cumulative_timing(self):
        """测试累计计时"""
        # 第一次计时
        self.stats.start_timing("test.txt")
        time.sleep(0.1)
        self.stats.stop_timing("test.txt")
        time1 = self.stats.get_editing_time("test.txt")
        
        # 第二次计时（应该累加）
        self.stats.start_timing("test.txt")
        time.sleep(0.1)
        self.stats.stop_timing("test.txt")
        time2 = self.stats.get_editing_time("test.txt")
        
        self.assertGreater(time2, time1)
    
    def test_reset_timing(self):
        """测试重置时长"""
        self.stats.start_timing("test.txt")
        time.sleep(0.1)
        self.stats.stop_timing("test.txt")
        
        self.stats.reset_timing("test.txt")
        elapsed = self.stats.get_editing_time("test.txt")
        
        self.assertEqual(elapsed, 0)
    
    def test_switch_files(self):
        """测试文件切换时自动停止旧文件计时"""
        # 开始编辑file1
        self.stats.start_timing("file1.txt")
        time.sleep(0.1)
        
        # 切换到file2（应该自动停止file1）
        self.stats.start_timing("file2.txt")
        time1 = self.stats.get_editing_time("file1.txt")
        
        time.sleep(0.1)
        time2 = self.stats.get_editing_time("file1.txt")
        
        # file1的时长不应再增加
        self.assertAlmostEqual(time1, time2, delta=0.01)
        
        # file2的时长应该在增加
        time3 = self.stats.get_editing_time("file2.txt")
        self.assertGreater(time3, 0)


class TestTimeFormatting(unittest.TestCase):
    """测试时长格式化"""
    
    def setUp(self):
        """准备测试环境"""
        self.stats = Statistics.StatisticsManager()
    
    def test_format_seconds(self):
        """测试格式化秒"""
        result = self.stats.format_time(45)
        self.assertEqual(result, "45秒")
    
    def test_format_minutes(self):
        """测试格式化分钟"""
        result = self.stats.format_time(150)  # 2分30秒
        self.assertEqual(result, "2分钟")
        
        result = self.stats.format_time(3540)  # 59分钟
        self.assertEqual(result, "59分钟")
    
    def test_format_hours(self):
        """测试格式化小时"""
        result = self.stats.format_time(7200)  # 2小时
        self.assertEqual(result, "2小时")
        
        result = self.stats.format_time(7800)  # 2小时10分
        self.assertEqual(result, "2小时10分钟")
    
    def test_format_days(self):
        """测试格式化天"""
        result = self.stats.format_time(86400)  # 1天
        self.assertEqual(result, "1天")
        
        result = self.stats.format_time(93600)  # 1天2小时
        self.assertEqual(result, "1天2小时")
    
    def test_format_zero(self):
        """测试格式化零"""
        result = self.stats.format_time(0)
        self.assertEqual(result, "0秒")
        
        result = self.stats.format_time(-10)
        self.assertEqual(result, "0秒")


class TestTimeDecorator(unittest.TestCase):
    """测试时间装饰器（装饰器模式）"""
    
    def setUp(self):
        """准备测试环境"""
        self.stats = Statistics.StatisticsManager()
        self.decorator = Statistics.TimeDecorator(self.stats)
        
        # 模拟一些编辑时长
        self.stats._total_editing_time["file1.txt"] = 45
        self.stats._total_editing_time["file2.txt"] = 7800
    
    def test_decorate_simple(self):
        """测试简单装饰"""
        result = self.decorator.decorate("file1.txt")
        self.assertEqual(result, "file1.txt (45秒)")
    
    def test_decorate_with_status(self):
        """测试带状态的装饰"""
        # 活动且已修改
        result = self.decorator.decorate_with_status(
            "file1.txt", is_active=True, is_modified=True
        )
        self.assertEqual(result, "* file1.txt [modified] (45秒)")
        
        # 非活动且未修改
        result = self.decorator.decorate_with_status(
            "file2.txt", is_active=False, is_modified=False
        )
        self.assertEqual(result, "  file2.txt (2小时10分钟)")
    
    def test_decorate_different_formats(self):
        """测试不同时长格式的装饰"""
        self.stats._total_editing_time["short.txt"] = 30
        self.stats._total_editing_time["medium.txt"] = 1800
        self.stats._total_editing_time["long.txt"] = 90000
        
        result1 = self.decorator.decorate("short.txt")
        self.assertIn("30秒", result1)
        
        result2 = self.decorator.decorate("medium.txt")
        self.assertIn("30分钟", result2)
        
        result3 = self.decorator.decorate("long.txt")
        self.assertIn("1天", result3)


class TestGetFormattedTime(unittest.TestCase):
    """测试获取格式化时间"""
    
    def setUp(self):
        """准备测试环境"""
        self.stats = Statistics.StatisticsManager()
    
    def test_get_formatted_time_active_file(self):
        """测试获取正在编辑的文件的格式化时间"""
        self.stats.start_timing("test.txt")
        time.sleep(0.1)
        
        result = self.stats.get_formatted_time("test.txt")
        
        # 应该返回格式化的字符串
        self.assertIsInstance(result, str)
        self.assertIn("秒", result)
    
    def test_get_formatted_time_stopped_file(self):
        """测试获取已停止的文件的格式化时间"""
        self.stats.start_timing("test.txt")
        time.sleep(0.1)
        self.stats.stop_timing("test.txt")
        
        result = self.stats.get_formatted_time("test.txt")
        
        self.assertIsInstance(result, str)
        self.assertIn("秒", result)
    
    def test_get_formatted_time_nonexistent_file(self):
        """测试获取不存在文件的格式化时间"""
        result = self.stats.get_formatted_time("nonexistent.txt")
        
        self.assertEqual(result, "0秒")


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStatisticsManager))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTimeFormatting))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTimeDecorator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGetFormattedTime))
    
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

