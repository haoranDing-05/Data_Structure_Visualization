import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QMessageBox, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QUrl, QPoint, QPropertyAnimation, QEasingCurve, QPointF
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QCursor, QPainter, QPainterPath, QColor, QPen, QPolygonF
from PyQt5.QtMultimedia import QSoundEffect

import traceback

from visualization import StackVisualizer, SequenceListVisualizer, LinkedListVisualizer, BinaryTreeVisualizer, \
    HuffmanTreeVisualizer, BinarySearchTreeVisualizer
from qianwen_api import QianWenAPI, AIAssistantThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_sound_effects()
        #添加背景音乐



        self.setWindowTitle("数据结构课设——数据结构可视化")
        self.setGeometry(100, 100, 640, 852)

        central_frame = QFrame()
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame, "./DataStructureVisualization/微信图片_20250922183759_13_117.jpg")

        main_layout = QVBoxLayout(central_frame)

        title_label = QLabel("数据结构课设——数据结构可视化")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMargin(40)
        title_label.setStyleSheet("color: blue; text-shadow: 2px 2px 4px #000000;")
        main_layout.addWidget(title_label)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(50)
        button_layout.setAlignment(Qt.AlignCenter)

        self.button1 = QPushButton("线性结构")
        self.button1.setMinimumSize(150, 60)
        self.button1.setFont(QFont("SimHei", 12))
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

        self.button2 = QPushButton("树形结构")
        self.button2.setMinimumSize(150, 60)
        self.button2.setFont(QFont("SimHei", 12))
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

        main_layout.addLayout(button_layout)
        main_layout.addSpacing(80)
        self.ai_assistant = None

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)

    def play_click_sound(self):
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()

    def on_button1_clicked(self):
        self.play_click_sound()
        self.go_to_sequential()

    def go_to_sequential(self):
        self.sequential_window = LinearStructureWindow(self)
        self.sequential_window.show()
        self.hide()

    def on_button2_clicked(self):
        self.play_click_sound()
        self.go_to_tree()

    def go_to_tree(self):
        self.tree_window = TreeStructureWindow(self)
        self.tree_window.show()
        self.hide()

    def set_background_image(self, widget, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)


class BubbleWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_sound_effects()
        self.preload_sound()
        self.setup_ui()
        self.direction = "right"
        self.qianwen_api = None
        self.ai_thread = None
        self.send_btn.setEnabled(False)
        self.welcome_shown = True

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/燕小北welcome语音包.wav"))
        self.click_sound.setVolume(0.7)

    def preload_sound(self):
        if not self.click_sound.source().isEmpty():
            self.click_sound.setLoopCount(0)

    def setup_ui(self):
        self.setFixedSize(500, 700)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            BubbleWidget {
                background: white;
                border-radius: 15px;
            }
        """)
        self.setAutoFillBackground(True)
        main_layout = QVBoxLayout(self)
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
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.question_input)
        input_layout.addWidget(self.send_btn)
        main_layout.addWidget(title)
        main_layout.addLayout(api_layout)
        main_layout.addWidget(QLabel("对话记录:"))
        main_layout.addWidget(self.chat_display)
        main_layout.addWidget(QLabel("输入问题:"))
        main_layout.addLayout(input_layout)

    def showEvent(self, event):
        super().showEvent(event)
        if self.welcome_shown:
            self.show_welcome_message()
            self.welcome_shown = False

    def show_welcome_message(self):
        welcome_message = "你好！我是燕小北，你的AI助手。我可以帮你解答关于数据结构的问题，比如线性结构、树形结构等各种算法和概念。请先配置API Key，然后就可以开始提问了！"
        self.show_message("燕小北", welcome_message)
        if not self.click_sound.source().isEmpty() and AI_Floating_Window.welcome_sound_play:
            self.click_sound.play()
            AI_Floating_Window.welcome_sound_play = False

    def config_api(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.show_message("系统", "请输入API Key")
            return
        self.qianwen_api = QianWenAPI(api_key)
        self.send_btn.setEnabled(True)
        self.api_key_input.clear()
        self.show_message("系统", "API配置成功！现在可以开始提问了。")

    def send_question(self):
        question = self.question_input.text().strip()
        if not question: return
        if not self.qianwen_api:
            self.show_message("系统", "请先配置API Key")
            return
        self.show_message("你", question)
        self.question_input.clear()
        self.send_btn.setEnabled(False)
        self.show_thinking_message()
        prompt = f"问题：{question}"
        self.ai_thread = AIAssistantThread(self.qianwen_api, prompt)
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.start()

    def show_thinking_message(self):
        self.chat_display.append("<b>系统:</b> <i>燕小北正在思考中，请稍候...</i>")
        self.chat_display.append("---")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def handle_ai_response(self, response):
        self.show_message("燕小北", response)
        self.send_btn.setEnabled(True)

    def show_message(self, sender, message):
        self.chat_display.append(f"<b>{sender}:</b> {message}")
        self.chat_display.append("---")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())


class AI_Floating_Window(QMainWindow):
    welcome_sound_play = True

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        ai_image_path = "./DataStructureVisualization/燕小北.png"
        import os
        if not os.path.exists(ai_image_path):
            self.pixmap = QPixmap(100, 100)
            self.pixmap.fill(Qt.red)
        else:
            self.pixmap = QPixmap(ai_image_path)
        scale_factor = 0.15
        new_width = int(self.pixmap.width() * scale_factor)
        new_height = int(self.pixmap.height() * scale_factor)
        self.pixmap = self.pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.resize(self.pixmap.width(), self.pixmap.height())
        self.setCentralWidget(self.image_label)
        self.dragging = False
        self.offset = QPoint()
        self.bubble = None
        self.bubble_visible = False
        self.bubble_direction = "right"
        self.ai_assistant = None
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setup_animations()

    def setup_animations(self):
        self.show_animation = QPropertyAnimation()
        self.show_animation.setDuration(500)
        self.show_animation.setEasingCurve(QEasingCurve.OutBack)
        self.hide_animation = QPropertyAnimation()
        self.hide_animation.setDuration(300)
        self.hide_animation.setEasingCurve(QEasingCurve.InBack)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.pos()
            self.dragging = True
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            if self.bubble_visible and self.bubble:
                self.bubble_offset = self.bubble.pos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)
            if self.bubble_visible and self.bubble:
                self.bubble.move(new_pos + self.bubble_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.PointingHandCursor))

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.bubble_visible:
                self.show_bubble()
            else:
                self.hide_bubble()

    def show_bubble(self):
        if self.bubble and self.bubble_visible: return
        self.bubble_direction = "left"
        self.bubble = BubbleWidget()
        self.bubble.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        bubble_x, bubble_y = self.calculate_bubble_position()
        self.bubble.move(bubble_x, bubble_y)
        self.bubble_offset = self.bubble.pos() - self.pos()
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
        if not self.bubble or not self.bubble_visible: return
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
        if self.bubble:
            self.bubble.close()
            self.bubble = None
        self.bubble_visible = False

    def calculate_bubble_position(self):
        icon_rect = self.geometry()
        if self.bubble_direction == "right":
            x = icon_rect.x() + icon_rect.width() + 10
            y = icon_rect.y() - (200 - icon_rect.height()) // 2
        else:
            x = icon_rect.x() - 600 - 10
            y = icon_rect.y() - (1000 - icon_rect.height()) // 2
        return x, y

    def closeEvent(self, event):
        if self.bubble: self.bubble.close()
        if self.ai_assistant: self.ai_assistant.close()
        event.accept()


class LinearStructureWindow(QMainWindow):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.init_sound_effects()
        self.setWindowTitle("线性结构可视化")
        self.setGeometry(100, 100, 640, 852)
        central_frame = QFrame()
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame, "./DataStructureVisualization/微信图片_20250922183759_13_117.jpg")
        main_layout = QVBoxLayout(central_frame)
        title_label = QLabel("线性结构")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMargin(40)
        title_label.setStyleSheet("color: blue; text-shadow: 2px 2px 4px #000000;")
        main_layout.addWidget(title_label)
        main_layout.addStretch()
        button_layout1 = QHBoxLayout()
        button_layout1.setSpacing(50)
        button_layout1.setAlignment(Qt.AlignCenter)
        button_layout2 = QHBoxLayout()
        button_layout2.setSpacing(50)
        button_layout2.setAlignment(Qt.AlignCenter)
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
        self.button_stack = QPushButton("栈")
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
        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)
        main_layout.addSpacing(80)

    def on_button_return_clicked(self):
        self.play_click_sound()
        self.back_to_main()

    def on_button_stack_clicked(self):
        self.play_click_sound()
        self.go_to_stack()

    def on_button_sequencelist_clicked(self):
        self.play_click_sound()
        self.go_to_sequencelist()

    def on_button_linkedlist_clicked(self):
        self.play_click_sound()
        self.go_to_linkedlist()

    def back_to_main(self):
        self.mainwindow.show()
        self.close()

    def go_to_stack(self):
        try:
            self.stack_window = StackVisualizer(self.mainwindow, self)
            self.stack_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"出错: {e}")

    def go_to_sequencelist(self):
        try:
            self.sequencelist_window = SequenceListVisualizer(self.mainwindow, self)
            self.sequencelist_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"出错: {e}")

    def go_to_linkedlist(self):
        try:
            self.linkedlist_window = LinkedListVisualizer(self.mainwindow, self)
            self.linkedlist_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"出错: {e}")

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)

    def play_click_sound(self):
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()

    def set_background_image(self, widget, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)


class TreeStructureWindow(QMainWindow):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.init_sound_effects()
        self.setWindowTitle("树形结构可视化")
        self.setGeometry(100, 100, 640, 852)
        central_frame = QFrame()
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame, "./DataStructureVisualization/微信图片_20250922183759_13_117.jpg")
        main_layout = QVBoxLayout(central_frame)
        title_label = QLabel("树形结构")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMargin(40)
        title_label.setStyleSheet("color: blue; text-shadow: 2px 2px 4px #000000;")
        main_layout.addWidget(title_label)
        main_layout.addStretch()

        button_layout1 = QHBoxLayout()
        button_layout1.setSpacing(50)
        button_layout1.setAlignment(Qt.AlignCenter)

        button_layout2 = QHBoxLayout()
        button_layout2.setSpacing(50)
        button_layout2.setAlignment(Qt.AlignCenter)

        # --- 新增/修改部分: 二叉搜索树按钮 ---

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

        # 新增按钮: 二叉搜索树
        self.button_BST = QPushButton("二叉搜索树")
        self.button_BST.setMinimumSize(150, 60)
        self.button_BST.setFont(QFont("SimHei", 12))
        self.button_BST.setStyleSheet("""
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
        self.button_BST.clicked.connect(self.on_button_BST_clicked)
        # 添加到第二行或其他合适位置
        button_layout1.addWidget(self.button_BST)

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

        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)
        main_layout.addSpacing(80)

    def on_button_return_clicked(self):
        self.play_click_sound()
        self.back_to_main()

    def back_to_main(self):
        self.mainwindow.show()
        self.close()

    def on_button_Binary_tree_clicked(self):
        self.play_click_sound()
        self.go_to_Binary_tree()

    def on_button_Huffman_tree_clicked(self):
        self.play_click_sound()
        self.go_to_Huffman_tree()

    def on_button_BST_clicked(self):
        self.play_click_sound()
        self.go_to_BST()

    def go_to_Binary_tree(self):
        try:
            self.Binary_tree_window = BinaryTreeVisualizer(self.mainwindow, self)
            self.Binary_tree_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"出错: {e}")

    def go_to_Huffman_tree(self):
        try:
            self.Huffman_tree_window = HuffmanTreeVisualizer(self.mainwindow, self)
            self.Huffman_tree_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"出错: {e}")

    def go_to_BST(self):
        try:
            self.BST_window = BinarySearchTreeVisualizer(self.mainwindow, self)
            self.BST_window.show()
            self.hide()
            print("二叉搜索树可视化工具启动成功")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"出错: {e}")

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)

    def play_click_sound(self):
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()

    def set_background_image(self, widget, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    #ai_window = AI_Floating_Window()
    window.show()
    #ai_window.show()
    sys.exit(app.exec_())