import sys
import traceback
import math
from fileinput import filename
from msilib.schema import SelfReg

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QGroupBox, QMessageBox, QTextEdit, QGridLayout,
                             QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QUrl,QPointF,QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush,QPolygonF
from PyQt5.QtMultimedia import QSoundEffect
from model import Stack, SequenceList, LinkedList,BinaryTree,BinarySearchTree,HuffmanTree,HuffmanNode,BinaryTreeNode
from PyQt5.QtWidgets import QFileDialog
import os
from datetime import datetime
import json

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
            elif isinstance(self.data_structure, (BinaryTree, HuffmanTree)):
                self._draw_tree(painter)  # 新增：绘制树形结构
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

    def _draw_tree(self, painter):
        """绘制树形结构（二叉树、哈夫曼树等），使用圆形节点 - 修复版本"""
        tree = self.data_structure
        if tree.is_empty():
            painter.setFont(QFont("Arial", 12, QFont.Italic))
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "空树")
            return

        # 计算树的高度以确定布局
        tree_height = self._get_tree_height(tree.root)
        area_width = self.width()
        area_height = self.height()

        # 计算根节点起始位置
        start_x = area_width // 2
        start_y = 80  # 增加顶部间距

        # 根据树高度动态计算水平间距
        base_spacing = min(area_width // max(tree_height, 1), 200)
        level_spacing = base_spacing

        # 递归绘制树
        self._draw_tree_node(painter, tree.root, start_x, start_y, level_spacing, tree_height)

        # 显示树的基本信息
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Arial", 9))
        tree_type = "哈夫曼树" if isinstance(tree, HuffmanTree) else "二叉树"
        painter.drawText(10, 10, 200, 20, Qt.AlignLeft, f"{tree_type} 节点数: {tree.length()}")

    def _get_tree_height(self, node):
        """计算树的高度"""
        if not node:
            return 0
        return 1 + max(self._get_tree_height(node.left_child), self._get_tree_height(node.right_child))

    def _draw_tree_node(self, painter, node, x, y, level_spacing, remaining_height):
        """递归绘制树节点 - 修复版本"""
        if not node:
            return

        # 节点半径
        radius = 25

        # 绘制当前节点（圆形）
        if hasattr(self, 'highlighted_node') and self.highlighted_node == node:
            painter.setBrush(QBrush(QColor(255, 215, 0)))  # 高亮色（金色）
        else:
            # 哈夫曼树的叶子节点和内部节点用不同颜色
            if isinstance(node, HuffmanNode):
                if node.data is not None:  # 叶子节点
                    painter.setBrush(QBrush(QColor(144, 238, 144)))  # 浅绿色
                else:  # 内部节点
                    painter.setBrush(QBrush(QColor(255, 182, 193)))  # 浅粉色
            else:
                painter.setBrush(QBrush(QColor(173, 216, 230)))  # 浅蓝色

        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(QPoint(int(x), int(y)), radius, radius)

        # 绘制节点数据
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setFont(QFont("Arial", 8, QFont.Bold))  # 减小字体以适应圆形

        # 哈夫曼树显示数据和权重
        if isinstance(node, HuffmanNode):
            if node.data is not None:
                display_text = f"{node.data}\n{node.weight}"
            else:
                display_text = f"W:{node.weight}"
        else:
            display_text = str(node.data)

        # 确保文本在圆形内
        text_rect = painter.boundingRect(int(x - radius), int(y - radius),
                                         radius * 2, radius * 2,
                                         Qt.AlignCenter, display_text)
        painter.drawText(text_rect, Qt.AlignCenter, display_text)

        # 计算下一层的水平间距和垂直位置
        next_level_spacing = level_spacing * 0.6  # 减少水平间距避免重叠
        next_y = y + self.tree_level_spacing

        # 绘制左子树
        if node.left_child:
            left_x = x - next_level_spacing
            # 绘制连接线
            self._draw_tree_edge(painter, x, y, left_x, next_y, radius, is_left=True)
            # 递归绘制左子节点
            self._draw_tree_node(painter, node.left_child, left_x, next_y, next_level_spacing, remaining_height - 1)

        # 绘制右子树
        if node.right_child:
            right_x = x + next_level_spacing
            # 绘制连接线
            self._draw_tree_edge(painter, x, y, right_x, next_y, radius, is_left=False)
            # 递归绘制右子节点
            self._draw_tree_node(painter, node.right_child, right_x, next_y, next_level_spacing, remaining_height - 1)

    def _draw_tree_edge(self, painter, parent_x, parent_y, child_x, child_y, radius, is_left):
        """绘制树节点间的连接线 - 修复版本"""
        # 计算连接点（从父节点底部边缘到子节点顶部边缘）
        parent_edge_y = parent_y + radius
        child_edge_y = child_y - radius

        # 计算连接线的起点和终点
        start_x = parent_x
        start_y = parent_edge_y
        end_x = child_x
        end_y = child_edge_y

        # 绘制连接线
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        painter.drawLine(
            int(round(start_x)),
            int(round(start_y)),
            int(round(end_x)),
            int(round(end_y))
        )

        # 绘制左/右标记（0/1）
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.setPen(QPen(QColor(255, 0, 0)))  # 红色标记
        painter.drawText(
            int(round(mid_x - 5)),
            int(round(mid_y - 10)),
            10, 10,
            Qt.AlignCenter,
            "0" if is_left else "1"
        )

    def add_child(self, is_left):
        try:
            parent_index_text = self.parent_index_input.text().strip()
            value = self.child_value_input.text().strip()

            # 先检查输入是否为空
            if not parent_index_text:
                QMessageBox.warning(self, "输入错误", "请输入父节点索引")
                return

            if not value:
                QMessageBox.warning(self, "输入错误", "请输入子节点值")
                return

            # 再转换为整数
            parent_index = int(parent_index_text)

            if is_left:
                self.data_structure.insert_left(parent_index, value)
            else:
                self.data_structure.insert_right(parent_index, value)

            self.update_display()
            self.play_click_sound()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的父节点索引（必须是整数）")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加子节点失败: {str(e)}")


