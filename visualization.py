import sys
import traceback
import math
import random
import os
import json
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QGroupBox, QMessageBox, QTextEdit, QGridLayout,
                             QScrollArea, QSizePolicy, QFileDialog, QCheckBox)  # 导入 QCheckBox
from PyQt5.QtCore import Qt, QTimer, QUrl, QPointF, QPoint, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPolygonF
from PyQt5.QtMultimedia import QSoundEffect
from DSL_handler import DSLHandler

try:
    from model import Stack, SequenceList, LinkedList, BinaryTree, BinarySearchTree, HuffmanTree, HuffmanStructNode, \
        AVLTree
except ImportError:
    # 兼容没有 model.py 的运行环境，提供 SequenceList 桩代码
    class Stack:
        def __init__(self): self._data = []; self._size = 0

        def length(self): return self._size

        def push(self, val): self._data.append(val); self._size += 1

        def pop(self): return self._data.pop()

        def is_empty(self): return self._size == 0

        def clear(self): self._data = []; self._size = 0

        def __getitem__(self, key): return self._data[key]

        pass


    class SequenceList:
        def __init__(self): self._data = []; self._size = 0

        def length(self): return self._size

        def get(self, i): return self._data[i]

        def __getitem__(self, key): return self._data[key]

        def insert(self, i, val): self._data.insert(i, val); self._size += 1

        def remove(self, i): del self._data[i]; self._size -= 1

        def locate(self, val): return -1

        def clear(self): self._data = []; self._size = 0

        def is_empty(self): return self._size == 0


    class LinkedList:
        def __init__(self): self._data = []; self._size = 0

        def length(self): return self._size

        def get(self, i): return self._data[i]

        def __getitem__(self, key): return self._data[key]

        def insert(self, i, val): self._data.insert(i, val); self._size += 1

        def remove(self, i): val = self._data[i]; del self._data[i]; self._size -= 1; return val

        def locate(self, val): return self._data.index(val) if val in self._data else -1

        def clear(self): self._data = []; self._size = 0

        def is_empty(self): return self._size == 0

        def append(self, val): self.insert(self.length(), val)

        pass


    class BinaryTree:
        def __init__(self, root_data=None):
            class Node:
                def __init__(self, data):
                    self.data = data
                    self.left_child = None
                    self.right_child = None
                    self.parent = None

            self.root = Node(root_data) if root_data is not None else None
            self._size = 1 if self.root else 0

        def is_empty(self):
            return self.root is None

        def length(self):
            return self._size

        def clear(self):
            self.root = None; self._size = 0

        def _get_node(self, index):
            if self.root is None: return None
            queue = [(self.root, 0)]
            while queue:
                node, idx = queue.pop(0)
                if idx == index: return node
                if node.left_child: queue.append((node.left_child, 2 * idx + 1))
                if node.right_child: queue.append((node.right_child, 2 * idx + 2))
            return None

        def insert_left(self, p_idx, val):
            p = self._get_node(p_idx)
            if not p: raise ValueError("Parent node not found")
            if p.left_child: raise ValueError("Left child already exists")

            class Node:
                def __init__(self, data):
                    self.data = data
                    self.left_child = None
                    self.right_child = None
                    self.parent = None

            new_node = Node(val)
            p.left_child = new_node
            new_node.parent = p
            self._size += 1

        def insert_right(self, p_idx, val):
            p = self._get_node(p_idx)
            if not p: raise ValueError("Parent node not found")
            if p.right_child: raise ValueError("Right child already exists")

            class Node:
                def __init__(self, data):
                    self.data = data
                    self.left_child = None
                    self.right_child = None
                    self.parent = None

            new_node = Node(val)
            p.right_child = new_node
            new_node.parent = p
            self._size += 1

        pass


    class BinarySearchTree:
        def __init__(self):
            class Node:
                def __init__(self, data):
                    self.data = data
                    self.left_child = None
                    self.right_child = None
                    self.parent = None

            self.root = None
            self._size = 0

        def is_empty(self):
            return self.root is None

        def length(self):
            return self._size

        def clear(self):
            self.root = None; self._size = 0

        def insert(self, val):
            class Node:
                def __init__(self, data):
                    self.data = data
                    self.left_child = None
                    self.right_child = None
                    self.parent = None

            if self.root is None:
                self.root = Node(val)
                self._size += 1
                return

            curr = self.root
            while curr:
                if val == curr.data: return  # 不插入重复元素
                parent = curr
                if val < curr.data:
                    curr = curr.left_child
                else:
                    curr = curr.right_child

            new_node = Node(val)
            new_node.parent = parent
            if val < parent.data:
                parent.left_child = new_node
            else:
                parent.right_child = new_node
            self._size += 1

        def delete(self, val):
            pass

        pass


    class HuffmanTree:
        pass


    class HuffmanStructNode:
        def __init__(self, data=None, weight=0, left=-1, right=-1, parent=-1, index=-1):
            self.data = data  # 字符或None
            self.weight = weight  # 权重
            self.left = left  # 左孩子在数组中的下标
            self.right = right  # 右孩子在数组中的下标
            self.parent = parent  # 父节点在数组中的下标
            self.index = index  # 自身在数组中的下标

        pass

    class AVLTree(BinarySearchTree):
        pass

# --- 样式常量 ---
STYLES = {
    "btn_primary": "QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; min-height: 30px; } QPushButton:hover { background-color: #2563eb; }",
    "btn_success": "QPushButton { background-color: #10b981; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; min-height: 30px; } QPushButton:hover { background-color: #059669; }",
    "btn_danger": "QPushButton { background-color: #ef4444; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; min-height: 30px; } QPushButton:hover { background-color: #dc2626; }",
    "btn_warning": "QPushButton { background-color: #f59e0b; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; min-height: 30px; } QPushButton:hover { background-color: #d97706; }",
    "btn_random": "QPushButton { background-color: #8b5cf6; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; min-height: 30px; } QPushButton:hover { background-color: #7c3aed; }",
    "btn_secondary": "QPushButton { background-color: #6b7280; color: white; border-radius: 6px; padding: 8px 16px; min-height: 20px; } QPushButton:hover { background-color: #4b5563; }",
    "input": "QLineEdit { border: 1px solid #d1d5db; border-radius: 6px; padding: 8px; background-color: #f9fafb; min-height: 20px; } QLineEdit:focus { border: 1px solid #3b82f6; background-color: white; }",
    "group_box": "QGroupBox { font-weight: bold; border: 1px solid #e5e7eb; border-radius: 8px; margin-top: 12px; background-color: white; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #374151; }"
}


def lerp(start, end, t):
    return start + (end - start) * t


