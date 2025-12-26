import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QMessageBox, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QUrl, QPoint, QPropertyAnimation, QEasingCurve, QPointF
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QCursor, QPainter, QPainterPath, QColor, QPen, QPolygonF
from PyQt5.QtMultimedia import QSoundEffect

import traceback

# 确保导入了所有的 Visualizer，包括 QueueVisualizer
from visualization import StackVisualizer, SequenceListVisualizer, LinkedListVisualizer, BinaryTreeVisualizer, \
    HuffmanTreeVisualizer, BinarySearchTreeVisualizer, AVLTreeVisualizer, QueueVisualizer
from qianwen_api import QianWenAPI, AIAssistantThread
# 【关键修复】导入 DSLHandler，用于本地执行指令
from DSL_handler import DSLHandler


def adjust_window_to_screen(window, width_ratio=0.6, height_ratio=0.8):
    """根据屏幕大小自动调整窗口尺寸并居中"""
    screen = QApplication.primaryScreen().availableGeometry()
    target_width = int(screen.width() * width_ratio)
    target_height = int(screen.height() * height_ratio)

    x = (screen.width() - target_width) // 2
    y = (screen.height() - target_height) // 2

    window.setGeometry(x, y, target_width, target_height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_sound_effects()
        self.setWindowTitle("数据结构课设——数据结构可视化")

        adjust_window_to_screen(self, 0.5, 0.8)

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

        # 保存子窗口引用以便查找
        self.sequential_window = None
        self.tree_window = None

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
        if not self.sequential_window:
            self.sequential_window = LinearStructureWindow(self)
        self.sequential_window.show()
        self.hide()

    def on_button2_clicked(self):
        self.play_click_sound()
        self.go_to_tree()

    def go_to_tree(self):
        if not self.tree_window:
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

        # 请确保此 API Key 有效
        self.api_key = "sk-e3e7f71402ad4dc28e87b9763b5c82f4"

        self.setup_ui()
        self.direction = "right"

        self.qianwen_api = QianWenAPI(self.api_key)
        self.ai_thread = None

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
                border: 1px solid #e0e0e0;
            }
        """)
        self.setAutoFillBackground(True)
        main_layout = QVBoxLayout(self)

        title = QLabel("燕小北 AI 助手")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1565c0;
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
        """)
        title.setAlignment(Qt.AlignCenter)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
                    QTextEdit {
                        background: #f5f5f5;
                        border: none;
                        border-radius: 8px;
                        padding: 10px;
                        font-size: 14px;
                        font-family: "Microsoft YaHei";
                    }
                """)

        input_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("输入问题或DSL指令 (如 ENQUEUE:8)...")
        self.question_input.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #bdbdbd;
                        border-radius: 20px;
                        padding: 8px 15px;
                        background: white;
                        font-size: 14px;
                    }
                    QLineEdit:focus {
                        border: 1px solid #42a5f5;
                    }
                """)
        self.question_input.returnPressed.connect(self.send_question)

        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(70, 36)
        self.send_btn.setStyleSheet("""
                    QPushButton {
                        background: #42a5f5;
                        color: white;
                        border: none;
                        border-radius: 18px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: #64b5f6;
                    }
                    QPushButton:pressed {
                        background: #1e88e5;
                    }
                    QPushButton:disabled {
                        background: #e0e0e0;
                        color: #9e9e9e;
                    }
                """)
        self.send_btn.clicked.connect(self.send_question)
        self.send_btn.setEnabled(True)

        input_layout.addWidget(self.question_input)
        input_layout.addWidget(self.send_btn)

        main_layout.addWidget(title)
        main_layout.addWidget(self.chat_display, 1)
        main_layout.addLayout(input_layout)
        main_layout.setContentsMargins(15, 15, 15, 15)

    def showEvent(self, event):
        super().showEvent(event)
        if self.welcome_shown:
            self.show_welcome_message()
            self.welcome_shown = False

    def show_welcome_message(self):
        welcome_message = "你好！我是燕小北。你可以问我问题，也可以直接输入 DSL 指令（如 QUEUE ENQUEUE: 8）来控制动画！"
        self.show_message("燕小北", welcome_message)
        if not self.click_sound.source().isEmpty() and AI_Floating_Window.welcome_sound_play:
            self.click_sound.play()
            AI_Floating_Window.welcome_sound_play = False

    # 【核心逻辑 1】检测是否为 DSL 指令
    def check_is_dsl(self, text):
        """检测输入是否为 DSL 指令"""
        # 必须把 QUEUE, ENQUEUE, DEQUEUE 加进去
        keywords = ['BUILD', 'INSERT', 'DELETE', 'SEARCH', 'PUSH', 'POP',
                    'ENQUEUE', 'DEQUEUE', 'QUEUE', 'STACK', 'BST', 'AVL',
                    'SEQLIST', 'LINKEDLIST', 'BINARYTREE', 'HUFFMANTREE']
        upper_text = text.strip().upper()
        # 只要以关键字开头，就认为是指令
        for kw in keywords:
            if upper_text.startswith(kw):
                return True
        return False

    def get_active_visualizer(self):
        """查找当前激活的可视化窗口"""
        # 1. 找到主窗口
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, MainWindow):
                main_win = widget
                break

        if not main_win: return None

        # 2. 检查线性结构窗口
        if main_win.sequential_window and main_win.sequential_window.isVisible():
            lw = main_win.sequential_window
            # 依次检查哪个子窗口是显示的
            if hasattr(lw, 'stack_window') and lw.stack_window and lw.stack_window.isVisible(): return lw.stack_window
            if hasattr(lw, 'queue_window') and lw.queue_window and lw.queue_window.isVisible(): return lw.queue_window
            if hasattr(lw,
                       'sequencelist_window') and lw.sequencelist_window and lw.sequencelist_window.isVisible(): return lw.sequencelist_window
            if hasattr(lw,
                       'linkedlist_window') and lw.linkedlist_window and lw.linkedlist_window.isVisible(): return lw.linkedlist_window

        # 3. 检查树形结构窗口
        if main_win.tree_window and main_win.tree_window.isVisible():
            tw = main_win.tree_window
            if hasattr(tw, 'BST_window') and tw.BST_window and tw.BST_window.isVisible(): return tw.BST_window
            if hasattr(tw, 'AVL_window') and tw.AVL_window and tw.AVL_window.isVisible(): return tw.AVL_window
            if hasattr(tw,
                       'Binary_tree_window') and tw.Binary_tree_window and tw.Binary_tree_window.isVisible(): return tw.Binary_tree_window
            if hasattr(tw,
                       'Huffman_tree_window') and tw.Huffman_tree_window and tw.Huffman_tree_window.isVisible(): return tw.Huffman_tree_window

        return None

    # 【核心逻辑 2】本地执行 DSL，不走 AI
    def execute_local_dsl(self, dsl_text):
        """在本地执行 DSL 指令，不经过 AI"""
        print(f"DEBUG: 检测到本地指令: {dsl_text}")  # 调试信息
        viz = self.get_active_visualizer()

        if not viz:
            self.show_message("系统",
                              "⚠️ 未检测到激活的可视化窗口。<br>请先在主界面打开具体的数据结构（如队列、栈），然后再输入指令。")
            return

        try:
            self.show_message("系统", f"正在本地执行指令: {dsl_text}")
            handler = DSLHandler(viz)
            # flag=0 表示启用动画
            result = handler.execute_script(dsl_text, flag=0)

            if result and result != "执行成功":
                self.show_message("系统", f"执行结果: {result}")
            else:
                self.show_message("系统", "✅ 指令已执行")
        except Exception as e:
            traceback.print_exc()
            self.show_message("系统", f"❌ 执行出错: {str(e)}")

    def send_question(self):
        question = self.question_input.text().strip()
        if not question: return

        self.show_message("你", question)
        self.question_input.clear()

        # === 优先检测是否为 DSL 指令 ===
        # 如果是 ENQUEUE:8，这里会返回 True
        if self.check_is_dsl(question):
            self.execute_local_dsl(question)
            return

        # === 只有不是指令时，才发送给 AI ===
        print(f"DEBUG: 未识别为指令，准备发送 AI: {question}")
        if not self.qianwen_api:
            self.show_message("系统", "API 初始化失败")
            return

        self.send_btn.setEnabled(False)
        self.show_thinking_message()

        prompt = f"问题：{question}"
        self.ai_thread = AIAssistantThread(self.qianwen_api, prompt)
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.start()

    def show_thinking_message(self):
        self.chat_display.append("<div style='color: #757575; font-style: italic;'>燕小北正在思考...</div>")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def handle_ai_response(self, response):
        self.show_message("燕小北", response)
        self.send_btn.setEnabled(True)

        # 增强功能：如果 AI 返回的内容纯粹是 DSL 指令（例如用户让 AI 生成代码），也自动执行
        if self.check_is_dsl(response):
            self.show_message("系统", "检测到 AI 生成了 DSL 指令，正在自动执行...")
            self.execute_local_dsl(response)

    def show_message(self, sender, message):
        color = "#1565c0" if sender == "燕小北" else "#2e7d32"
        if sender == "系统": color = "#d32f2f"

        formatted_msg = f"<div style='margin-bottom: 10px;'><b style='color: {color};'>{sender}:</b><br>{message}</div>"
        self.chat_display.append(formatted_msg)
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
        adjust_window_to_screen(self, 0.5, 0.8)  # 宽度占屏幕50%，高度占80%
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

        # 按钮布局
        button_layout1 = QHBoxLayout()
        button_layout1.setSpacing(30)
        button_layout1.setAlignment(Qt.AlignCenter)

        button_layout2 = QHBoxLayout()
        button_layout2.setSpacing(50)
        button_layout2.setAlignment(Qt.AlignCenter)

        # 统一样式
        btn_style = """
            QPushButton {
                background-color: rgba(60, 130, 255, 0.8);
                color: white;
                border-radius: 10px;
                border: none;
                font-family: SimHei;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(60, 130, 255, 1.0);
                transform: scale(1.05);
            }
        """

        self.button_stack = QPushButton("栈 (Stack)")
        self.button_stack.setMinimumSize(150, 60)
        self.button_stack.setStyleSheet(btn_style)
        self.button_stack.clicked.connect(self.on_button_stack_clicked)
        button_layout1.addWidget(self.button_stack)

        self.button_sequencelist = QPushButton("顺序表 (SeqList)")
        self.button_sequencelist.setMinimumSize(150, 60)
        self.button_sequencelist.setStyleSheet(btn_style)
        self.button_sequencelist.clicked.connect(self.on_button_sequencelist_clicked)
        button_layout1.addWidget(self.button_sequencelist)

        self.button_linkedlist = QPushButton("链表 (LinkedList)")
        self.button_linkedlist.setMinimumSize(150, 60)
        self.button_linkedlist.setStyleSheet(btn_style)
        self.button_linkedlist.clicked.connect(self.on_button_linkedlist_clicked)
        button_layout1.addWidget(self.button_linkedlist)

        # 新增：队列按钮
        self.button_queue = QPushButton("队列 (Queue)")
        self.button_queue.setMinimumSize(150, 60)
        self.button_queue.setStyleSheet(btn_style)
        self.button_queue.clicked.connect(self.on_button_queue_clicked)
        button_layout1.addWidget(self.button_queue)

        # 返回按钮
        self.button_return = QPushButton("返回主界面")
        self.button_return.setMinimumSize(150, 60)
        self.button_return.setStyleSheet(btn_style)
        self.button_return.clicked.connect(self.on_button_return_clicked)
        button_layout2.addWidget(self.button_return)

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

    def on_button_queue_clicked(self):
        self.play_click_sound()
        self.go_to_queue()

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

    def go_to_queue(self):
        try:
            self.queue_window = QueueVisualizer(self.mainwindow, self)
            self.queue_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"出错: {e}")
            print(e)

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
        adjust_window_to_screen(self, 0.5, 0.8)
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
        button_layout1.addWidget(self.button_BST)

        self.button_AVL = QPushButton("AVL树")
        self.button_AVL.setMinimumSize(150, 60)
        self.button_AVL.setFont(QFont("SimHei", 12))
        self.button_AVL.setStyleSheet("""
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
        self.button_AVL.clicked.connect(self.on_button_AVL_clicked)
        # 添加到第二行或其他合适位置
        button_layout1.addWidget(self.button_AVL)


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

    def on_button_AVL_clicked(self):
        self.play_click_sound()
        self.go_to_AVL()

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

    def go_to_AVL(self):
        try:
            self.AVL_window = AVLTreeVisualizer(self.mainwindow, self)
            self.AVL_window.show()
            self.hide()
            print("AVL树可视化工具启动成功")
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
    # --- 新增：启用高分屏缩放支持 ---
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    # -----------------------------
    app = QApplication(sys.argv)
    window = MainWindow()
    ai_window = AI_Floating_Window()
    window.show()
    ai_window.show()
    sys.exit(app.exec_())