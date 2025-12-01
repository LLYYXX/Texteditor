"""
Lab2新增: 拼写检查模块
使用适配器模式(Adapter Pattern)集成第三方拼写检查库
"""
import WorkSpace


class SpellCheckInterface:
    """拼写检查接口(抽象类)"""
    def check_text(self, text):
        raise NotImplementedError


class PySpellCheckerAdapter(SpellCheckInterface):
    """PySpellChecker适配器"""
    def __init__(self):
        try:
            from spellchecker import SpellChecker
            self.spell_checker = SpellChecker()
        except ImportError:
            self.spell_checker = None
            print("[Warning] pyspellchecker库未安装，拼写检查功能不可用")
            print("请运行: pip install pyspellchecker")
    
    def check_text(self, text):
        if not self.spell_checker:
            return []
        words = text.split()
        errors = []
        position = 0
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word and clean_word not in self.spell_checker:
                suggestions = self.spell_checker.candidates(clean_word)
                errors.append({
                    'word': clean_word,
                    'original': word,
                    'suggestions': list(suggestions) if suggestions else [],
                    'position': position
                })
            position += len(word) + 1
        return errors


class MockSpellChecker(SpellCheckInterface):
    """Mock拼写检查器"""
    def __init__(self):
        self.known_errors = {
            'recieve': ['receive'],
            'occured': ['occurred'],
            'seperate': ['separate'],
            'Itallian': ['Italian'],
            'Rowlling': ['Rowling'],
        }
    
    def check_text(self, text):
        words = text.split()
        errors = []
        position = 0
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in self.known_errors:
                errors.append({
                    'word': clean_word,
                    'original': word,
                    'suggestions': self.known_errors[clean_word],
                    'position': position
                })
            position += len(word) + 1
        return errors


class SpellCheckService:
    """拼写检查服务"""
    def __init__(self, spell_checker=None):
        if spell_checker:
            self.spell_checker = spell_checker
        else:
            self.spell_checker = PySpellCheckerAdapter()
            if not self.spell_checker.spell_checker:
                print("[Info] 使用Mock拼写检查器")
                self.spell_checker = MockSpellChecker()
    
    def check_text_file(self, file_obj):
        """检查文本文件的拼写"""
        if not hasattr(file_obj, 'content'):
            print("文件对象无效")
            return
        print("拼写检查结果:")
        has_errors = False
        for line_num, line in enumerate(file_obj.content, 1):
            if line.strip().startswith('# log'):
                continue
            errors = self.spell_checker.check_text(line)
            for error in errors:
                has_errors = True
                word = error['word']
                suggestions = error['suggestions']
                col = line.find(word) + 1 if word in line else 1
                if suggestions:
                    suggestions_str = ", ".join(suggestions[:3])
                    print(f'第{line_num}行，第{col}列: "{word}" -> 建议: {suggestions_str}')
                else:
                    print(f'第{line_num}行，第{col}列: "{word}" -> 无建议')
        if not has_errors:
            print("未发现拼写错误")
    
    def check_xml_file(self, file_obj):
        """检查XML文件的拼写"""
        if not hasattr(file_obj, 'root'):
            print("无效的XML文件对象")
            return
        print("拼写检查结果:")
        has_errors = False
        errors_found = []
        self._check_xml_element(file_obj.root, errors_found)
        for error in errors_found:
            has_errors = True
            element_id = error['element_id']
            word = error['word']
            suggestions = error['suggestions']
            if suggestions:
                suggestions_str = ", ".join(suggestions[:3])
                print(f'元素 {element_id}: "{word}" -> 建议: {suggestions_str}')
            else:
                print(f'元素 {element_id}: "{word}" -> 无建议')
        if not has_errors:
            print("未发现拼写错误")
    
    def _check_xml_element(self, element, errors_found):
        """递归检查XML元素的文本内容"""
        if element.text and element.text.strip():
            errors = self.spell_checker.check_text(element.text)
            for error in errors:
                errors_found.append({
                    'element_id': element.get_id(),
                    'word': error['word'],
                    'suggestions': error['suggestions']
                })
        for child in element.children:
            self._check_xml_element(child, errors_found)


class SpellCheckCommand:
    """spell-check命令"""
    def __init__(self, spell_check_service=None):
        self.spell_check_service = spell_check_service or SpellCheckService()
    
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
            print("参数错误，应为：spell-check [file]")
            return False
        file = WorkSpace.WorkSpace.current_workFile_list.get(file_path)
        if not file:
            print(f"文件未打开: {file_path}")
            return False
        if hasattr(file, 'file_type'):
            if file.file_type == 'xml':
                self.spell_check_service.check_xml_file(file)
            else:
                self.spell_check_service.check_text_file(file)
        else:
            self.spell_check_service.check_text_file(file)
        return False
    
    def can_undo(self):
        return False


