import sys
import traceback
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QUrl,QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush,QPolygonF
from PyQt5.QtMultimedia import QSoundEffect
from model import Stack, SequenceList, LinkedList


class VisualArea(QWidget):
    """通用数据结构可视化组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(500)
        self.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")

        # 核心数据
        self.data_structure = None  # 待可视化的数据结构实例
        self.highlighted_index = -1  # 高亮索引

        # 样式参数
        self.cell_width = 120
        self.cell_height = 40
        self.cell_spacing = 5
        self.tree_level_spacing = 80  # 树的层级间距
        self.tree_node_spacing = 40  # 树的节点间距

    def set_data_structure(self, ds):
        """设置要可视化的数据结构"""
        self.data_structure = ds
        self.update()

    def update_visualization(self, ds=None, highlighted_index=-1):
        """更新可视化状态"""
        if ds is not None:
            self.data_structure = ds
        self.highlighted_index = highlighted_index
        self.update()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            if not self.data_structure:
                painter.setFont(QFont("Arial", 12))
                painter.drawText(self.rect(), Qt.AlignCenter, "可视化区域准备就绪")
                return

            # 根据数据结构类型选择绘制方法
            if isinstance(self.data_structure, (Stack, SequenceList)):
                self._draw_linear_structure(painter)
            elif isinstance(self.data_structure, LinkedList):
                self._draw_linked_list(painter)
            else:
                painter.drawText(self.rect(), Qt.AlignCenter, "不支持的结构类型")

        except Exception as e:
            print(f"绘图错误: {e}")
            traceback.print_exc()

    def _draw_linear_structure(self, painter):
        """绘制线性结构（栈/顺序表/链表）"""
        ds = self.data_structure
        length = ds.length()
        if length == 0:
            painter.setFont(QFont("Arial", 12, QFont.Italic))
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "空结构")
            return

        # 计算起始位置
        area_width = self.width()
        area_height = self.height()
        total_width = length * self.cell_width + (length - 1) * self.cell_spacing
        start_x = max(10, (area_width - total_width) // 2)  # 水平居中
        start_y = (area_height - self.cell_height) // 2  # 垂直居中

        # 判断是否为栈
        is_stack = isinstance(ds, Stack)

        # 绘制元素
        for i in range(length):
            if is_stack:
                # 栈保持纵向绘制
                x_pos = start_x
                y_pos = start_y - i * (self.cell_height + self.cell_spacing)
            else:
                # 线性表横向绘制
                x_pos = start_x + i * (self.cell_width + self.cell_spacing)
                y_pos = start_y

            # 超出边界处理
            if is_stack:    #栈的超出边界处理
                if y_pos < 20:
                    painter.setPen(QPen(QColor(255, 0, 0), 1))
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(start_x, 10, self.cell_width, 15,
                                     Qt.AlignCenter, f"...还有{length - i}个元素未显示")
                    break
            else:           #顺序表和链表的超出边界处理
                if x_pos + self.cell_width > area_width - 10:
                    painter.setPen(QPen(QColor(255, 0, 0), 1))
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(area_width - 150, start_y + self.cell_height + 20,
                                     140, 15, Qt.AlignRight,
                                     f"...还有{length - i}个元素未显示")
                    break

            # 设置颜色
            if i == self.highlighted_index:
                painter.setBrush(QBrush(QColor(255, 215, 0)))  # 高亮色
            else:
                painter.setBrush(QBrush(QColor(200, 230, 255)))  # 正常色

            # 绘制矩形框
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawRect(x_pos, y_pos, self.cell_width, self.cell_height)


            # 绘制元素值
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            try:
                value = str(ds[i])
                if len(value) > 15:
                    value = value[:15] + "..."
                painter.drawText(x_pos, y_pos, self.cell_width, self.cell_height,
                                 Qt.AlignCenter, value)
            except (IndexError, TypeError) as e:
                print(f"绘制元素错误: {e}")
                break

        # 绘制结构标识
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Arial", 9))

        if is_stack:
            # 栈的可视化绘制组件
            if length > 0:
                top_index = min(length - 1,
                                (start_y - 20) // (self.cell_height + self.cell_spacing))
                top_y = start_y - top_index * (self.cell_height + self.cell_spacing) - 20
                painter.drawText(start_x, top_y, self.cell_width, 20,
                                 Qt.AlignCenter, "↑ 栈顶 Top")

                bottom_y = start_y + self.cell_height + 5
                painter.drawText(start_x, bottom_y, self.cell_width, 20,
                                 Qt.AlignCenter, "↓ 栈底 Bottom")

            painter.drawText(10, 10, 200, 20, Qt.AlignLeft, f"栈大小: {length}")
        else:
            # 顺序表的可视化绘制组件
            painter.drawText(start_x - 30, start_y + self.cell_height // 2,
                             25, 20, Qt.AlignCenter, "头")
            last_x = start_x + (length - 1) * (self.cell_width + self.cell_spacing)
            painter.drawText(last_x + self.cell_width + 5, start_y + self.cell_height // 2,
                             25, 20, Qt.AlignCenter, "尾")

            # 显示线性表长度
            painter.drawText(10, 10, 200, 20, Qt.AlignLeft, f"长度: {length} 个元素")

    def drawArrow(self, painter, start_x, start_y, end_x, end_y):
        """绘制从起点到终点的带箭头的线"""

        # 设置线条样式
        pen = QPen(Qt.blue, 2)
        painter.setPen(pen)

        # 绘制主线
        painter.drawLine(start_x, start_y, end_x, end_y)

        # 计算箭头角度
        import math
        angle = math.atan2(end_y - start_y, end_x - start_x) * 180 / math.pi

        # 设置箭头大小
        arrow_size = 10

        # 计算箭头两个点的位置
        arrow_p1 = QPointF(
            end_x - arrow_size * math.cos(math.radians(angle + 30)),
            end_y - arrow_size * math.sin(math.radians(angle + 30))
        )
        arrow_p2 = QPointF(
            end_x - arrow_size * math.cos(math.radians(angle - 30)),
            end_y - arrow_size * math.sin(math.radians(angle - 30))
        )

        # 绘制箭头
        painter.setBrush(QBrush(Qt.blue))
        arrow_head = QPolygonF()
        arrow_head.append(QPointF(end_x, end_y))
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)
        painter.drawPolygon(arrow_head)

    def _draw_linked_list(self, painter):
        """绘制链表结构，每个节点为矩形，节点间用箭头连接"""
        ll = self.data_structure
        length = ll.length()
        if length == 0:
            painter.setFont(QFont("Arial", 12, QFont.Italic))
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "空链表")
            return

        # 计算起始位置
        area_width = self.width()
        area_height = self.height()
        total_width = length * self.cell_width + (length - 1) * (self.cell_spacing + 30)  # 额外留箭头空间
        start_x = max(10, (area_width - total_width) // 2)  # 水平居中
        start_y = (area_height - self.cell_height) // 2  # 垂直居中

        # 绘制每个节点
        node_positions = []  # 存储每个节点的位置，用于绘制箭头
        for i in range(length):
            x_pos = start_x + i * (self.cell_width + self.cell_spacing + 30)
            y_pos = start_y

            # 超出边界处理
            if x_pos + self.cell_width > area_width - 10:
                painter.setPen(QPen(QColor(255, 0, 0), 1))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(area_width - 150, start_y + self.cell_height + 20,
                                 140, 15, Qt.AlignRight,
                                 f"...还有{length - i}个节点未显示")
                break

            # 保存节点位置
            node_positions.append((x_pos, y_pos))

            # 设置颜色
            if i == self.highlighted_index:
                painter.setBrush(QBrush(QColor(255, 215, 0)))  # 高亮色
            else:
                painter.setBrush(QBrush(QColor(200, 230, 255)))  # 正常色

            # 绘制节点矩形
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawRect(x_pos, y_pos, self.cell_width, self.cell_height)

            # 绘制节点值
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            try:
                value = str(ll[i])
                if len(value) > 15:
                    value = value[:15] + "..."
                painter.drawText(x_pos, y_pos, self.cell_width, self.cell_height,
                                 Qt.AlignCenter, value)
            except (IndexError, TypeError) as e:
                print(f"绘制元素错误: {e}")
                break

        # 绘制节点间的箭头
        for i in range(len(node_positions) - 1):
            x1, y1 = node_positions[i]
            x2, y2 = node_positions[i + 1]

            # 箭头从当前节点右侧中间指向下一节点左侧中间
            start_arrow_x = x1 + self.cell_width
            start_arrow_y = y1 + self.cell_height // 2
            end_arrow_x = x2
            end_arrow_y = y2 + self.cell_height // 2

            self.drawArrow(painter, start_arrow_x, start_arrow_y, end_arrow_x, end_arrow_y)

        # 绘制头节点标识
        if node_positions:
            first_x, first_y = node_positions[0]
            painter.drawText(first_x, first_y - 20, self.cell_width, 20,
                             Qt.AlignCenter, "头节点 (Head)")

        # 绘制链表长度
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(10, 10, 200, 20, Qt.AlignLeft, f"链表长度: {length} 个节点")


class BaseVisualizer(QWidget):
    """数据结构可视化父类"""

    def __init__(self, main_window=None, title="数据结构可视化工具"):
        super().__init__()
        # 保存主窗口引用
        self.main_window = main_window
        # 数据结构实例（由子类初始化）
        self.data_structure = None
        # 动画相关
        self.animation_speed = 500
        self.animating = False
        self.current_operation = None
        self.operation_data = None

        # 可视化参数
        self.highlighted_index = -1
        self.title = title

        self.init_ui()
        self.init_sound_effects()

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(
            QUrl.fromLocalFile("C:/Users/dhrnb/Desktop/DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)

    def play_click_sound(self):
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()
        else:
            QMessageBox.warning(self, "提示", "未设置点击音效文件")

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 操作区域
        control_group = QGroupBox(f"{self.title.split('(')[0].strip()}操作")
        control_layout = QVBoxLayout()

        # 输入行和按钮行由子类实现
        control_layout.addLayout(self._create_input_layout())
        control_layout.addLayout(self._create_button_layout())

        # 返回按钮布局
        button_return_layout = QHBoxLayout()
        self.button_return_main = QPushButton("返回主界面")
        self.button_return_main.setMinimumSize(150, 40)
        self.button_return_main.setFont(QFont("SimHei", 10))
        self.button_return_main.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 130, 255, 0.8);
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(60, 130, 255, 1.0);
            }
        """)
        self.button_return_main.clicked.connect(self.on_button_return_main_clicked)
        button_return_layout.addWidget(self.button_return_main)
        button_return_layout.addStretch()

        # 速度控制
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("动画速度:"))
        self.speed_slider = QLineEdit(str(self.animation_speed))
        self.speed_slider.setMaximumWidth(80)
        self.speed_slider.setToolTip("单位: 毫秒 (100-2000)")
        self.speed_slider.returnPressed.connect(self.update_speed)

        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(QLabel("毫秒"))
        speed_layout.addStretch()

        control_layout.addLayout(button_return_layout)
        control_layout.addLayout(speed_layout)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # 可视化区域
        visual_group = QGroupBox(f"{self.title.split('(')[0].strip()}可视化")
        visual_layout = QVBoxLayout()
        self.visual_area = VisualArea(self)  # 使用通用可视化组件
        visual_layout.addWidget(self.visual_area)
        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)

        # 状态信息
        self.status_label = QLabel("就绪 - 结构为空")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333; 
                padding: 8px; 
                background-color: #e3f2fd; 
                border: 1px solid #90caf9;
                border-radius: 4px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        self.setWindowTitle(self.title)
        self.resize(700, 600)

        # 初始更新
        self.update_display()

    def _create_input_layout(self):
        """创建输入布局，由子类实现"""
        raise NotImplementedError("子类必须实现_create_input_layout方法")

    def _create_button_layout(self):
        """创建按钮布局，由子类实现"""
        raise NotImplementedError("子类必须实现_create_button_layout方法")

    def on_button_return_main_clicked(self):
        self.play_click_sound()
        self.back_to_main()

    def back_to_main(self):
        if self.main_window:
            self.main_window.show()
        self.close()

    def update_display(self):
        try:
            self.visual_area.update_visualization(self.data_structure, self.highlighted_index)

            if self.data_structure.is_empty():
                self.status_label.setText(f"{self.title.split('(')[0].strip()}状态: 空")
            else:
                self._update_status_text()
        except Exception as e:
            print(f"更新显示错误: {e}")

    def _update_status_text(self):
        """更新状态文本，由子类实现"""
        raise NotImplementedError("子类必须实现_update_status_text方法")

    def update_speed(self):
        try:
            speed = int(self.speed_slider.text())
            if 100 <= speed <= 2000:
                self.animation_speed = speed
                self.status_label.setText(f"动画速度已设置为 {speed} 毫秒")
                QTimer.singleShot(2000, lambda: self.update_display())
            else:
                QMessageBox.warning(self, "无效值", "请输入100-2000之间的数值")
                self.speed_slider.setText(str(self.animation_speed))
        except ValueError:
            QMessageBox.warning(self, "无效输入", "请输入有效的数字")
            self.speed_slider.setText(str(self.animation_speed))

    def set_buttons_enabled(self, enabled):
        """设置按钮状态，由子类实现具体按钮"""
        raise NotImplementedError("子类必须实现set_buttons_enabled方法")

    def clear_highlight(self):
        self.highlighted_index = -1
        self.update_display()

    def execute_operation(self):
        """执行具体操作，由子类实现"""
        raise NotImplementedError("子类必须实现execute_operation方法")


