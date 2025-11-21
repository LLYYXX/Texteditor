# 文本编辑器 (Text Editor)

基于命令行的文本编辑器，支持多文件管理、撤销重做、日志记录等功能。

## 项目简介

本项目是一个基于字符命令界面的文本编辑器，采用面向对象设计，运用多种设计模式实现模块化的架构。

本项目为复旦大学**EIE50009 高级软件开发技术**课程2025学年第22组的课程实验项目

### 核心功能

- **多文件管理**: 支持同时打开和编辑多个文本文件
- **文本编辑**: 追加、插入、删除、替换等基本编辑操作
- **撤销重做**: 完整的Undo/Redo功能支持
- **工作区管理**: 工作区状态持久化，支持会话恢复
- **日志记录**: 可选的命令执行日志功能

### 设计模式

- **命令模式 (Command)**: 实现可撤销的编辑操作
- **备忘录模式 (Memento)**: 工作区状态持久化
- **观察者模式 (Observer)**: 日志事件通知（待实现）

## 快速开始

### 环境要求

- Python 3.8+
- UTF-8编码支持

### 运行程序

```bash
python Run.py
```

### 基本命令

#### 文件操作
```bash
> load test.txt          # 加载文件
> init new.txt           # 创建新文件
> save                   # 保存当前文件
> close                  # 关闭当前文件
> edit test.txt          # 切换活动文件
> editor-list            # 显示文件列表
```

#### 文本编辑
```bash
> append "Hello World"           # 追加一行
> insert 1:7 "Beautiful "        # 在指定位置插入
> delete 1:7 10                  # 删除指定长度字符
> replace 1:1 5 "Hi"            # 替换指定长度字符
> show                           # 显示全文
> show 1:5                       # 显示指定行范围
```

#### 撤销重做
```bash
> undo                   # 撤销上一次操作
> redo                   # 重做上一次撤销
```

#### 其他
```bash
> dir-tree               # 显示目录树
> exit                   # 退出程序
```

## 项目结构

```
.
├── Run.py                    # 程序入口，命令工厂
├── WorkSpace.py              # 工作区管理，工作区命令
├── File.py                   # 文件类定义
├── EditorActions.py          # 文本编辑命令实现
├── CommonUtils.py            # 通用工具函数
├── Memento.py                # 状态持久化
│
├── tests/                    # 测试目录
│   └── test_editor_actions.py
│
├── docs/                     # 文档目录
│   ├── 测试说明.md
│   ├── 设计模式_lab1.md
│   └── 设计模式Lab说明.md
│
└── .github/workflows/        # CI/CD配置
    └── test.yml
```

## 开发

### 运行测试

```bash
# 运行所有测试
python -m unittest discover -s tests

# 详细输出
python -m unittest discover -s tests -v

# 运行特定测试文件
python -m unittest tests.test_editor_actions
```

## 持续集成

项目配置了GitHub Actions自动化测试：
- ✅ 自动运行单元测试
- ✅ 支持Python 3.8-3.11多版本
- ✅ Push和PR时自动触发

详见：[测试说明.md](docs/测试说明.md)


## 设计文档

详细的整体功能需求和设计说明请参考：
- [设计模式Lab说明](docs/设计模式Lab说明.md)
- [Lab1设计模式说明](docs/设计模式_lab1.md)