class VisualArea(QWidget):
    """通用数据结构可视化组件 (完整防崩溃融合版)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px;")

        self.data_structure = None
        self.highlighted_index = -1
        self.highlighted_node = None
        self.highlight_color = QColor(255, 215, 0)

        # 动画状态
        self.anim_state = {}
        self.traversal_text = None
        self.bfs_index_map = {}

        # 绘图参数
        self.cell_width = 120
        self.cell_height = 45
        self.cell_spacing = 8
        self.tree_level_spacing = 60
        self.node_radius = 22

        self.node_positions = {}
        self.current_frame_node_pos = {}

    def set_data_structure(self, ds):
        self.data_structure = ds
        self.update()

    def update_visualization(self, ds=None, highlighted_index=-1):
        if ds is not None:
            self.data_structure = ds
        self.highlighted_index = highlighted_index
        self.update()

    # --- [安全工具] 坐标转换工具 (防止 SIGABRT 的关键) ---
    def _safe_int(self, val):
        """将浮点数安全转换为整数，防止溢出或 NaN"""
        try:
            if math.isnan(val) or math.isinf(val): return 0
            # 限制坐标范围，防止底层绘图库崩溃
            return max(-10000, min(10000, int(val)))
        except:
            return 0

    def _safe_point(self, x, y):
        return QPoint(self._safe_int(x), self._safe_int(y))

    def _safe_rect(self, x, y, w, h):
        return QRectF(self._safe_int(x), self._safe_int(y), self._safe_int(w), self._safe_int(h))

    def _get_safe_pos(self, key):
        pos = self.node_positions.get(key)
        if not pos: return None
        try:
            x, y = float(pos[0]), float(pos[1])
            if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y): return None
            if abs(x) > 50000 or abs(y) > 50000: return None
            return int(x), int(y)
        except:
            return None

    # --- [核心修复] 布局计算 (统一入口 + 防死循环) ---
    def calculate_all_node_positions(self):
        """计算树节点位置（统一入口）"""
        positions = {}

        # 1. 基础检查
        if not self.data_structure:
            return positions

        # 兼容不同类型的树结构引用
        tree = self.data_structure
        # 只要有 root 属性就可以尝试计算
        root = getattr(tree, 'root', None)

        if not root:
            return positions

        # 2. 计算树高 (防止递归溢出)
        try:
            tree_height = self._get_tree_height(root)
        except RecursionError:
            return positions

        # 3. 计算布局参数
        area_width = self.width()
        if area_width < 50: area_width = 800  # 防止宽度过小导致除以零

        start_x = area_width // 2
        start_y = 50

        # 动态调整间距
        denominator = (2 ** (min(10, tree_height) - 1) + 1)
        ideal_spacing = area_width / denominator if denominator > 0 else 50
        base_spacing = max(min(ideal_spacing, 120), 35)

        visited = set()

        def traverse(node, x, y, level_spacing):
            if not node: return
            if node in visited: return
            visited.add(node)

            positions[node] = (x, y)
            next_y = y + self.tree_level_spacing
            next_spacing = level_spacing * 0.55

            # 安全获取左右子节点
            left = getattr(node, 'left_child', None)
            right = getattr(node, 'right_child', None)

            if left:
                traverse(left, x - level_spacing, next_y, next_spacing)
            if right:
                traverse(right, x + level_spacing, next_y, next_spacing)

            visited.remove(node)

        try:
            traverse(root, start_x, start_y, base_spacing)
        except RecursionError:
            pass

        return positions

    def _get_tree_height(self, node, depth=0):
        if not node or depth > 20: return 0
        left = getattr(node, 'left_child', None)
        right = getattr(node, 'right_child', None)
        return 1 + max(self._get_tree_height(left, depth + 1),
                       self._get_tree_height(right, depth + 1))

    # --- [核心修复] 绘图事件 (安全分发) ---
    def paintEvent(self, event):
        # 窗口太小时不绘图，防止计算错误
        if self.width() < 10 or self.height() < 10:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._draw_background_grid(painter)

        if self.data_structure is None:
            self._draw_placeholder(painter)
            return

        self.current_frame_node_pos = {}
        state = self.anim_state

        try:
            # --- 1. Morph 动画 (最高优先级) ---
            if state and state.get('type') == 'morph':
                if state.get('start_positions') and state.get('end_positions'):
                    self.draw_morph_frame(painter, state)
                return

                # --- 2. 线性结构 ---
            if isinstance(self.data_structure, (Stack, SequenceList)):
                self._draw_linear_structure(painter)

            # --- 3. 链表 ---
            elif isinstance(self.data_structure, LinkedList):
                self._draw_linked_list(painter)

            # --- 4. 哈夫曼树 ---
            elif isinstance(self.data_structure, list):
                if len(self.data_structure) > 0 and isinstance(self.data_structure[0], HuffmanStructNode):
                    self._draw_huffman_array_process(painter)

            # --- 5. 二叉树/BST/AVL (统一使用预计算布局) ---
            elif hasattr(self.data_structure, 'root'):
                # 即使是静态，也先计算位置，确保逻辑统一
                self.node_positions = self.calculate_all_node_positions()
                root = getattr(self.data_structure, 'root', None)
                if root:
                    self._draw_tree_recursive(painter, root)
                    self._draw_tree_info(painter)
                else:
                    self._draw_empty_tree_msg(painter)

        except Exception as e:
            # 捕获所有绘图异常，防止程序直接崩溃
            print(f"Paint Error: {e}")
            # traceback.print_exc()

        # 绘制浮动层
        anim_type = self.anim_state.get('type')
        if anim_type in ['bst_search', 'bst_insert', 'bst_delete']:
            self._draw_bst_overlay(painter)

        if self.traversal_text:
            self._draw_traversal_text(painter)

    # === [新功能] 统一树形结构绘制逻辑 ===
    def _draw_tree_recursive(self, painter, node):
        if not node: return

        # 必须从 node_positions 获取坐标，如果没有则跳过
        if node not in self.node_positions:
            return

        x, y = self.node_positions[node]
        self.current_frame_node_pos[node] = (x, y)  # 记录下来供 overlay 使用

        left = getattr(node, 'left_child', None)
        right = getattr(node, 'right_child', None)

        painter.setPen(QPen(QColor(31, 41, 55), 2))

        # 画连线
        if left and left in self.node_positions:
            lx, ly = self.node_positions[left]
            painter.drawLine(self._safe_point(x, y), self._safe_point(lx, ly))
            self._draw_tree_recursive(painter, left)

        if right and right in self.node_positions:
            rx, ry = self.node_positions[right]
            painter.drawLine(self._safe_point(x, y), self._safe_point(rx, ry))
            self._draw_tree_recursive(painter, right)

        # 画节点
        self.draw_single_node(painter, node, x, y, self.anim_state)

    def draw_single_node(self, painter, node, x, y, state):
        radius = self.node_radius
        bg_color = QColor(186, 230, 253)  # 默认浅蓝
        border_color = QColor(31, 41, 55)

        is_pivot = (state.get('pivot') == node)
        is_new_root = (state.get('new_root') == node)
        is_highlight = (self.highlighted_node == node)

        if is_pivot:
            bg_color = QColor(252, 211, 77)
        elif is_new_root:
            bg_color = QColor(16, 185, 129)
        elif is_highlight:
            bg_color = self.highlight_color

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))

        # 使用 safe_point 防止崩溃
        center = self._safe_point(x, y)
        painter.drawEllipse(center, radius, radius)

        painter.setPen(QPen(Qt.black, 1))
        painter.setFont(QFont("Arial", 9, QFont.Bold))

        rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        painter.drawText(rect, Qt.AlignCenter, str(node.data))

    def draw_morph_frame(self, painter, state):
        """Morph 动画帧绘制"""
        t = state.get('progress', 0.0)
        start_pos = state['start_positions']
        end_pos = state['end_positions']

        current_positions = {}
        all_nodes = set(start_pos.keys()) | set(end_pos.keys())

        for node in all_nodes:
            p_start = start_pos.get(node)
            p_end = end_pos.get(node)

            cx, cy, opacity = 0, 0, 1.0

            if p_start and p_end:
                cx = p_start[0] + (p_end[0] - p_start[0]) * t
                cy = p_start[1] + (p_end[1] - p_start[1]) * t
            elif p_start and not p_end:
                cx, cy = p_start
                opacity = 1.0 - t
            elif not p_start and p_end:
                cx, cy = p_end
                opacity = t

            if opacity < 0: opacity = 0
            if opacity > 1: opacity = 1
            current_positions[node] = (cx, cy, opacity)

        # 绘制连线
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        for node, (cx, cy, opacity) in current_positions.items():
            parent = getattr(node, 'parent', None)
            if parent and parent in current_positions:
                px, py, p_opacity = current_positions[parent]
                line_opacity = min(opacity, p_opacity)
                if line_opacity > 0.05:
                    painter.setOpacity(line_opacity)
                    painter.drawLine(self._safe_point(cx, cy), self._safe_point(px, py))

        # 绘制节点
        for node, (cx, cy, opacity) in current_positions.items():
            if opacity > 0.05:
                painter.setOpacity(opacity)
                self.draw_single_node(painter, node, cx, cy, state)

        painter.setOpacity(1.0)

    # === [辅助绘制] 占位符与网格 ===
    def _draw_placeholder(self, painter, text="可视化区域准备就绪"):
        painter.setFont(QFont("Microsoft YaHei", 14))
        painter.setPen(QColor(156, 163, 175))
        painter.drawText(self.rect(), Qt.AlignCenter, text)

    def _draw_empty_tree_msg(self, painter):
        painter.setFont(QFont("Microsoft YaHei", 12, QFont.Italic))
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(self.rect(), Qt.AlignCenter, "空树 (Empty Tree)")

    def _draw_tree_info(self, painter):
        painter.setPen(QPen(QColor(107, 114, 128), 1))
        painter.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        t_type = type(self.data_structure).__name__
        count = 0
        if hasattr(self.data_structure, 'length'):
            count = self.data_structure.length()
        elif hasattr(self.data_structure, '_size'):
            count = self.data_structure._size
        painter.drawText(20, 30, 400, 30, Qt.AlignLeft, f"{t_type} - 节点数: {count}")

    def _draw_background_grid(self, painter):
        painter.save()
        painter.setPen(QPen(QColor(243, 244, 246), 1))
        step = 40
        w, h = self.width(), self.height()
        if w > 0 and h > 0:
            for x in range(0, w, step):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, step):
                painter.drawLine(0, y, w, y)
        if isinstance(self.data_structure, list) and len(self.data_structure) > 0 and isinstance(self.data_structure[0],
                                                                                                 HuffmanStructNode):
            painter.setPen(QPen(QColor(209, 213, 219), 2, Qt.DashLine))
            painter.drawLine(220, 0, 220, h)
        painter.restore()

    def _draw_traversal_text(self, painter):
        painter.save()
        painter.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        painter.setPen(QColor(37, 99, 235))
        rect = self.rect()
        text_rect = rect.adjusted(20, rect.height() - 80, -20, -20)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.traversal_text)
        painter.restore()

    # === [遗留业务逻辑] 栈、顺序表、链表、哈夫曼树（完整保留） ===

    def _draw_linear_structure(self, painter):
        ds = self.data_structure
        length = ds.length()
        area_width = self.width()
        area_height = self.height()
        is_stack = isinstance(ds, Stack)

        if is_stack:
            if length == 0:
                self._draw_placeholder(painter, "空结构")
                return
            stack_height = length * self.cell_height + (length - 1) * self.cell_spacing
            start_x = max(10, (area_width - self.cell_width) // 2)
            start_y = (area_height + stack_height) // 2
            if start_y + 40 > area_height: start_y = area_height - 40

            for i in range(length):
                painter.save()
                x_pos = start_x
                y_pos = start_y - i * (self.cell_height + self.cell_spacing)
                bg_color = QColor(219, 234, 254)
                if i == self.highlighted_index: bg_color = QColor(250, 204, 21)

                if self.anim_state and self.anim_state.get('index') == i:
                    anim_type = self.anim_state.get('type')
                    if anim_type == 'push':
                        scale = self.anim_state.get('scale', 1.0)
                        cx, cy = x_pos + self.cell_width / 2, y_pos + self.cell_height / 2
                        painter.translate(cx, cy);
                        painter.scale(scale, scale);
                        painter.translate(-cx, -cy)
                        if scale < 0.8:
                            bg_color = QColor(16, 185, 129)
                        else:
                            bg_color = QColor(250, 204, 21)
                    elif anim_type == 'pop':
                        offset_y = self.anim_state.get('offset_y', 0)
                        painter.translate(0, offset_y)
                        bg_color = QColor(239, 68, 68)
                        painter.setOpacity(max(0, 1.0 + offset_y / 200.0))
                    elif anim_type == 'highlight':
                        bg_color = QColor(245, 158, 11)

                painter.setBrush(QBrush(bg_color))
                painter.setPen(QPen(QColor(30, 58, 138), 2))
                painter.drawRect(self._safe_rect(x_pos, y_pos, self.cell_width, self.cell_height))
                painter.setPen(QPen(QColor(107, 114, 128), 1))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(self._safe_rect(x_pos - 35, y_pos, 30, self.cell_height),
                                 Qt.AlignRight | Qt.AlignVCenter, str(i))
                painter.setPen(QPen(QColor(17, 24, 39), 1))
                painter.setFont(QFont("Arial", 11, QFont.Bold))
                try:
                    painter.drawText(self._safe_rect(x_pos, y_pos, self.cell_width, self.cell_height),
                                     Qt.AlignCenter, str(ds[i]))
                except:
                    pass
                painter.restore()

            if length > 0:
                bottom_y = start_y + self.cell_height + 5
                painter.setPen(QPen(QColor(75, 85, 99), 2))
                painter.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
                painter.drawText(int(start_x), int(bottom_y), self.cell_width, 30, Qt.AlignCenter, "Stack Bottom")
                top_y = start_y - (length - 1) * (self.cell_height + self.cell_spacing) - 30
                painter.setPen(QPen(QColor(220, 38, 38), 2))
                painter.drawText(int(start_x), int(top_y), self.cell_width, 25, Qt.AlignCenter, "Stack Top")
            return

        # SequenceList
        mem_w = self.cell_width + 10
        mem_h = self.cell_height + 10
        mem_spacing = self.cell_spacing + 5
        max_capacity = max(length + 2, 10)
        total_width = max_capacity * mem_w + (max_capacity - 1) * mem_spacing
        start_x = 20 if total_width > area_width - 40 else (area_width - total_width) // 2
        base_y = area_height // 2 - mem_h // 2
        state = self.anim_state
        anim_type = state.get('type', '')
        phase = state.get('phase', '')
        progress = state.get('progress', 0.0)
        target_idx = state.get('target_idx', -1)
        shift_idx = state.get('shift_index', -1)
        new_val = state.get('new_val')

        painter.save()
        painter.setPen(QPen(QColor(209, 213, 219), 1, Qt.DotLine))
        painter.setBrush(Qt.NoBrush)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        for i in range(max_capacity):
            mx = start_x + i * (mem_w + mem_spacing)
            painter.drawRect(self._safe_rect(mx, base_y, mem_w, mem_h))
            painter.setPen(QPen(QColor(220, 38, 38)))
            painter.drawText(self._safe_rect(mx, base_y - 15, 30, 15), Qt.AlignLeft, str(i))
            painter.setPen(QPen(QColor(209, 213, 219), 1, Qt.DotLine))
        painter.restore()

        for i in range(length):
            painter.save()
            offset_x = (mem_w - self.cell_width) / 2
            offset_y = (mem_h - self.cell_height) / 2
            ox_pos = start_x + i * (mem_w + mem_spacing) + offset_x
            oy_pos = base_y + offset_y
            x_pos = ox_pos
            y_pos = oy_pos
            bg_color = QColor(219, 234, 254)
            opacity = 1.0

            if anim_type == 'seq_insert':
                move_unit = (mem_w + mem_spacing)
                if i >= target_idx:
                    if phase == 'shift_forward':
                        if i > shift_idx:
                            x_pos += move_unit
                        elif i == shift_idx:
                            x_pos += progress * move_unit
                    elif phase in ['hover', 'move_in', 'shift_complete']:
                        x_pos += move_unit
            elif anim_type == 'seq_delete':
                move_unit = (mem_w + mem_spacing)
                if i == target_idx:
                    if phase == 'flash_target':
                        flash_intensity = abs(math.sin(state.get('flash_count', 0) * math.pi / 2))
                        bg_color = QColor.fromRgb(255, 100 + int(150 * flash_intensity),
                                                  100 + int(150 * flash_intensity))
                    elif phase == 'move_out':
                        y_pos -= progress * 100
                        opacity = 1.0 - progress
                    if opacity <= 0.01 and phase not in ['flash_target']:
                        painter.restore();
                        continue
                if i >= target_idx and phase == 'shift_backward':
                    if i < shift_idx:
                        pass
                    elif i == shift_idx:
                        x_pos += move_unit * (1.0 - progress)
                    elif i > shift_idx:
                        x_pos += move_unit
            elif anim_type == 'seq_search' and i == state.get('current_idx'):
                bg_color = QColor(255, 215, 0)
            if i == self.highlighted_index: bg_color = QColor(250, 204, 21)

            painter.setOpacity(opacity)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(30, 58, 138), 2))
            painter.drawRect(self._safe_rect(x_pos, y_pos, self.cell_width, self.cell_height))
            painter.setPen(QPen(QColor(17, 24, 39), 1))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            try:
                painter.drawText(self._safe_rect(x_pos, y_pos, self.cell_width, self.cell_height), Qt.AlignCenter,
                                 str(ds[i]))
            except:
                pass
            painter.restore()

        if anim_type == 'seq_insert' and phase in ['hover', 'move_in', 'shift_forward']:
            painter.save()
            offset_x = (mem_w - self.cell_width) / 2
            offset_y = (mem_h - self.cell_height) / 2
            tx = start_x + target_idx * (mem_w + mem_spacing) + offset_x
            ty_hover = base_y - 80
            ty_target = base_y + offset_y
            y_pos_new = ty_hover
            if phase == 'move_in': y_pos_new = lerp(ty_hover, ty_target, progress)
            painter.setBrush(QBrush(QColor(16, 185, 129)))
            painter.setPen(QPen(QColor(5, 150, 105), 2))
            painter.drawRect(self._safe_rect(tx, y_pos_new, self.cell_width, self.cell_height))
            painter.setPen(QPen(Qt.white))
            painter.drawText(self._safe_rect(tx, y_pos_new, self.cell_width, self.cell_height), Qt.AlignCenter,
                             str(new_val))
            painter.restore()

    def _draw_linked_list(self, painter):
        ll = self.data_structure
        length = ll.length()
        state = self.anim_state
        anim_type = state.get('type', '')
        phase = state.get('phase', '')
        progress = state.get('progress', 0.0)
        target_idx = state.get('target_idx', -1)
        new_val = state.get('new_val', '')
        node_w = self.cell_width
        node_h = self.cell_height
        gap = 70
        step_w = node_w + gap
        disp_cnt = length if anim_type == 'linked_insert' else length
        total_w = disp_cnt * step_w + (step_w if anim_type == 'linked_insert' else 0)
        start_x = 40 if total_w > self.width() - 40 else (self.width() - total_w) // 2 + 20
        base_y = self.height() // 2 - node_h // 2
        for i in range(length):
            curr_x = start_x + i * step_w
            curr_y = base_y
            if anim_type == 'linked_insert' and i >= target_idx:
                s = 0
                if phase == 'shift':
                    s = lerp(0, step_w, progress)
                elif phase in ['appear', 'link_next', 'link_prev', 'lift']:
                    s = step_w
                curr_x += s
            if anim_type == 'linked_delete':
                if i == target_idx:
                    if phase == 'drop':
                        curr_y += lerp(0, 100, progress)
                    elif phase in ['connect_bypass', 'fade_next_link', 'close']:
                        curr_y += 100
                elif i > target_idx:
                    if phase == 'close': curr_x -= lerp(0, step_w, progress)
            bg = QColor(219, 234, 254)
            border = QColor(30, 58, 138)
            if i == self.highlighted_index: bg = QColor(250, 204, 21)
            if anim_type == 'linked_search' and i == state.get('current_idx'):
                if phase == 'scanning':
                    bg = QColor(147, 197, 253)
                elif phase == 'found':
                    t = state.get('flash_time', 0)
                    bg = QColor(50, 205, 50) if int(t * 5) % 2 == 0 else QColor(250, 204, 21)
            if anim_type == 'linked_delete' and i == target_idx:
                bg = QColor(254, 202, 202)
                border = QColor(220, 38, 38)
                if phase == 'close': painter.setOpacity(1.0 - progress)
            painter.save()
            painter.setBrush(QBrush(bg))
            painter.setPen(QPen(border, 2))
            painter.drawRect(self._safe_rect(curr_x, curr_y, node_w, node_h))
            painter.setPen(QPen(QColor(17, 24, 39), 1))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(self._safe_rect(curr_x, curr_y, node_w, node_h), Qt.AlignCenter, str(ll[i]))
            painter.setPen(QPen(QColor(220, 38, 38)))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(self._safe_rect(curr_x, curr_y - 5, 30, 15), Qt.AlignLeft, str(i))
            if i == 0:
                painter.setPen(QPen(Qt.black))
                painter.setFont(QFont("Arial", 10, QFont.Bold))
                painter.drawText(self._safe_rect(curr_x, curr_y - 25, node_w, 20), Qt.AlignCenter, "HEAD")
            painter.restore()
            if i < length - 1:
                ni = i + 1
                nxv = start_x + ni * step_w
                nyv = base_y
                if anim_type == 'linked_insert' and ni >= target_idx:
                    s = 0
                    if phase == 'shift':
                        s = lerp(0, step_w, progress)
                    elif phase in ['appear', 'link_next', 'link_prev', 'lift']:
                        s = step_w
                    nxv += s
                if anim_type == 'linked_delete':
                    if ni == target_idx:
                        if phase == 'drop':
                            nyv += lerp(0, 100, progress)
                        elif phase in ['connect_bypass', 'fade_next_link', 'close']:
                            nyv += 100
                    elif ni > target_idx:
                        if phase == 'close': nxv -= lerp(0, step_w, progress)
                p1 = QPointF(curr_x + node_w, curr_y + node_h / 2)
                p2 = QPointF(nxv, nyv + node_h / 2)
                if anim_type == 'linked_insert' and i == target_idx - 1:
                    a = 1.0
                    if phase == 'link_prev':
                        a = 1.0 - progress
                    elif phase == 'lift':
                        a = 0.0
                    if a > 0: self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y(), opacity=a)
                    if phase in ['link_prev', 'lift']:
                        nnx = start_x + target_idx * step_w
                        nny = base_y + 100
                        if phase == 'lift': nny = lerp(base_y + 100, base_y, progress)
                        pt = QPointF(nnx, nny + node_h / 2)
                        g = progress if phase == 'link_prev' else 1.0
                        self.drawArrow(painter, p1.x(), p1.y(), pt.x(), pt.y(), color=QColor(16, 185, 129), progress=g)
                    continue
                if anim_type == 'linked_delete' and i == target_idx - 1:
                    a = 1.0
                    if phase == 'fade_prev_link':
                        a = 1.0 - progress
                    elif phase in ['drop', 'connect_bypass', 'fade_next_link', 'close']:
                        a = 0.0
                    if a > 0: self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y(), opacity=a)
                    if phase in ['connect_bypass', 'fade_next_link', 'close']:
                        bdi = target_idx + 1
                        if bdi < length:
                            dx = start_x + bdi * step_w
                            if phase == 'close': dx -= lerp(0, step_w, progress)
                            bp2 = QPointF(dx, base_y + node_h / 2)
                            g = 1.0
                            if phase == 'connect_bypass': g = progress
                            self.drawArrow(painter, p1.x(), p1.y(), bp2.x(), bp2.y(), color=QColor(220, 38, 38),
                                           progress=g)
                    continue
                if anim_type == 'linked_delete' and i == target_idx:
                    a = 1.0
                    if phase == 'fade_next_link':
                        a = 1.0 - progress
                    elif phase == 'close':
                        a = 0.0
                    self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y(), opacity=a)
                    continue
                self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y())
        if anim_type == 'linked_insert':
            nx = start_x + target_idx * step_w
            ny = base_y + 100
            a = 0.0
            if phase == 'appear':
                a = progress
            elif phase in ['link_next', 'link_prev', 'lift']:
                a = 1.0
            if phase == 'lift': ny = lerp(base_y + 100, base_y, progress)
            if a > 0:
                painter.save()
                painter.setOpacity(a)
                painter.setBrush(QBrush(QColor(167, 243, 208)))
                painter.setPen(QPen(QColor(5, 150, 105), 2))
                painter.drawRect(self._safe_rect(nx, ny, node_w, node_h))
                painter.setPen(Qt.black)
                painter.drawText(self._safe_rect(nx, ny, node_w, node_h), Qt.AlignCenter, str(new_val))
                painter.restore()
                if phase in ['link_next', 'link_prev', 'lift'] and target_idx < length:
                    nnx = start_x + (target_idx + 1) * step_w
                    nny = base_y
                    g = progress if phase == 'link_next' else 1.0
                    self.drawArrow(painter, nx + node_w, ny + node_h / 2, nnx, nny + node_h / 2,
                                   color=QColor(16, 185, 129), progress=g)

    def _draw_huffman_array_process(self, painter):
        struct_array = self.data_structure
        painter.save()
        painter.setPen(QPen(QColor(156, 163, 175), 2))

        for idx, pos_data in self.node_positions.items():
            if idx < 0 or idx >= len(struct_array): continue
            node = struct_array[idx]
            current_pos = self._get_safe_pos(idx)
            if not current_pos: continue
            cx, cy = current_pos

            if node.left != -1:
                l_pos = self._get_safe_pos(node.left)
                if l_pos:
                    lx, ly = l_pos
                    painter.drawLine(self._safe_point(cx, cy), self._safe_point(lx, ly))

            if node.right != -1:
                r_pos = self._get_safe_pos(node.right)
                if r_pos:
                    rx, ry = r_pos
                    painter.drawLine(self._safe_point(cx, cy), self._safe_point(rx, ry))
        painter.restore()

        for idx in self.node_positions.keys():
            if idx < 0 or idx >= len(struct_array): continue
            node = struct_array[idx]
            pos = self._get_safe_pos(idx)
            if pos: self._draw_single_huffman_struct_node(painter, node, pos[0], pos[1])

    def _draw_single_huffman_struct_node(self, painter, node, x, y):
        radius = self.node_radius
        painter.save()
        if node.left == -1 and node.right == -1:
            bg_color = QColor(167, 243, 208)
        else:
            bg_color = QColor(254, 215, 170)
        anim_targets = self.anim_state.get('targets', {})
        active_parent_idx = self.anim_state.get('active_parent_idx', -1)
        if (node.index in anim_targets) or (node.index == active_parent_idx): bg_color = QColor(250, 204, 21)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(31, 41, 55), 2))

        center = self._safe_point(x, y)
        painter.drawEllipse(center, radius, radius)

        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        if node.data:
            disp = f"{node.data}\n{node.weight}"
        else:
            disp = f"{node.weight}"

        text_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        painter.drawText(text_rect, Qt.AlignCenter, disp)
        painter.restore()

    def drawArrow(self, painter, start_x, start_y, end_x, end_y, color=QColor(59, 130, 246), opacity=1.0, progress=1.0):
        if progress <= 0.01 or opacity <= 0.01: return
        painter.save()
        painter.setOpacity(opacity)
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(color))
        dx = start_x + (end_x - start_x) * progress
        dy = start_y + (end_y - start_y) * progress

        p1 = self._safe_point(start_x, start_y)
        p2 = self._safe_point(dx, dy)
        painter.drawLine(p1, p2)

        if progress > 0.8:
            ang = math.atan2(end_y - start_y, end_x - start_x) * 180 / math.pi
            sz = 10
            # 安全转换点
            ax = dx - sz * math.cos(math.radians(ang + 30))
            ay = dy - sz * math.sin(math.radians(ang + 30))
            bx = dx - sz * math.cos(math.radians(ang - 30))
            by = dy - sz * math.sin(math.radians(ang - 30))

            head = QPolygonF()
            head.append(QPointF(float(dx), float(dy)))
            head.append(QPointF(float(ax), float(ay)))
            head.append(QPointF(float(bx), float(by)))
            painter.drawPolygon(head)
        painter.restore()

    def _draw_bst_overlay(self, painter):
        state = self.anim_state
        target_val = state.get('target_val')
        curr_node = state.get('current_node')
        next_node = state.get('next_node')
        progress = state.get('progress', 0.0)
        status = state.get('status')

        sx, sy = 0, 0
        if not curr_node:
            if status == 'insert_found' and getattr(self.data_structure, 'root', None) is None:
                sx, sy = self.width() // 2, 50
            else:
                return
        else:
            pos = self.current_frame_node_pos.get(curr_node)
            if not pos: return
            sx, sy = pos

        draw_x, draw_y = sx, sy

        if status == 'move' and next_node:
            end_pos = self.current_frame_node_pos.get(next_node)
            if end_pos:
                ex, ey = end_pos
                draw_x = lerp(sx, ex, progress)
                draw_y = lerp(sy, ey, progress)
        elif status == 'insert_found':
            draw_y += 40

        painter.save()
        bg_color = QColor(59, 130, 246)
        if status == 'found':
            bg_color = QColor(34, 197, 94)
        elif status == 'not_found':
            bg_color = QColor(239, 68, 68)

        center = self._safe_point(draw_x, draw_y)
        painter.translate(center)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(bg_color.red(), bg_color.green(), bg_color.blue(), 150))
        painter.drawEllipse(QPoint(0, 0), 18, 18)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(QRectF(-18, -18, 36, 36), Qt.AlignCenter, str(target_val))
        painter.restore()


class BaseVisualizer(QWidget):
    response_received = pyqtSignal(str)

    def __init__(self, main_window=None, last_window=None, title="数据结构可视化工具"):
        super().__init__()
        self.main_window = main_window
        self.last_window = last_window
        self.structure_type_mapping = {"栈 (Stack) 可视化工具": "Stack",
                                       "顺序表 (SequenceList) 可视化工具": "SequenceList",
                                       "链表 (LinkedList) 可视化工具": "LinkedList", "二叉树可视化工具": "BinaryTree",
                                       "哈夫曼树可视化工具": "HuffmanTree",
                                       "二叉搜索树 (BST) 可视化工具": "BinarySearchTree"}
        self.current_structure_type = self.structure_type_mapping.get(title, "")
        self.data_structure = None
        self.animation_speed = 500
        self.animating = False
        self.current_operation = None
        self.operation_data = None
        self.highlighted_index = -1
        self.title = title
        self.recent_files = []
        self.max_recent_files = 5
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.recent_files_file = os.path.join(current_dir, "recent_files.json")
        self.load_recent_files()

        # --- 新增属性：动画开关 ---
        self.anim_enabled = True

        self.init_ui()
        self.setWindowState(Qt.WindowMaximized)
        self.update_recent_files_display()
        self.init_sound_effects()

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        # 假设文件路径正确
        self.click_sound.setSource(
            QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)

    def play_click_sound(self):
        if not self.click_sound.source().isEmpty():
            self.click_sound.play()

    def init_ui(self):
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setLayout(root_layout)

        # === 侧边栏配置 ===
        sidebar = QWidget()
        # [修改点1] 减小宽度，适应小屏幕
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet("background-color: #f3f4f6; border-right: 1px solid #e5e7eb;")

        sidebar_layout = QVBoxLayout(sidebar)
        # [修改点2] 减小边距和间距，防止高度溢出
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(10)

        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            "font-family: 'Microsoft YaHei'; font-size: 20px; font-weight: bold; color: #111827; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        sidebar_layout.addWidget(title_label)

        # === 核心操作区域 (使用 QScrollArea) ===
        control_group = QGroupBox("核心操作")
        # [修改点3] 适当减小最小高度限制
        control_group.setMinimumHeight(180)
        control_group.setStyleSheet(STYLES["group_box"])

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(2, 2, 2, 2)

        scroll_layout.addLayout(self._create_input_layout())
        scroll_layout.addLayout(self._create_button_layout())
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)

        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2, 15, 2, 2)
        group_layout.addWidget(scroll)
        control_group.setLayout(group_layout)

        # 核心操作区也是主要区域，给予拉伸权重 1
        sidebar_layout.addWidget(control_group, 1)
        # ==========================================

        # === 文件管理 ===
        file_group = QGroupBox("文件管理")
        file_group.setStyleSheet(STYLES["group_box"])
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(10, 15, 10, 10)
        file_layout.setSpacing(8)
        btn_io_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存结构")
        self.save_btn.setStyleSheet(STYLES["btn_success"])
        self.save_btn.clicked.connect(self.save_structure)
        self.load_btn = QPushButton("打开结构")
        self.load_btn.setStyleSheet(STYLES["btn_primary"])
        self.load_btn.clicked.connect(self.load_structure)
        btn_io_layout.addWidget(self.save_btn)
        btn_io_layout.addWidget(self.load_btn)
        file_layout.addLayout(btn_io_layout)
        file_group.setLayout(file_layout)
        sidebar_layout.addWidget(file_group, 0)

        # === 最近保存 (ScrollArea) ===
        recent_group = QGroupBox("最近保存")
        recent_group.setStyleSheet(STYLES["group_box"])
        recent_group_layout = QVBoxLayout()
        recent_group_layout.setContentsMargins(1, 15, 1, 1)

        self.recent_list_widget = QWidget()
        self.recent_list_widget.setStyleSheet("background-color: white;")
        self.recent_list_layout = QVBoxLayout(self.recent_list_widget)
        self.recent_list_layout.setSpacing(4)
        self.recent_list_layout.setContentsMargins(5, 5, 5, 5)
        self.recent_list_layout.setAlignment(Qt.AlignTop)

        scroll_recent = QScrollArea()
        scroll_recent.setWidgetResizable(True)
        scroll_recent.setWidget(self.recent_list_widget)
        # 稍微减小高度
        scroll_recent.setMinimumHeight(100)
        scroll_recent.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        recent_group_layout.addWidget(scroll_recent)
        recent_group.setLayout(recent_group_layout)

        # 给最近保存列表也一点拉伸权重，但比核心操作小
        sidebar_layout.addWidget(recent_group, 1)

        # === DSL 脚本控制区 ===
        dsl_group = QGroupBox("DSL脚本控制区")
        dsl_group.setStyleSheet(STYLES["group_box"])
        dsl_layout = QVBoxLayout(dsl_group)
        # 减小边距
        dsl_layout.setContentsMargins(10, 15, 10, 10)

        self.dsl_input = QTextEdit()
        self.dsl_input.setPlaceholderText("在此输入指令，例如：\nBUILD: 10, 20, 30\nINSERT: 40\nDELETE: 10")
        self.dsl_input.setStyleSheet("border: 1px solid #d1d5db; border-radius: 6px; background-color: #f9fafb;")
        # [修改点4] 限制高度，节省空间
        self.dsl_input.setMaximumHeight(80)

        run_btn = QPushButton("执行脚本")
        run_btn.setStyleSheet(STYLES["btn_primary"])
        run_btn.clicked.connect(self.run_dsl)

        dsl_layout.addWidget(self.dsl_input)
        dsl_layout.addWidget(run_btn)
        dsl_group.setLayout(dsl_layout)

        sidebar_layout.addWidget(dsl_group, 0)

        # === 设置区域 ===
        settings_group = QGroupBox("设置")
        settings_group.setStyleSheet(STYLES["group_box"])
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(10, 15, 10, 10)
        settings_layout.setSpacing(8)

        # 动画开关
        self.anim_checkbox = QCheckBox("启用动画效果")
        self.anim_checkbox.setChecked(self.anim_enabled)
        self.anim_checkbox.stateChanged.connect(self._toggle_animation)
        self.anim_checkbox.setStyleSheet("font-family: 'Microsoft YaHei'; color: #4b5563; padding-left: 0;")
        settings_layout.addWidget(self.anim_checkbox)

        # 速度控制
        speed_layout = QHBoxLayout()
        speed_lbl = QLabel("动画速度(ms):")
        speed_lbl.setStyleSheet("font-family: 'Microsoft YaHei'; color: #4b5563;")
        speed_layout.addWidget(speed_lbl)
        self.speed_slider = QLineEdit(str(self.animation_speed))
        self.speed_slider.setStyleSheet(STYLES["input"])
        self.speed_slider.returnPressed.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        settings_layout.addLayout(speed_layout)

        # 返回按钮
        ret_layout = QHBoxLayout()
        self.button_return = QPushButton("返回上一级")
        self.button_return.clicked.connect(self.on_button_return_clicked)
        self.button_return_main = QPushButton("返回主界面")
        self.button_return_main.clicked.connect(self.on_button_return_main_clicked)
        for btn in [self.button_return, self.button_return_main]:
            btn.setStyleSheet(STYLES["btn_secondary"])
            ret_layout.addWidget(btn)
        settings_layout.addLayout(ret_layout)

        settings_group.setLayout(settings_layout)
        sidebar_layout.addWidget(settings_group, 0)

        # 移除底部的 addStretch，让上面的 addWidget(..., 1) 自动分配空间
        # sidebar_layout.addStretch()

        # === 右侧可视化内容区域 ===
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        # 减小外边距
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        visual_box = QGroupBox("可视化演示")
        visual_box.setStyleSheet(
            "QGroupBox { background-color: white; border: 1px solid #d1d5db; border-radius: 8px; font-size: 16px; font-weight: bold; color: #1f2937; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; top: 10px; }")
        vb_layout = QVBoxLayout()
        vb_layout.setContentsMargins(5, 30, 5, 5)
        self.visual_area = VisualArea(self)
        vb_layout.addWidget(self.visual_area)
        visual_box.setLayout(vb_layout)
        content_layout.addWidget(visual_box)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(
            "background: #eff6ff; color: #1e40af; padding: 10px; border-radius: 6px; border: 1px solid #bfdbfe; font-family: 'Microsoft YaHei'; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.status_label)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content_widget)

    # --- 新增方法 ---
    def _toggle_animation(self, state):
        self.anim_enabled = state == Qt.Checked
        # 如果禁用动画，强制停止当前动画
        if not self.anim_enabled and hasattr(self, 'anim_timer') and self.anim_timer.isActive():
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.update_display()
        self.status_label.setText(f"动画 {'已启用' if self.anim_enabled else '已禁用'}")

    # ----------------

    def _create_input_layout(self):
        raise NotImplementedError

    def _create_button_layout(self):
        raise NotImplementedError

    def on_button_return_main_clicked(self):
        self.play_click_sound()
        self.back_to_main()

    def on_button_return_clicked(self):
        self.play_click_sound()
        if self.last_window:
            self.last_window.show()
        self.close()

    def back_to_main(self):
        if self.main_window:
            self.main_window.show()
        self.close()

    def update_display(self):
        try:
            self.visual_area.update_visualization(self.data_structure, self.highlighted_index)
            self._update_status_text()
        except Exception as e:
            print(f"Display Error: {e}")

    def _update_status_text(self):
        raise NotImplementedError

    def update_speed(self):
        try:
            val = int(self.speed_slider.text())
            if val > 0:
                self.animation_speed = val
        except:
            pass
        self.speed_slider.setText(str(self.animation_speed))

    def load_recent_files(self):
        try:
            if os.path.exists(self.recent_files_file):
                with open(self.recent_files_file, 'r', encoding='utf-8') as f:
                    self.recent_files = json.load(f)
            else:
                self.recent_files = []
        except:
            self.recent_files = []

    def save_recent_files(self):
        try:
            with open(self.recent_files_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, indent=2, ensure_ascii=False)
        except:
            pass

    def add_to_recent_files(self, filename):
        self.recent_files = [f for f in self.recent_files if f['path'] != filename]
        self.recent_files.insert(0, {'path': filename, 'name': os.path.basename(filename),
                                     'time': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                     'type': self.current_structure_type})
        self.recent_files = self.recent_files[:self.max_recent_files]
        self.save_recent_files()
        self.update_recent_files_display()

    def update_recent_files_display(self):
        for i in reversed(range(self.recent_list_layout.count())):
            self.recent_list_layout.itemAt(i).widget().deleteLater()
        filtered = [f for f in self.recent_files if f.get('type') == self.current_structure_type]
        if not filtered:
            self.recent_list_layout.addWidget(QLabel("暂无记录"))
            return
        for f in filtered:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(12, 10, 12, 10)
            item_layout.setSpacing(4)
            name_lbl = QLabel(f.get('name', 'Unknown'))
            name_lbl.setStyleSheet(
                "font-family: 'Microsoft YaHei'; font-weight: bold; color: #1f2937; font-size: 13px;")
            time_lbl = QLabel(f.get('time', ''))
            time_lbl.setStyleSheet("font-size: 11px; color: #6b7280;")
            item_layout.addWidget(name_lbl)
            item_layout.addWidget(time_lbl)
            item_widget.setStyleSheet(
                "QWidget { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; } QWidget:hover { background-color: #eff6ff; border-color: #3b82f6; }")
            item_widget.setCursor(Qt.PointingHandCursor)
            item_widget.mousePressEvent = lambda e, p=f['path']: self.load_recent_file(p)
            self.recent_list_layout.addWidget(item_widget)

    def load_recent_file(self, filepath):
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "错误", f"文件不存在:\n{filepath}")
            return
        try:
            from model import DataStructureManager
            obj = DataStructureManager.load_structure(filepath)
            if obj:
                self.data_structure = obj
                self.visual_area.set_data_structure(obj)
                self.update_display()
                self.status_label.setText(f"已加载: {os.path.basename(filepath)}")
            else:
                QMessageBox.warning(self, "错误", "文件加载失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载异常: {e}")

    def save_structure(self):
        fname, _ = QFileDialog.getSaveFileName(self, "保存", "", "JSON (*.json)")
        if fname:
            if not fname.endswith('.json'):
                fname += '.json'
            try:
                from model import DataStructureManager
                if DataStructureManager.save_structure(self.data_structure, fname):
                    self.add_to_recent_files(fname)
                    QMessageBox.information(self, "成功", "保存成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", str(e))

    def load_structure(self):
        fname, _ = QFileDialog.getOpenFileName(self, "打开", "", "JSON (*.json)")
        if fname:
            try:
                from model import DataStructureManager
                obj = DataStructureManager.load_structure(fname)
                if obj:
                    self.data_structure = obj
                    self.visual_area.set_data_structure(obj)
                    self.update_display()
                    self.add_to_recent_files(fname)
            except Exception as e:
                QMessageBox.warning(self, "错误", str(e))

    def run_dsl(self):
        script = self.dsl_input.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "提示", "脚本内容不能为空")
            return

        handler = DSLHandler(self)

        # --- 传递动画标志：0-执行动画，1-不执行动画 ---
        flag = 0 if self.anim_enabled else 1
        result = handler.execute_script(script, flag)

        if result == "执行成功":
            # 无论是否执行动画，都需要最终刷新
            self.update_display()
            self.status_label.setText("DSL 脚本执行完毕")
        else:
            QMessageBox.warning(self, "执行错误", result)


class StackVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "栈 (Stack) 可视化工具")
        self.data_structure = Stack()
        self.visual_area.set_data_structure(self.data_structure)
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)

    def _create_input_layout(self):
        l = QHBoxLayout()
        self.push_input = QLineEdit()
        self.push_input.setStyleSheet(STYLES["input"])
        self.push_input.setPlaceholderText("元素值")
        btn = QPushButton("入栈")
        btn.setStyleSheet(STYLES["btn_success"])
        btn.clicked.connect(self.handle_push)
        l.addWidget(self.push_input)
        l.addWidget(btn)
        return l

    def _create_button_layout(self):
        l = QHBoxLayout()
        l.setSpacing(15)
        b1 = QPushButton("出栈")
        b1.clicked.connect(self.handle_pop)
        b1.setStyleSheet(STYLES["btn_warning"])
        b2 = QPushButton("随机生成")
        b2.clicked.connect(self.random_build)
        b2.setStyleSheet(STYLES["btn_random"])
        b3 = QPushButton("清空")
        b3.clicked.connect(self.handle_clear)
        b3.setStyleSheet(STYLES["btn_danger"])
        l.addWidget(b1)
        l.addWidget(b2)
        l.addWidget(b3)
        return l

    def handle_push(self):
        try:
            text = self.push_input.text()
            if not text:
                return

            if self.anim_enabled:
                self.data_structure.push(text)  # 先入栈，后动画
                self.push_input.clear()
                self.visual_area.anim_state = {'type': 'push', 'index': self.data_structure.length() - 1, 'scale': 0.1}
                self.anim_timer.setInterval(30)
                self.anim_timer.start()
                self.update_display()
            else:
                self.data_structure.push(text)
                self.push_input.clear()
                self.update_display()
                self.status_label.setText(f"已入栈: {text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def handle_pop(self):
        try:
            if self.data_structure.is_empty():
                QMessageBox.warning(self, "错误", "栈已空")
                return

            if self.anim_enabled:
                self.visual_area.anim_state = {'type': 'highlight', 'index': self.data_structure.length() - 1,
                                               'offset_y': 0}
                self.update_display()
                QTimer.singleShot(500, self.start_pop_animation)
            else:
                val = self.data_structure.pop()
                self.update_display()
                self.status_label.setText(f"已出栈: {val}")

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def start_pop_animation(self):
        self.visual_area.anim_state = {'type': 'pop', 'index': self.data_structure.length() - 1,
                                       'offset_y': 0}
        self.anim_timer.setInterval(30)
        self.anim_timer.start()

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state:
            self.anim_timer.stop()
            return

        # 确保动画开关开启
        if not self.anim_enabled:
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.update_display()
            return

        if state['type'] == 'push':
            state['scale'] += 0.1
            if state['scale'] >= 1.0:
                state['scale'] = 1.0
                self.anim_timer.stop()
                self.visual_area.anim_state = {}
                self.status_label.setText(f"入栈完成, 当前栈深: {self.data_structure.length()}")
        elif state['type'] == 'pop':
            state['offset_y'] -= 15
            if state['offset_y'] < -300:
                self.anim_timer.stop()
                self.visual_area.anim_state = {}
                self.data_structure.pop()  # 动画结束后才真正移除数据
                self.status_label.setText(f"出栈完成, 当前栈深: {self.data_structure.length()}")
        self.update_display()

    def handle_clear(self):
        self.data_structure.clear()
        self.update_display()
        self.status_label.setText("栈已清空")

    def random_build(self):
        self.data_structure.clear()
        [self.data_structure.push(random.randint(1, 100)) for _ in range(random.randint(5, 10))]
        self.update_display()
        self.status_label.setText("已随机生成栈")

    def _update_status_text(self):
        self.status_label.setText(f"当前栈深: {self.data_structure.length()}")


class SequenceListVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "顺序表 (SequenceList) 可视化工具")
        self.data_structure = SequenceList()
        self.visual_area.set_data_structure(self.data_structure)
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)

    def _create_input_layout(self):
        l = QVBoxLayout()
        l.setSpacing(12)
        row1 = QHBoxLayout()
        self.input_val = QLineEdit()
        self.input_val.setStyleSheet(STYLES["input"])
        self.input_val.setPlaceholderText("数值 (Value)")
        self.input_idx = QLineEdit()
        self.input_idx.setStyleSheet(STYLES["input"])
        self.input_idx.setPlaceholderText("索引 (Index)")
        self.input_idx.setFixedWidth(100)
        row1.addWidget(QLabel("值:"))
        row1.addWidget(self.input_val)
        row1.addWidget(QLabel("下标:"))
        row1.addWidget(self.input_idx)
        l.addLayout(row1)
        return l

    def _create_button_layout(self):
        grid = QGridLayout()
        grid.setSpacing(12)
        btn_insert = QPushButton("插入")
        btn_insert.setStyleSheet(STYLES["btn_success"])
        btn_insert.clicked.connect(self.handle_insert)
        btn_delete = QPushButton("删除")
        btn_delete.setStyleSheet(STYLES["btn_warning"])
        btn_delete.clicked.connect(self.handle_delete)
        btn_locate = QPushButton("查找")
        btn_locate.setStyleSheet(STYLES["btn_primary"])
        btn_locate.clicked.connect(self.handle_locate)
        btn_rand = QPushButton("随机生成")
        btn_rand.setStyleSheet(STYLES["btn_random"])
        btn_rand.clicked.connect(self.random_build)
        btn_clear = QPushButton("清空")
        btn_clear.setStyleSheet(STYLES["btn_danger"])
        btn_clear.clicked.connect(self.handle_clear)
        grid.addWidget(btn_insert, 0, 0)
        grid.addWidget(btn_delete, 0, 1)
        grid.addWidget(btn_locate, 1, 0)
        grid.addWidget(btn_rand, 1, 1)
        grid.addWidget(btn_clear, 2, 0, 1, 2)
        return grid

    def _get_val_from_input(self, text):
        try:
            return int(text)
        except:
            return text

    def push_input_clear(self):
        self.input_val.clear()
        self.input_idx.clear()

    # --- 插入操作修改 ---
    def handle_insert(self):
        try:
            text = self.input_val.text()
            if not text:
                QMessageBox.warning(self, "错误", "请输入数值")
                return
            val = self._get_val_from_input(text)

            if self.input_idx.text():
                idx = int(self.input_idx.text())
            else:
                idx = self.data_structure.length()

            if idx < 0 or idx > self.data_structure.length():
                QMessageBox.warning(self, "错误", "索引越界")
                return

            self.push_input_clear()
            self.highlighted_index = -1

            if self.anim_enabled:
                if idx == self.data_structure.length() or self.data_structure.is_empty():
                    start_phase = 'move_in'
                else:
                    start_phase = 'shift_forward'

                self.visual_area.anim_state = {
                    'type': 'seq_insert',
                    'target_idx': idx,
                    'new_val': val,
                    'phase': start_phase,
                    'shift_index': self.data_structure.length() - 1,
                    'progress': 0.0,
                    'original_length': self.data_structure.length()
                }

                self.anim_timer.setInterval(30)
                self.anim_timer.start()
                self.status_label.setText(f"元素 {val} 悬浮在索引 {idx}，准备位移...")
            else:
                # 禁用动画：直接插入
                self.data_structure.insert(idx, val)
                self.update_display()
                self.status_label.setText(f"已插入: {val} @ {idx}")

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    # --- 删除操作修改 ---
    def handle_delete(self):
        val_text = self.input_val.text().strip()
        idx_text = self.input_idx.text().strip()

        if not val_text and not idx_text:
            QMessageBox.warning(self, "错误", "请填写【数值】或【索引】进行删除")
            return

        self.push_input_clear()
        self.highlighted_index = -1

        try:
            target_idx = -1
            if idx_text:
                target_idx = int(idx_text)
                if target_idx < 0 or target_idx >= self.data_structure.length():
                    QMessageBox.warning(self, "错误", "索引越界")
                    return

                if self.anim_enabled:
                    self.start_deletion_phase(target_idx)
                else:
                    # 禁用动画：直接删除
                    val = self.data_structure.get(target_idx)
                    self.data_structure.remove(target_idx)
                    self.update_display()
                    self.status_label.setText(f"已删除: {val} @ {target_idx}")
            else:
                val = self._get_val_from_input(val_text)
                target_idx = self.data_structure.locate(val)

                if not self.anim_enabled:
                    if target_idx != -1:
                        self.data_structure.remove(target_idx)
                        self.update_display()
                        self.status_label.setText(f"已删除: {val} @ {target_idx}")
                    else:
                        QMessageBox.information(self, "查找结果", f"未找到元素: {val}")
                    return

                # 启用动画：按值删除，先启动查找动画
                self.visual_area.anim_state = {
                    'type': 'seq_search',
                    'target_val': val,
                    'current_idx': 0,
                    'progress': 0.0
                }
                self.anim_timer.setInterval(400)
                self.anim_timer.start()
                self.status_label.setText(f"开始查找元素 {val}...")

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def start_deletion_phase(self, idx):
        """开始执行删除动画的各个阶段"""
        if self.data_structure.is_empty(): return

        self.visual_area.anim_state = {
            'type': 'seq_delete',
            'target_idx': idx,
            'phase': 'flash_target',
            'progress': 0.0,
            'flash_count': 0
        }
        self.anim_timer.setInterval(100)
        self.anim_timer.start()
        self.status_label.setText(f"找到待删除元素，索引: {idx}，准备删除...")

    # --- 动画更新逻辑修改 (降低速度，修正跳跃) ---
    def update_animation(self):
        state = self.visual_area.anim_state
        if not state:
            self.anim_timer.stop()
            self.update_display()
            return

        # 确保动画开关开启
        if not self.anim_enabled:
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.update_display()
            return

        anim_type = state['type']

        if anim_type == 'seq_insert':
            self.anim_timer.setInterval(30)
            state['progress'] += 0.04

            if state['phase'] == 'shift_forward':
                if state['progress'] >= 1.0:
                    state['progress'] = 0.0
                    state['shift_index'] -= 1

                    if state['shift_index'] < state['target_idx']:
                        state['phase'] = 'move_in'
                        self.status_label.setText("腾出空间，新元素移入...")

            elif state['phase'] == 'move_in':
                if state['progress'] >= 1.0:
                    self.anim_timer.stop()
                    self.data_structure.insert(state['target_idx'], state['new_val'])
                    self.visual_area.anim_state = {}
                    self.update_display()
                    self.status_label.setText(f"插入完成: {state['new_val']} @ {state['target_idx']}")
                    return

        elif anim_type == 'seq_search':
            self.highlighted_index = state['current_idx']
            if state['current_idx'] < self.data_structure.length():
                curr_val = self.data_structure.get(state['current_idx'])
                self.status_label.setText(f"查找中... 检查索引 {state['current_idx']} (值: {curr_val})")

                if str(curr_val) == str(state['target_val']):
                    self.anim_timer.stop()
                    self.highlighted_index = -1
                    self.start_deletion_phase(state['current_idx'])
                    return
                else:
                    state['current_idx'] += 1
            else:
                self.anim_timer.stop()
                self.highlighted_index = -1
                self.visual_area.anim_state = {}
                self.update_display()
                QMessageBox.information(self, "查找结果", f"未找到元素: {state['target_val']}")
                return

        elif anim_type == 'seq_delete':
            self.anim_timer.setInterval(30)
            state['progress'] += 0.04

            if state['phase'] == 'flash_target':
                state['flash_count'] += 1
                if state['flash_count'] >= 15:
                    state['progress'] = 0.0
                    state['phase'] = 'move_out'
                    self.anim_timer.setInterval(30)
                    self.status_label.setText("目标元素移出...")
                else:
                    self.anim_timer.setInterval(100)

            elif state['phase'] == 'move_out':
                if state['progress'] >= 1.0:
                    state['progress'] = 0.0
                    self.data_structure.remove(state['target_idx'])

                    if state['target_idx'] >= self.data_structure.length():
                        state['phase'] = 'cleanup'
                    else:
                        state['phase'] = 'shift_backward'
                        state['shift_index'] = state['target_idx']
                        self.status_label.setText("后置元素向前位移...")

            elif state['phase'] == 'shift_backward':
                if state['progress'] >= 1.0:
                    state['progress'] = 0.0
                    state['shift_index'] += 1

                    if state['shift_index'] >= self.data_structure.length():
                        state['phase'] = 'cleanup'

            elif state['phase'] == 'cleanup':
                self.anim_timer.stop()
                self.visual_area.anim_state = {}
                self.update_display()
                self.status_label.setText("删除并位移完成")
                return

        self.update_display()

    def handle_locate(self):
        text = self.input_val.text()
        if not text:
            QMessageBox.warning(self, "错误", "请输入要查找的值")
            return
        val = self._get_val_from_input(text)
        idx = self.data_structure.locate(val)
        if idx != -1:
            self.highlighted_index = idx
            self.update_display()
            self.status_label.setText(f"找到元素 {val} 在索引: {idx}")
        else:
            self.highlighted_index = -1
            self.update_display()
            QMessageBox.information(self, "查找结果", f"未找到元素: {val}")

    def handle_clear(self):
        self.data_structure.clear()
        self.highlighted_index = -1
        self.update_display()
        self.status_label.setText("顺序表已清空")

    def random_build(self):
        self.data_structure.clear()
        [self.data_structure.insert(i, random.randint(1, 100)) for i in range(random.randint(5, 10))]
        self.update_display()
        self.status_label.setText("已随机生成顺序表")

    def _update_status_text(self):
        self.status_label.setText(f"顺序表长度: {self.data_structure.length()}")


class LinkedListVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "链表 (LinkedList) 可视化工具")
        self.data_structure = LinkedList()
        self.visual_area.set_data_structure(self.data_structure)
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)

    def _create_input_layout(self):
        l = QVBoxLayout()
        l.setSpacing(12)
        row1 = QHBoxLayout()
        self.input_val = QLineEdit()
        self.input_val.setStyleSheet(STYLES["input"])
        self.input_val.setPlaceholderText("节点值")
        self.input_idx = QLineEdit()
        self.input_idx.setStyleSheet(STYLES["input"])
        self.input_idx.setPlaceholderText("索引")
        self.input_idx.setFixedWidth(100)
        row1.addWidget(QLabel("值:"))
        row1.addWidget(self.input_val)
        row1.addWidget(QLabel("索引:"))
        row1.addWidget(self.input_idx)
        l.addLayout(row1)
        return l

    def _create_button_layout(self):
        grid = QGridLayout()
        grid.setSpacing(12)
        btn_head = QPushButton("头插")
        btn_head.setStyleSheet(STYLES["btn_success"])
        btn_head.clicked.connect(self.handle_head_insert)
        btn_tail = QPushButton("尾插")
        btn_tail.setStyleSheet(STYLES["btn_success"])
        btn_tail.clicked.connect(self.handle_tail_insert)
        btn_insert = QPushButton("指定插入")
        btn_insert.setStyleSheet(STYLES["btn_primary"])
        btn_insert.clicked.connect(self.handle_insert_idx)
        btn_del = QPushButton("删除")
        btn_del.setStyleSheet(STYLES["btn_warning"])
        btn_del.clicked.connect(self.handle_delete)
        btn_loc = QPushButton("查找")
        btn_loc.setStyleSheet(STYLES["btn_primary"])
        btn_loc.clicked.connect(self.handle_locate)
        btn_rand = QPushButton("随机生成")
        btn_rand.setStyleSheet(STYLES["btn_random"])
        btn_rand.clicked.connect(self.random_build)
        btn_clr = QPushButton("清空")
        btn_clr.setStyleSheet(STYLES["btn_danger"])
        btn_clr.clicked.connect(self.handle_clear)
        grid.addWidget(btn_head, 0, 0)
        grid.addWidget(btn_tail, 0, 1)
        grid.addWidget(btn_insert, 1, 0)
        grid.addWidget(btn_del, 1, 1)
        grid.addWidget(btn_loc, 2, 0)
        grid.addWidget(btn_rand, 2, 1)
        grid.addWidget(btn_clr, 3, 0, 1, 2)
        return grid

    def _get_val_from_input(self, text):
        try:
            return int(text)
        except:
            return text

    def start_insert_animation(self, idx, val):
        if not self.anim_enabled:
            self.data_structure.insert(idx, val)
            self.update_display()
            self.status_label.setText(f"已插入: {val} @ {idx}")
            return

        start_phase = 'shift'
        if idx >= self.data_structure.length():
            start_phase = 'appear'
        self.visual_area.anim_state = {'type': 'linked_insert', 'target_idx': idx, 'new_val': val, 'phase': start_phase,
                                       'progress': 0.0}
        self.anim_timer.setInterval(20)
        self.anim_timer.start()

    def start_delete_animation(self, idx):
        if not self.anim_enabled:
            val = self.data_structure.remove(idx)
            self.update_display()
            self.status_label.setText(f"已删除: {val} @ {idx}")
            return

        self.visual_area.anim_state = {'type': 'linked_delete', 'target_idx': idx, 'phase': 'fade_prev_link',
                                       'progress': 0.0}
        self.anim_timer.setInterval(20)
        self.anim_timer.start()

    def start_search_animation(self, val):
        if not self.anim_enabled:
            idx = self.data_structure.locate(val)
            if idx != -1:
                self.highlighted_index = idx
                self.status_label.setText(f"找到元素 {val} 在索引: {idx}")
            else:
                self.highlighted_index = -1
                QMessageBox.information(self, "提示", "未找到元素")
            self.update_display()
            return

        self.visual_area.anim_state = {'type': 'linked_search', 'current_idx': 0, 'target_val': val,
                                       'phase': 'scanning', 'flash_time': 0}
        self.visual_area.highlighted_index = -1
        self.update_display()
        self.anim_timer.setInterval(400)
        self.anim_timer.start()

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state:
            self.anim_timer.stop()
            return

        # 确保动画开关开启
        if not self.anim_enabled:
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.update_display()
            return

        # Search Animation
        if state['type'] == 'linked_search':
            if state['phase'] == 'scanning':
                idx = state['current_idx']
                if idx < self.data_structure.length():
                    self.visual_area.highlighted_index = -1
                    curr_val = self.data_structure.get(idx)
                    if str(curr_val) == str(state['target_val']):
                        state['phase'] = 'found'
                        self.highlighted_index = idx
                        self.anim_timer.setInterval(100)
                        self.status_label.setText(f"找到元素 {curr_val} 在索引 {idx}")
                    else:
                        state['current_idx'] += 1
                else:
                    self.highlighted_index = -1
                    self.anim_timer.stop()
                    self.visual_area.anim_state = {}
                    self.update_display()
                    QMessageBox.information(self, "提示", "未找到元素")
                    return
            elif state['phase'] == 'found':
                state['flash_time'] += 1
                if state['flash_time'] > 30:
                    self.anim_timer.stop()
                    self.visual_area.anim_state = {}
                    self.highlighted_index = -1
                    self.update_display()
                    return
            self.update_display()
            if state['phase'] == 'found':
                self.status_label.setText(f"找到元素 {state['target_val']} 在索引 {state['current_idx']}")
            return

        # Insert/Delete Animation
        state['progress'] += 0.05
        if state['progress'] >= 1.0:
            state['progress'] = 0.0
            if state['type'] == 'linked_insert':
                curr = state['phase']
                if curr == 'shift':
                    state['phase'] = 'appear'
                elif curr == 'appear':
                    if state['target_idx'] < self.data_structure.length():
                        state['phase'] = 'link_next'
                    elif state['target_idx'] > 0:
                        state['phase'] = 'link_prev'
                    else:
                        state['phase'] = 'lift'
                elif curr == 'link_next':
                    if state['target_idx'] > 0:
                        state['phase'] = 'link_prev'
                    else:
                        state['phase'] = 'lift'
                elif curr == 'link_prev':
                    state['phase'] = 'lift'
                elif curr == 'lift':
                    self.data_structure.insert(state['target_idx'], state['new_val'])
                    self.visual_area.anim_state = {}
                    self.anim_timer.stop()
                    self.status_label.setText("插入完成")
            elif state['type'] == 'linked_delete':
                curr = state['phase']
                if curr == 'fade_prev_link':
                    state['phase'] = 'drop'
                elif curr == 'drop':
                    state['phase'] = 'connect_bypass'
                elif curr == 'connect_bypass':
                    state['phase'] = 'fade_next_link'
                elif curr == 'fade_next_link':
                    state['phase'] = 'close'
                elif curr == 'close':
                    val = self.data_structure.remove(state['target_idx'])
                    self.visual_area.anim_state = {}
                    self.anim_timer.stop()
                    self.status_label.setText(f"删除完成: {val}")
        self.update_display()

    def handle_head_insert(self):
        text = self.input_val.text()
        if text:
            val = self._get_val_from_input(text)
            self.start_insert_animation(0, val)
            self.input_val.clear()
        else:
            QMessageBox.warning(self, "错误", "请输入值")

    def handle_tail_insert(self):
        text = self.input_val.text()
        if text:
            val = self._get_val_from_input(text)
            idx = self.data_structure.length()
            self.start_insert_animation(idx, val)
            self.input_val.clear()
        else:
            QMessageBox.warning(self, "错误", "请输入值")

    def handle_insert_idx(self):
        try:
            text = self.input_val.text()
            if not text:
                raise ValueError("请输入值")
            val = self._get_val_from_input(text)

            idx_text = self.input_idx.text()
            if not idx_text:
                raise ValueError("请输入索引")

            idx = int(idx_text)
            if idx < 0 or idx > self.data_structure.length():
                QMessageBox.warning(self, "错误", "索引越界")
                return

            self.start_insert_animation(idx, val)
            self.input_val.clear()
            self.input_idx.clear()

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def handle_delete(self):
        try:
            idx_text = self.input_idx.text()
            val_text = self.input_val.text()

            target_idx = -1

            if idx_text:
                target_idx = int(idx_text)
                if target_idx < 0 or target_idx >= self.data_structure.length():
                    QMessageBox.warning(self, "错误", "索引越界")
                    return
            elif val_text:
                val = self._get_val_from_input(val_text)
                target_idx = self.data_structure.locate(val)
                if target_idx == -1:
                    QMessageBox.warning(self, "错误", "未找到值")
                    return
            else:
                QMessageBox.warning(self, "错误", "请输入索引或值")
                return

            self.start_delete_animation(target_idx)
            self.input_val.clear()
            self.input_idx.clear()

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def handle_locate(self):
        text = self.input_val.text()
        if not text:
            QMessageBox.warning(self, "错误", "请输入值")
            return
        val = self._get_val_from_input(text)
        self.start_search_animation(val)
        self.input_val.clear()

    def handle_clear(self):
        self.data_structure.clear()
        self.highlighted_index = -1
        self.update_display()
        self.status_label.setText("链表已清空")

    def random_build(self):
        self.data_structure.clear()
        [self.data_structure.append(random.randint(1, 100)) for _ in range(random.randint(5, 10))]
        self.update_display()
        self.status_label.setText("已随机生成链表")

    def _update_status_text(self):
        self.status_label.setText(f"链表长度: {self.data_structure.length()}")


class BinaryTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "二叉树可视化工具")
        self.data_structure = BinaryTree()
        self.visual_area.set_data_structure(self.data_structure)
        self.current_traversal_result = []
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)
        self.is_animating = False  # 新增属性

    def _create_input_layout(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        root_layout = QHBoxLayout()
        self.root_input = QLineEdit()
        self.root_input.setStyleSheet(STYLES["input"])
        self.root_input.setPlaceholderText("根节点数据")
        btn_root = QPushButton("创建/重置根")
        btn_root.setStyleSheet(STYLES["btn_danger"])
        btn_root.clicked.connect(self.create_root)
        root_layout.addWidget(QLabel("根:"))
        root_layout.addWidget(self.root_input)
        root_layout.addWidget(btn_root)
        layout.addLayout(root_layout)
        child_layout = QHBoxLayout()
        self.parent_idx_input = QLineEdit()
        self.parent_idx_input.setStyleSheet(STYLES["input"])
        self.parent_idx_input.setPlaceholderText("父节点索引")
        self.parent_idx_input.setFixedWidth(80)
        self.child_val_input = QLineEdit()
        self.child_val_input.setStyleSheet(STYLES["input"])
        self.child_val_input.setPlaceholderText("新节点数据")
        child_layout.addWidget(QLabel("父索引:"))
        child_layout.addWidget(self.parent_idx_input)
        child_layout.addWidget(QLabel("数据:"))
        child_layout.addWidget(self.child_val_input)
        layout.addLayout(child_layout)
        return layout

    def _create_button_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        add_layout = QHBoxLayout()
        btn_left = QPushButton("添加左节点")
        btn_left.setStyleSheet(STYLES["btn_success"])
        btn_left.clicked.connect(self.handle_add_left)
        btn_right = QPushButton("添加右节点")
        btn_right.setStyleSheet(STYLES["btn_success"])
        btn_right.clicked.connect(self.handle_add_right)
        add_layout.addWidget(btn_left)
        add_layout.addWidget(btn_right)
        main_layout.addLayout(add_layout)
        del_layout = QHBoxLayout()
        self.del_idx_input = QLineEdit()
        self.del_idx_input.setStyleSheet(STYLES["input"])
        self.del_idx_input.setPlaceholderText("待删索引")
        self.del_idx_input.setFixedWidth(80)
        btn_del = QPushButton("删除子树")
        btn_del.setStyleSheet(STYLES["btn_warning"])
        btn_del.clicked.connect(self.handle_delete_subtree)
        del_layout.addWidget(QLabel("删:"))
        del_layout.addWidget(self.del_idx_input)
        del_layout.addWidget(btn_del)
        main_layout.addLayout(del_layout)
        trav_layout = QHBoxLayout()
        btn_pre = QPushButton("前序")
        btn_pre.setStyleSheet(STYLES["btn_primary"])
        btn_pre.clicked.connect(lambda: self.start_traversal('pre'))
        btn_in = QPushButton("中序")
        btn_in.setStyleSheet(STYLES["btn_primary"])
        btn_in.clicked.connect(lambda: self.start_traversal('in'))
        btn_post = QPushButton("后序")
        btn_post.setStyleSheet(STYLES["btn_primary"])
        btn_post.clicked.connect(lambda: self.start_traversal('post'))
        trav_layout.addWidget(btn_pre)
        trav_layout.addWidget(btn_in)
        trav_layout.addWidget(btn_post)
        main_layout.addLayout(trav_layout)
        btn_rand = QPushButton("随机生成")
        btn_rand.setStyleSheet(STYLES["btn_random"])
        btn_rand.clicked.connect(self.random_build)
        main_layout.addWidget(btn_rand)
        return main_layout

    def create_root(self):
        if self.root_input.text():
            self.data_structure = BinaryTree(self.root_input.text())
            self.visual_area.set_data_structure(self.data_structure)
            self.update_display()
            self.status_label.setText("根节点已创建")
            self.root_input.clear()
        else:
            QMessageBox.warning(self, "错误", "请输入根节点数据")

    def start_add_animation(self, p_idx, val, is_left):
        parent_node = self.data_structure._get_node(p_idx)
        if not parent_node:
            QMessageBox.warning(self, "错误", "父节点不存在")
            return
        if (is_left and parent_node.left_child) or (not is_left and parent_node.right_child):
            QMessageBox.warning(self, "错误", "该位置已有节点")
            return

        if self.anim_enabled:
            # 先执行插入，然后用动画显示
            if is_left:
                self.data_structure.insert_left(p_idx, val)
            else:
                self.data_structure.insert_right(p_idx, val)

            # 获取新插入的节点
            new_node = parent_node.left_child if is_left else parent_node.right_child

            self.is_animating = True
            self.visual_area.anim_state = {'type': 'tree_insert', 'target_node': new_node, 'phase': 'extend_line',
                                           'progress': 0.0}
            self.anim_timer.setInterval(30)
            self.anim_timer.start()
        else:
            if is_left:
                self.data_structure.insert_left(p_idx, val)
            else:
                self.data_structure.insert_right(p_idx, val)
            self.update_display()
            self.status_label.setText(f"已添加 {'左' if is_left else '右'} 节点: {val} @ {p_idx}")

    def handle_add_left(self):
        try:
            if not self.parent_idx_input.text():
                raise ValueError("请输入父节点索引")
            p_idx = int(self.parent_idx_input.text())
            val = self.child_val_input.text()
            if not val:
                raise ValueError("请输入新节点数据")
            self.start_add_animation(p_idx, val, True)
            self.parent_idx_input.clear()
            self.child_val_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "添加失败", str(e))

    def handle_add_right(self):
        try:
            if not self.parent_idx_input.text():
                raise ValueError("请输入父节点索引")
            p_idx = int(self.parent_idx_input.text())
            val = self.child_val_input.text()
            if not val:
                raise ValueError("请输入新节点数据")
            self.start_add_animation(p_idx, val, False)
            self.parent_idx_input.clear()
            self.child_val_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "添加失败", str(e))

    def handle_delete_subtree(self):
        try:
            idx_text = self.del_idx_input.text()
            if not idx_text:
                raise ValueError("请输入待删索引")
            idx = int(idx_text)
            node_to_del = self.data_structure._get_node(idx)
            if not node_to_del:
                raise ValueError("节点不存在")

            self.del_idx_input.clear()

            if node_to_del == self.data_structure.root:
                self.data_structure.clear()
                self.update_display()
                self.status_label.setText("已清空整棵树")
                return

            # 找到父节点并确定是左还是右
            parent_node = node_to_del.parent
            if parent_node is None:  # 非根节点但无父节点，异常情况，直接删除
                self.data_structure.clear()
                self.update_display()
                return

            if self.anim_enabled:
                self.is_animating = True
                self.visual_area.anim_state = {'type': 'tree_delete', 'target_node': node_to_del, 'phase': 'fade',
                                               'progress': 0.0}
                self.anim_timer.setInterval(30)
                self.anim_timer.start()
            else:
                if parent_node.left_child == node_to_del:
                    parent_node.left_child = None
                elif parent_node.right_child == node_to_del:
                    parent_node.right_child = None

                # 简单更新 size (不精确，但比没做好)
                # 由于 _get_node 依赖索引，删除子树后索引会变化，这里先不精确更新
                self.data_structure._size -= 1  # 这是一个不精确的简化，实际应该递归计算

                self.update_display()
                self.status_label.setText(f"已删除索引 {idx} 及其子树")

        except Exception as e:
            QMessageBox.warning(self, "删除失败", str(e))

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state:
            self.anim_timer.stop()
            self.is_animating = False
            return

        # 确保动画开关开启
        if not self.anim_enabled:
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.is_animating = False
            self.update_display()
            return

        state['progress'] += 0.05
        if state['progress'] >= 1.0:
            state['progress'] = 0.0
            if state['type'] == 'tree_insert':
                if state['phase'] == 'extend_line':
                    state['phase'] = 'grow_node'
                elif state['phase'] == 'grow_node':
                    self.visual_area.anim_state = {}
                    self.anim_timer.stop()
                    self.is_animating = False
                    self.status_label.setText("添加完成")
            elif state['type'] == 'tree_delete':
                if state['phase'] == 'fade':
                    node = state['target_node']
                    if node.parent:
                        if node.parent.left_child == node:
                            node.parent.left_child = None
                        else:
                            node.parent.right_child = None
                        self.data_structure._size -= 1  # 简化处理
                    self.visual_area.anim_state = {}
                    self.anim_timer.stop()
                    self.is_animating = False
                    self.status_label.setText("删除完成")
        self.update_display()

    def start_traversal(self, type_):
        if self.data_structure.is_empty():
            QMessageBox.warning(self, "错误", "树为空")
            return

        self.animation_steps = []
        self.current_traversal_result = []
        self.visual_area.traversal_text = ""

        if type_ == 'pre':
            self._get_preorder_nodes(self.data_structure.root, self.animation_steps)
            name = "前序"
        elif type_ == 'in':
            self._get_inorder_nodes(self.data_structure.root, self.animation_steps)
            name = "中序"
        else:
            self._get_postorder_nodes(self.data_structure.root, self.animation_steps)
            name = "后序"

        self.is_animating = True
        self.status_label.setText(f"正在进行{name}遍历...")

        if self.anim_enabled:
            QTimer.singleShot(100, self._run_traversal_animation)
        else:
            # 禁用动画：直接显示结果
            result = [str(node.data) for node in self.animation_steps]
            self.visual_area.traversal_text = f"[ {', '.join(result)} ]"
            self.visual_area.highlighted_node = None
            self.update_display()
            self.is_animating = False
            self.status_label.setText(f"{name}遍历完成: {self.visual_area.traversal_text}")
            QTimer.singleShot(5000, self.clear_traversal_text)

    def _get_preorder_nodes(self, node, res):
        if node:
            res.append(node)
            self._get_preorder_nodes(node.left_child, res)
            self._get_preorder_nodes(node.right_child, res)

    def _get_inorder_nodes(self, node, res):
        if node:
            self._get_inorder_nodes(node.left_child, res)
            res.append(node)
            self._get_inorder_nodes(node.right_child, res)

    def _get_postorder_nodes(self, node, res):
        if node:
            self._get_postorder_nodes(node.left_child, res)
            self._get_postorder_nodes(node.right_child, res)
            res.append(node)

    def _run_traversal_animation(self):
        if not self.animation_steps or not self.anim_enabled:  # 再次检查开关
            self.visual_area.highlighted_node = None
            self.is_animating = False
            QTimer.singleShot(5000, self.clear_traversal_text)
            self.update_display()
            self.status_label.setText("遍历完成")
            return

        node = self.animation_steps.pop(0)
        self.current_traversal_result.append(str(node.data))
        content = ", ".join(self.current_traversal_result)
        self.visual_area.traversal_text = f"[ {content} ]"
        self.visual_area.highlighted_node = node
        self.visual_area.highlight_color = QColor(50, 205, 50)
        self.update_display()
        QTimer.singleShot(self.animation_speed, self._run_traversal_animation)

    def clear_traversal_text(self):
        self.visual_area.traversal_text = None
        self.update_display()

    def random_build(self):
        self.data_structure = BinaryTree(str(random.randint(1, 100)))
        for i in range(random.randint(5, 10)):
            curr_len = self.data_structure.length()
            parent_idx = (curr_len - 1) // 2
            val = str(random.randint(1, 100))
            if curr_len % 2 != 0:
                self.data_structure.insert_left(parent_idx, val)
            else:
                self.data_structure.insert_right(parent_idx, val)
        self.update_display()
        self.status_label.setText("已随机生成完全二叉树")

    def _update_status_text(self):
        self.status_label.setText(f"节点总数: {self.data_structure.length()}")


class HuffmanTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "哈夫曼树可视化工具")

        self.struct_array = []
        self.visual_area.set_data_structure(self.struct_array)

        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)

        self.forest_indices = []
        self.current_run_token = 0
        self.is_animating = False  # 新增属性

    def _create_input_layout(self):
        l = QVBoxLayout()
        l.setSpacing(10)
        self.weight_input = QTextEdit()
        self.weight_input.setStyleSheet(
            "border: 1px solid #d1d5db; border-radius: 6px; padding: 8px; background-color: #f9fafb;")
        self.weight_input.setMaximumHeight(70)
        self.weight_input.setPlaceholderText("例: A:5, B:10, C:3")
        l.addWidget(QLabel("输入权重 (Key:Weight):"))
        l.addWidget(self.weight_input)
        return l

    def _create_button_layout(self):
        l = QHBoxLayout()
        btn = QPushButton("构建哈夫曼树")
        btn.setStyleSheet(STYLES["btn_success"])
        btn.clicked.connect(self.build)
        btn_rand = QPushButton("随机生成")
        btn_rand.setStyleSheet(STYLES["btn_random"])
        btn_rand.clicked.connect(self.random_build)
        l.addWidget(btn)
        l.addWidget(btn_rand)
        return l

    def reset_environment(self):
        """强制重置环境，防止动画冲突"""
        self.anim_timer.stop()
        self.visual_area.anim_state = {}
        self.visual_area.node_positions = {}

        self.struct_array = []
        self.forest_indices = []

        self.visual_area.set_data_structure(self.struct_array)
        self.current_run_token += 1
        self.is_animating = False  # 重置动画状态

    def safe_callback(self, token, func):
        if token == self.current_run_token:
            func()

    def build(self):
        try:
            self.reset_environment()
            text = self.weight_input.toPlainText()
            d = {}
            for item in text.split(','):
                if ':' not in item: continue
                k, v = item.split(':')
                d[k.strip()] = int(v.strip())

            if not d: raise ValueError("No input")

            idx_counter = 0
            for k, v in d.items():
                node = HuffmanStructNode(data=k, weight=v, index=idx_counter)
                self.struct_array.append(node)
                self.forest_indices.append(idx_counter)

                target_y = 60 + idx_counter * 60
                self.visual_area.node_positions[idx_counter] = [float(80), float(target_y)]
                idx_counter += 1

            self.visual_area.set_data_structure(self.struct_array)
            self.update_display()

            if self.anim_enabled:
                self.is_animating = True
                self.status_label.setText("准备排序...")
                token = self.current_run_token
                QTimer.singleShot(500, lambda: self.safe_callback(token, self.start_sorting_phase))
            else:
                self.non_animated_build()
                self.status_label.setText("哈夫曼树已构建 (无动画)")


        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入格式错误: {e}")

    def non_animated_build(self):
        if not self.struct_array: return

        current_nodes = sorted(self.struct_array, key=lambda n: n.weight)
        temp_struct_array = self.struct_array[:]

        while len(current_nodes) > 1:
            n1 = current_nodes.pop(0)
            n2 = current_nodes.pop(0)

            new_weight = n1.weight + n2.weight
            new_idx = len(temp_struct_array)

            # 使用 temp_struct_array 的索引
            n1_idx = n1.index
            n2_idx = n2.index

            parent_node = HuffmanStructNode(weight=new_weight, index=new_idx)
            parent_node.left = n1_idx
            parent_node.right = n2_idx
            temp_struct_array.append(parent_node)

            # 更新原始数组中的父指针 (这一步是必须的，否则无法绘制)
            self.struct_array[n1_idx].parent = new_idx
            self.struct_array[n2_idx].parent = new_idx

            # 找到新节点的插入位置并插入
            import bisect
            bisect.insort_left(current_nodes, parent_node, key=lambda n: n.weight)

            # 由于索引的变化，需要更新 struct_array
            self.struct_array = temp_struct_array[:]

        # 强制设置根节点位置 (中心)
        if self.struct_array:
            root_idx = len(self.struct_array) - 1
            self.forest_indices = [root_idx]
            self.calculate_final_positions(root_idx)
            self.update_display()

    def start_sorting_phase(self):
        if not self.anim_enabled: return

        self.forest_indices.sort(key=lambda i: self.struct_array[i].weight)

        target_positions = {}

        queue_pos_index = 0
        for root_idx in self.forest_indices:
            curr_pos = self.visual_area.node_positions.get(root_idx, [0, 0])

            if curr_pos[0] < 200:
                target_y = 60 + queue_pos_index * 60
                delta_y = target_y - curr_pos[1]
                self._recursively_move_tree_by_index(root_idx, 0, delta_y, target_positions)
                queue_pos_index += 1
            else:
                pass

        self.visual_area.anim_state = {
            'type': 'SORT',
            'targets': target_positions,
            'progress': 0.0
        }
        self.anim_timer.setInterval(30)
        self.anim_timer.start()
        self.status_label.setText("按权重排序 (结构体数组索引)...")

    def _recursively_move_tree_by_index(self, idx, delta_x, delta_y, new_positions, visited=None):
        if idx == -1: return
        if visited is None: visited = set()
        if idx in visited: return
        visited.add(idx)

        curr_pos = self.visual_area.node_positions.get(idx)
        if not curr_pos: return

        # 累计移动量
        nx = curr_pos[0] + delta_x
        ny = curr_pos[1] + delta_y

        if abs(nx) > 20000 or abs(ny) > 20000: return

        new_positions[idx] = [nx, ny]

        node = self.struct_array[idx]
        self._recursively_move_tree_by_index(node.left, delta_x, delta_y, new_positions, visited)
        self._recursively_move_tree_by_index(node.right, delta_x, delta_y, new_positions, visited)

    def _get_tree_width(self, root_idx):
        if root_idx == -1: return 0
        node = self.struct_array[root_idx]
        if node.left == -1 and node.right == -1: return 1
        return self._get_tree_width(node.left) + self._get_tree_width(node.right)

    def _get_root_relative_x(self, root_idx, unit_width):
        if root_idx == -1: return 0
        node = self.struct_array[root_idx]
        if node.left == -1 and node.right == -1: return 0.5 * unit_width

        w_l = self._get_tree_width(node.left) * unit_width
        rx_l = self._get_root_relative_x(node.left, unit_width)
        rx_r = self._get_root_relative_x(node.right, unit_width)

        return (rx_l + (w_l + rx_r)) / 2

    def start_merge_cycle(self):
        if not self.anim_enabled: return

        if len(self.forest_indices) < 2:
            self.finish_construction()
            return

        left_idx = self.forest_indices[0]
        right_idx = self.forest_indices[1]
        left_node = self.struct_array[left_idx]
        right_node = self.struct_array[right_idx]

        stage_roots = []
        for idx in self.forest_indices:
            if idx == left_idx or idx == right_idx: continue
            pos = self.visual_area.node_positions.get(idx)
            if pos and pos[0] > 220:
                stage_roots.append(idx)

        new_weight = left_node.weight + right_node.weight
        stage_roots.append({'is_new': True, 'weight': new_weight, 'l': left_idx, 'r': right_idx})
        stage_roots.sort(key=lambda x: x['weight'] if isinstance(x, dict) else self.struct_array[x].weight)

        UNIT_W = 50
        GAP = 30
        tree_specs = []
        total_raw_width = 0

        for item in stage_roots:
            if isinstance(item, dict):
                w_l_leaves = self._get_tree_width(item['l'])
                w_r_leaves = self._get_tree_width(item['r'])
                total_leaves = w_l_leaves + w_r_leaves
                tree_specs.append({'type': 'new', 'leaves': total_leaves, 'obj': item})
            else:
                leaves = self._get_tree_width(item)
                tree_specs.append({'type': 'existing', 'leaves': leaves, 'id': item})
            total_raw_width += tree_specs[-1]['leaves'] * UNIT_W

        total_raw_width += (len(tree_specs) - 1) * GAP

        available_w = self.visual_area.width() - 260
        scale = 1.0
        if total_raw_width > available_w and available_w > 100:
            scale = available_w / total_raw_width
            if scale < 0.4: scale = 0.4

        eff_unit = UNIT_W * scale
        eff_gap = GAP * scale

        final_specs = []
        current_w_accum = 0
        for spec in tree_specs:
            width_px = spec['leaves'] * eff_unit
            if spec['type'] == 'new':
                item = spec['obj']
                rx_l = self._get_root_relative_x(item['l'], eff_unit)
                rx_r = self._get_root_relative_x(item['r'], eff_unit)
                w_l_px = self._get_tree_width(item['l']) * eff_unit

                root_x = (rx_l + (w_l_px + rx_r)) / 2
                final_specs.append({
                    'type': 'new', 'width': width_px, 'root_x': root_x,
                    'l_idx': item['l'], 'r_idx': item['r'],
                    'l_rx': rx_l, 'r_rx': rx_r + w_l_px
                })
            else:
                rx = self._get_root_relative_x(spec['id'], eff_unit)
                final_specs.append({
                    'type': 'existing', 'width': width_px, 'root_x': rx, 'id': spec['id']
                })
            current_w_accum += width_px + eff_gap

        total_final_width = current_w_accum - eff_gap
        start_x = 240 + (available_w - total_final_width) / 2
        if start_x < 240: start_x = 240

        target_positions = {}
        curr_x = start_x
        base_y = 80
        new_parent_pos = [0, 0]

        for fspec in final_specs:
            root_world_x = curr_x + fspec['root_x']

            if fspec['type'] == 'existing':
                curr_pos = self.visual_area.node_positions.get(fspec['id'], [0, 0])
                self._recursively_move_tree_by_index(fspec['id'], root_world_x - curr_pos[0], base_y - curr_pos[1],
                                                     target_positions)
            else:
                new_parent_pos = [root_world_x, base_y]
                lx = curr_x + fspec['l_rx']
                ly = base_y + 60 * max(0.6, scale)
                l_curr = self.visual_area.node_positions.get(fspec['l_idx'], [0, 0])
                self._recursively_move_tree_by_index(fspec['l_idx'], lx - l_curr[0], ly - l_curr[1], target_positions)

                rx = curr_x + fspec['r_rx']
                ry = ly
                r_curr = self.visual_area.node_positions.get(fspec['r_idx'], [0, 0])
                self._recursively_move_tree_by_index(fspec['r_idx'], rx - r_curr[0], ry - r_curr[1], target_positions)

            curr_x += fspec['width'] + eff_gap

        self.visual_area.anim_state = {
            'type': 'MOVE_TO_STAGE',
            'targets': target_positions,
            'left_idx': left_idx,
            'right_idx': right_idx,
            'parent_pos': new_parent_pos,
            'progress': 0.0
        }
        self.status_label.setText(f"合并: {left_node.weight} + {right_node.weight}")
        self.anim_timer.setInterval(30)
        self.anim_timer.start()

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state:
            self.anim_timer.stop()
            self.is_animating = False
            return

        if not self.anim_enabled:  # 再次检查
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.is_animating = False
            self.update_display()
            return

        state['progress'] += 0.05
        prog = state['progress']

        if prog >= 1.0:
            prog = 1.0
            self.anim_timer.stop()
            self.handle_phase_end(state)
        else:
            if 'targets' in state:
                for idx, target in state['targets'].items():
                    curr = self.visual_area.node_positions.get(idx)
                    if not curr: curr = target

                    # 平滑插值
                    nx = curr[0] + (target[0] - curr[0]) * 0.2
                    ny = curr[1] + (target[1] - curr[1]) * 0.2

                    if abs(nx - target[0]) < 1 and abs(ny - target[1]) < 1:
                        nx, ny = target

                    self.visual_area.node_positions[idx] = [nx, ny]

            if prog >= 0.95:
                self.anim_timer.stop()
                self.handle_phase_end(state)
                return

        self.update_display()

    def handle_phase_end(self, state):
        stype = state['type']
        token = self.current_run_token

        if stype == 'SORT':
            self.visual_area.anim_state = {}
            QTimer.singleShot(300, lambda: self.safe_callback(token, self.start_merge_cycle))

        elif stype == 'MOVE_TO_STAGE':
            left_idx = state['left_idx']
            right_idx = state['right_idx']
            p_pos = state['parent_pos']

            left_node = self.struct_array[left_idx]
            right_node = self.struct_array[right_idx]

            new_weight = left_node.weight + right_node.weight
            new_idx = len(self.struct_array)

            parent_node = HuffmanStructNode(weight=new_weight, index=new_idx)
            parent_node.left = left_idx
            parent_node.right = right_idx
            self.struct_array.append(parent_node)

            self.struct_array[left_idx].parent = new_idx
            self.struct_array[right_idx].parent = new_idx

            if left_idx in self.forest_indices: self.forest_indices.remove(left_idx)
            if right_idx in self.forest_indices: self.forest_indices.remove(right_idx)
            self.forest_indices.append(new_idx)

            self.visual_area.node_positions[new_idx] = p_pos

            self.visual_area.anim_state = {
                'type': 'MERGE_FLASH',
                'active_parent_idx': new_idx,
                'progress': 0.0
            }
            self.status_label.setText(f"生成父节点 [{new_idx}] 权重: {new_weight}")
            self.anim_timer.setInterval(30)
            self.anim_timer.start()

        elif stype == 'MERGE_FLASH':
            self.visual_area.anim_state = {}
            self.status_label.setText(f"合并完成，准备下一轮...")
            QTimer.singleShot(500, lambda: self.safe_callback(token, self.start_sorting_phase))

        elif stype == 'FINAL_MOVE':
            self.visual_area.anim_state = {}
            self.is_animating = False
            self.status_label.setText("构建完成")

    def finish_construction(self):
        if not self.forest_indices: return
        root_idx = self.forest_indices[0]
        self.calculate_final_positions(root_idx)

        if self.anim_enabled:
            self.visual_area.anim_state = {
                'type': 'FINAL_MOVE',
                'targets': self.visual_area.node_positions.copy(),
                'progress': 0.0
            }
            self.status_label.setText("构建完成！展示最终哈夫曼树")
            self.anim_timer.setInterval(30)
            self.anim_timer.start()
        else:
            self.is_animating = False
            self.status_label.setText("构建完成 (无动画)")
            self.update_display()

    def calculate_final_positions(self, root_idx):
        """非动画模式或最终移动模式下，直接计算所有节点的最终位置"""
        self.visual_area.node_positions = {}
        if root_idx == -1: return

        UNIT_W = 50
        width_leaves = self._get_tree_width(root_idx)
        raw_width = width_leaves * UNIT_W

        available_w = self.visual_area.width()
        scale = 1.0
        if raw_width > available_w - 40:
            scale = (available_w - 40) / raw_width
            if scale < 0.4: scale = 0.4

        eff_unit = UNIT_W * scale
        cx = available_w // 2
        cy = 80

        # 使用一个独立的字典来存储计算出的位置，避免影响动画
        final_targets = {}

        def place_node(idx, x, y, current_unit):
            if idx == -1: return
            final_targets[idx] = [x, y]
            node = self.struct_array[idx]

            my_rel = self._get_root_relative_x(idx, current_unit)

            if node.left != -1:
                l_rel = self._get_root_relative_x(node.left, current_unit)
                l_x = (x - my_rel) + l_rel
                place_node(node.left, l_x, y + 60 * max(0.6, scale), current_unit)

            if node.right != -1:
                w_l = self._get_tree_width(node.left) * current_unit
                r_rel = self._get_root_relative_x(node.right, current_unit)
                r_x = (x - my_rel) + w_l + r_rel
                place_node(node.right, r_x, y + 60 * max(0.6, scale), current_unit)

        place_node(root_idx, cx, cy, eff_unit)
        self.visual_area.node_positions = final_targets

    def random_build(self):
        self.reset_environment()
        import string
        d = {}
        chars = string.ascii_uppercase
        count = random.randint(3, 8)
        for i in range(count):
            d[chars[i]] = random.randint(1, 50)
        txt = ", ".join([f"{k}:{v}" for k, v in d.items()])
        self.weight_input.setText(txt)
        self.build()

    def _update_status_text(self):
        pass


class BinarySearchTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, last_window=None):
        super().__init__(main_window, last_window, "二叉搜索树 (BST) 可视化工具")
        self.data_structure = BinarySearchTree()
        self.visual_area.set_data_structure(self.data_structure)

        self.is_animating = False
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)

        # 预设一些数据
        for v in [50, 30, 70, 20, 40, 60, 80]:
            self.data_structure.insert(v)
        self.update_display()

    def _create_input_layout(self):
        l = QHBoxLayout()
        self.value_input = QLineEdit()
        self.value_input.setStyleSheet(STYLES["input"])
        self.value_input.setPlaceholderText("整数值")
        self.value_input.returnPressed.connect(self.start_insert)
        l.addWidget(QLabel("数值:"))
        l.addWidget(self.value_input)
        return l

    def _create_button_layout(self):
        grid = QGridLayout()
        grid.setSpacing(12)
        btn_ins = QPushButton("插入")
        btn_ins.setStyleSheet(STYLES["btn_success"])
        btn_ins.clicked.connect(self.start_insert)
        btn_sch = QPushButton("查找")
        btn_sch.setStyleSheet(STYLES["btn_primary"])
        btn_sch.clicked.connect(self.start_search)
        btn_del = QPushButton("删除")
        btn_del.setStyleSheet(STYLES["btn_warning"])
        btn_del.clicked.connect(self.start_delete)
        btn_rand = QPushButton("随机")
        btn_rand.setStyleSheet(STYLES["btn_random"])
        btn_rand.clicked.connect(self.random_build)
        btn_clr = QPushButton("清空")
        btn_clr.setStyleSheet(STYLES["btn_danger"])
        btn_clr.clicked.connect(self.clear_tree)
        grid.addWidget(btn_ins, 0, 0)
        grid.addWidget(btn_sch, 0, 1)
        grid.addWidget(btn_del, 1, 0)
        grid.addWidget(btn_rand, 1, 1)
        grid.addWidget(btn_clr, 2, 0, 1, 2)
        return grid

    def _get_value(self):
        try:
            return int(self.value_input.text().strip())
        except:
            return None

    def start_insert(self):
        """启动插入动画"""
        if self.is_animating: return
        val = self._get_value()
        if val is None:
            QMessageBox.warning(self, "错误", "请输入有效整数")
            return

        self.value_input.clear()

        if not self.anim_enabled:
            self.data_structure.insert(val)
            self.update_display()
            self.status_label.setText(f"已插入: {val}")
            return

        if self.data_structure.is_empty():
            self.data_structure.insert(val)
            self.status_label.setText(f"插入根节点: {val}")
            self.update_display()
            return

        self.is_animating = True
        self.status_label.setText(f"查找插入位置: {val}...")

        self.visual_area.anim_state = {
            'type': 'bst_insert',
            'target_val': val,
            'current_node': self.data_structure.root,
            'next_node': None,
            'status': 'appear',
            'progress': 0.0,
            'path_history': []
        }
        self.anim_timer.setInterval(30)
        self.anim_timer.start()
        self.update_display()

    def start_delete(self):
        """启动删除动画"""
        if self.is_animating: return
        val = self._get_value()
        if val is None:
            QMessageBox.warning(self, "错误", "请输入有效整数")
            return

        self.value_input.clear()

        if self.data_structure.is_empty():
            QMessageBox.warning(self, "错误", "树为空")
            return

        if not self.anim_enabled:
            self.data_structure.delete(val)
            self.update_display()
            self.status_label.setText(f"已删除: {val}")
            return

        self.is_animating = True
        self.status_label.setText(f"查找删除目标: {val}...")

        self.visual_area.anim_state = {
            'type': 'bst_delete',
            'target_val': val,
            'current_node': self.data_structure.root,
            'next_node': None,
            'status': 'appear',
            'progress': 0.0,
            'path_history': []
        }
        self.anim_timer.setInterval(30)
        self.anim_timer.start()
        self.update_display()

    def start_search(self):
        """启动查找动画"""
        if self.is_animating: return
        val = self._get_value()
        if val is None:
            QMessageBox.warning(self, "错误", "请输入有效整数")
            return

        self.value_input.clear()

        if self.data_structure.is_empty():
            QMessageBox.information(self, "提示", "树为空")
            return

        if not self.anim_enabled:
            # 禁用动画：直接查找并高亮
            found_node = self.data_structure.search(val)
            if found_node:
                self.visual_area.highlighted_node = found_node
                self.status_label.setText(f"找到元素: {val}")
            else:
                self.visual_area.highlighted_node = None
                self.status_label.setText(f"未找到元素: {val}")
                QMessageBox.information(self, "提示", "未找到元素")
            self.update_display()
            return

        self.is_animating = True
        self.status_label.setText(f"查找: {val}...")

        self.visual_area.anim_state = {
            'type': 'bst_search',
            'target_val': val,
            'current_node': self.data_structure.root,
            'next_node': None,
            'status': 'appear',
            'progress': 0.0,
            'path_history': []
        }

        self.anim_timer.setInterval(30)
        self.anim_timer.start()
        self.update_display()

    def update_animation(self):
        state = self.visual_area.anim_state
        anim_type = state.get('type')
        if not state or anim_type not in ['bst_search', 'bst_insert', 'bst_delete']:
            self.anim_timer.stop()
            self.is_animating = False
            return

        if not self.anim_enabled:  # 再次检查
            self.anim_timer.stop()
            self.visual_area.anim_state = {}
            self.is_animating = False
            self.update_display()
            return

        status = state['status']
        target_val = state['target_val']
        curr = state['current_node']

        # 1. 出现阶段
        if status == 'appear':
            state['progress'] += 0.1
            if state['progress'] >= 1.0:
                state['progress'] = 0.0
                state['status'] = 'compare'

        # 2. 比较阶段
        elif status == 'compare':
            state['progress'] += 0.05
            if state['progress'] >= 1.0:
                state['progress'] = 0.0

                if target_val == curr.data:
                    if anim_type == 'bst_search':
                        state['status'] = 'found'
                        self.status_label.setText(f"找到元素: {target_val}")
                    elif anim_type == 'bst_insert':
                        state['status'] = 'found'
                        self.status_label.setText(f"元素 {target_val} 已存在，不执行插入")
                    elif anim_type == 'bst_delete':
                        state['status'] = 'delete_found'
                        self.status_label.setText(f"找到待删元素: {target_val}")

                elif target_val < curr.data:
                    if curr.left_child:
                        state['next_node'] = curr.left_child
                        state['status'] = 'move'
                    else:
                        if anim_type == 'bst_search' or anim_type == 'bst_delete':
                            state['status'] = 'not_found'
                            self.status_label.setText("元素不存在")
                        elif anim_type == 'bst_insert':
                            state['status'] = 'insert_found'
                            self.status_label.setText("找到插入位置 (左)")

                else:
                    if curr.right_child:
                        state['next_node'] = curr.right_child
                        state['status'] = 'move'
                    else:
                        if anim_type == 'bst_search' or anim_type == 'bst_delete':
                            state['status'] = 'not_found'
                            self.status_label.setText("元素不存在")
                        elif anim_type == 'bst_insert':
                            state['status'] = 'insert_found'
                            self.status_label.setText("找到插入位置 (右)")

        # 3. 移动阶段
        elif status == 'move':
            state['progress'] += 0.05
            if state['progress'] >= 1.0:
                state['path_history'].append(curr)
                state['current_node'] = state['next_node']
                state['next_node'] = None
                state['progress'] = 0.0
                state['status'] = 'compare'

        # 4. 终结阶段处理
        elif status in ['found', 'not_found', 'insert_found', 'delete_found']:
            state['progress'] += 0.04
            if state['progress'] >= 2.0:
                self.anim_timer.stop()
                self.is_animating = False

                if status == 'insert_found':
                    self.data_structure.insert(target_val)
                    self.status_label.setText(f"已插入: {target_val}")
                elif status == 'delete_found':
                    self.data_structure.delete(target_val)
                    self.status_label.setText(f"已删除: {target_val}")
                elif status == 'not_found' and anim_type == 'bst_search':
                    QMessageBox.information(self, "查找结果", f"未找到元素: {target_val}")

                self.visual_area.anim_state = {}
                self.value_input.setFocus()
                self.update_display()
                return

        self.update_display()

    def clear_tree(self):
        self.data_structure.clear()
        self.update_display()
        self.status_label.setText("BST已清空")

    def random_build(self):
        self.clear_tree()
        [self.data_structure.insert(v) for v in random.sample(range(1, 100), 7)]
        self.update_display()
        self.status_label.setText("已随机生成BST")

    def _update_status_text(self):
        self.status_label.setText(f"节点数: {self.data_structure.length()}")


class AVLTreeVisualizer(BinarySearchTreeVisualizer):
    def __init__(self, main_window=None, last_window=None):
        super().__init__(main_window, last_window)
        self.title = "AVL树 (全自动平衡演示版)"
        self.setWindowTitle(self.title)

        # 初始化 AVL 树
        self.data_structure = AVLTree()
        self.visual_area.set_data_structure(self.data_structure)

        # 核心变量：平衡检查的起点
        self.balance_check_start_node = None

        # 预设演示数据 (生成题目描述中的树: 根30, 左20(10,25), 右50(40))
        for v in [30, 20, 50, 10, 25, 40]:
            self.data_structure.insert(v, auto_balance=True)

        self._sync_root()
        self.update_display()
        self.status_label.setText("AVL树已就绪 - 尝试删除节点40或50观察动画")

    def _sync_root(self):
        """确保根节点引用正确"""
        if self.data_structure.root and self.data_structure.root.parent:
            curr = self.data_structure.root
            while curr.parent: curr = curr.parent
            self.data_structure.root = curr

    def _connect_timer(self, callback):
        """辅助函数：安全连接定时器"""
        try:
            self.anim_timer.timeout.disconnect()
        except:
            pass
        self.anim_timer.timeout.connect(callback)
        self.anim_timer.setInterval(30)
        self.anim_timer.start()

    def start_insert(self):
        """插入入口"""
        if self.is_animating: return
        val = self._get_value()
        if val is None: return
        self.value_input.clear()

        # 空树或无动画直接处理
        if self.data_structure.is_empty() or not self.anim_enabled:
            self.data_structure.insert(val, auto_balance=True)
            self._sync_root()
            self.update_display()
            self.status_label.setText(f"已插入: {val}")
            return

        # 1. 启动查找动画
        self.is_animating = True
        self.visual_area.anim_state = {
            'type': 'bst_insert', 'target_val': val,
            'current_node': self.data_structure.root, 'next_node': None,
            'status': 'appear', 'progress': 0.0, 'path_history': []
        }
        self._connect_timer(self.update_insert_animation)
        self.status_label.setText(f"查找插入位置: {val}...")

    def start_delete(self):
        """删除入口"""
        if self.is_animating: return
        val = self._get_value()
        if val is None: return
        self.value_input.clear()
        if self.data_structure.is_empty(): return

        # 无动画直接处理
        if not self.anim_enabled:
            self.data_structure.delete(val, auto_balance=True)
            self._sync_root()
            self.update_display()
            self.status_label.setText(f"已删除: {val}")
            return

        # 1. 启动查找动画
        self.is_animating = True
        self.status_label.setText(f"查找删除目标: {val}...")
        self.visual_area.anim_state = {
            'type': 'bst_delete', 'target_val': val,
            'current_node': self.data_structure.root, 'next_node': None,
            'status': 'appear', 'progress': 0.0, 'path_history': []
        }
        self._connect_timer(self.update_delete_animation)

    def update_insert_animation(self):
        """插入动画逻辑"""
        state = self.visual_area.anim_state
        if state.get('type') == 'bst_insert' and state.get('status') in ['insert_found', 'found'] and state.get(
                'progress') >= 1.0:
            self.anim_timer.stop()
            val = state['target_val']

            if state['status'] == 'found':
                self.finish_operation("元素已存在")
                return

            # [步骤1] 记住当前树（虽然插入是新挂节点，但为了统一逻辑）
            start_positions = self.visual_area.calculate_all_node_positions()

            # [步骤2] 物理插入 (auto_balance=False)
            new_node = self.data_structure.insert(val, auto_balance=False)
            self.balance_check_start_node = new_node  # 记录检查点
            self._sync_root()

            # [步骤3] 计算新树布局
            end_positions = self.visual_area.calculate_all_node_positions()

            # [步骤4] 启动 Morph 动画 (平滑展示新节点出现)
            # 虽然插入通常是直接出现，但如果导致了挤压，morph 会更自然
            self.visual_area.anim_state = {
                'type': 'morph',
                'start_positions': start_positions,
                'end_positions': end_positions,
                'pivot': None,
                'new_root': None,
                'progress': 0.0,
                'next_action': 'check_balance'  # 动画结束后，去检查平衡
            }
            self.status_label.setText(f"节点插入完成，准备检查平衡...")
            self._connect_timer(self.update_morph_animation)
            return
        super().update_animation()

    import traceback  # 引入这个库以便打印详细错误堆栈

    def update_delete_animation(self):
        """删除动画逻辑（全包裹安全版）"""
        state = self.visual_area.anim_state

        # 目标状态列表，确保包含 delete_found
        target_statuses = ['found', 'delete_found', 'not_found']

        if state.get('type') == 'bst_delete' and state.get('status') in target_statuses and state.get(
                'progress') >= 1.0:

            self.anim_timer.stop()

            # --- 【安全网开始】将所有逻辑包裹起来 ---
            try:
                val = state['target_val']
                print(f"DEBUG: 开始处理删除逻辑，目标值: {val}")

                if state['status'] == 'not_found':
                    self.finish_operation("元素不存在，无法删除")
                    return

                # [步骤1] 记录删除前位置
                start_positions = self.visual_area.calculate_all_node_positions()

                # [步骤2] 物理删除 (auto_balance=False)
                # 注意：这里我们信任 delete 方法已经修改为返回 Node 了
                balance_start_node = self.data_structure.delete(val, auto_balance=False)

                print(f"DEBUG: 物理删除完成，返回平衡点: {balance_start_node}")

                # [步骤3] 同步根节点与记录检查点
                # 这一步之前可能在 try 外面，导致如果 root 没了就崩溃
                self.balance_check_start_node = balance_start_node
                self._sync_root()

                # [步骤4] 计算新树布局
                # 如果树空了，这里必须能处理空树的情况
                end_positions = self.visual_area.calculate_all_node_positions()

                # [步骤5] 启动 Morph 动画
                # 判断树是否为空
                is_tree_empty = self.data_structure.root is None

                self.visual_area.anim_state = {
                    'type': 'morph',
                    'start_positions': start_positions,
                    'end_positions': end_positions,
                    'pivot': None,
                    'new_root': None,
                    'progress': 0.0,
                    # 如果树空了，直接 finish；否则检查平衡
                    'next_action': 'finish' if is_tree_empty else 'check_balance'
                }

                print("DEBUG: 启动 Morph 动画")
                self.status_label.setText(f"节点删除完成，正在调整树结构...")
                self._connect_timer(self.update_morph_animation)

            except Exception as e:
                # --- 【安全网捕获】 ---
                print("\n!!! 严重错误: 动画逻辑发生异常 !!!")
                print(f"错误信息: {e}")
                print("错误堆栈:")
                traceback.print_exc()  # 这行代码会打印出具体哪一行崩溃了

                # 尝试恢复状态，避免界面卡死
                self.finish_operation("发生内部错误")

            return

        # 没满足条件时，继续之前的查找动画
        super().update_animation()

    def check_balance_step(self):
        """平衡检查循环：这是在每一次结构调整（删除/插入）动画完成后调用的"""
        self._sync_root()

        # 查找最深的不平衡节点
        unbalanced = self.data_structure.get_lowest_unbalanced_node(self.balance_check_start_node)

        if not unbalanced:
            self.finish_operation("平衡检查完成，结构稳定")
            return

        # 发现不平衡，准备旋转
        # 此时，树是“歪”的，我们准备把它“转正”
        self.prepare_rotation_animation(unbalanced)

    def prepare_rotation_animation(self, node):
        """准备旋转动画：同样遵循 记忆->旋转->形态变化 的流程"""
        balance = self.data_structure._get_balance(node)
        desc = ""

        # [步骤 1] 记住旋转前的样子 (Snapshot A)
        start_positions = self.visual_area.calculate_all_node_positions()

        # [步骤 2] 后台执行物理旋转
        # 这一步执行后，数据结构的父子关系瞬间改变
        pivot = node
        new_root = None

        if balance > 1:  # 左偏
            if self.data_structure._get_balance(node.left_child) >= 0:
                desc = "右旋 (LL)"
                new_root = self.data_structure.rotate_right(node)
            else:
                desc = "先左后右 (LR)"
                self.data_structure.rotate_left(node.left_child)
                new_root = self.data_structure.rotate_right(node)
        else:  # 右偏
            if self.data_structure._get_balance(node.right_child) <= 0:
                desc = "左旋 (RR)"
                new_root = self.data_structure.rotate_left(node)
            else:
                desc = "先右后左 (RL)"
                self.data_structure.rotate_right(node.right_child)
                new_root = self.data_structure.rotate_left(node)

        self._sync_root()

        # [步骤 3] 计算旋转后的样子 (Snapshot B)
        # 此时新的父节点已经到了上面
        end_positions = self.visual_area.calculate_all_node_positions()

        # [步骤 4] 启动 Morph 动画
        # 播放旋转过程，并在结束后**再次**调用 check_balance，形成循环
        self.visual_area.anim_state = {
            'type': 'morph',
            'start_positions': start_positions,
            'end_positions': end_positions,
            'pivot': pivot,
            'new_root': new_root,
            'progress': 0.0,
            'next_action': 'check_balance'
        }

        self.status_label.setText(f"检测到不平衡 (BF={balance})，正在执行 {desc}...")
        self._connect_timer(self.update_morph_animation)

    def update_morph_animation(self):
        """处理节点移动、消失的插值动画"""
        state = self.visual_area.anim_state

        # 增加进度
        state['progress'] += 0.05  # 调节速度：越小越慢

        if state['progress'] >= 1.0:
            self.anim_timer.stop()
            state['progress'] = 1.0

            # 动画结束，决定下一步去哪
            next_action = state.get('next_action')

            if next_action == 'check_balance':
                # 去执行平衡检查（对应 AVL/红黑树逻辑）
                # 确保你 connect 到了正确的检查函数
                self.start_balance_check_animation()
            elif next_action == 'finish':
                self.finish_operation("操作完成")

            # 刷新一下以显示最终准确位置
            self.visual_area.update()
            return

        # 触发重绘，paintEvent 会根据 progress 计算位置
        self.visual_area.update()

    # --- 配合 PaintEvent 使用的辅助函数 ---

    def draw_morph_frame(self, painter, state):
        """
        根据 progress，在 start_positions 和 end_positions 之间插值画图
        """
        t = state['progress']
        start_pos = state['start_positions']
        end_pos = state['end_positions']

        # 获取所有涉及的节点（包括即将消失的）
        all_nodes = set(start_pos.keys()) | set(end_pos.keys())

        for node in all_nodes:
            # 计算插值坐标
            p_start = start_pos.get(node)
            p_end = end_pos.get(node)

            current_x, current_y = 0, 0

            if p_start and p_end:
                # 移动：从 A 到 B
                current_x = p_start[0] + (p_end[0] - p_start[0]) * t
                current_y = p_start[1] + (p_end[1] - p_start[1]) * t
                opacity = 1.0
            elif p_start and not p_end:
                # 消失：节点被删除了
                current_x, current_y = p_start
                # 让他慢慢变透明，或者慢慢缩小
                opacity = 1.0 - t
            elif not p_start and p_end:
                # 出现：新插入的节点（删除逻辑里一般没有这个，除非有替补节点飞过来）
                current_x, current_y = p_end
                opacity = t

            # 拿到坐标后，画出这个节点
            # 注意：你需要设置 painter 的透明度来配合 opacity
            painter.setOpacity(opacity)
            self.draw_node(painter, node, current_x, current_y)
            painter.setOpacity(1.0)  # 还原

    def finish_operation(self, msg=""):
        self.is_animating = False
        self.visual_area.anim_state = {}
        if msg: self.status_label.setText(msg)
        try:
            self.anim_timer.timeout.disconnect()
        except:
            pass
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.stop()
        self.update_display()

    def start_balance_check_animation(self):
        """
        [缺失的函数] 启动平衡检查动画
        从删除/插入的受影响节点开始，一路向上检查 BF 值
        """
        node = self.balance_check_start_node

        # 情况处理：如果节点为空（比如删除了根节点导致树空），直接结束
        if node is None:
            # 尝试获取根节点，如果连根都没了，说明树空了
            if self.data_structure.root:
                node = self.data_structure.root
            else:
                self.finish_operation("树已清空，操作结束")
                return

        # 初始化动画状态
        self.visual_area.anim_state = {
            'type': 'balance_check',  # 状态类型
            'current_node': node,  # 当前检查的节点
            'status': 'checking',
            'progress': 0.0
        }

        self.status_label.setText(f"Morph 完成，开始从节点 {node.data} 向上检查平衡...")
        self._connect_timer(self.update_balance_check_animation)

    def update_balance_check_animation(self):
        """
        [已修复] 平衡检查的帧循环逻辑 (Timer 调用)
        """
        state = self.visual_area.anim_state
        node = state.get('current_node')

        # 1. 安全检查
        if not node:
            self.finish_operation("平衡检查完成")
            return

        # 2. 计算平衡因子 (BF)
        try:
            # 优先尝试调用 model.py 中的私有方法 _get_balance
            if hasattr(self.data_structure, '_get_balance'):
                bf = self.data_structure._get_balance(node)
            elif hasattr(self.data_structure, 'get_balance'):
                bf = self.data_structure.get_balance(node)
            else:
                # 手动计算 fallback
                l_h = node.left_child.height if node.left_child else 0
                r_h = node.right_child.height if node.right_child else 0
                bf = l_h - r_h
        except Exception:
            bf = 0

        # 3. 更新界面文字
        self.status_label.setText(f"正在检查节点 {node.data} (BF = {bf})...")
        self.visual_area.highlighted_node = node  # 高亮当前节点
        self.visual_area.update()  # 强制重绘

        # 4. 判断是否失衡 (|BF| > 1)
        if abs(bf) > 1:
            self.anim_timer.stop()
            self.status_label.setText(f"发现失衡节点 {node.data} (BF={bf})，准备旋转修复...")

            # --- [修复点 A] 方法名修正：改为调用 prepare_rotation_animation ---
            if hasattr(self, 'prepare_rotation_animation'):
                self.prepare_rotation_animation(node)
            else:
                # --- [修复点 B] 保底逻辑修正：调用存在的 rebalance_all ---
                print("DEBUG: 未找到 prepare_rotation_animation，执行瞬间平衡")
                self.data_structure.rebalance_all()
                self.visual_area.node_positions = self.visual_area.calculate_all_node_positions()
                self.finish_operation("平衡完成 (无旋转动画)")
            return

        # 5. 如果当前节点平衡，继续向上检查父节点
        if node.parent:
            state['current_node'] = node.parent
        else:
            # 已经到了根节点，且根节点也平衡
            self.visual_area.highlighted_node = None
            self.finish_operation("平衡检查完成，树结构稳定")

    def random_build(self):
        self.data_structure.clear()
        vals = random.sample(range(1, 100), 8)
        for v in vals:
            self.data_structure.insert(v, auto_balance=True)
        self._sync_root()
        self.update_display()
        self.status_label.setText("已随机生成 AVL 树")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DS Visualizer")
    app.setStyle('Fusion')

    window = AVLTreeVisualizer()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())