class StackVisualizer(BaseVisualizer):
    def __init__(self, main_window=None):
        super().__init__(main_window, "栈 (Stack) 可视化工具")
        # 初始化栈
        self.data_structure = Stack()
        self.visual_area.set_data_structure(self.data_structure)  # 设置栈为可视化数据结构

    def _create_input_layout(self):
        input_layout = QHBoxLayout()
        self.push_input = QLineEdit()
        self.push_input.setPlaceholderText("输入要入栈的元素...")
        self.push_input.returnPressed.connect(self.handle_push)

        self.push_btn = QPushButton("入栈 (Push)")
        self.push_btn.clicked.connect(self.handle_push)
        self.push_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        input_layout.addWidget(QLabel("元素:"))
        input_layout.addWidget(self.push_input)
        input_layout.addWidget(self.push_btn)
        input_layout.addStretch()
        return input_layout

    def _create_button_layout(self):
        button_layout = QHBoxLayout()
        self.pop_btn = QPushButton("出栈 (Pop)")
        self.pop_btn.clicked.connect(self.handle_pop)
        self.pop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")

        self.peek_btn = QPushButton("查看栈顶 (Peek)")
        self.peek_btn.clicked.connect(self.handle_peek)
        self.peek_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")

        self.clear_btn = QPushButton("清空栈")
        self.clear_btn.clicked.connect(self.handle_clear)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")

        button_layout.addWidget(self.pop_btn)
        button_layout.addWidget(self.peek_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        return button_layout

    def _update_status_text(self):
        self.status_label.setText(f"栈状态: {self.data_structure.length()} 个元素, 栈顶: {self.data_structure.peek()}")

    def handle_push(self):
        self.play_click_sound()
        if self.animating:
            return

        value = self.push_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要入栈的元素")
            self.push_input.setFocus()
            return

        if len(value) > 50:
            value = value[:50]
            self.push_input.setText(value)

        self.current_operation = "push"
        self.operation_data = value
        self.animating = True

        self.highlighted_index = self.data_structure.length()
        self.status_label.setText(f"正在入栈: {value}...")
        self.update_display()

        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_pop(self):
        self.play_click_sound()
        if self.animating:
            return

        if self.data_structure.is_empty():
            QMessageBox.warning(self, "操作错误", "栈为空，无法出栈")
            return

        self.current_operation = "pop"
        self.operation_data = self.data_structure.peek()
        self.animating = True

        self.highlighted_index = self.data_structure.length() - 1
        self.status_label.setText(f"正在出栈: {self.operation_data}...")
        self.update_display()

        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_peek(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.information(self, "栈顶元素", "栈为空，没有元素")
            return

        top_value = self.data_structure.peek()
        self.highlighted_index = self.data_structure.length() - 1
        self.status_label.setText(f"栈顶元素: {top_value}")
        self.update_display()

        QTimer.singleShot(2000, self.clear_highlight)

    def handle_clear(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.information(self, "提示", "栈已经是空的")
            return

        reply = QMessageBox.question(self, "确认清空",
                                     "确定要清空栈中的所有元素吗？",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.data_structure.clear()
            self.highlighted_index = -1
            self.status_label.setText("栈已清空")
            self.update_display()

    def set_buttons_enabled(self, enabled):
        self.push_btn.setEnabled(enabled)
        self.pop_btn.setEnabled(enabled)
        self.peek_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.push_input.setEnabled(enabled)

    def execute_operation(self):
        try:
            if self.current_operation == "push":
                self.data_structure.push(self.operation_data)
                self.status_label.setText(f"已入栈: {self.operation_data}")
                self.push_input.clear()

            elif self.current_operation == "pop":
                popped_value = self.data_structure.pop()
                self.status_label.setText(f"已出栈: {popped_value}")

            self.animating = False
            self.highlighted_index = -1
            self.set_buttons_enabled(True)
            self.update_display()

        except Exception as e:
            print(f"操作执行错误: {e}")
            self.status_label.setText(f"错误: {str(e)}")
            self.animating = False
            self.highlighted_index = -1
            self.set_buttons_enabled(True)
            self.update_display()


class SequenceListVisualizer(BaseVisualizer):
    def __init__(self, main_window=None):
        super().__init__(main_window, "顺序表 (SequenceList) 可视化工具")
        # 初始化顺序表
        self.data_structure = SequenceList()
        self.visual_area.set_data_structure(self.data_structure)
        self.current_operation = None
        self.operation_data = None

    def _create_input_layout(self):
        # 主输入布局
        main_input_layout = QVBoxLayout()

        # 插入操作布局
        insert_layout = QHBoxLayout()
        self.insert_input_val = QLineEdit()
        self.insert_input_val.setPlaceholderText("输入元素值")
        self.insert_input_pos = QLineEdit()
        self.insert_input_pos.setPlaceholderText("输入位置")
        self.insert_btn = QPushButton("插入(Insert)")
        self.insert_btn.clicked.connect(self.handle_insert)
        self.insert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        insert_layout.addWidget(QLabel("插入元素:"))
        insert_layout.addWidget(self.insert_input_val)
        insert_layout.addWidget(QLabel("位置:"))
        insert_layout.addWidget(self.insert_input_pos)
        insert_layout.addWidget(self.insert_btn)

        # 修改操作布局
        modify_layout = QHBoxLayout()
        self.modify_input_val = QLineEdit()
        self.modify_input_val.setPlaceholderText("新元素值")
        self.modify_input_pos = QLineEdit()
        self.modify_input_pos.setPlaceholderText("修改位置")
        self.modify_btn = QPushButton("修改(Update)")
        self.modify_btn.clicked.connect(self.handle_modify)
        self.modify_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")

        modify_layout.addWidget(QLabel("修改元素:"))
        modify_layout.addWidget(self.modify_input_val)
        modify_layout.addWidget(QLabel("位置:"))
        modify_layout.addWidget(self.modify_input_pos)
        modify_layout.addWidget(self.modify_btn)

        # 查找/删除操作布局
        search_del_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入查找/删除的值")
        self.search_btn = QPushButton("查找(Find)")
        self.search_btn.clicked.connect(self.handle_search)
        self.search_btn.setStyleSheet("QPushButton { background-color: #FFC107; color: black; }")
        self.delete_val_btn = QPushButton("按值删除")
        self.delete_val_btn.clicked.connect(self.handle_delete_by_value)
        self.delete_val_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")

        search_del_layout.addWidget(QLabel("值操作:"))
        search_del_layout.addWidget(self.search_input)
        search_del_layout.addWidget(self.search_btn)
        search_del_layout.addWidget(self.delete_val_btn)

        # 按位置删除布局
        del_pos_layout = QHBoxLayout()
        self.delete_pos_input = QLineEdit()
        self.delete_pos_input.setPlaceholderText("输入删除位置")
        self.delete_pos_btn = QPushButton("按位置删除")
        self.delete_pos_btn.clicked.connect(self.handle_delete_by_position)
        self.delete_pos_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")

        del_pos_layout.addWidget(QLabel("删除位置:"))
        del_pos_layout.addWidget(self.delete_pos_input)
        del_pos_layout.addWidget(self.delete_pos_btn)

        # 添加所有子布局到主布局
        main_input_layout.addLayout(insert_layout)
        main_input_layout.addLayout(modify_layout)
        main_input_layout.addLayout(search_del_layout)
        main_input_layout.addLayout(del_pos_layout)

        return main_input_layout

    def _create_button_layout(self):
        button_layout = QHBoxLayout()

        self.get_btn = QPushButton("获取元素(Get)")
        self.get_btn.clicked.connect(self.handle_get)
        self.get_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; }")

        self.clear_btn = QPushButton("清空(Clear)")
        self.clear_btn.clicked.connect(self.handle_clear)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")

        self.length_btn = QPushButton("长度(Length)")
        self.length_btn.clicked.connect(self.handle_length)
        self.length_btn.setStyleSheet("QPushButton { background-color: #795548; color: white; }")

        button_layout.addWidget(self.get_btn)
        button_layout.addWidget(self.length_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        return button_layout

    def handle_insert(self):
        self.play_click_sound()
        if self.animating:
            return

        value = self.insert_input_val.text().strip()
        pos_text = self.insert_input_pos.text().strip()

        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要插入的元素")
            self.insert_input_val.setFocus()
            return

        if not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入要插入的位置")
            self.insert_input_pos.setFocus()
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            self.insert_input_pos.clear()
            return

        length = self.data_structure.length()
        if pos < 0 or pos > length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length}之间")
            return

        if len(value) > 50:
            value = value[:50]
            self.insert_input_val.setText(value)

        self.current_operation = "insert"
        self.operation_data = (value, pos)
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在插入: {value} 到位置 {pos}...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_delete_by_position(self):
        self.play_click_sound()
        if self.animating or self.data_structure.is_empty():
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "操作错误", "顺序表为空，无法删除")
            return

        pos_text = self.delete_pos_input.text().strip()
        if not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入删除位置")
            self.delete_pos_input.setFocus()
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            self.delete_pos_input.clear()
            return

        length = self.data_structure.length()
        if pos < 0 or pos >= length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length - 1}之间")
            return

        self.current_operation = "delete_by_position"
        self.operation_data = pos
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在删除位置 {pos} 的元素...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_delete_by_value(self):
        self.play_click_sound()
        if self.animating or self.data_structure.is_empty():
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "操作错误", "顺序表为空，无法删除")
            return

        value = self.search_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要删除的值")
            self.search_input.setFocus()
            return

        index = self.data_structure.locate(value)
        if index == -1:
            QMessageBox.information(self, "未找到", f"未找到元素: {value}")
            return

        self.current_operation = "delete_by_value"
        self.operation_data = index
        self.animating = True
        self.highlighted_index = index
        self.status_label.setText(f"正在删除值为 {value} 的元素...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_modify(self):
        self.play_click_sound()
        if self.animating or self.data_structure.is_empty():
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "操作错误", "顺序表为空，无法修改")
            return

        value = self.modify_input_val.text().strip()
        pos_text = self.modify_input_pos.text().strip()

        if not value:
            QMessageBox.warning(self, "输入错误", "请输入新元素值")
            self.modify_input_val.setFocus()
            return

        if not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入修改位置")
            self.modify_input_pos.setFocus()
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            self.modify_input_pos.clear()
            return

        length = self.data_structure.length()
        if pos < 0 or pos >= length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length - 1}之间")
            return

        self.current_operation = "modify"
        self.operation_data = (value, pos)
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在修改位置 {pos} 的元素...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_search(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.warning(self, "操作错误", "顺序表为空，无法查找")
            return

        value = self.search_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要查找的值")
            self.search_input.setFocus()
            return

        index = self.data_structure.locate(value)
        if index != -1:
            self.highlighted_index = index
            self.status_label.setText(f"找到元素 {value} 在位置 {index}")
            self.update_display()
            QTimer.singleShot(2000, self.clear_highlight)
        else:
            self.status_label.setText(f"未找到元素: {value}")
            self.update_display()

    def handle_get(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.warning(self, "操作错误", "顺序表为空，无法获取元素")
            return

        pos_text = self.modify_input_pos.text().strip()  # 复用修改的位置输入
        if not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入要获取元素的位置")
            self.modify_input_pos.setFocus()
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            self.modify_input_pos.clear()
            return

        length = self.data_structure.length()
        if pos < 0 or pos >= length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length - 1}之间")
            return

        value = self.data_structure.get(pos)
        self.highlighted_index = pos
        self.status_label.setText(f"位置 {pos} 的元素是: {value}")
        self.update_display()
        QTimer.singleShot(2000, self.clear_highlight)

    def handle_clear(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.information(self, "提示", "顺序表已经是空的")
            return

        reply = QMessageBox.question(self, "确认清空",
                                     "确定要清空顺序表中的所有元素吗？",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.data_structure.clear()
            self.highlighted_index = -1
            self.status_label.setText("顺序表已清空")
            self.update_display()

    def handle_length(self):
        self.play_click_sound()
        length = self.data_structure.length()
        self.status_label.setText(f"顺序表长度: {length} 个元素")
        self.update_display()

    def _update_status_text(self):
        length = self.data_structure.length()
        if length > 0:
            self.status_label.setText(f"顺序表状态: {length} 个元素")
        else:
            self.status_label.setText("顺序表状态: 空")

    def set_buttons_enabled(self, enabled):
        # 所有按钮和输入框的启用状态控制
        self.insert_btn.setEnabled(enabled)
        self.modify_btn.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)
        self.delete_val_btn.setEnabled(enabled)
        self.delete_pos_btn.setEnabled(enabled)
        self.get_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.length_btn.setEnabled(enabled)

        self.insert_input_val.setEnabled(enabled)
        self.insert_input_pos.setEnabled(enabled)
        self.modify_input_val.setEnabled(enabled)
        self.modify_input_pos.setEnabled(enabled)
        self.search_input.setEnabled(enabled)
        self.delete_pos_input.setEnabled(enabled)

    def execute_operation(self):
        try:
            if self.current_operation == "insert":
                value, pos = self.operation_data
                self.data_structure.insert(pos, value)
                self.status_label.setText(f"已插入: {value} 到位置 {pos}")
                self.insert_input_val.clear()
                self.insert_input_pos.clear()

            elif self.current_operation == "delete_by_position":
                pos = self.operation_data
                deleted_value = self.data_structure.remove(pos)
                self.status_label.setText(f"已删除位置 {pos} 的元素: {deleted_value}")
                self.delete_pos_input.clear()

            elif self.current_operation == "delete_by_value":
                pos = self.operation_data
                deleted_value = self.data_structure.remove(pos)
                self.status_label.setText(f"已删除元素: {deleted_value} (位置 {pos})")
                self.search_input.clear()

            elif self.current_operation == "modify":
                value, pos = self.operation_data
                old_value = self.data_structure.get(pos)
                self.data_structure.set(pos, value)
                self.status_label.setText(f"已修改位置 {pos}: {old_value} → {value}")
                self.modify_input_val.clear()
                self.modify_input_pos.clear()

            self.animating = False
            self.highlighted_index = -1
            self.set_buttons_enabled(True)
            self.update_display()

        except Exception as e:
            print(f"操作执行错误: {e}")
            self.status_label.setText(f"错误: {str(e)}")
            self.animating = False
            self.highlighted_index = -1
            self.set_buttons_enabled(True)
            self.update_display()

class LinkedListVisualizer(BaseVisualizer):
    def __init__(self, main_window=None):
        super().__init__(main_window, "链表 (LinkedList) 可视化工具")
        # 初始化链表
        self.data_structure = LinkedList()
        self.visual_area.set_data_structure(self.data_structure)
        self.current_operation = None
        self.operation_data = None

    def _create_input_layout(self):
        # 主输入布局
        main_input_layout = QVBoxLayout()

        # 头部插入布局
        head_insert_layout = QHBoxLayout()
        self.head_insert_input = QLineEdit()
        self.head_insert_input.setPlaceholderText("输入元素值")
        self.head_insert_btn = QPushButton("头部插入")
        self.head_insert_btn.clicked.connect(self.handle_head_insert)
        self.head_insert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        head_insert_layout.addWidget(QLabel("头部插入:"))
        head_insert_layout.addWidget(self.head_insert_input)
        head_insert_layout.addWidget(self.head_insert_btn)

        # 尾部插入布局
        tail_insert_layout = QHBoxLayout()
        self.tail_insert_input = QLineEdit()
        self.tail_insert_input.setPlaceholderText("输入元素值")
        self.tail_insert_btn = QPushButton("尾部插入")
        self.tail_insert_btn.clicked.connect(self.handle_tail_insert)
        self.tail_insert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        tail_insert_layout.addWidget(QLabel("尾部插入:"))
        tail_insert_layout.addWidget(self.tail_insert_input)
        tail_insert_layout.addWidget(self.tail_insert_btn)

        # 按位置插入布局
        pos_insert_layout = QHBoxLayout()
        self.pos_insert_val = QLineEdit()
        self.pos_insert_val.setPlaceholderText("元素值")
        self.pos_insert_pos = QLineEdit()
        self.pos_insert_pos.setPlaceholderText("位置")
        self.pos_insert_btn = QPushButton("按位置插入")
        self.pos_insert_btn.clicked.connect(self.handle_pos_insert)
        self.pos_insert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        pos_insert_layout.addWidget(QLabel("按位置插入:"))
        pos_insert_layout.addWidget(self.pos_insert_val)
        pos_insert_layout.addWidget(QLabel("位置:"))
        pos_insert_layout.addWidget(self.pos_insert_pos)
        pos_insert_layout.addWidget(self.pos_insert_btn)

        # 修改、查找布局
        modify_search_layout = QHBoxLayout()
        self.modify_val = QLineEdit()
        self.modify_val.setPlaceholderText("新值")
        self.modify_pos = QLineEdit()
        self.modify_pos.setPlaceholderText("位置")
        self.modify_btn = QPushButton("修改")
        self.modify_btn.clicked.connect(self.handle_modify)
        self.modify_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("查找值")
        self.search_btn = QPushButton("查找")
        self.search_btn.clicked.connect(self.handle_search)
        self.search_btn.setStyleSheet("QPushButton { background-color: #FFC107; color: black; }")

        modify_search_layout.addWidget(QLabel("修改:"))
        modify_search_layout.addWidget(self.modify_val)
        modify_search_layout.addWidget(QLabel("位置:"))
        modify_search_layout.addWidget(self.modify_pos)
        modify_search_layout.addWidget(self.modify_btn)
        modify_search_layout.addWidget(QLabel("查找:"))
        modify_search_layout.addWidget(self.search_input)
        modify_search_layout.addWidget(self.search_btn)

        # 删除布局
        delete_layout = QHBoxLayout()
        self.delete_pos = QLineEdit()
        self.delete_pos.setPlaceholderText("删除位置")
        self.delete_pos_btn = QPushButton("按位置删除")
        self.delete_pos_btn.clicked.connect(self.handle_delete_by_pos)
        self.delete_pos_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")

        self.delete_val = QLineEdit()
        self.delete_val.setPlaceholderText("删除值")
        self.delete_val_btn = QPushButton("按值删除")
        self.delete_val_btn.clicked.connect(self.handle_delete_by_val)
        self.delete_val_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")

        delete_layout.addWidget(QLabel("按位置删除:"))
        delete_layout.addWidget(self.delete_pos)
        delete_layout.addWidget(self.delete_pos_btn)
        delete_layout.addWidget(QLabel("按值删除:"))
        delete_layout.addWidget(self.delete_val)
        delete_layout.addWidget(self.delete_val_btn)

        # 添加所有子布局
        main_input_layout.addLayout(head_insert_layout)
        main_input_layout.addLayout(tail_insert_layout)
        main_input_layout.addLayout(pos_insert_layout)
        main_input_layout.addLayout(modify_search_layout)
        main_input_layout.addLayout(delete_layout)

        return main_input_layout

    def _create_button_layout(self):
        button_layout = QHBoxLayout()

        self.get_btn = QPushButton("获取元素")
        self.get_btn.clicked.connect(self.handle_get)
        self.get_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; }")

        self.clear_btn = QPushButton("清空链表")
        self.clear_btn.clicked.connect(self.handle_clear)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")

        self.length_btn = QPushButton("链表长度")
        self.length_btn.clicked.connect(self.handle_length)
        self.length_btn.setStyleSheet("QPushButton { background-color: #795548; color: white; }")

        button_layout.addWidget(self.get_btn)
        button_layout.addWidget(self.length_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        return button_layout

    def handle_head_insert(self):
        self.play_click_sound()
        if self.animating:
            return

        value = self.head_insert_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要插入的元素")
            return

        self.current_operation = "head_insert"
        self.operation_data = value
        self.animating = True
        self.highlighted_index = 0
        self.status_label.setText(f"正在头部插入: {value}...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_tail_insert(self):
        self.play_click_sound()
        if self.animating:
            return

        value = self.tail_insert_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要插入的元素")
            return

        pos = self.data_structure.length()
        self.current_operation = "tail_insert"
        self.operation_data = value
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在尾部插入: {value}...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_pos_insert(self):
        self.play_click_sound()
        if self.animating:
            return

        value = self.pos_insert_val.text().strip()
        pos_text = self.pos_insert_pos.text().strip()

        if not value or not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入元素值和位置")
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            return

        length = self.data_structure.length()
        if pos < 0 or pos > length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length}之间")
            return

        self.current_operation = "pos_insert"
        self.operation_data = (value, pos)
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在位置 {pos} 插入: {value}...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_delete_by_pos(self):
        self.play_click_sound()
        if self.animating or self.data_structure.is_empty():
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "操作错误", "链表为空，无法删除")
            return

        pos_text = self.delete_pos.text().strip()
        if not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入删除位置")
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            return

        length = self.data_structure.length()
        if pos < 0 or pos >= length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length-1}之间")
            return

        self.current_operation = "delete_by_pos"
        self.operation_data = pos
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在删除位置 {pos} 的元素...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_delete_by_val(self):
        self.play_click_sound()
        if self.animating or self.data_structure.is_empty():
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "操作错误", "链表为空，无法删除")
            return

        value = self.delete_val.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要删除的值")
            return

        index = self.data_structure.locate(value)
        if index == -1:
            QMessageBox.information(self, "未找到", f"未找到元素: {value}")
            return

        self.current_operation = "delete_by_val"
        self.operation_data = index
        self.animating = True
        self.highlighted_index = index
        self.status_label.setText(f"正在删除值为 {value} 的元素...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_modify(self):
        self.play_click_sound()
        if self.animating or self.data_structure.is_empty():
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "操作错误", "链表为空，无法修改")
            return

        value = self.modify_val.text().strip()
        pos_text = self.modify_pos.text().strip()

        if not value or not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入新值和位置")
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            return

        length = self.data_structure.length()
        if pos < 0 or pos >= length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length-1}之间")
            return

        self.current_operation = "modify"
        self.operation_data = (value, pos)
        self.animating = True
        self.highlighted_index = pos
        self.status_label.setText(f"正在修改位置 {pos} 的元素...")
        self.update_display()
        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_search(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.warning(self, "操作错误", "链表为空，无法查找")
            return

        value = self.search_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要查找的值")
            return

        index = self.data_structure.locate(value)
        if index != -1:
            self.highlighted_index = index
            self.status_label.setText(f"找到元素 {value} 在位置 {index}")
            self.update_display()
            QTimer.singleShot(2000, self.clear_highlight)
        else:
            self.status_label.setText(f"未找到元素: {value}")
            self.update_display()

    def handle_get(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.warning(self, "操作错误", "链表为空，无法获取元素")
            return

        pos_text = self.modify_pos.text().strip()
        if not pos_text:
            QMessageBox.warning(self, "输入错误", "请输入要获取元素的位置")
            return

        try:
            pos = int(pos_text)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "位置必须是整数")
            return

        length = self.data_structure.length()
        if pos < 0 or pos >= length:
            QMessageBox.warning(self, "位置无效", f"位置必须在0到{length-1}之间")
            return

        value = self.data_structure.get(pos)
        self.highlighted_index = pos
        self.status_label.setText(f"位置 {pos} 的元素是: {value}")
        self.update_display()
        QTimer.singleShot(2000, self.clear_highlight)

    def handle_clear(self):
        self.play_click_sound()
        if self.data_structure.is_empty():
            QMessageBox.information(self, "提示", "链表已经是空的")
            return

        reply = QMessageBox.question(self, "确认清空",
                                     "确定要清空链表中的所有元素吗？",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.data_structure.clear()
            self.highlighted_index = -1
            self.status_label.setText("链表已清空")
            self.update_display()

    def handle_length(self):
        self.play_click_sound()
        length = self.data_structure.length()
        self.status_label.setText(f"链表长度: {length} 个元素")
        self.update_display()

    def _update_status_text(self):
        length = self.data_structure.length()
        if length > 0:
            self.status_label.setText(f"链表状态: {length} 个元素")
        else:
            self.status_label.setText("链表状态: 空")

    def set_buttons_enabled(self, enabled):
        # 所有按钮和输入框的启用状态控制
        self.head_insert_btn.setEnabled(enabled)
        self.tail_insert_btn.setEnabled(enabled)
        self.pos_insert_btn.setEnabled(enabled)
        self.modify_btn.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)
        self.delete_pos_btn.setEnabled(enabled)
        self.delete_val_btn.setEnabled(enabled)
        self.get_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.length_btn.setEnabled(enabled)

        self.head_insert_input.setEnabled(enabled)
        self.tail_insert_input.setEnabled(enabled)
        self.pos_insert_val.setEnabled(enabled)
        self.pos_insert_pos.setEnabled(enabled)
        self.modify_val.setEnabled(enabled)
        self.modify_pos.setEnabled(enabled)
        self.search_input.setEnabled(enabled)
        self.delete_pos.setEnabled(enabled)
        self.delete_val.setEnabled(enabled)

    def execute_operation(self):
        try:
            if self.current_operation == "head_insert":
                value = self.operation_data
                self.data_structure.insert(0, value)
                self.status_label.setText(f"已在头部插入: {value}")
                self.head_insert_input.clear()

            elif self.current_operation == "tail_insert":
                value = self.operation_data
                pos = self.data_structure.length()
                self.data_structure.insert(pos, value)
                self.status_label.setText(f"已在尾部插入: {value}")
                self.tail_insert_input.clear()

            elif self.current_operation == "pos_insert":
                value, pos = self.operation_data
                self.data_structure.insert(pos, value)
                self.status_label.setText(f"已在位置 {pos} 插入: {value}")
                self.pos_insert_val.clear()
                self.pos_insert_pos.clear()

            elif self.current_operation == "delete_by_pos":
                pos = self.operation_data
                deleted_value = self.data_structure.remove(pos)
                self.status_label.setText(f"已删除位置 {pos} 的元素: {deleted_value}")
                self.delete_pos.clear()

            elif self.current_operation == "delete_by_val":
                pos = self.operation_data
                deleted_value = self.data_structure.remove(pos)
                self.status_label.setText(f"已删除元素: {deleted_value} (位置 {pos})")
                self.delete_val.clear()

            elif self.current_operation == "modify":
                value, pos = self.operation_data
                old_value = self.data_structure.get(pos)
                self.data_structure.set(pos, value)
                self.status_label.setText(f"已修改位置 {pos}: {old_value} → {value}")
                self.modify_val.clear()
                self.modify_pos.clear()

            self.animating = False
            self.highlighted_index = -1
            self.set_buttons_enabled(True)
            self.update_display()

        except Exception as e:
            print(f"操作执行错误: {e}")
            self.status_label.setText(f"错误: {str(e)}")
            self.animating = False
            self.highlighted_index = -1
            self.set_buttons_enabled(True)
            self.update_display()


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("SequenceList Visualizer")
        app.setStyle('Fusion')

        #window = SequenceListVisualizer()
        #window = StackVisualizer()
        window=LinkedListVisualizer()
        window.show()

        print("顺序表可视化工具启动成功")
        return app.exec_()

    except Exception as e:
        print(f"应用程序错误: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

