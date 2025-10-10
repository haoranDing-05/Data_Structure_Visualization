import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame,QMessageBox)
from PyQt5.QtCore import Qt,QUrl
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtMultimedia import QSoundEffect  # 用于音效播放

import traceback

from model import SequenceList

from visualization import StackVisualizer, SequenceListVisualizer


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
        self.set_background_image(central_frame, "C:/Users/dhrnb/Desktop/DataStructureVisualization/微信图片_20250922183759_13_117.jpg")  # 替换为你的背景图片路径

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
        # 美化按钮样式（修改12）
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

    def init_sound_effects(self):
        self.click_sound=QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("C:/Users/dhrnb/Desktop/DataStructureVisualization/button_click.wav"))
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
        self.sequential_window = SequentialStructureWindow(self)  # 传入self
        self.sequential_window.show()
        self.hide()

    def on_button2_clicked(self):
        """第二个按钮点击事件处理"""
        print("button2 is clicked")
        self.play_click_sound()  # 播放音效
        # 这里可以添加树形结构界面的逻辑
        #QMessageBox.information(self, "提示", "您点击了树形结构按钮")

    # 添加背景图片的方法（修改14）
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


class SequentialStructureWindow(QMainWindow):
    def __init__(self,mainwindow):
        super().__init__()   #调用其父类（QMainWindow）的构造方法

        self.mainwindow=mainwindow

        self.init_sound_effects()   #初始化音效

        #设置窗口的标题和窗口的大小
        self.setWindowTitle("顺序结构可视化")
        self.setGeometry(100,100,640,852)

        #添加带背景图片的中心组件
        central_frame=QFrame()     #创建组件
        self.setCentralWidget(central_frame)
        self.set_background_image(central_frame,"C:/Users/dhrnb/Desktop/DataStructureVisualization/微信图片_20250922183759_13_117.jpg")


        main_layout=QVBoxLayout(central_frame)

        #添加标题 标签
        title_label=QLabel("顺序结构")
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

        # 添加按钮布局（水平布局）
        button_layout = QHBoxLayout()
        button_layout.setSpacing(50)  # 增大按钮间距
        button_layout.setAlignment(Qt.AlignCenter)  # 按钮居中


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
        button_layout.addWidget(self.button_return)



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
        button_layout.addWidget(self.button_stack)



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
        button_layout.addWidget(self.button_sequencelist)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)







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


    def back_to_main(self):
        self.mainwindow.show()  # 显示原主窗口
        self.close()  # 关闭子窗口

    def go_to_stack(self):
        try:

            self.stack_window = StackVisualizer(self.mainwindow)
            self.stack_window.show()
            self.hide()
            print("栈可视化工具启动成功")

        except Exception as e:
            print(f"应用程序错误: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"打开栈可视化工具时出错: {e}")

    def go_to_sequencelist(self):
        try:
            self.sequencelist_window=SequenceListVisualizer(self.mainwindow)
            self.sequencelist_window.show()
            self.hide()
            print("顺序表可视化工具启动成功")
        except Exception as e:
            print(f"应用程序错误:{e}")
            traceback.print_exc()
            QMessageBox.critical(self,"错误",f"打开顺序表可视化工具时出错:{e}")


    def init_sound_effects(self):
        self.click_sound=QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("C:/Users/dhrnb/Desktop/DataStructureVisualization/button_click.wav"))
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
    window.show()

    # 进入应用主循环
    sys.exit(app.exec_())

