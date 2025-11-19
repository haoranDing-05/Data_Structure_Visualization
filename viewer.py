import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QMessageBox, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QUrl, QPoint, QPropertyAnimation, QEasingCurve,QPointF
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QCursor,QPainter, QPainterPath, QColor, QPen, QPolygonF
from PyQt5.QtMultimedia import QSoundEffect

from PyQt5.QtWidgets import QApplication

import traceback

###from model import SequenceList
from visualization import StackVisualizer, SequenceListVisualizer, LinkedListVisualizer,BinaryTreeVisualizer,HuffmanTreeVisualizer
from qianwen_api import  QianWenAPI, AIAssistantThread  # 导入AI助手


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #初始化音效
        self.init_sound_effects()

        # 设置窗口标题和大小
        self.setWindowTitle("主界面")  # 可修改窗口标题
        self.setGeometry(100, 100, 640, 852)  # 增大窗口尺寸

        # 创建带背景的中心部件
        central_frame = QFrame()
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame, "./DataStructureVisualization/微信图片_20250922183759_13_117.jpg")  # 替换为你的背景图片路径

        # 创建主布局（垂直布局）
        main_layout = QVBoxLayout(central_frame)

        # 添加标题标签
        title_label = QLabel("数据结构课设——数据结构可视化")  # 保留你的标题文本
        title_font = QFont()
        title_font.setPointSize(15)  # 增大标题字体（修改2）
        title_font.setBold(True)  # 标题加粗
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)  # 标题居中
        title_label.setMargin(40)  # 增大标题边距
        title_label.setStyleSheet("color: blue; text-shadow: 2px 2px 4px #000000;")
        main_layout.addWidget(title_label)

        # 添加伸缩项，使按钮位置更合理
        main_layout.addStretch()

        # 添加按钮布局（水平布局）
        button_layout = QHBoxLayout()
        button_layout.setSpacing(50)  # 增大按钮间距
        button_layout.setAlignment(Qt.AlignCenter)  # 按钮居中

        # 创建第一个按钮
        self.button1 = QPushButton("线性结构")  # 保留你的按钮文本
        self.button1.setMinimumSize(150, 60)  # 增大按钮大小
        self.button1.setFont(QFont("SimHei", 12))  # 设置按钮字体
        # 美化按钮样式
        self.button1.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 130, 255, 0.8);
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(60, 130, 255, 1.0);
                transform: scale(1.05);
            }
        """)
        self.button1.clicked.connect(self.on_button1_clicked)
        button_layout.addWidget(self.button1)

        # 创建第二个按钮
        self.button2 = QPushButton("树形结构")  # 保留你的按钮文本
        self.button2.setMinimumSize(150, 60)  # 增大按钮大小（修改10）
        self.button2.setFont(QFont("SimHei", 12))  # 设置按钮字体（修改11）

        self.button2.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 130, 255, 0.8);
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(60, 130, 255, 1.0);
                transform: scale(1.05);
            }
        """)
        self.button2.clicked.connect(self.on_button2_clicked)
        button_layout.addWidget(self.button2)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 添加底部间距（修改13）
        main_layout.addSpacing(80)

        self.ai_assistant=None


    def init_sound_effects(self):
        self.click_sound=QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)  # 设置音量（0.0-1.0）

    def play_click_sound(self):
        """播放点击音效"""
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()
        else:
            # 如果音效文件未设置，显示提示
            QMessageBox.warning(self, "提示", "未设置点击音效文件")

    def on_button1_clicked(self):
        """第一个按钮点击事件处理"""
        print("button1 is clicked")
        self.play_click_sound()  # 播放按钮点击音效
        self.go_to_sequential()
        print(1)

    def go_to_sequential(self):
        self.sequential_window = LinearStructureWindow(self)  # 传入self
        self.sequential_window.show()
        self.hide()

    def on_button2_clicked(self):
        """第二个按钮点击事件处理"""
        print("button2 is clicked")
        self.play_click_sound()  # 播放音效
        print(1)
        # 这里可以添加树形结构界面的逻辑
        self.go_to_tree()
        print(2)

    def go_to_tree(self):
        self.tree_window = TreeStructureWindow(self)  # 传入self
        self.tree_window.show()
        self.hide()


    def set_background_image(self, widget, image_path):
        """设置控件的背景图片"""
        palette = QPalette()
        pixmap = QPixmap(image_path)

        # 缩放图片以适应窗口大小
        scaled_pixmap = pixmap.scaled(
            widget.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)



class BubbleWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化音效
        self.init_sound_effects()
        self.preload_sound()

        self.setup_ui()
        self.direction="right" #对话框尖头朝向
        self.qianwen_api = None
        self.ai_thread = None
        self.send_btn.setEnabled(False)

        self.welcome_shown=True

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/燕小北welcome语音包.wav"))
        self.click_sound.setVolume(0.7)  # 设置音量（0.0-1.0）

    def preload_sound(self):
        """预加载音效以减少首次播放延迟"""
        if not self.click_sound.source().isEmpty():
            # 预加载音效
            self.click_sound.setLoopCount(0)  # 不循环

    def setup_ui(self):
        self.setFixedSize(500,700)
        self.setFrameStyle(QFrame.NoFrame)

        # 设置气泡样式
        self.setStyleSheet("""
            BubbleWidget {
                background: white
                border-radius: 15px;
            }
        """)
        self.setAutoFillBackground(True)

        #添加主布局
        main_layout = QVBoxLayout(self)

        # 标题
        title = QLabel("燕小北")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1565c0;
                padding: 5px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)

        # API Key 输入
        api_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入通义千问API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #90caf9;
                        border-radius: 5px;
                        padding: 5px;
                        background: white;
                    }
                """)

        config_btn = QPushButton("配置")
        config_btn.setFixedSize(60, 30)
        config_btn.setStyleSheet("""
                    QPushButton {
                        background: #42a5f5;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background: #64b5f6;
                    }
                """)

        config_btn.clicked.connect(self.config_api)

        api_layout.addWidget(self.api_key_input)
        api_layout.addWidget(config_btn)

        # 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
                    QTextEdit {
                        background: white;
                        border: 1px solid #90caf9;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 12px;
                    }
                """)

        # 问题输入区域
        input_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("输入你的问题...")
        self.question_input.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #90caf9;
                        border-radius: 5px;
                        padding: 5px;
                        background: white;
                    }
                """)
        self.question_input.returnPressed.connect(self.send_question)

        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(60, 30)
        self.send_btn.setStyleSheet("""
                    QPushButton {
                        background: #42a5f5;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover:enabled {
                        background: #64b5f6;
                    }
                    QPushButton:disabled {
                        background: #bdbdbd;
                    }
                """)
        self.send_btn.clicked.connect(self.send_question)
        self.send_btn.setEnabled(False)  # 初始禁用

        input_layout.addWidget(self.question_input)
        input_layout.addWidget(self.send_btn)

        # 添加到主布局
        main_layout.addWidget(title)
        main_layout.addLayout(api_layout)
        main_layout.addWidget(QLabel("对话记录:"))
        main_layout.addWidget(self.chat_display)
        main_layout.addWidget(QLabel("输入问题:"))
        main_layout.addLayout(input_layout)

    def showEvent(self, event):
        """窗口显示时显示欢迎消息"""
        super().showEvent(event)
        if  self.welcome_shown:
            self.show_welcome_message()
            self.welcome_shown = False

    def show_welcome_message(self):
        """显示欢迎消息"""
        welcome_message = "你好！我是燕小北，你的AI助手。我可以帮你解答关于数据结构的问题，比如线性结构、树形结构等各种算法和概念。请先配置API Key，然后就可以开始提问了！"
        self.show_message("燕小北", welcome_message)
        if not self.click_sound.source().isEmpty() and AI_Floating_Window.welcome_sound_play:
            self.click_sound.play()
            AI_Floating_Window.welcome_sound_play=False
        elif self.click_sound.source().isEmpty():
            # 如果音效文件未设置，显示提示
            QMessageBox.warning(self, "提示", "未设置点击音效文件")
        else:
            pass

    def config_api(self):
        """配置API Key"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.show_message("系统", "请输入API Key")
            return

        self.qianwen_api = QianWenAPI(api_key)
        self.send_btn.setEnabled(True)
        self.api_key_input.clear()
        self.show_message("系统", "API配置成功！现在可以开始提问了。")

    def send_question(self):
        """发送问题"""
        question = self.question_input.text().strip()
        if not question:
            return

        if not self.qianwen_api:
            self.show_message("系统", "请先配置API Key")
            return

        # 显示用户问题
        self.show_message("你", question)
        self.question_input.clear()
        self.send_btn.setEnabled(False)
        self.show_thinking_message()

        # 生成提示词
        prompt = f"问题：{question}"

        # 在新线程中处理请求
        self.ai_thread = AIAssistantThread(self.qianwen_api, prompt)
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.start()

    def show_thinking_message(self):
        """显示正在思考的提示"""
        # 在聊天区域添加思考提示
        self.chat_display.append("<b>系统:</b> <i>燕小北正在思考中，请稍候...</i>")
        self.chat_display.append("---")
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def handle_ai_response(self, response):
        """处理AI响应"""

        self.show_message("燕小北", response)
        self.send_btn.setEnabled(True)


    def show_message(self, sender, message):
        """显示消息"""
        self.chat_display.append(f"<b>{sender}:</b> {message}")
        self.chat_display.append("---")
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

