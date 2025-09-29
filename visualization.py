import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
from model import Stack

class VisualArea(QWidget):
    """专门用于绘图的组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(1000)
        self.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        self.stack = None  # 直接存储stack引用
        self.cell_width = 120
        self.cell_height = 40
        self.cell_spacing = 5
        self.highlighted_index = -1

    def set_stack(self, stack):
        """设置要可视化的栈"""
        self.stack = stack
        self.update()  # 触发重绘

    def update_visualization(self, stack=None, highlighted_index=-1):
        """更新可视化"""
        if stack is not None:
            self.stack = stack
        self.highlighted_index = highlighted_index
        self.update()  # 强制重绘

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            if not self.stack:
                # 绘制默认提示
                painter.setFont(QFont("Arial", 12))
                painter.drawText(self.rect(), Qt.AlignCenter, "可视化区域准备就绪")
                painter.end()
                return

            # 使用类属性中的参数
            cell_width = self.cell_width
            cell_height = self.cell_height
            cell_spacing = self.cell_spacing
            highlighted_index = self.highlighted_index

            # 计算起始位置（从中间偏下开始，留出足够的顶部空间）
            area_width = self.width()
            area_height = self.height()
            start_x = max(10, (area_width - cell_width) // 2)
            start_y = area_height - 100  # 提高起始位置，留出更多顶部空间

            stack_length = self.stack.length()

            # 绘制栈元素（从栈底到栈顶）
            for i in range(stack_length):
                # 计算Y位置（从下往上）
                y_pos = start_y - i * (cell_height + cell_spacing)

                # 如果超出顶部边界，停止绘制
                if y_pos < 20:  # 留出20像素的顶部边距
                    # 绘制溢出提示
                    painter.setPen(QPen(QColor(255, 0, 0), 1))
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(start_x, 10, cell_width, 15,
                                     Qt.AlignCenter, f"...还有{stack_length - i}个元素未显示")
                    break

                # 设置颜色
                if i == highlighted_index:
                    painter.setBrush(QBrush(QColor(255, 215, 0)))  # 高亮色
                else:
                    painter.setBrush(QBrush(QColor(200, 230, 255)))  # 正常色

                # 绘制矩形框
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.drawRect(start_x, y_pos, cell_width, cell_height)

                # 绘制元素值
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.setFont(QFont("Arial", 10, QFont.Bold))
                try:
                    value = str(self.stack[i])
                    # 限制显示长度
                    if len(value) > 15:
                        value = value[:15] + "..."
                    painter.drawText(start_x, y_pos, cell_width, cell_height,
                                     Qt.AlignCenter, value)
                except (IndexError, TypeError) as e:
                    print(f"绘制元素错误: {e}")
                    break

            # 绘制栈标记
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setFont(QFont("Arial", 9))

            if stack_length > 0:
                # 栈顶标记（最上面的元素）
                top_index = min(stack_length - 1,
                                (start_y - 20) // (cell_height + cell_spacing))  # 计算实际显示的元素数量
                top_y = start_y - top_index * (cell_height + cell_spacing) - 20
                painter.drawText(start_x, top_y, cell_width, 20,
                                 Qt.AlignCenter, "↑ 栈顶 Top")

                # 栈底标记（最下面的元素）
                bottom_y = start_y + cell_height + 5
                painter.drawText(start_x, bottom_y, cell_width, 20,
                                 Qt.AlignCenter, "↓ 栈底 Bottom")

                # 显示栈大小信息
                info_text = f"栈大小: {stack_length}"
                painter.drawText(10, 10, 200, 20, Qt.AlignLeft, info_text)

            else:
                # 空栈提示
                painter.setFont(QFont("Arial", 12, QFont.Italic))
                painter.setPen(QPen(QColor(150, 150, 150), 1))
                painter.drawText(self.rect(), Qt.AlignCenter, "空栈 - 请添加元素")

            painter.end()

        except Exception as e:
            print(f"绘图错误: {e}")
            traceback.print_exc()


class StackVisualizer(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化栈
        self.stack = Stack()

        # 动画相关
        self.animation_speed = 500
        self.animating = False
        self.current_operation = None
        self.operation_data = None

        # 可视化参数
        self.cell_width = 120
        self.cell_height = 40
        self.cell_spacing = 5
        self.highlighted_index = -1

        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title_label = QLabel("栈 (Stack) 可视化工具")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 操作区域
        control_group = QGroupBox("栈操作")
        control_layout = QVBoxLayout()

        # 输入行
        input_layout = QHBoxLayout()
        self.push_input = QLineEdit()
        self.push_input.setPlaceholderText("输入要入栈的元素...")
        self.push_input.returnPressed.connect(self.handle_push)  # 回车键触发

        self.push_btn = QPushButton("入栈 (Push)")
        self.push_btn.clicked.connect(self.handle_push)
        self.push_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        input_layout.addWidget(QLabel("元素:"))
        input_layout.addWidget(self.push_input)
        input_layout.addWidget(self.push_btn)
        input_layout.addStretch()

        # 操作按钮行
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

        control_layout.addLayout(input_layout)
        control_layout.addLayout(button_layout)
        control_layout.addLayout(speed_layout)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # 可视化区域
        visual_group = QGroupBox("栈可视化")
        visual_layout = QVBoxLayout()
        self.visual_area = VisualArea(self)
        # 关键修改：将stack传递给可视化区域
        self.visual_area.set_stack(self.stack)
        visual_layout.addWidget(self.visual_area)
        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)

        # 状态信息
        self.status_label = QLabel("就绪 - 栈为空")
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
        self.setWindowTitle("栈可视化工具")
        self.resize(700, 600)

        # 初始更新
        self.update_display()

    def update_display(self):
        """更新显示"""
        try:
            # 关键修改：更新可视化区域
            self.visual_area.update_visualization(self.stack, self.highlighted_index)

            # 更新状态标签
            if self.stack.is_empty():
                self.status_label.setText("栈状态: 空")
            else:
                self.status_label.setText(f"栈状态: {self.stack.length()} 个元素, 栈顶: {self.stack.peek()}")
        except Exception as e:
            print(f"更新显示错误: {e}")

    def update_speed(self):
        try:
            speed = int(self.speed_slider.text())
            if 100 <= speed <= 2000:
                self.animation_speed = speed
                self.status_label.setText(f"动画速度已设置为 {speed} 毫秒")
                QTimer.singleShot(2000, lambda: self.update_status_text())
            else:
                QMessageBox.warning(self, "无效值", "请输入100-2000之间的数值")
                self.speed_slider.setText(str(self.animation_speed))
        except ValueError:
            QMessageBox.warning(self, "无效输入", "请输入有效的数字")
            self.speed_slider.setText(str(self.animation_speed))

    def update_status_text(self):
        """更新状态文本"""
        if self.stack.is_empty():
            self.status_label.setText("栈状态: 空")
        else:
            self.status_label.setText(f"栈状态: {self.stack.length()} 个元素, 栈顶: {self.stack.peek()}")

    def handle_push(self):
        if self.animating:
            return

        value = self.push_input.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要入栈的元素")
            self.push_input.setFocus()
            return

        # 限制输入长度
        if len(value) > 50:
            value = value[:50]
            self.push_input.setText(value)

        self.current_operation = "push"
        self.operation_data = value
        self.animating = True

        # 高亮将要添加的位置
        self.highlighted_index = self.stack.length()
        self.status_label.setText(f"正在入栈: {value}...")
        self.update_display()  # 立即更新显示以显示高亮

        # 禁用按钮防止重复操作
        self.set_buttons_enabled(False)

        # 执行动画
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_pop(self):
        if self.animating:
            return

        if self.stack.is_empty():
            QMessageBox.warning(self, "操作错误", "栈为空，无法出栈")
            return

        self.current_operation = "pop"
        self.operation_data = self.stack.peek()
        self.animating = True

        # 高亮将要移除的元素
        self.highlighted_index = self.stack.length() - 1
        self.status_label.setText(f"正在出栈: {self.operation_data}...")
        self.update_display()  # 立即更新显示以显示高亮

        self.set_buttons_enabled(False)
        QTimer.singleShot(self.animation_speed, self.execute_operation)

    def handle_peek(self):
        if self.stack.is_empty():
            QMessageBox.information(self, "栈顶元素", "栈为空，没有元素")
            return

        top_value = self.stack.peek()
        # 高亮栈顶元素
        self.highlighted_index = self.stack.length() - 1
        self.status_label.setText(f"栈顶元素: {top_value}")
        self.update_display()

        # 2秒后清除高亮
        QTimer.singleShot(2000, self.clear_highlight)

    def handle_clear(self):
        if self.stack.is_empty():
            QMessageBox.information(self, "提示", "栈已经是空的")
            return

        reply = QMessageBox.question(self, "确认清空",
                                     "确定要清空栈中的所有元素吗？",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.stack.clear()
            self.highlighted_index = -1
            self.status_label.setText("栈已清空")
            self.update_display()

    def set_buttons_enabled(self, enabled):
        """统一设置按钮状态"""
        self.push_btn.setEnabled(enabled)
        self.pop_btn.setEnabled(enabled)
        self.peek_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.push_input.setEnabled(enabled)

    def clear_highlight(self):
        """清除高亮状态"""
        self.highlighted_index = -1
        self.update_display()

    def execute_operation(self):
        """执行实际的操作"""
        try:
            if self.current_operation == "push":
                self.stack.push(self.operation_data)
                self.status_label.setText(f"已入栈: {self.operation_data}")
                self.push_input.clear()

            elif self.current_operation == "pop":
                popped_value = self.stack.pop()
                self.status_label.setText(f"已出栈: {popped_value}")

            # 重置状态
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
    """安全的主函数"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Stack Visualizer")

        # 设置应用样式
        app.setStyle('Fusion')

        window = StackVisualizer()
        window.show()

        print("栈可视化工具启动成功")
        return app.exec_()

    except Exception as e:
        print(f"应用程序错误: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
