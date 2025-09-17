import sys
import pandas as pd
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QProgressBar, 
                            QTextEdit, QFileDialog, QMessageBox, QFrame,
                            QGridLayout, QGroupBox, QScrollArea, QDialog,
                            QLineEdit, QListWidget, QListWidgetItem, QComboBox,
                            QTextEdit, QToolTip)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QSyntaxHighlighter, QTextCharFormat
import re
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

VERSION = "label-tool-v1"

class SentimentHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        self.load_dictionary()
        
    def load_dictionary(self):
        try:
            if os.path.exists('sentiment_dict.json'):
                with open('sentiment_dict.json', 'r', encoding='utf-8') as f:
                    self.dictionary = json.load(f)
            else:
                self.dictionary = {
                    'negative': [
                        "差", "烂", "糟糕", "失望", "不满", "投诉", "问题", "错误", "失败", "不好",
                        "讨厌", "厌恶", "反感", "愤怒", "生气", "恼火", "烦躁", "焦虑", "担心", "害怕",
                        "恐惧", "紧张", "痛苦", "悲伤", "难过", "伤心", "绝望", "无助", "孤独", "寂寞",
                        "后悔", "遗憾", "懊悔", "自责", "内疚", "羞愧", "尴尬", "难堪", "丢脸", "抱怨",
                        "埋怨", "指责", "批评", "否定", "反对", "拒绝", "排斥", "抵制", "抗议", "可恶",
                        "可恨", "可气", "可恼", "可悲", "可叹", "可耻", "可鄙", "可憎", "可厌", "可恨",
                        "可气", "可恼", "可悲", "可叹", "可耻",
                        "痛苦", "悲伤", "难过", "伤心", "绝望", "无助", "孤独", "寂寞", "后悔", "遗憾",
                        "懊悔", "自责", "内疚", "羞愧", "尴尬", "难堪", "丢脸", "抱怨", "埋怨", "指责",
                        "批评", "否定", "反对", "拒绝", "排斥", "抵制", "抗议", "可恶", "可恨", "可气",
                        "可恼", "可悲", "可叹", "可耻", "可鄙", "可憎", "可厌", "可恨", "可气", "可恼",
                        "非常", "极其", "特别", "十分", "太", "很", "相当", "比较", "有点", "稍微",
                        "完全", "彻底", "根本", "简直", "实在",
                        "竟然", "居然", "简直", "真是", "确实", 
                    ],
                    'positive': [
                        # 正面情绪词
                        "好", "优秀", "满意", "赞", "推荐", "喜欢", "支持", "感谢", "成功", "不错",
                        "开心", "快乐", "高兴", "喜悦", "兴奋", "激动", "热情", "积极", "乐观", "自信",
                        "自豪", "骄傲", "满足", "幸福", "温暖", "温馨", "舒适", "安逸", "轻松", "愉快",
                        "期待", "盼望", "希望", "憧憬", "向往", "渴望", "追求", "努力", "奋斗", "拼搏",
                        "进步", "提升", "改善", "优化", "创新", "突破", "发展", "成长", "成熟", "完善",
                        "可爱", "可亲", "可敬", "可佩", "可赞", "可嘉", "可贺", "可喜", "可贺", "可嘉",
                        "可爱", "可亲", "可敬", "可佩", "可赞", "可嘉", "可贺", "可喜", "可贺", "可嘉",
                        "可爱", "可亲", "可敬", "可佩", "可赞", "可嘉", "可贺", "可喜", "可贺", "可嘉",
                        # 新增正面情感词
                        "开心", "快乐", "高兴", "喜悦", "兴奋", "激动", "热情", "积极", "乐观", "自信",
                        "自豪", "骄傲", "满足", "幸福", "温暖", "温馨", "舒适", "安逸", "轻松", "愉快",
                        "期待", "盼望", "希望", "憧憬", "向往", "渴望", "追求", "努力", "奋斗", "拼搏",
                        "进步", "提升", "改善", "优化", "创新", "突破", "发展", "成长", "成熟", "完善",
                        # 正面程度词
                        "非常", "极其", "特别", "十分", "太", "很", "相当", "比较", "有点", "稍微",
                        "完全", "彻底", "根本", "简直", "实在", "确实", "真的", "确实", "确实", "确实",
                        # 正面语气词
                        "确实", "真的", "确实", "确实", "确实", "确实", "确实", "确实", "确实", "确实",
                        "确实", "真的", "确实", "确实", "确实", "确实", "确实", "确实", "确实", "确实"
                    ],
                    'neutral': [
                        # 中性情绪词
                        "一般", "普通", "还行", "可以", "正常", "标准", "常规", "基本", "通常", "常见",
                        "了解", "知道", "明白", "理解", "认识", "熟悉", "掌握", "运用", "使用", "应用",
                        "思考", "考虑", "分析", "研究", "探讨", "讨论", "交流", "沟通", "表达", "说明",
                        "观察", "注意", "关注", "重视", "重视", "重视", "重视", "重视", "重视", "重视",
                        "可能", "也许", "大概", "似乎", "好像", "仿佛", "似乎", "好像", "仿佛", "似乎",
                        "可能", "也许", "大概", "似乎", "好像", "仿佛", "似乎", "好像", "仿佛", "似乎",
                        "可能", "也许", "大概", "似乎", "好像", "仿佛", "似乎", "好像", "仿佛", "似乎",
                        # 新增中性情感词
                        "一般", "普通", "还行", "可以", "正常", "标准", "常规", "基本", "通常", "常见",
                        "了解", "知道", "明白", "理解", "认识", "熟悉", "掌握", "运用", "使用", "应用",
                        "思考", "考虑", "分析", "研究", "探讨", "讨论", "交流", "沟通", "表达", "说明",
                        "观察", "注意", "关注", "重视", "重视", "重视", "重视", "重视", "重视", "重视",
                        # 中性程度词
                        "一般", "普通", "还行", "可以", "正常", "标准", "常规", "基本", "通常", "常见",
                        "可能", "也许", "大概", "似乎", "好像", "仿佛", "似乎", "好像", "仿佛", "似乎",
                        # 中性语气词
                        "可能", "也许", "大概", "似乎", "好像", "仿佛", "似乎", "好像", "仿佛", "似乎",
                        "可能", "也许", "大概", "似乎", "好像", "仿佛", "似乎", "好像", "仿佛", "似乎"
                    ]
                }
                # 去重
                for key in self.dictionary:
                    self.dictionary[key] = list(set(self.dictionary[key]))
                self.save_dictionary()
        except Exception as e:
            print(f"加载情感词典失败: {str(e)}")
            self.dictionary = {'negative': [], 'positive': [], 'neutral': []}
            
    def save_dictionary(self):
        try:
            with open('sentiment_dict.json', 'w', encoding='utf-8') as f:
                json.dump(self.dictionary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存情感词典失败: {str(e)}")
            
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        
        # 负面情感词
        negative_format = QTextCharFormat()
        negative_format.setBackground(QColor("#ffebee"))
        negative_format.setForeground(QColor("#b71c1c"))
        negative_format.setFontWeight(QFont.Bold)  # 加粗显示
        for word in sorted(self.dictionary['negative'], key=len, reverse=True):  # 按长度排序，优先匹配长词
            # 使用更精确的中文词语匹配模式
            pattern = re.compile(f'(?<![a-zA-Z0-9]){re.escape(word)}(?![a-zA-Z0-9])')
            self.highlighting_rules.append((pattern, negative_format))
            
        # 正面情感词
        positive_format = QTextCharFormat()
        positive_format.setBackground(QColor("#e8f5e9"))
        positive_format.setForeground(QColor("#1b5e20"))
        positive_format.setFontWeight(QFont.Bold)  # 加粗显示
        for word in sorted(self.dictionary['positive'], key=len, reverse=True):  # 按长度排序，优先匹配长词
            # 使用更精确的中文词语匹配模式
            pattern = re.compile(f'(?<![a-zA-Z0-9]){re.escape(word)}(?![a-zA-Z0-9])')
            self.highlighting_rules.append((pattern, positive_format))
            
        # 中性情感词
        neutral_format = QTextCharFormat()
        neutral_format.setBackground(QColor("#f5f5f5"))
        neutral_format.setForeground(QColor("#424242"))
        neutral_format.setFontWeight(QFont.Bold)  # 加粗显示
        for word in sorted(self.dictionary['neutral'], key=len, reverse=True):  # 按长度排序，优先匹配长词
            # 使用更精确的中文词语匹配模式
            pattern = re.compile(f'(?<![a-zA-Z0-9]){re.escape(word)}(?![a-zA-Z0-9])')
            self.highlighting_rules.append((pattern, neutral_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
                
    def rehighlight(self):
        """重新应用所有高亮规则"""
        super().rehighlight()

class DictionaryEditor(QDialog):
    def __init__(self, highlighter, parent=None):
        super().__init__(parent)
        self.highlighter = highlighter
        self.default_dictionary = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('情感词典编辑')
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 词典类型选择
        type_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(['负面词', '正面词', '中性词'])
        self.type_combo.currentIndexChanged.connect(self.update_word_list)
        type_layout.addWidget(QLabel('词典类型:'))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 单词列表
        self.word_list = QListWidget()
        layout.addWidget(self.word_list)
        
        # 添加/删除单词
        edit_layout = QVBoxLayout()
        self.word_input = QTextEdit()
        self.word_input.setPlaceholderText("请输入情感词，每行一个词")
        self.word_input.setMaximumHeight(100)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton('添加')
        self.delete_button = QPushButton('删除')
        self.clear_button = QPushButton('清空')
        self.reset_button = QPushButton('恢复默认')
        
        self.add_button.clicked.connect(self.add_words)
        self.delete_button.clicked.connect(self.delete_word)
        self.clear_button.clicked.connect(self.clear_words)
        self.reset_button.clicked.connect(self.reset_dictionary)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.reset_button)
        
        edit_layout.addWidget(self.word_input)
        edit_layout.addLayout(button_layout)
        layout.addLayout(edit_layout)
        
        # 提示信息
        self.tip_label = QLabel("提示：每行输入一个词，点击添加按钮批量添加")
        self.tip_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.tip_label)
        
        # 确定按钮
        self.ok_button = QPushButton('确定')
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        
        self.update_word_list()
        
    def update_word_list(self):
        self.word_list.clear()
        type_map = {0: 'negative', 1: 'positive', 2: 'neutral'}
        current_type = type_map[self.type_combo.currentIndex()]
        for word in sorted(self.highlighter.dictionary[current_type]):
            self.word_list.addItem(word)
            
    def add_words(self):
        text = self.word_input.toPlainText().strip()
        if text:
            words = [word.strip() for word in text.split('\n') if word.strip()]
            type_map = {0: 'negative', 1: 'positive', 2: 'neutral'}
            current_type = type_map[self.type_combo.currentIndex()]
            
            # 去重
            existing_words = set(self.highlighter.dictionary[current_type])
            new_words = [word for word in words if word not in existing_words]
            
            if new_words:
                self.highlighter.dictionary[current_type].extend(new_words)
                self.word_input.clear()
                self.highlighter.save_dictionary()
                self.highlighter.update_highlighting_rules()
                self.highlighter.rehighlight()  # 重新应用高亮规则
                self.update_word_list()
                QMessageBox.information(self, '成功', f'成功添加 {len(new_words)} 个新词')
            else:
                QMessageBox.warning(self, '警告', '所有词都已存在')
                
    def delete_word(self):
        current_item = self.word_list.currentItem()
        if current_item:
            word = current_item.text()
            type_map = {0: 'negative', 1: 'positive', 2: 'neutral'}
            current_type = type_map[self.type_combo.currentIndex()]
            self.highlighter.dictionary[current_type].remove(word)
            self.word_list.takeItem(self.word_list.row(current_item))
            self.highlighter.save_dictionary()
            self.highlighter.update_highlighting_rules()
            self.highlighter.rehighlight()  # 重新应用高亮规则
            
    def clear_words(self):
        type_map = {0: 'negative', 1: 'positive', 2: 'neutral'}
        current_type = type_map[self.type_combo.currentIndex()]
        self.highlighter.dictionary[current_type] = []
        self.word_list.clear()
        self.highlighter.save_dictionary()
        self.highlighter.update_highlighting_rules()
        self.highlighter.rehighlight()  # 重新应用高亮规则
        
    def reset_dictionary(self):
        reply = QMessageBox.question(self, '确认', '确定要恢复默认词典吗？这将清除所有自定义修改。',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.highlighter.load_dictionary()
            self.update_word_list()
            self.highlighter.save_dictionary()
            self.highlighter.update_highlighting_rules()
            self.highlighter.rehighlight()  # 重新应用高亮规则
            QMessageBox.information(self, '成功', '已恢复默认词典')

class SentimentAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.current_index = 0
        self.output_file = None
        self.last_file = None
        self.is_dark_mode = False
        self.load_last_session()
        self.initUI()
        
    def load_last_session(self):
        try:
            if os.path.exists('last_session.json'):
                with open('last_session.json', 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    self.last_file = session_data.get('last_file')
                    self.is_dark_mode = session_data.get('is_dark_mode', False)
                    self.has_shown_manual = session_data.get('has_shown_manual', False)
            else:
                self.has_shown_manual = False
        except Exception as e:
            print(f"加载上次会话失败: {str(e)}")
            self.has_shown_manual = False
        
    def save_last_session(self):
        try:
            session_data = {
                'last_file': self.output_file if self.output_file else self.last_file,
                'is_dark_mode': self.is_dark_mode,
                'has_shown_manual': True
            }
            with open('last_session.json', 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False)
        except Exception as e:
            print(f"保存会话失败: {str(e)}")
        
    def initUI(self):
        self.setWindowTitle(f'社交媒体情感标注工具 - {VERSION}')
        self.setMinimumSize(1400, 900)
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # 左侧面板 - 主要内容
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 创建顶部按钮区域
        top_buttons = QHBoxLayout()
        self.load_button = QPushButton('加载CSV文件')
        self.load_button.clicked.connect(self.load_csv)
        self.auto_load_button = QPushButton('加载上次文件')
        self.auto_load_button.clicked.connect(self.auto_load_last_file)
        self.theme_button = QPushButton('切换主题')
        self.theme_button.clicked.connect(self.toggle_theme)
        self.dict_edit_button = QPushButton('编辑词典')
        self.dict_edit_button.clicked.connect(self.edit_dictionary)
        self.view_output_button = QPushButton('查看标注文件')
        self.view_output_button.clicked.connect(self.show_output_location)
        self.manual_button = QPushButton('使用说明')
        self.manual_button.clicked.connect(self.show_manual)
        
        top_buttons.addWidget(self.load_button)
        top_buttons.addWidget(self.auto_load_button)
        top_buttons.addWidget(self.theme_button)
        top_buttons.addWidget(self.dict_edit_button)
        top_buttons.addWidget(self.view_output_button)
        top_buttons.addWidget(self.manual_button)
        left_layout.addLayout(top_buttons)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        # 创建内容显示区域
        content_group = QGroupBox("内容")
        content_layout = QVBoxLayout(content_group)
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setFont(QFont('Microsoft YaHei', 12))
        self.content_display.setMinimumHeight(400)
        self.highlighter = SentimentHighlighter(self.content_display.document())
        content_layout.addWidget(self.content_display)
        left_layout.addWidget(content_group)
        
        # 创建元数据显示区域
        meta_group = QGroupBox("元数据")
        meta_layout = QVBoxLayout(meta_group)
        self.meta_label = QLabel()
        self.meta_label.setFont(QFont('Microsoft YaHei', 10))
        meta_layout.addWidget(self.meta_label)
        left_layout.addWidget(meta_group)
        
        # 创建情感标注按钮
        sentiment_group = QGroupBox("情感标注")
        sentiment_layout = QHBoxLayout(sentiment_group)
        self.negative_btn = QPushButton('负面 (-1)')
        self.neutral_btn = QPushButton('中性 (0)')
        self.positive_btn = QPushButton('正面 (1)')
        
        # 设置按钮样式
        self.button_style = {
            'default': """
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #666;
                }
            """,
            'selected': """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """
        }
        
        for btn in [self.negative_btn, self.neutral_btn, self.positive_btn]:
            btn.setMinimumHeight(60)
            btn.setFont(QFont('Microsoft YaHei', 12))
            btn.setStyleSheet(self.button_style['default'])
            sentiment_layout.addWidget(btn)
            
        self.negative_btn.clicked.connect(lambda: self.annotate_sentiment(-1))
        self.neutral_btn.clicked.connect(lambda: self.annotate_sentiment(0))
        self.positive_btn.clicked.connect(lambda: self.annotate_sentiment(1))
        
        left_layout.addWidget(sentiment_group)
        
        # 创建导航按钮
        nav_group = QGroupBox("导航")
        nav_layout = QHBoxLayout(nav_group)
        
        # 添加跳转到指定序号的输入框和按钮
        self.goto_input = QLineEdit()
        self.goto_input.setPlaceholderText("输入序号(1-N)")
        self.goto_input.setMaximumWidth(150)
        self.goto_button = QPushButton('跳转到序号')
        self.goto_button.clicked.connect(self.goto_index)
        
        # 添加跳转到未标注的按钮
        self.goto_unlabeled_button = QPushButton('下一个未标注')
        self.goto_unlabeled_button.clicked.connect(self.goto_next_unlabeled)
        
        self.prev_btn = QPushButton('上一个')
        self.next_btn = QPushButton('下一个')
        
        self.prev_btn.clicked.connect(self.previous_item)
        self.next_btn.clicked.connect(self.next_item)
        
        nav_layout.addWidget(self.goto_input)
        nav_layout.addWidget(self.goto_button)
        nav_layout.addWidget(self.goto_unlabeled_button)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        left_layout.addWidget(nav_group)
        
        # 右侧面板 - 统计信息
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 统计信息组
        stats_group = QGroupBox("标注统计")
        stats_layout = QVBoxLayout(stats_group)
        
        # 创建图表
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        stats_layout.addWidget(self.canvas)
        
        # 统计标签
        self.total_label = QLabel("总数据量: 0")
        self.negative_label = QLabel("负面标注: 0")
        self.neutral_label = QLabel("中性标注: 0")
        self.positive_label = QLabel("正面标注: 0")
        self.unlabeled_label = QLabel("未标注: 0")
        
        for label in [self.total_label, self.negative_label, self.neutral_label, 
                     self.positive_label, self.unlabeled_label]:
            label.setFont(QFont('Microsoft YaHei', 10))
            stats_layout.addWidget(label)
            
        right_layout.addWidget(stats_group)
        
        # 情感词典组
        dict_group = QGroupBox("情感词典")
        dict_layout = QVBoxLayout(dict_group)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 添加词典标签
        self.negative_dict_label = QLabel("负面词: " + ", ".join(self.highlighter.dictionary['negative']))
        self.positive_dict_label = QLabel("正面词: " + ", ".join(self.highlighter.dictionary['positive']))
        self.neutral_dict_label = QLabel("中性词: " + ", ".join(self.highlighter.dictionary['neutral']))
        
        for label in [self.negative_dict_label, self.positive_dict_label, self.neutral_dict_label]:
            label.setFont(QFont('Microsoft YaHei', 10))
            label.setWordWrap(True)
            scroll_layout.addWidget(label)
            
        scroll.setWidget(scroll_content)
        dict_layout.addWidget(scroll)
        right_layout.addWidget(dict_group)
        
        # 添加左右面板到主布局
        layout.addWidget(left_panel, stretch=7)
        layout.addWidget(right_panel, stretch=3)
        
        # 设置样式
        self.update_theme()
        
        # 初始化按钮状态
        self.update_button_states()
        
        # 显示欢迎提示
        QTimer.singleShot(500, self.show_welcome_tip)
        
    def show_welcome_tip(self):
        if not self.has_shown_manual:
            self.show_manual()
        else:
            QMessageBox.information(self, '欢迎使用', 
                                  '欢迎使用社交媒体情感标注工具！\n\n'
                                  '1. 点击"加载CSV文件"开始标注\n'
                                  '2. 使用"编辑词典"管理情感词\n'
                                  '3. 点击情感按钮进行标注\n'
                                  '4. 使用"切换主题"改变界面风格\n\n'
                                  '标注结果会自动保存，下次打开可以继续标注。')
            
    def show_manual(self):
        try:
            with open('README.md', 'r', encoding='utf-8') as f:
                manual_text = f.read()
                
            dialog = QDialog(self)
            dialog.setWindowTitle('使用说明书')
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # 创建文本显示区域
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setMarkdown(manual_text)
            text_edit.setFont(QFont('Microsoft YaHei', 10))
            
            # 创建滚动区域
            scroll = QScrollArea()
            scroll.setWidget(text_edit)
            scroll.setWidgetResizable(True)
            
            layout.addWidget(scroll)
            
            # 添加关闭按钮
            close_button = QPushButton('关闭')
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'无法加载使用说明书：{str(e)}')
        
    def update_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a1a;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #444;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                    background-color: #2d2d2d;
                    color: #fff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    color: #fff;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #666;
                }
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #fff;
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 8px;
                }
                QProgressBar {
                    border: 1px solid #444;
                    border-radius: 4px;
                    text-align: center;
                    height: 20px;
                    background-color: #2d2d2d;
                    color: #fff;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                }
                QLabel {
                    padding: 5px;
                    color: #fff;
                }
                QScrollArea {
                    border: none;
                    background-color: #2d2d2d;
                }
                QListWidget {
                    background-color: #2d2d2d;
                    color: #fff;
                    border: 1px solid #444;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #fff;
                    border: 1px solid #444;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
                QTextEdit {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                }
                QProgressBar {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                }
                QLabel {
                    padding: 5px;
                }
                QScrollArea {
                    border: none;
                }
                QListWidget {
                    background-color: white;
                    border: 1px solid #ddd;
                }
                QLineEdit {
                    background-color: white;
                    border: 1px solid #ddd;
                    padding: 5px;
                }
            """)
        
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.update_theme()
        self.save_last_session()
        
    def edit_dictionary(self):
        dialog = DictionaryEditor(self.highlighter, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_dictionary_display()
            
    def update_dictionary_display(self):
        self.negative_dict_label.setText("负面词: " + ", ".join(self.highlighter.dictionary['negative']))
        self.positive_dict_label.setText("正面词: " + ", ".join(self.highlighter.dictionary['positive']))
        self.neutral_dict_label.setText("中性词: " + ", ".join(self.highlighter.dictionary['neutral']))
        
    def update_statistics(self):
        if self.df is not None:
            total = len(self.df)
            # 使用更安全的方式计算统计数据
            negative = len(self.df[self.df['sentiment'].astype(float) == -1])
            neutral = len(self.df[self.df['sentiment'].astype(float) == 0])
            positive = len(self.df[self.df['sentiment'].astype(float) == 1])
            unlabeled = len(self.df[pd.isna(self.df['sentiment'])])
            
            self.total_label.setText(f"总数据量: {total}")
            self.negative_label.setText(f"负面标注: {negative}")
            self.neutral_label.setText(f"中性标注: {neutral}")
            self.positive_label.setText(f"正面标注: {positive}")
            self.unlabeled_label.setText(f"未标注: {unlabeled}")
            
            # 更新图表
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            labels = ['负面', '中性', '正面', '未标注']
            sizes = [negative, neutral, positive, unlabeled]
            colors = ['#ffcdd2', '#e0e0e0', '#c8e6c9', '#f5f5f5']
            if sum(sizes) > 0:  # 只在有数据时绘制饼图
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
                ax.axis('equal')
            self.canvas.draw()
    
    def validate_dataframe(self, df):
        """验证数据框是否包含所需的列"""
        required_columns = ['content', 'nick_name', 'time', '转发数', '评价数', '点赞数']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"CSV文件缺少必需的列: {', '.join(missing_columns)}")
        
        return True
        
    def prepare_dataframe(self, df):
        """准备数据框，确保包含所有必需的列和正确的数据类型"""
        # 如果没有sentiment列，添加一个，并用None填充
        if 'sentiment' not in df.columns:
            df['sentiment'] = None
            
        # 确保数值列为数值类型，无效值填充为0
        numeric_columns = ['转发数', '评价数', '点赞数']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
        return df
        
    def auto_load_last_file(self):
        try:
            # 打开文件选择对话框，让用户选择标注文件
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                '选择标注文件',
                '',
                'CSV files (*_annotated.csv);;All files (*.*)'
            )
            
            if file_name:
                # 加载选择的文件
                df = pd.read_csv(file_name)
                
                # 验证和准备数据
                self.validate_dataframe(df)
                self.df = self.prepare_dataframe(df)
                self.output_file = file_name
                self.last_file = file_name.replace('_annotated.csv', '.csv')
                self.save_last_session()
                
                self.current_index = 0
                self.update_display()
                self.update_progress()
                self.update_statistics()
                QMessageBox.information(self, '成功', '成功加载标注文件！')
            else:
                QMessageBox.information(self, '提示', '未选择文件')
                
        except ValueError as ve:
            QMessageBox.critical(self, '错误', f'数据格式错误：{str(ve)}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载文件时出错：{str(e)}')
        
    def load_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '选择CSV文件', '', 'CSV files (*.csv)')
        if file_name:
            try:
                # 检查是否存在对应的标注结果文件
                output_file = file_name.replace('.csv', '_annotated.csv')
                if os.path.exists(output_file):
                    df = pd.read_csv(output_file)
                else:
                    df = pd.read_csv(file_name)
                
                # 验证和准备数据
                self.validate_dataframe(df)
                self.df = self.prepare_dataframe(df)
                self.output_file = output_file
                self.last_file = file_name
                self.save_last_session()
                
                self.current_index = 0
                self.update_display()
                self.update_progress()
                self.update_statistics()
                QMessageBox.information(self, '成功', 'CSV文件加载成功！')
            except ValueError as ve:
                QMessageBox.critical(self, '错误', f'数据格式错误：{str(ve)}')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'加载CSV文件时出错：{str(e)}')
    
    def update_display(self):
        if self.df is not None and self.current_index < len(self.df):
            row = self.df.iloc[self.current_index]
            
            # 显示内容
            self.content_display.clear()
            self.content_display.setText(row['content'])
            
            # 确保高亮规则被应用
            self.highlighter.update_highlighting_rules()
            self.highlighter.rehighlight()
            
            # 显示元数据
            meta_text = f"用户: {row['nick_name']} | 时间: {row['time']} | 转发: {row['转发数']} | 评论: {row['评价数']} | 点赞: {row['点赞数']}"
            if pd.notna(row.get('sentiment')):
                sentiment_map = {-1: "负面", 0: "中性", 1: "正面"}
                meta_text += f" | 当前标注: {sentiment_map[row['sentiment']]}"
            self.meta_label.setText(meta_text)
            
            # 更新进度
            self.update_progress()
            
            # 更新按钮颜色
            self.update_button_colors()
    
    def update_progress(self):
        if self.df is not None:
            total = len(self.df)
            current = self.current_index + 1
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.progress_bar.setFormat(f'进度: {current}/{total}')
    
    def update_button_states(self):
        """更新按钮状态"""
        if self.df is not None:
            self.prev_btn.setEnabled(self.current_index > 0)
            self.next_btn.setEnabled(self.current_index < len(self.df) - 1)
            self.goto_button.setEnabled(True)
            self.goto_unlabeled_button.setEnabled(True)
            self.goto_input.setEnabled(True)
            # 更新跳转输入框的提示文本
            self.goto_input.setPlaceholderText(f"输入序号(1-{len(self.df)})")
        else:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.goto_button.setEnabled(False)
            self.goto_unlabeled_button.setEnabled(False)
            self.goto_input.setEnabled(False)
            self.goto_input.setPlaceholderText("输入序号(1-N)")
    
    def update_button_colors(self):
        """更新按钮颜色以反映当前标注状态"""
        if self.df is not None and self.current_index < len(self.df):
            current_sentiment = self.df.iloc[self.current_index]['sentiment']
            
            # 重置所有按钮样式
            self.negative_btn.setStyleSheet(self.button_style['default'])
            self.neutral_btn.setStyleSheet(self.button_style['default'])
            self.positive_btn.setStyleSheet(self.button_style['default'])
            
            # 设置当前选中的按钮样式
            if pd.notna(current_sentiment):
                if current_sentiment == -1:
                    self.negative_btn.setStyleSheet(self.button_style['selected'])
                elif current_sentiment == 0:
                    self.neutral_btn.setStyleSheet(self.button_style['selected'])
                elif current_sentiment == 1:
                    self.positive_btn.setStyleSheet(self.button_style['selected'])
                    
    def annotate_sentiment(self, sentiment):
        if self.df is not None:
            self.df.at[self.current_index, 'sentiment'] = sentiment
            self.save_progress()
            self.update_statistics()
            self.update_button_colors()  # 立即更新按钮颜色
            self.next_item()
    
    def save_progress(self):
        if self.output_file:
            self.df.to_csv(self.output_file, index=False)
    
    def previous_item(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            self.update_button_states()
    
    def next_item(self):
        if self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.update_display()
            self.update_button_states()

    def show_output_location(self):
        if self.output_file:
            # 获取文件的绝对路径
            abs_path = os.path.abspath(self.output_file)
            # 获取文件所在的目录
            dir_path = os.path.dirname(abs_path)
            # 使用系统默认的文件管理器打开目录
            if sys.platform == 'win32':
                os.startfile(dir_path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{dir_path}"')
            else:  # Linux
                os.system(f'xdg-open "{dir_path}"')
        else:
            QMessageBox.information(self, '提示', '当前没有打开的标注文件。')

    def goto_index(self):
        """跳转到指定序号的条目"""
        if self.df is None:
            QMessageBox.warning(self, '警告', '请先加载数据文件！')
            return
            
        try:
            # 获取用户输入的序号（1-based）
            index = int(self.goto_input.text()) - 1
            
            # 验证序号范围
            if 0 <= index < len(self.df):
                self.current_index = index
                self.update_display()
                self.update_button_states()
            else:
                QMessageBox.warning(self, '警告', f'请输入1到{len(self.df)}之间的数字！')
        except ValueError:
            QMessageBox.warning(self, '警告', '请输入有效的数字！')
            
    def goto_next_unlabeled(self):
        """跳转到下一个未标注的条目"""
        if self.df is None:
            QMessageBox.warning(self, '警告', '请先加载数据文件！')
            return
            
        # 从当前位置开始查找下一个未标注的条目
        start_index = self.current_index + 1 if self.current_index < len(self.df) - 1 else 0
        
        # 首先从当前位置到末尾查找
        for i in range(start_index, len(self.df)):
            if pd.isna(self.df.iloc[i]['sentiment']):
                self.current_index = i
                self.update_display()
                self.update_button_states()
                return
                
        # 如果没找到，从开头到当前位置查找
        if start_index > 0:
            for i in range(0, start_index):
                if pd.isna(self.df.iloc[i]['sentiment']):
                    self.current_index = i
                    self.update_display()
                    self.update_button_states()
                    return
                    
        QMessageBox.information(self, '提示', '没有找到未标注的条目！')

def main():
    app = QApplication(sys.argv)
    ex = SentimentAnnotator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 