class BaseVisualizer(QWidget):
    """数据结构可视化父类"""

    def __init__(self, main_window=None,last_window=None, title="数据结构可视化工具"):
        super().__init__()
        # 保存主窗口引用
        self.main_window = main_window
        #保存上一级窗口引用
        self.last_window=last_window

        # 数据结构类型映射
        self.structure_type_mapping = {
            "栈 (Stack) 可视化工具": "Stack",
            "顺序表 (SequenceList) 可视化工具": "SequenceList",
            "链表 (LinkedList) 可视化工具": "LinkedList",
            "二叉树可视化工具": "BinaryTree",
            "哈夫曼树可视化工具": "HuffmanTree"
        }

        # 当前数据结构类型
        self.current_structure_type = self.structure_type_mapping.get(title, "")


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

        # 最近保存文件管理
        self.recent_files = []
        self.max_recent_files = 5
        self.recent_files_file = "recent_files.json"
        self.load_recent_files()

        self.init_ui()
        self.update_recent_files_display()
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

        # 文件操作布局
        file_group=QGroupBox("文件保存加载操作")
        file_layout = QVBoxLayout()

        # 保存/加载按钮行
        file_buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("保存结构")
        self.save_btn.setMinimumSize(120, 35)
        self.save_btn.setFont(QFont("SimHei", 9))
        self.save_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border-radius: 8px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
        self.save_btn.clicked.connect(self.save_structure)

        self.load_btn = QPushButton("打开结构")
        self.load_btn.setMinimumSize(120, 35)
        self.load_btn.setFont(QFont("SimHei", 9))
        self.load_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #17a2b8;
                        color: white;
                        border-radius: 8px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #138496;
                    }
                """)
        self.load_btn.clicked.connect(self.load_structure)

        file_buttons_layout.addWidget(self.save_btn)
        file_buttons_layout.addWidget(self.load_btn)
        #file_buttons_layout.setAlignment(Qt.AlignCenter)

        file_buttons_layout.addStretch()



        # 最近保存文件区域
        recent_group = QGroupBox("最近保存的结构")
        recent_layout = QVBoxLayout()

        self.recent_list_widget = QWidget()
        self.recent_list_layout = QVBoxLayout(self.recent_list_widget)
        self.recent_list_layout.setSpacing(5)
        self.recent_list_layout.setContentsMargins(5, 5, 5, 5)

        # 滚动区域
        scroll_area = QWidget()
        scroll_layout = QHBoxLayout(scroll_area)
        scroll_layout.addWidget(self.recent_list_widget)

        recent_scroll = QScrollArea()
        recent_scroll.setWidgetResizable(True)
        recent_scroll.setWidget(scroll_area)
        recent_scroll.setMaximumHeight(120)
        recent_scroll.setStyleSheet("QScrollArea { border: 1px solid #ccc; border-radius: 4px; }")

        recent_layout.addWidget(recent_scroll)
        recent_group.setLayout(recent_layout)

        file_layout.addLayout(file_buttons_layout)
        file_layout.addWidget(recent_group)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 返回按钮
        #button_return_layout = QHBoxLayout()
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
        ##button_return_layout.addWidget(self.button_return_main)


        self.button_return=QPushButton("返回")
        self.button_return.setMinimumSize(150, 40)
        self.button_return.setFont(QFont("SimHei", 10))
        self.button_return.setStyleSheet("""
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
        self.button_return.clicked.connect(self.on_button_return_clicked)
        #button_return_layout.addWidget(self.button_return)
        #button_return_layout.addStretch()


        # 速度控制
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("动画速度:"))
        self.speed_slider = QLineEdit(str(self.animation_speed))
        self.speed_slider.setMaximumWidth(80)
        self.speed_slider.setToolTip("单位: 毫秒 (100-2000)")
        self.speed_slider.returnPressed.connect(self.update_speed)

        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(QLabel("毫秒"))
        speed_layout.addWidget(self.button_return)
        speed_layout.addWidget(self.button_return_main)
        speed_layout.addStretch()

        #control_layout.addLayout(button_return_layout)
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

    def on_button_return_clicked(self):
        """返回按钮点击事件处理"""
        print("返回按钮被点击")  # 添加调试信息
        self.play_click_sound()
        if self.last_window:
            print(f"显示上一级窗口: {self.last_window}")
            self.last_window.show()
        else:
            print("last_window 为 None")
        self.close()

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

    def load_recent_files(self):
        """加载最近保存的文件列表"""
        try:
            if os.path.exists(self.recent_files_file):
                with open(self.recent_files_file, 'r', encoding='utf-8') as f:
                    self.recent_files = json.load(f)
        except Exception as e:
            print(f"加载最近文件列表失败: {e}")
            self.recent_files = []

    def save_recent_files(self):
        """保存最近文件列表到文件"""
        try:
            with open(self.recent_files_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, ensure_ascii=False, indent=2)
                print(1)
        except Exception as e:
            print(f"保存最近文件列表失败: {e}")

    def add_to_recent_files(self, filename):
        """添加文件到最近保存列表"""
        # 移除已存在的相同文件
        self.recent_files = [f for f in self.recent_files if f['path'] != filename]

        # 添加新文件到开头
        file_info = {
            'path': filename,
            'name': os.path.basename(filename),
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': self.current_structure_type  # 确保使用当前可视化器的类型
        }
        self.recent_files.insert(0, file_info)

        # 限制列表长度
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]

        # 保存更新后的列表
        self.save_recent_files()
        self.update_recent_files_display()

    def update_recent_files_display(self):
        """更新最近文件显示 - 只显示当前数据结构类型的文件"""
        # 清空现有显示
        for i in reversed(range(self.recent_list_layout.count())):
            widget = self.recent_list_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 过滤出当前数据结构类型的文件
        filtered_files = [f for f in self.recent_files if f.get('type') == self.current_structure_type]

        print(f"调试信息: 当前类型={self.current_structure_type}, 过滤后文件数={len(filtered_files)}")  # 调试用

        if not filtered_files:
            no_files_label = QLabel(f"暂无最近保存的{self._get_structure_name()}文件")
            no_files_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
            no_files_label.setAlignment(Qt.AlignCenter)
            no_files_label.setMinimumHeight(60)
            self.recent_list_layout.addWidget(no_files_label)
            return

        for file_info in filtered_files:
            file_widget = self.create_recent_file_widget(file_info)
            self.recent_list_layout.addWidget(file_widget)

    def _get_structure_name(self):
        """获取数据结构的中文名称"""
        name_mapping = {
            "Stack": "栈",
            "SequenceList": "顺序表",
            "LinkedList": "链表",
            "BinaryTree": "二叉树",
            "HuffmanTree": "哈夫曼树"
        }
        return name_mapping.get(self.current_structure_type, "数据结构")

    def _get_loaded_structure_name(self, loaded_type):
        """获取已加载数据结构的中文名称"""
        name_mapping = {
            "Stack": "栈",
            "SequenceList": "顺序表",
            "LinkedList": "链表",
            "BinaryTree": "二叉树",
            "HuffmanTree": "哈夫曼树"
        }
        return name_mapping.get(loaded_type, "未知数据结构")


    def create_recent_file_widget(self, file_info):
        """创建单个最近文件的小部件 - 修改为可点击加载"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)

        # 文件信息标签 - 现在整个区域都可点击
        structure_name = self._get_structure_name()
        file_label = QLabel(f"{file_info['name']} ({file_info['time']})")
        file_label.setStyleSheet("font-size: 9pt;")
        file_label.setToolTip(f"路径: {file_info['path']}\n类型: {structure_name}\n点击加载此文件")

        layout.addWidget(file_label)
        layout.addStretch()

        # 设置widget的样式和鼠标悬停效果
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
                margin: 2px;
            }
            QWidget:hover {
                background-color: #e9ecef;
                border: 1px solid #17a2b8;
            }
        """)

        widget.setMinimumHeight(35)  # 确保每个文件项有合适的高度

        # 设置widget可点击，连接点击事件到加载函数
        widget.mousePressEvent = lambda event: self.load_recent_file(file_info['path'])

        # 添加鼠标悬停时的手型光标
        widget.setCursor(Qt.PointingHandCursor)

        return widget

    def load_recent_file(self, filepath):
        """加载最近文件列表中的文件"""
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "文件不存在", f"文件不存在: {filepath}")
            # 从最近文件中移除
            self.recent_files = [f for f in self.recent_files if f['path'] != filepath]
            self.save_recent_files()
            self.update_recent_files_display()
            return

        try:
            from model import DataStructureManager
            loaded_structure = DataStructureManager.load_structure(filepath)

            if loaded_structure:
                # 检查加载的数据结构类型是否匹配当前可视化器
                loaded_type = type(loaded_structure).__name__
                expected_type = self.current_structure_type

                type_mapping = {
                    'Stack': 'Stack',
                    'SequenceList': 'SequenceList',
                    'LinkedList': 'LinkedList',
                    'BinaryTree': 'BinaryTree',
                    'HuffmanTree': 'HuffmanTree'
                }

                actual_loaded_type = type_mapping.get(loaded_type, '')

                if actual_loaded_type != expected_type:
                    structure_name = self._get_structure_name()
                    QMessageBox.warning(
                        self,
                        "类型不匹配",
                        f"文件包含的数据结构类型与当前{structure_name}可视化器不匹配\n"
                        f"请使用对应的可视化器打开此文件"
                    )
                    return

                self.data_structure = loaded_structure
                self.visual_area.set_data_structure(self.data_structure)
                self.update_display()
                self.status_label.setText(f"结构已加载: {os.path.basename(filepath)}")
                self.play_click_sound()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载数据结构文件")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")

    def load_recent_file(self, filepath):
        """加载最近文件列表中的文件"""
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "文件不存在", f"文件不存在: {filepath}")
            # 从最近文件中移除
            self.recent_files = [f for f in self.recent_files if f['path'] != filepath]
            self.save_recent_files()
            self.update_recent_files_display()
            return

        try:
            from model import DataStructureManager
            loaded_structure = DataStructureManager.load_structure(filepath)

            if loaded_structure:
                self.data_structure = loaded_structure
                self.visual_area.set_data_structure(self.data_structure)
                self.update_display()
                self.status_label.setText(f"结构已加载: {os.path.basename(filepath)}")
                self.play_click_sound()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载数据结构文件")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")

    def save_structure(self):
        """保存数据结构到文件"""
        if self.data_structure.is_empty():
            QMessageBox.warning(self, "保存失败", "数据结构为空，无法保存")
            return

        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "保存数据结构",
                "",
                "JSON Files (*.json);;All Files (*)"
            )

            if filename:
                if not filename.endswith('.json'):
                    filename += '.json'

                from model import DataStructureManager
                if DataStructureManager.save_structure(self.data_structure, filename):
                    # 添加到最近文件列表
                    self.add_to_recent_files(filename)
                    QMessageBox.information(self, "保存成功", f"数据结构已保存到: {filename}")
                    self.status_label.setText(f"结构已保存: {os.path.basename(filename)}")
                else:
                    QMessageBox.warning(self, "保存失败", "保存数据结构时发生错误")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def load_structure(self):
        """从文件加载数据结构 - 添加类型检查"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "打开数据结构",
                "",
                "JSON Files (*.json);;All Files (*)"
            )

            if filename:
                from model import DataStructureManager
                loaded_structure = DataStructureManager.load_structure(filename)

                if loaded_structure:
                    # 检查加载的数据结构类型是否匹配当前可视化器
                    loaded_type = type(loaded_structure).__name__
                    expected_type = self.current_structure_type

                    # 更严格的类型映射
                    type_mapping = {
                        'Stack': 'Stack',
                        'SequenceList': 'SequenceList',
                        'LinkedList': 'LinkedList',
                        'BinaryTree': 'BinaryTree',
                        'HuffmanTree': 'HuffmanTree'
                    }

                    actual_loaded_type = type_mapping.get(loaded_type, '')

                    print(f"调试信息: 加载类型={loaded_type}, 期望类型={expected_type}")  # 调试用

                    if actual_loaded_type != expected_type:
                        structure_name = self._get_structure_name()
                        loaded_structure_name = self._get_loaded_structure_name(loaded_type)
                        QMessageBox.warning(
                            self,
                            "类型不匹配",
                            f"无法加载文件！\n\n"
                            f"当前可视化器: {structure_name}\n"
                            f"文件数据结构: {loaded_structure_name}\n\n"
                            f"请使用对应的可视化器打开此文件"
                        )
                        return

                    self.data_structure = loaded_structure
                    self.visual_area.set_data_structure(self.data_structure)
                    self.update_display()
                    # 添加到最近文件列表
                    self.add_to_recent_files(filename)
                    self.status_label.setText(f"结构已加载: {os.path.basename(filename)}")
                    QMessageBox.information(self, "加载成功", f"数据结构已从文件加载")
                else:
                    QMessageBox.warning(self, "加载失败", "无法加载数据结构文件")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")

class StackVisualizer(BaseVisualizer):
    def __init__(self, main_window=None,lastwindow=None):
        super().__init__(main_window, lastwindow,"栈 (Stack) 可视化工具")
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
        self.save_btn.setEnabled(enabled)
        self.load_btn.setEnabled(enabled)


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
    def __init__(self, main_window=None,lastwindow=None):
        super().__init__(main_window, lastwindow,"顺序表 (SequenceList) 可视化工具")
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
        self.insert_input_pos.setPlaceholderText("输入位置/默认为第0个")
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
        self.delete_val_btn = QPushButton("按值删除(delete by val)")
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
        self.delete_pos_btn = QPushButton("按位置删除(delete by pos)")
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

        self.clear_btn = QPushButton("清空(Clear)")
        self.clear_btn.clicked.connect(self.handle_clear)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
        #button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)


        self.status_btn=QPushButton("状态信息(status)")
        #self.status_btn.clicked.connect(self.handle_status)
        self.status_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
        button_layout.addWidget(self.status_btn)

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
            pos_text=0     #若用户没有输入插入位置则默认在第0个插入

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
        self.clear_btn.setEnabled(enabled)

        self.insert_input_val.setEnabled(enabled)
        self.insert_input_pos.setEnabled(enabled)
        self.modify_input_val.setEnabled(enabled)
        self.modify_input_pos.setEnabled(enabled)
        self.search_input.setEnabled(enabled)
        self.delete_pos_input.setEnabled(enabled)

        self.save_btn.setEnabled(enabled)
        self.load_btn.setEnabled(enabled)

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
    def __init__(self, main_window=None,lastwindow=None):
        super().__init__(main_window,lastwindow, "链表 (LinkedList) 可视化工具")
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

        self.clear_btn = QPushButton("清空链表")
        self.clear_btn.clicked.connect(self.handle_clear)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")

        self.status_btn = QPushButton("状态信息(status)")
        # self.status_btn.clicked.connect(self.handle_status)
        self.status_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")

        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.status_btn)

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

        self.save_btn.setEnabled(enabled)
        self.load_btn.setEnabled(enabled)

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


# 实现TreeVisualizer子类
class BinaryTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None,lastwindow=None):
        super().__init__(main_window, lastwindow,"二叉树可视化工具")
        self.data_structure = BinaryTree()
        self.visual_area.set_data_structure(self.data_structure)
        self.highlighted_node = None

    def _create_input_layout(self):
        layout = QGridLayout()

        # 根节点输入
        layout.addWidget(QLabel("根节点值:"), 0, 0)
        self.root_input = QLineEdit()
        layout.addWidget(self.root_input, 0, 1)

        # 父节点索引和子节点值输入
        layout.addWidget(QLabel("父节点索引:"), 1, 0)
        self.parent_index_input = QLineEdit()
        layout.addWidget(self.parent_index_input, 1, 1)

        layout.addWidget(QLabel("子节点值:"), 2, 0)
        self.child_value_input = QLineEdit()
        layout.addWidget(self.child_value_input, 2, 1)

        return layout

    def _create_button_layout(self):
        layout = QHBoxLayout()

        self.btn_create_root = QPushButton("创建根节点")
        self.btn_create_root.clicked.connect(self.create_root)

        self.btn_add_left = QPushButton("添加左子节点")
        self.btn_add_left.clicked.connect(lambda: self.add_child(True))

        self.btn_add_right = QPushButton("添加右子节点")
        self.btn_add_right.clicked.connect(lambda: self.add_child(False))

        self.btn_clear = QPushButton("清空树")
        self.btn_clear.clicked.connect(self.clear_tree)

        self.btn_traverse = QPushButton("显示遍历结果")
        self.btn_traverse.clicked.connect(self.show_traversal)

        for btn in [self.btn_create_root, self.btn_add_left, self.btn_add_right, self.btn_clear, self.btn_traverse]:
            btn.setMinimumHeight(30)
            layout.addWidget(btn)

        return layout

    def create_root(self):
        try:
            value = self.root_input.text().strip()
            if not value:
                QMessageBox.warning(self, "输入错误", "请输入根节点值")
                return

            self.data_structure = BinaryTree(value)
            self.visual_area.set_data_structure(self.data_structure)
            self.update_display()
            self.play_click_sound()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建根节点失败: {str(e)}")

    def add_child(self, is_left):
        try:
            parent_index = int(self.parent_index_input.text().strip())
            value = self.child_value_input.text().strip()

            if not value:
                QMessageBox.warning(self, "输入错误", "请输入子节点值")
                return

            if is_left:
                self.data_structure.insert_left(parent_index, value)
            else:
                self.data_structure.insert_right(parent_index, value)

            self.update_display()
            self.play_click_sound()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的父节点索引")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加子节点失败: {str(e)}")

    def clear_tree(self):
        self.data_structure.clear()
        self.visual_area.set_data_structure(self.data_structure)
        self.update_display()
        self.play_click_sound()

    def show_traversal(self):
        if self.data_structure.is_empty():
            QMessageBox.information(self, "遍历结果", "树为空")
            return

        preorder = []
        inorder = []
        postorder = []
        self.data_structure._preorder_traversal(self.data_structure.root, preorder)
        self.data_structure._inorder_traversal(self.data_structure.root, inorder)
        self.data_structure._postorder_traversal(self.data_structure.root, postorder)

        msg = f"前序遍历: {preorder}\n中序遍历: {inorder}\n后序遍历: {postorder}"
        QMessageBox.information(self, "遍历结果", msg)

    def _update_status_text(self):
        self.status_label.setText(f"二叉树状态: {self.data_structure.length()} 个节点")

    def set_buttons_enabled(self, enabled):
        for btn in [self.btn_create_root, self.btn_add_left, self.btn_add_right, self.btn_clear, self.btn_traverse]:
            btn.setEnabled(enabled)

        self.save_btn.setEnabled(enabled)
        self.load_btn.setEnabled(enabled)


class HuffmanTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None,lastwindow=None):
        super().__init__(main_window, lastwindow,"哈夫曼树可视化工具")
        self.data_structure = HuffmanTree()
        self.visual_area.set_data_structure(self.data_structure)
        self.highlighted_node = None

    def _create_input_layout(self):
        layout = QVBoxLayout()

        self.weight_input = QTextEdit()
        self.weight_input.setPlaceholderText(
            "请输入数据和权重，格式：数据1:权重1,数据2:权重2,...\n例如：A:5,B:9,C:12,D:13,E:16,F:45")
        self.weight_input.setMinimumHeight(60)

        layout.addWidget(QLabel("输入数据及权重:"))
        layout.addWidget(self.weight_input)

        return layout

    def _create_button_layout(self):
        layout = QHBoxLayout()

        self.btn_build = QPushButton("构建哈夫曼树")
        self.btn_build.clicked.connect(self.build_huffman_tree)

        self.btn_show_codes = QPushButton("显示哈夫曼编码")
        self.btn_show_codes.clicked.connect(self.show_huffman_codes)

        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self.clear_tree)

        for btn in [self.btn_build, self.btn_show_codes, self.btn_clear]:
            btn.setMinimumHeight(30)
            layout.addWidget(btn)

        return layout

    def build_huffman_tree(self):
        try:
            input_text = self.weight_input.toPlainText().strip()
            if not input_text:
                QMessageBox.warning(self, "输入错误", "请输入数据和权重")
                return

            # 解析输入
            weight_dict = {}
            items = input_text.split(',')
            for item in items:
                data, weight = item.split(':')
                weight_dict[data.strip()] = int(weight.strip())

            # 构建哈夫曼树
            self.data_structure = HuffmanTree(weight_dict)
            self.visual_area.set_data_structure(self.data_structure)
            self.update_display()
            self.play_click_sound()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"构建哈夫曼树失败: {str(e)}")

    def show_huffman_codes(self):
        if self.data_structure.is_empty():
            QMessageBox.information(self, "哈夫曼编码", "哈夫曼树为空")
            return

        codes = self.data_structure.get_huffman_code()
        if not codes:
            QMessageBox.information(self, "哈夫曼编码", "无法生成编码")
            return

        msg = "哈夫曼编码:\n"
        for data, code in codes.items():
            msg += f"{data}: {code}\n"

        QMessageBox.information(self, "哈夫曼编码", msg)

    def clear_tree(self):
        self.data_structure = HuffmanTree()
        self.visual_area.set_data_structure(self.data_structure)
        self.update_display()
        self.play_click_sound()

    def _update_status_text(self):
        self.status_label.setText(f"哈夫曼树状态: {self.data_structure.length()} 个节点")

    def set_buttons_enabled(self, enabled):
        for btn in [self.btn_build, self.btn_show_codes, self.btn_clear]:
            btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.load_btn.setEnabled(enabled)


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("BinaryTree Visualizer")
        app.setStyle('Fusion')

        #window = SequenceListVisualizer()
        #window = StackVisualizer()
        #window=LinkedListVisualizer()
        #window=BinaryTreeVisualizer()
        window=HuffmanTreeVisualizer()
        window.show()

        print("二叉树可视化工具启动成功")
        return app.exec_()

    except Exception as e:
        print(f"应用程序错误: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