class AI_Floating_Window(QMainWindow):
    # 添加类变量
    welcome_sound_play = True
    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 加载图片 - 确保路径正确
        ai_image_path = "./DataStructureVisualization/燕小北.png"

        # 检查文件是否存在
        import os
        if not os.path.exists(ai_image_path):
            print(f"图片文件不存在: {ai_image_path}")
            self.pixmap = QPixmap(100, 100)  # 创建空图片
            self.pixmap.fill(Qt.red)  # 用红色填充以便调试
        else:
            self.pixmap = QPixmap(ai_image_path)

        # 等比例缩小图片 使其满足ai浮窗助手的大小需求
        scale_factor = 0.15
        new_width = int(self.pixmap.width() * scale_factor)
        new_height = int(self.pixmap.height() * scale_factor)
        self.pixmap = self.pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 创建标签显示图片
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        # 设置窗口大小与图片一致
        self.resize(self.pixmap.width(), self.pixmap.height())

        # 设置中心部件
        self.setCentralWidget(self.image_label)

        # 鼠标拖动相关变量
        self.dragging = False
        self.offset = QPoint()
        self.bubble = None
        self.bubble_visible = False
        self.bubble_direction = "right"  # 默认从右侧弹出
        self.ai_assistant = None  # AI助手实例

        # 设置鼠标样式为手型，表示可拖动
        self.setCursor(QCursor(Qt.PointingHandCursor))



        # 初始化动画
        self.setup_animations()

    def setup_animations(self):
        # 气泡显示动画
        self.show_animation = QPropertyAnimation()
        self.show_animation.setDuration(500)
        self.show_animation.setEasingCurve(QEasingCurve.OutBack)

        # 气泡隐藏动画
        self.hide_animation = QPropertyAnimation()
        self.hide_animation.setDuration(300)
        self.hide_animation.setEasingCurve(QEasingCurve.InBack)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录鼠标位置和窗口位置的偏移
            self.offset = event.globalPos() - self.pos()
            self.dragging = True
            # 临时改变鼠标样式为闭合手型，表示正在拖动
            self.setCursor(QCursor(Qt.ClosedHandCursor))

            # 如果气泡可见，记录气泡相对于图标的位置
            if self.bubble_visible and self.bubble:
                self.bubble_offset = self.bubble.pos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            # 移动主窗口到新的位置
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)

            # 如果气泡可见，同时移动气泡
            if self.bubble_visible and self.bubble:
                self.bubble.move(new_pos + self.bubble_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # 恢复鼠标样式
            self.setCursor(QCursor(Qt.PointingHandCursor))

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("图片被双击点击了!")
            if not self.bubble_visible:
                self.show_bubble()   #如果ai功能页未打开 双击燕小北时打开ai功能页
            else:
                self.hide_bubble()   #如果ai功能页已经打开 双击燕小北时关闭ai功能页

    def show_bubble(self):
        if self.bubble and self.bubble_visible:
            return

        # 随机选择弹出方向
        self.bubble_direction = "left"

        # 创建气泡窗口
        self.bubble = BubbleWidget()
        self.bubble.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.bubble.setAttribute(Qt.WA_TranslucentBackground)

        # 计算气泡位置
        bubble_x, bubble_y = self.calculate_bubble_position()
        self.bubble.move(bubble_x, bubble_y)

        # 记录气泡相对于图标的位置
        self.bubble_offset = self.bubble.pos() - self.pos()

        # 设置动画
        if self.bubble_direction == "right":
            self.show_animation.setPropertyName(b"pos")
            self.show_animation.setStartValue(QPoint(bubble_x - 50, bubble_y))
            self.show_animation.setEndValue(QPoint(bubble_x, bubble_y))
        else:
            self.show_animation.setPropertyName(b"pos")
            self.show_animation.setStartValue(QPoint(bubble_x + 50, bubble_y))
            self.show_animation.setEndValue(QPoint(bubble_x, bubble_y))

        self.show_animation.setTargetObject(self.bubble)
        self.bubble.show()
        self.show_animation.start()

        self.bubble_visible = True

    def hide_bubble(self):
        if not self.bubble or not self.bubble_visible:
            return

        # 设置隐藏动画
        bubble_x, bubble_y = self.bubble.pos().x(), self.bubble.pos().y()

        if self.bubble_direction == "right":
            self.hide_animation.setPropertyName(b"pos")
            self.hide_animation.setStartValue(QPoint(bubble_x, bubble_y))
            self.hide_animation.setEndValue(QPoint(bubble_x - 50, bubble_y))
        else:
            self.hide_animation.setPropertyName(b"pos")
            self.hide_animation.setStartValue(QPoint(bubble_x, bubble_y))
            self.hide_animation.setEndValue(QPoint(bubble_x + 50, bubble_y))

        self.hide_animation.setTargetObject(self.bubble)
        self.hide_animation.finished.connect(self.on_bubble_hidden)
        self.hide_animation.start()

    def on_bubble_hidden(self):
        """气泡隐藏完成后的回调"""
        if self.bubble:
            self.bubble.close()
            self.bubble = None
        self.bubble_visible = False


    def calculate_bubble_position(self):
        # 计算气泡应该出现的位置
        icon_rect = self.geometry()

        if self.bubble_direction == "right":
            # 气泡出现在图标右侧
            x = icon_rect.x() + icon_rect.width() + 10
            y = icon_rect.y() - (200 - icon_rect.height()) // 2
        else:
            # 气泡出现在图标左侧
            x = icon_rect.x() - 600 - 10  # 气泡宽度为600
            y = icon_rect.y() - (1000 - icon_rect.height()) // 2  # 气泡高度为1000

        return x, y

    def closeEvent(self, event):
        """窗口关闭时确保气泡也关闭"""
        if self.bubble:
            self.bubble.close()
        if self.ai_assistant:
            self.ai_assistant.close()
        event.accept()



class LinearStructureWindow(QMainWindow):
    def __init__(self,mainwindow):
        super().__init__()   #调用其父类（QMainWindow）的构造方法

        self.mainwindow=mainwindow

        self.init_sound_effects()   #初始化音效

        #设置窗口的标题和窗口的大小
        self.setWindowTitle("线性结构可视化")
        self.setGeometry(100,100,640,852)

        #添加带背景图片的中心组件
        central_frame=QFrame()     #创建组件
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame,"./DataStructureVisualization/微信图片_20250922183759_13_117.jpg")


        main_layout=QVBoxLayout(central_frame)

        #添加标题 标签
        title_label=QLabel("线性结构")
        title_font=QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMargin(40)
        # 添加标题样式
        title_label.setStyleSheet("color: blue; text-shadow: 2px 2px 4px #000000;")
        main_layout.addWidget(title_label)

        # 添加伸缩项，使按钮位置更合理
        main_layout.addStretch()

        # 添加功能按钮布局
        button_layout1 = QHBoxLayout()  #水平布局
        button_layout1.setSpacing(50)  # 增大按钮间距
        button_layout1.setAlignment(Qt.AlignCenter)  # 按钮居中

        #添加
        button_layout2=QHBoxLayout()  #水平布局
        button_layout2.setSpacing(50)
        button_layout2.setAlignment(Qt.AlignCenter)  # 按钮居中

        #创建返回按钮
        self.button_return=QPushButton("返回主界面")
        self.button_return.setMinimumSize(150,60)
        self.button_return.setFont(QFont("SimHei", 12))
        self.button_return.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(60, 130, 255, 0.8);
                        color: white;
                        border-radius: 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: rgba(60, 130, 255, 1.0);
                        transform: scale(1.05);
                    }
                """)
        self.button_return.clicked.connect(self.on_button_return_clicked)
        button_layout2.addWidget(self.button_return)



        self.button_stack=QPushButton("栈")
        self.button_stack.setMinimumSize(150, 60)
        self.button_stack.setFont(QFont("SimHei", 12))
        self.button_stack.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(60, 130, 255, 0.8);
                        color: white;
                        border-radius: 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: rgba(60, 130, 255, 1.0);
                        transform: scale(1.05);
                    }
                """)
        self.button_stack.clicked.connect(self.on_button_stack_clicked)
        button_layout1.addWidget(self.button_stack)



        self.button_sequencelist = QPushButton("顺序表")
        self.button_sequencelist.setMinimumSize(150, 60)
        self.button_sequencelist.setFont(QFont("SimHei", 12))
        self.button_sequencelist.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(60, 130, 255, 0.8);
                                color: white;
                                border-radius: 10px;
                                border: none;
                            }
                            QPushButton:hover {
                                background-color: rgba(60, 130, 255, 1.0);
                                transform: scale(1.05);
                            }
                        """)
        self.button_sequencelist.clicked.connect(self.on_button_sequencelist_clicked)
        button_layout1.addWidget(self.button_sequencelist)

        self.button_linkedlist = QPushButton("链表")
        self.button_linkedlist.setMinimumSize(150, 60)
        self.button_linkedlist.setFont(QFont("SimHei", 12))
        self.button_linkedlist.setStyleSheet("""
                                    QPushButton {
                                        background-color: rgba(60, 130, 255, 0.8);
                                        color: white;
                                        border-radius: 10px;
                                        border: none;
                                    }
                                    QPushButton:hover {
                                        background-color: rgba(60, 130, 255, 1.0);
                                        transform: scale(1.05);
                                    }
                                """)
        self.button_linkedlist.clicked.connect(self.on_button_linkedlist_clicked)
        button_layout1.addWidget(self.button_linkedlist)


        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)

        # 添加底部间距
        main_layout.addSpacing(80)


    def on_button_return_clicked(self):
        """返回按钮点击事件处理"""
        print("button_return is clicked")
        self.play_click_sound()
        self.back_to_main()

    def on_button_stack_clicked(self):
        """栈可视化按钮点击事件处理"""
        self.play_click_sound()
        self.go_to_stack()

    def on_button_sequencelist_clicked(self):
        """顺序表可视化按钮点击事件处理"""
        self.play_click_sound()
        self.go_to_sequencelist()

    def on_button_linkedlist_clicked(self):
        """链表可视化按钮点击事件处理"""
        self.play_click_sound()
        self.go_to_linkedlist()


    def back_to_main(self):
        self.mainwindow.show()  # 显示原主窗口
        self.close()  # 关闭子窗口

    def go_to_stack(self):
        try:
            # 确保传递了 self 作为 last_window
            self.stack_window = StackVisualizer(self.mainwindow, self)  # 添加 self 作为 last_window
            self.stack_window.show()
            self.hide()
            print("栈可视化工具启动成功")
        except Exception as e:
            print(f"应用程序错误: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"打开栈可视化工具时出错: {e}")

    def go_to_sequencelist(self):
        try:
            self.sequencelist_window=SequenceListVisualizer(self.mainwindow,self)
            self.sequencelist_window.show()
            self.hide()
            print("顺序表可视化工具启动成功")
        except Exception as e:
            print(f"应用程序错误:{e}")
            traceback.print_exc()
            QMessageBox.critical(self,"错误",f"打开顺序表可视化工具时出错:{e}")

    def go_to_linkedlist(self):
        try:
            self.linkedlist_window=LinkedListVisualizer(self.mainwindow,self)
            self.linkedlist_window.show()
            self.hide()
            print("链表可视化工具启动成功")
        except Exception as e:
            print(f"应用程序错误:{e}")
            traceback.print_exc()
            QMessageBox.critical(self,"错误",f"打开链表可视化工具时出错:{e}")


    def init_sound_effects(self):
        self.click_sound=QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)  # 设置音量（0.0-1.0）

    def play_click_sound(self):
        """播放点击音效"""
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()
        else:
            # 如果音效文件未设置，显示提示
            QMessageBox.warning(self, "提示", "未设置点击音效文件")

    def set_background_image(self,widget,image_path):
        palette=QPalette()
        pixmap=QPixmap(image_path)    #将路径中的图片以像素形式存储在变量pixmap中
        print(type(pixmap))

        #缩放图片以适应窗口大小
        scaled_pixmap=pixmap.scaled(
            widget.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)


class TreeStructureWindow(QMainWindow):
    def __init__(self,mainwindow):
        super().__init__()   #调用其父类（QMainWindow）的构造方法

        self.mainwindow=mainwindow

        self.init_sound_effects()   #初始化音效

        #设置窗口的标题和窗口的大小
        self.setWindowTitle("树形结构可视化")
        self.setGeometry(100,100,640,852)

        #添加带背景图片的中心组件
        central_frame=QFrame()     #创建组件
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame,"./DataStructureVisualization/微信图片_20250922183759_13_117.jpg")


        main_layout=QVBoxLayout(central_frame)

        #添加标题 标签
        title_label=QLabel("树形结构")
        title_font=QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMargin(40)
        # 添加标题样式
        title_label.setStyleSheet("color: blue; text-shadow: 2px 2px 4px #000000;")
        main_layout.addWidget(title_label)

        # 添加伸缩项，使按钮位置更合理
        main_layout.addStretch()

        # 添加功能按钮布局
        button_layout1 = QHBoxLayout()  # 水平布局
        button_layout1.setSpacing(50)  # 增大按钮间距
        button_layout1.setAlignment(Qt.AlignCenter)  # 按钮居中

        # 添加
        button_layout2 = QHBoxLayout()  # 水平布局
        button_layout2.setSpacing(50)
        button_layout2.setAlignment(Qt.AlignCenter)  # 按钮居中

        # 创建返回按钮
        self.button_return = QPushButton("返回主界面")
        self.button_return.setMinimumSize(150, 60)
        self.button_return.setFont(QFont("SimHei", 12))
        self.button_return.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(60, 130, 255, 0.8);
                                color: white;
                                border-radius: 10px;
                                border: none;
                            }
                            QPushButton:hover {
                                background-color: rgba(60, 130, 255, 1.0);
                                transform: scale(1.05);
                            }
                        """)
        self.button_return.clicked.connect(self.on_button_return_clicked)
        button_layout2.addWidget(self.button_return)

        self.button_Binary_tree = QPushButton("二叉树")
        self.button_Binary_tree.setMinimumSize(150, 60)
        self.button_Binary_tree.setFont(QFont("SimHei", 12))
        self.button_Binary_tree.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(60, 130, 255, 0.8);
                                color: white;
                                border-radius: 10px;
                                border: none;
                            }
                            QPushButton:hover {
                                background-color: rgba(60, 130, 255, 1.0);
                                transform: scale(1.05);
                            }
                        """)
        self.button_Binary_tree.clicked.connect(self.on_button_Binary_tree_clicked)
        button_layout1.addWidget(self.button_Binary_tree)

        self.button_Huffman_tree = QPushButton("哈夫曼树")
        self.button_Huffman_tree.setMinimumSize(150, 60)
        self.button_Huffman_tree.setFont(QFont("SimHei", 12))
        self.button_Huffman_tree.setStyleSheet("""
                                    QPushButton {
                                        background-color: rgba(60, 130, 255, 0.8);
                                        color: white;
                                        border-radius: 10px;
                                        border: none;
                                    }
                                    QPushButton:hover {
                                        background-color: rgba(60, 130, 255, 1.0);
                                        transform: scale(1.05);
                                    }
                                """)
        self.button_Huffman_tree.clicked.connect(self.on_button_Huffman_tree_clicked)
        button_layout1.addWidget(self.button_Huffman_tree)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)

        # 添加底部间距
        main_layout.addSpacing(80)

    def on_button_return_clicked(self):
        """返回按钮点击事件处理"""
        print("button_return is clicked")
        self.play_click_sound()
        self.back_to_main()

    def back_to_main(self):
        self.mainwindow.show()
        self.close()


    def on_button_Binary_tree_clicked(self):
        """二叉树按钮点击事件处理"""
        print("button_Binary_tree is clicked")
        self.play_click_sound()
        self.go_to_Binary_tree()

    def on_button_Huffman_tree_clicked(self):
        """哈夫曼树按钮点击事件处理"""
        print("button_Huffman_tree is clicked")
        self.play_click_sound()
        self.go_to_Huffman_tree()



    def go_to_Binary_tree(self):
        try:
            self.Binary_tree_window=BinaryTreeVisualizer(self.mainwindow,self)
            self.Binary_tree_window.show()
            self.hide()
            print("二叉树可视化工具启动成功")
        except Exception as e:
            print(f"应用程序错误:{e}")
            traceback.print_exc()
            QMessageBox.critical(self,"错误",f"打开二叉树可视化工具时出错:{e}")

    def go_to_Huffman_tree(self):
        try:
            self.Huffman_tree_window=HuffmanTreeVisualizer(self.mainwindow,self)
            self.Huffman_tree_window.show()
            self.hide()
            print("哈夫曼树可视化工具启动成功")
        except Exception as e:
            print(f"应用程序错误:{e}")
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"打开哈夫曼树可视化工具时出错:{e}")





    def init_sound_effects(self):
        self.click_sound=QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)  # 设置音量（0.0-1.0）

    def play_click_sound(self):
        """播放点击音效"""
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()
        else:
            # 如果音效文件未设置，显示提示
            QMessageBox.warning(self, "提示", "未设置点击音效文件")

    def set_background_image(self,widget,image_path):
        palette=QPalette()
        pixmap=QPixmap(image_path)    #将路径中的图片以像素形式存储在变量pixmap中
        print(type(pixmap))

        #缩放图片以适应窗口大小
        scaled_pixmap=pixmap.scaled(
            widget.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)


if __name__ == "__main__":
    # 创建应用实例
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = MainWindow()
    ai_window = AI_Floating_Window()
    window.show()
    ai_window.show()

    # 进入应用主循环
    sys.exit(app.exec_())