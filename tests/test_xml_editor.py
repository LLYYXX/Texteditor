"""
Lab2新增: XML编辑器单元测试
测试XML解析、编辑命令、组合模式等功能
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import File
import WorkSpace
import XmlEditor


class TestXmlElement(unittest.TestCase):
    """测试XmlElement类（组合模式）"""
    
    def setUp(self):
        """准备测试数据"""
        self.root = XmlEditor.XmlElement('root', {'id': 'root'})
    
    def test_create_element(self):
        """测试创建元素"""
        element = XmlEditor.XmlElement('book', {'id': 'book1', 'category': 'COOKING'}, 'text')
        self.assertEqual(element.tag, 'book')
        self.assertEqual(element.get_id(), 'book1')
        self.assertEqual(element.text, 'text')
        self.assertEqual(len(element.children), 0)
    
    def test_add_child(self):
        """测试添加子元素"""
        child = XmlEditor.XmlElement('book', {'id': 'book1'})
        self.root.add_child(child)
        self.assertEqual(len(self.root.children), 1)
        self.assertEqual(child.parent, self.root)
    
    def test_remove_child(self):
        """测试移除子元素"""
        child = XmlEditor.XmlElement('book', {'id': 'book1'})
        self.root.add_child(child)
        self.root.remove_child(child)
        self.assertEqual(len(self.root.children), 0)
        self.assertIsNone(child.parent)
    
    def test_insert_before(self):
        """测试在指定元素前插入"""
        child1 = XmlEditor.XmlElement('book', {'id': 'book1'})
        child2 = XmlEditor.XmlElement('book', {'id': 'book2'})
        child3 = XmlEditor.XmlElement('book', {'id': 'book3'})
        
        self.root.add_child(child1)
        self.root.add_child(child3)
        self.root.insert_before(child2, child3)
        
        self.assertEqual(len(self.root.children), 3)
        self.assertEqual(self.root.children[0], child1)
        self.assertEqual(self.root.children[1], child2)
        self.assertEqual(self.root.children[2], child3)
    
    def test_to_xml_lines(self):
        """测试XML序列化"""
        child = XmlEditor.XmlElement('book', {'id': 'book1'}, 'Book Title')
        self.root.add_child(child)
        lines = self.root.to_xml_lines()
        
        # 验证包含关键标签（忽略缩进）
        xml_str = '\n'.join(lines)
        self.assertIn('<root id="root">', xml_str)
        self.assertIn('<book id="book1">Book Title</book>', xml_str)
        self.assertIn('</root>', xml_str)


class TestXmlParsing(unittest.TestCase):
    """测试XML解析功能"""
    
    def test_parse_simple_xml(self):
        """测试解析简单XML"""
        xml_string = """
        <?xml version="1.0" encoding="UTF-8"?>
        <root id="root">
            <book id="book1">Title</book>
        </root>
        """
        root, element_map, declaration, has_log = XmlEditor.parse_xml(xml_string)
        
        self.assertIsNotNone(root)
        self.assertEqual(root.tag, 'root')
        self.assertEqual(root.get_id(), 'root')
        self.assertIn('book1', element_map)
        self.assertEqual(len(root.children), 1)
    
    def test_parse_xml_with_log(self):
        """测试解析带日志注释的XML"""
        xml_string = """
        # log
        <?xml version="1.0" encoding="UTF-8"?>
        <root id="root"></root>
        """
        root, element_map, declaration, has_log = XmlEditor.parse_xml(xml_string)
        
        self.assertTrue(has_log)
    
    def test_parse_nested_xml(self):
        """测试解析嵌套XML"""
        xml_string = """
        <bookstore id="root">
            <book id="book1">
                <title id="title1">Harry Potter</title>
                <author id="author1">J.K. Rowling</author>
            </book>
        </bookstore>
        """
        root, element_map, declaration, has_log = XmlEditor.parse_xml(xml_string)
        
        self.assertEqual(len(element_map), 4)  # root, book1, title1, author1
        book = element_map['book1']
        self.assertEqual(len(book.children), 2)


class TestXmlCommands(unittest.TestCase):
    """测试XML编辑命令"""
    
    def setUp(self):
        """准备测试环境"""
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
        
        # 创建测试XML文件
        self.test_file = File.XmlFile("test.xml")
        WorkSpace.WorkSpace.current_workFile_path = "test.xml"
        WorkSpace.WorkSpace.current_workFile_list["test.xml"] = self.test_file
        File.FileList.all_files["test.xml"] = self.test_file
        File.FileList.all_files_path.add("test.xml")
    
    def test_append_child_command(self):
        """测试append-child命令"""
        cmd = XmlEditor.AppendChildCommand()
        result = cmd.execute('append-child book book1 root "Book Title"')
        
        self.assertTrue(result)
        self.assertIn('book1', self.test_file.element_map)
        book = self.test_file.element_map['book1']
        self.assertEqual(book.tag, 'book')
        self.assertEqual(book.text, 'Book Title')
        self.assertEqual(book.parent, self.test_file.root)
    
    def test_insert_before_command(self):
        """测试insert-before命令"""
        # 先添加两个元素
        cmd1 = XmlEditor.AppendChildCommand()
        cmd1.execute('append-child book book1 root ""')
        cmd1.execute('append-child book book3 root ""')
        
        # 在book3前插入book2
        cmd2 = XmlEditor.InsertBeforeCommand()
        result = cmd2.execute('insert-before book book2 book3 ""')
        
        self.assertTrue(result)
        self.assertEqual(len(self.test_file.root.children), 3)
        self.assertEqual(self.test_file.root.children[1].get_id(), 'book2')
    
    def test_edit_id_command(self):
        """测试edit-id命令"""
        # 先添加元素
        cmd1 = XmlEditor.AppendChildCommand()
        cmd1.execute('append-child book book1 root ""')
        
        # 修改ID
        cmd2 = XmlEditor.EditIdCommand()
        result = cmd2.execute('edit-id book1 book001')
        
        self.assertTrue(result)
        self.assertNotIn('book1', self.test_file.element_map)
        self.assertIn('book001', self.test_file.element_map)
    
    def test_edit_text_command(self):
        """测试edit-text命令"""
        # 先添加元素
        cmd1 = XmlEditor.AppendChildCommand()
        cmd1.execute('append-child book book1 root "Old Title"')
        
        # 修改文本
        cmd2 = XmlEditor.EditTextCommand()
        result = cmd2.execute('edit-text book1 "New Title"')
        
        self.assertTrue(result)
        book = self.test_file.element_map['book1']
        self.assertEqual(book.text, 'New Title')
    
    def test_delete_command(self):
        """测试delete命令"""
        # 先添加元素
        cmd1 = XmlEditor.AppendChildCommand()
        cmd1.execute('append-child book book1 root ""')
        cmd1.execute('append-child title title1 book1 "Title"')
        
        # 删除元素
        cmd2 = XmlEditor.DeleteElementCommand()
        result = cmd2.execute('delete book1')
        
        self.assertTrue(result)
        self.assertNotIn('book1', self.test_file.element_map)
        self.assertNotIn('title1', self.test_file.element_map)  # 子元素也应被删除
    
    def test_delete_root_should_fail(self):
        """测试删除根元素应该失败"""
        cmd = XmlEditor.DeleteElementCommand()
        result = cmd.execute('delete root')
        
        self.assertFalse(result)
        self.assertIn('root', self.test_file.element_map)
    
    def test_undo_redo_append_child(self):
        """测试undo/redo功能"""
        cmd = XmlEditor.AppendChildCommand()
        cmd.execute('append-child book book1 root ""')
        
        # 测试undo
        cmd.undo()
        self.assertNotIn('book1', self.test_file.element_map)
        
        # 测试redo
        cmd.redo()
        self.assertIn('book1', self.test_file.element_map)


class TestXmlTreeCommand(unittest.TestCase):
    """测试xml-tree命令"""
    
    def setUp(self):
        """准备测试环境"""
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        
        self.test_file = File.XmlFile("test.xml")
        WorkSpace.WorkSpace.current_workFile_path = "test.xml"
        WorkSpace.WorkSpace.current_workFile_list["test.xml"] = self.test_file
        
        # 构建测试树
        book = XmlEditor.XmlElement('book', {'id': 'book1', 'category': 'COOKING'})
        title = XmlEditor.XmlElement('title', {'id': 'title1'}, 'Book Title')
        book.add_child(title)
        self.test_file.root.add_child(book)
        self.test_file.element_map['book1'] = book
        self.test_file.element_map['title1'] = title
    
    def test_xml_tree_command(self):
        """测试xml-tree命令执行"""
        cmd = XmlEditor.XmlTreeCommand()
        result = cmd.execute('xml-tree')
        
        # xml-tree是查询命令，不应该进入历史栈
        self.assertFalse(result)
        self.assertFalse(cmd.can_undo())


class TestModifiedStateDecorator(unittest.TestCase):
    """测试装饰器模式 - 文件状态自动标记"""
    
    def setUp(self):
        """准备测试环境"""
        WorkSpace.WorkSpace.current_workFile_path = ""
        WorkSpace.WorkSpace.current_workFile_list = {}
        File.FileList.all_files_path.clear()
        File.FileList.all_files.clear()
        
        self.test_file = File.XmlFile("test.xml")
        self.test_file.state = "normal"
        WorkSpace.WorkSpace.current_workFile_path = "test.xml"
        WorkSpace.WorkSpace.current_workFile_list["test.xml"] = self.test_file
        File.FileList.all_files["test.xml"] = self.test_file
        File.FileList.all_files_path.add("test.xml")
    
    def test_decorator_marks_file_as_modified(self):
        """测试装饰器自动标记文件为已修改"""
        # 创建命令并用装饰器包装
        cmd = XmlEditor.AppendChildCommand()
        decorated_cmd = XmlEditor.ModifiedStateDecorator(cmd)
        
        # 执行命令
        result = decorated_cmd.execute('append-child book book1 root ""')
        
        # 验证文件状态被自动标记为modified
        self.assertTrue(result)
        self.assertEqual(self.test_file.state, "modified")
    
    def test_decorator_forwards_undo_redo(self):
        """测试装饰器正确转发undo/redo调用"""
        cmd = XmlEditor.AppendChildCommand()
        decorated_cmd = XmlEditor.ModifiedStateDecorator(cmd)
        
        decorated_cmd.execute('append-child book book1 root ""')
        
        # 测试undo
        decorated_cmd.undo()
        self.assertNotIn('book1', self.test_file.element_map)
        
        # 测试redo
        decorated_cmd.redo()
        self.assertIn('book1', self.test_file.element_map)
    
    def test_decorator_can_undo(self):
        """测试装饰器正确转发can_undo"""
        cmd = XmlEditor.AppendChildCommand()
        decorated_cmd = XmlEditor.ModifiedStateDecorator(cmd)
        
        self.assertTrue(decorated_cmd.can_undo())


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXmlElement))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXmlParsing))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXmlCommands))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXmlTreeCommand))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestModifiedStateDecorator))
    
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

