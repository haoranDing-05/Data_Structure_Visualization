import sys
import traceback
import math
import random
from fileinput import filename

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QGroupBox, QMessageBox, QTextEdit, QGridLayout,
                             QScrollArea, QInputDialog, QSizePolicy, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QUrl, QPointF, QPoint, QMetaObject, Q_ARG, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPolygonF, QPainterPath
from PyQt5.QtMultimedia import QSoundEffect
from model import Stack, SequenceList, LinkedList, BinaryTree, BinarySearchTree, HuffmanTree, HuffmanNode, \
    BinaryTreeNode
from PyQt5.QtWidgets import QFileDialog
import os
from datetime import datetime
import json
import threading
from qianwen_api import QianWenAPI

# --- 样式常量 ---
STYLES = {
    "btn_primary": "QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }",
    "btn_success": "QPushButton { background-color: #10b981; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #059669; }",
    "btn_danger": "QPushButton { background-color: #ef4444; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #dc2626; }",
    "btn_warning": "QPushButton { background-color: #f59e0b; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #d97706; }",
    "btn_random": "QPushButton { background-color: #8b5cf6; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #7c3aed; }",
    "btn_secondary": "QPushButton { background-color: #6b7280; color: white; border-radius: 6px; padding: 8px 16px; } QPushButton:hover { background-color: #4b5563; }",
    "input": "QLineEdit { border: 1px solid #d1d5db; border-radius: 6px; padding: 8px; background-color: #f9fafb; } QLineEdit:focus { border: 1px solid #3b82f6; background-color: white; }",
    "group_box": "QGroupBox { font-weight: bold; border: 1px solid #e5e7eb; border-radius: 8px; margin-top: 12px; background-color: white; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #374151; }"
}


def lerp(start, end, t):
    """线性插值"""
    return start + (end - start) * t


class VisualArea(QWidget):
    """通用数据结构可视化组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px;")
        self.data_structure = None
        self.highlighted_index = -1
        self.highlighted_node = None
        self.highlight_color = QColor(255, 215, 0)
        self.anim_state = {}
        self.traversal_text = None
        self.bfs_index_map = {}
        self.cell_width = 120
        self.cell_height = 45
        self.cell_spacing = 8
        self.tree_level_spacing = 60
        self.node_radius = 22

    def set_data_structure(self, ds):
        self.data_structure = ds
        self.update()

    def update_visualization(self, ds=None, highlighted_index=-1):
        if ds is not None: self.data_structure = ds
        self.highlighted_index = highlighted_index
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._draw_background_grid(painter)
        if not self.data_structure:
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.setPen(QColor(156, 163, 175))
            painter.drawText(self.rect(), Qt.AlignCenter, "可视化区域准备就绪\n请在左侧进行操作")
            return
        if isinstance(self.data_structure, (Stack, SequenceList)):
            self._draw_linear_structure(painter)
        elif isinstance(self.data_structure, LinkedList):
            self._draw_linked_list(painter)
        elif isinstance(self.data_structure, BinaryTree):
            self._draw_tree(painter)
        if self.traversal_text:
            self._draw_traversal_text(painter)

    def _draw_traversal_text(self, painter):
        painter.save()
        painter.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        painter.setPen(QColor(37, 99, 235))
        rect = self.rect()
        text_rect = rect.adjusted(20, rect.height() - 80, -20, -20)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.traversal_text)
        painter.restore()

    def _draw_background_grid(self, painter):
        painter.save()
        painter.setPen(QPen(QColor(243, 244, 246), 1))
        step = 40
        for x in range(0, self.width(), step): painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step): painter.drawLine(0, y, self.width(), y)
        painter.restore()

    def _draw_linear_structure(self, painter):
        ds = self.data_structure
        length = ds.length()
        if length == 0:
            painter.setFont(QFont("Microsoft YaHei", 12, QFont.Italic))
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "空结构")
            return
        area_width = self.width()
        area_height = self.height()
        start_x = max(10, (area_width - self.cell_width) // 2)
        is_stack = isinstance(ds, Stack)

        if is_stack:
            stack_height = length * self.cell_height + (length - 1) * self.cell_spacing
            start_y = (area_height + stack_height) // 2
            if start_y + 40 > area_height: start_y = area_height - 40
        else:
            total_width = length * self.cell_width + (length - 1) * self.cell_spacing
            if total_width > area_width - 40:
                start_x_seq = 20
            else:
                start_x_seq = (area_width - total_width) // 2

        for i in range(length):
            painter.save()
            if is_stack:
                x_pos = start_x
                y_pos = start_y - i * (self.cell_height + self.cell_spacing)
            else:
                x_pos = start_x_seq + i * (self.cell_width + self.cell_spacing)
                y_pos = area_height // 2 - self.cell_height // 2

            bg_color = QColor(219, 234, 254)
            if i == self.highlighted_index: bg_color = QColor(250, 204, 21)

            if self.anim_state and self.anim_state.get('index') == i:
                anim_type = self.anim_state.get('type')
                if anim_type == 'push':
                    scale = self.anim_state.get('scale', 1.0)
                    center_x = x_pos + self.cell_width / 2
                    center_y = y_pos + self.cell_height / 2
                    painter.translate(center_x, center_y)
                    painter.scale(scale, scale)
                    painter.translate(-center_x, -center_y)
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
            painter.drawRect(int(x_pos), int(y_pos), self.cell_width, self.cell_height)

            painter.setPen(QPen(QColor(107, 114, 128), 1))
            painter.setFont(QFont("Arial", 9))
            idx_str = str(i)
            if is_stack:
                painter.drawText(int(x_pos - 35), int(y_pos), 30, self.cell_height, Qt.AlignRight | Qt.AlignVCenter,
                                 idx_str)
            else:
                painter.drawText(int(x_pos), int(y_pos - 25), self.cell_width, 20, Qt.AlignCenter, idx_str)

            painter.setPen(QPen(QColor(17, 24, 39), 1))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            try:
                painter.drawText(int(x_pos), int(y_pos), self.cell_width, self.cell_height, Qt.AlignCenter, str(ds[i]))
            except:
                pass
            painter.restore()

        if is_stack and length > 0:
            bottom_y = start_y + self.cell_height + 5
            painter.setPen(QPen(QColor(75, 85, 99), 2))
            painter.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
            painter.drawText(int(start_x), int(bottom_y), self.cell_width, 30, Qt.AlignCenter, "Stack Bottom")

            top_idx = length - 1
            top_y_pos = start_y - top_idx * (self.cell_height + self.cell_spacing)
            label_y = top_y_pos - 30
            painter.setPen(QPen(QColor(220, 38, 38), 2))
            painter.drawText(int(start_x), int(label_y), self.cell_width, 25, Qt.AlignCenter, "Stack Top")

    def drawArrow(self, painter, start_x, start_y, end_x, end_y, color=QColor(59, 130, 246), opacity=1.0, progress=1.0):
        if progress <= 0.01 or opacity <= 0.01: return
        painter.save()
        painter.setOpacity(opacity)
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(color))

        draw_end_x = start_x + (end_x - start_x) * progress
        draw_end_y = start_y + (end_y - start_y) * progress

        painter.drawLine(int(start_x), int(start_y), int(draw_end_x), int(draw_end_y))

        if progress > 0.8:
            angle = math.atan2(end_y - start_y, end_x - start_x) * 180 / math.pi
            arrow_size = 10
            p1 = QPointF(draw_end_x - arrow_size * math.cos(math.radians(angle + 30)),
                         draw_end_y - arrow_size * math.sin(math.radians(angle + 30)))
            p2 = QPointF(draw_end_x - arrow_size * math.cos(math.radians(angle - 30)),
                         draw_end_y - arrow_size * math.sin(math.radians(angle - 30)))
            arrow_head = QPolygonF()
            arrow_head.append(QPointF(draw_end_x, draw_end_y))
            arrow_head.append(p1)
            arrow_head.append(p2)
            painter.drawPolygon(arrow_head)
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

        area_width = self.width()
        area_height = self.height()
        node_w = self.cell_width
        node_h = self.cell_height
        gap = 70
        step_w = node_w + gap

        display_count = length
        if anim_type == 'linked_insert': display_count = length
        total_w = display_count * step_w
        if anim_type == 'linked_insert': total_w += step_w

        if total_w > area_width - 40:
            start_x = 40
        else:
            start_x = (area_width - total_w) // 2 + 20
        base_y = area_height // 2 - node_h // 2

        for i in range(length):
            curr_x = start_x + i * step_w
            curr_y = base_y

            if anim_type == 'linked_insert' and i >= target_idx:
                shift_val = 0
                if phase == 'shift':
                    shift_val = lerp(0, step_w, progress)
                elif phase in ['appear', 'link_next', 'link_prev', 'lift']:
                    shift_val = step_w
                curr_x += shift_val

            if anim_type == 'linked_delete':
                if i == target_idx:
                    if phase == 'drop':
                        curr_y += lerp(0, 100, progress)
                    elif phase in ['connect_bypass', 'fade_next_link', 'close']:
                        curr_y += 100
                elif i > target_idx:
                    if phase == 'close': curr_x -= lerp(0, step_w, progress)

            bg_c = QColor(219, 234, 254)
            border_c = QColor(30, 58, 138)
            if i == self.highlighted_index: bg_c = QColor(250, 204, 21)

            if anim_type == 'linked_search' and i == state.get('current_idx'):
                if phase == 'scanning':
                    bg_c = QColor(147, 197, 253)
                elif phase == 'found':
                    flash_t = state.get('flash_time', 0)
                    if int(flash_t * 5) % 2 == 0:
                        bg_c = QColor(50, 205, 50)
                    else:
                        bg_c = QColor(250, 204, 21)

            if anim_type == 'linked_delete' and i == target_idx:
                bg_c = QColor(254, 202, 202)
                border_c = QColor(220, 38, 38)
                if phase == 'close': painter.setOpacity(1.0 - progress)

            painter.save()
            painter.setBrush(QBrush(bg_c))
            painter.setPen(QPen(border_c, 2))
            painter.drawRect(int(curr_x), int(curr_y), node_w, node_h)
            painter.setPen(QPen(QColor(17, 24, 39), 1))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(int(curr_x), int(curr_y), node_w, node_h, Qt.AlignCenter, str(ll[i]))

            # Draw Index (Red, Top-Left)
            painter.setPen(QPen(QColor(220, 38, 38)))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(int(curr_x), int(curr_y - 5), 30, 15, Qt.AlignLeft, str(i))

            # Draw HEAD Label
            if i == 0:
                painter.setPen(QPen(Qt.black))
                painter.setFont(QFont("Arial", 10, QFont.Bold))
                painter.drawText(int(curr_x), int(curr_y - 25), node_w, 20, Qt.AlignCenter, "HEAD")

            painter.restore()

            if i < length - 1:
                next_i = i + 1
                next_x_v = start_x + next_i * step_w
                next_y_v = base_y

                if anim_type == 'linked_insert' and next_i >= target_idx:
                    shift_val = 0
                    if phase == 'shift':
                        shift_val = lerp(0, step_w, progress)
                    elif phase in ['appear', 'link_next', 'link_prev', 'lift']:
                        shift_val = step_w
                    next_x_v += shift_val

                if anim_type == 'linked_delete':
                    if next_i == target_idx:
                        if phase == 'drop':
                            next_y_v += lerp(0, 100, progress)
                        elif phase in ['connect_bypass', 'fade_next_link', 'close']:
                            next_y_v += 100
                    elif next_i > target_idx:
                        if phase == 'close': next_x_v -= lerp(0, step_w, progress)

                p1 = QPointF(curr_x + node_w, curr_y + node_h / 2)
                p2 = QPointF(next_x_v, next_y_v + node_h / 2)

                if anim_type == 'linked_insert' and i == target_idx - 1:
                    alpha = 1.0
                    if phase == 'link_prev':
                        alpha = 1.0 - progress
                    elif phase == 'lift':
                        alpha = 0.0
                    if alpha > 0: self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y(), opacity=alpha)

                    if phase in ['link_prev', 'lift']:
                        new_node_x = start_x + target_idx * step_w
                        new_node_y = base_y + 100
                        if phase == 'lift': new_node_y = lerp(base_y + 100, base_y, progress)
                        target_new = QPointF(new_node_x, new_node_y + node_h / 2)
                        growth = progress if phase == 'link_prev' else 1.0
                        self.drawArrow(painter, p1.x(), p1.y(), target_new.x(), target_new.y(),
                                       color=QColor(16, 185, 129), progress=growth)
                    continue

                if anim_type == 'linked_delete' and i == target_idx - 1:
                    alpha = 1.0
                    if phase == 'fade_prev_link':
                        alpha = 1.0 - progress
                    elif phase in ['drop', 'connect_bypass', 'fade_next_link', 'close']:
                        alpha = 0.0
                    if alpha > 0: self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y(), opacity=alpha)

                    if phase in ['connect_bypass', 'fade_next_link', 'close']:
                        bypass_dest_idx = target_idx + 1
                        if bypass_dest_idx < length:
                            dest_x = start_x + bypass_dest_idx * step_w
                            if phase == 'close': dest_x -= lerp(0, step_w, progress)
                            bypass_p2 = QPointF(dest_x, base_y + node_h / 2)
                            growth = 1.0
                            if phase == 'connect_bypass': growth = progress
                            self.drawArrow(painter, p1.x(), p1.y(), bypass_p2.x(), bypass_p2.y(),
                                           color=QColor(220, 38, 38), progress=growth)
                    continue

                if anim_type == 'linked_delete' and i == target_idx:
                    alpha = 1.0
                    if phase == 'fade_next_link':
                        alpha = 1.0 - progress
                    elif phase == 'close':
                        alpha = 0.0
                    self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y(), opacity=alpha)
                    continue

                self.drawArrow(painter, p1.x(), p1.y(), p2.x(), p2.y())

        if anim_type == 'linked_insert':
            nx = start_x + target_idx * step_w
            ny = base_y + 100

            alpha = 0.0
            if phase == 'shift':
                alpha = 0.0
            elif phase == 'appear':
                alpha = progress
            elif phase in ['link_next', 'link_prev']:
                alpha = 1.0
            elif phase == 'lift':
                alpha = 1.0
                ny = lerp(base_y + 100, base_y, progress)

            if alpha > 0:
                painter.save()
                painter.setOpacity(alpha)
                painter.setBrush(QBrush(QColor(167, 243, 208)))
                painter.setPen(QPen(QColor(5, 150, 105), 2))
                painter.drawRect(int(nx), int(ny), node_w, node_h)
                painter.setPen(QPen(Qt.black))
                painter.drawText(int(nx), int(ny), node_w, node_h, Qt.AlignCenter, str(new_val))
                painter.restore()

                if phase in ['link_next', 'link_prev', 'lift'] and target_idx < length:
                    next_node_x = start_x + (target_idx + 1) * step_w
                    next_node_y = base_y
                    arrow_op = progress if phase == 'link_next' else 1.0
                    self.drawArrow(painter, nx + node_w, ny + node_h / 2, next_node_x, next_node_y + node_h / 2,
                                   color=QColor(16, 185, 129), progress=arrow_op)

    def _draw_tree(self, painter):
        tree = self.data_structure
        if tree.is_empty():
            painter.setFont(QFont("Microsoft YaHei", 12, QFont.Italic))
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "空树")
            return
        self.bfs_index_map = {}
        if tree.root:
            queue = [tree.root]
            idx = 0
            while queue:
                node = queue.pop(0)
                self.bfs_index_map[node] = idx
                idx += 1
                if node.left_child: queue.append(node.left_child)
                if node.right_child: queue.append(node.right_child)
        tree_height = self._get_tree_height(tree.root)
        area_width = self.width()
        start_x = area_width // 2
        start_y = 50
        ideal_spacing = area_width / (2 ** (tree_height - 1) + 1)
        base_spacing = min(ideal_spacing, 120)
        base_spacing = max(base_spacing, 35)
        self._draw_tree_node(painter, tree.root, start_x, start_y, base_spacing, tree_height)
        painter.setPen(QPen(QColor(107, 114, 128), 1))
        painter.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        if isinstance(tree, HuffmanTree):
            tree_type = "哈夫曼树"
        elif isinstance(tree, BinarySearchTree):
            tree_type = "二叉搜索树"
        else:
            tree_type = "普通二叉树 (红色数字为操作索引)"
        painter.drawText(20, 30, 400, 30, Qt.AlignLeft, f"{tree_type} - 节点数: {tree.length()}")

    def _get_tree_height(self, node):
        if not node: return 0
        return 1 + max(self._get_tree_height(node.left_child), self._get_tree_height(node.right_child))

    def _draw_tree_node(self, painter, node, x, y, level_spacing, remaining_height):
        if not node: return
        radius = self.node_radius
        next_y = y + self.tree_level_spacing
        next_level_spacing = level_spacing * 0.55
        if node.left_child:
            left_x = x - level_spacing
            self._draw_tree_edge(painter, x, y, left_x, next_y, radius, is_left=True)
            self._draw_tree_node(painter, node.left_child, left_x, next_y, next_level_spacing, remaining_height - 1)
        if node.right_child:
            right_x = x + level_spacing
            self._draw_tree_edge(painter, x, y, right_x, next_y, radius, is_left=False)
            self._draw_tree_node(painter, node.right_child, right_x, next_y, next_level_spacing, remaining_height - 1)
        if hasattr(self, 'highlighted_node') and self.highlighted_node == node:
            painter.setBrush(QBrush(self.highlight_color))
        else:
            if isinstance(node, HuffmanNode):
                painter.setBrush(QBrush(QColor(167, 243, 208) if node.data is not None else QColor(254, 202, 202)))
            elif isinstance(self.data_structure, BinarySearchTree):
                painter.setBrush(QBrush(QColor(254, 215, 170)))
            else:
                painter.setBrush(QBrush(QColor(186, 230, 253)))
        painter.setPen(QPen(QColor(31, 41, 55), 2))
        painter.drawEllipse(QPoint(int(x), int(y)), radius, radius)
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        if isinstance(node, HuffmanNode):
            display_text = f"{node.data}\n{node.weight}" if node.data is not None else f"W:{node.weight}"
        else:
            display_text = str(node.data)
        text_rect = painter.boundingRect(int(x - radius), int(y - radius), radius * 2, radius * 2, Qt.AlignCenter,
                                         display_text)
        painter.drawText(text_rect, Qt.AlignCenter, display_text)
        if not isinstance(self.data_structure, (BinarySearchTree, HuffmanTree)):
            real_index = self.bfs_index_map.get(node, -1)
            if real_index != -1:
                painter.setPen(QPen(Qt.red))
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                painter.drawText(int(x + radius / 2), int(y - radius), 30, 15, Qt.AlignLeft, str(real_index))

    def _draw_tree_edge(self, painter, parent_x, parent_y, child_x, child_y, radius, is_left):
        angle = math.atan2(child_y - parent_y, child_x - parent_x)
        start_x = parent_x + radius * math.cos(angle)
        start_y = parent_y + radius * math.sin(angle)
        end_x = child_x - radius * math.cos(angle)
        end_y = child_y - radius * math.sin(angle)
        painter.setPen(QPen(QColor(156, 163, 175), 2))
        painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        if not isinstance(self.data_structure, BinarySearchTree):
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            painter.setFont(QFont("Arial", 8))
            painter.setPen(QPen(QColor(239, 68, 68)))
            offset_x = -8 if is_left else 4
            painter.drawText(int(mid_x + offset_x), int(mid_y), 15, 15, Qt.AlignCenter, "0" if is_left else "1")


class BaseVisualizer(QWidget):
    response_received = pyqtSignal(str)

    def __init__(self, main_window=None, last_window=None, title="数据结构可视化工具"):
        super().__init__()
        self.main_window = main_window
        self.last_window = last_window
        self.structure_type_mapping = {
            "栈 (Stack) 可视化工具": "Stack",
            "顺序表 (SequenceList) 可视化工具": "SequenceList",
            "链表 (LinkedList) 可视化工具": "LinkedList",
            "二叉树可视化工具": "BinaryTree",
            "哈夫曼树可视化工具": "HuffmanTree",
            "二叉搜索树 (BST) 可视化工具": "BinarySearchTree"
        }
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
        self.init_ui()
        self.setWindowState(Qt.WindowMaximized)
        self.update_recent_files_display()
        self.init_sound_effects()

    def init_sound_effects(self):
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("./DataStructureVisualization/button_click.wav"))
        self.click_sound.setVolume(0.7)

    def play_click_sound(self):
        if not self.click_sound.source().isEmpty(): self.click_sound.play()

    def init_ui(self):
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setLayout(root_layout)
        sidebar = QWidget()
        sidebar.setFixedWidth(380)
        sidebar.setStyleSheet("background-color: #f3f4f6; border-right: 1px solid #e5e7eb;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(20)
        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            "font-family: 'Microsoft YaHei'; font-size: 22px; font-weight: bold; color: #111827; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        sidebar_layout.addWidget(title_label)
        control_group = QGroupBox("核心操作")
        control_group.setStyleSheet(STYLES["group_box"])
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(15, 20, 15, 15)
        control_layout.setSpacing(15)
        control_layout.addLayout(self._create_input_layout())
        control_layout.addLayout(self._create_button_layout())
        control_group.setLayout(control_layout)
        sidebar_layout.addWidget(control_group)
        file_group = QGroupBox("文件管理")
        file_group.setStyleSheet(STYLES["group_box"])
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(15, 20, 15, 15)
        file_layout.setSpacing(12)
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
        sidebar_layout.addWidget(file_group)
        recent_group = QGroupBox("最近保存")
        recent_group.setStyleSheet(STYLES["group_box"])
        recent_group_layout = QVBoxLayout()
        recent_group_layout.setContentsMargins(1, 20, 1, 1)
        self.recent_list_widget = QWidget()
        self.recent_list_widget.setStyleSheet("background-color: white;")
        self.recent_list_layout = QVBoxLayout(self.recent_list_widget)
        self.recent_list_layout.setSpacing(6)
        self.recent_list_layout.setContentsMargins(10, 5, 10, 5)
        self.recent_list_layout.setAlignment(Qt.AlignTop)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.recent_list_widget)
        scroll.setMinimumHeight(130)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        recent_group_layout.addWidget(scroll)
        recent_group.setLayout(recent_group_layout)
        sidebar_layout.addWidget(recent_group)
        settings_group = QGroupBox("设置")
        settings_group.setStyleSheet(STYLES["group_box"])
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(15, 20, 15, 15)
        settings_layout.setSpacing(12)
        speed_layout = QHBoxLayout()
        speed_lbl = QLabel("动画速度(ms):")
        speed_lbl.setStyleSheet("font-family: 'Microsoft YaHei'; color: #4b5563;")
        speed_layout.addWidget(speed_lbl)
        self.speed_slider = QLineEdit(str(self.animation_speed))
        self.speed_slider.setStyleSheet(STYLES["input"])
        self.speed_slider.returnPressed.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        settings_layout.addLayout(speed_layout)
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
        sidebar_layout.addWidget(settings_group)
        sidebar_layout.addStretch()
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        visual_box = QGroupBox("可视化演示")
        visual_box.setStyleSheet(
            "QGroupBox { background-color: white; border: 1px solid #d1d5db; border-radius: 8px; font-size: 16px; font-weight: bold; color: #1f2937; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; top: 10px; }")
        vb_layout = QVBoxLayout()
        vb_layout.setContentsMargins(5, 35, 5, 5)
        self.visual_area = VisualArea(self)
        vb_layout.addWidget(self.visual_area)
        visual_box.setLayout(vb_layout)
        content_layout.addWidget(visual_box)
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(
            "background: #eff6ff; color: #1e40af; padding: 12px; border-radius: 6px; border: 1px solid #bfdbfe; font-family: 'Microsoft YaHei'; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.status_label)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(content_widget)

    def _create_input_layout(self):
        raise NotImplementedError

    def _create_button_layout(self):
        raise NotImplementedError

    def on_button_return_main_clicked(self):
        self.play_click_sound(); self.back_to_main()

    def on_button_return_clicked(self):
        self.play_click_sound(); self.last_window.show() if self.last_window else None; self.close()

    def back_to_main(self):
        self.main_window.show() if self.main_window else None; self.close()

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
            if 50 <= val <= 5000: self.animation_speed = val
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
        self.save_recent_files();
        self.update_recent_files_display()

    def update_recent_files_display(self):
        for i in reversed(range(self.recent_list_layout.count())): self.recent_list_layout.itemAt(
            i).widget().deleteLater()
        filtered = [f for f in self.recent_files if f.get('type') == self.current_structure_type]
        if not filtered: self.recent_list_layout.addWidget(QLabel("暂无记录")); return
        for f in filtered:
            item_widget = QWidget();
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(12, 10, 12, 10);
            item_layout.setSpacing(4)
            name_lbl = QLabel(f.get('name', 'Unknown'));
            name_lbl.setStyleSheet(
                "font-family: 'Microsoft YaHei'; font-weight: bold; color: #1f2937; font-size: 13px;")
            time_lbl = QLabel(f.get('time', ''));
            time_lbl.setStyleSheet("font-size: 11px; color: #6b7280;")
            item_layout.addWidget(name_lbl);
            item_layout.addWidget(time_lbl)
            item_widget.setStyleSheet(
                "QWidget { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; } QWidget:hover { background-color: #eff6ff; border-color: #3b82f6; }")
            item_widget.setCursor(Qt.PointingHandCursor);
            item_widget.mousePressEvent = lambda e, p=f['path']: self.load_recent_file(p)
            self.recent_list_layout.addWidget(item_widget)

    def load_recent_file(self, filepath):
        if not os.path.exists(filepath): QMessageBox.warning(self, "错误",
                                                             f"文件不存在:\n{filepath}"); self.recent_files = [f for f
                                                                                                               in
                                                                                                               self.recent_files
                                                                                                               if f[
                                                                                                                   'path'] != filepath]; self.save_recent_files(); self.update_recent_files_display(); return
        from model import DataStructureManager
        try:
            obj = DataStructureManager.load_structure(filepath)
            if obj:
                self.data_structure = obj; self.visual_area.set_data_structure(
                    obj); self.update_display(); self.status_label.setText(f"已加载: {os.path.basename(filepath)}")
            else:
                QMessageBox.warning(self, "错误", "文件加载失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载异常: {e}")

    def save_structure(self):
        fname, _ = QFileDialog.getSaveFileName(self, "保存", "", "JSON (*.json)")
        if fname:
            if not fname.endswith('.json'): fname += '.json'
            from model import DataStructureManager
            if DataStructureManager.save_structure(self.data_structure, fname): self.add_to_recent_files(
                fname); QMessageBox.information(self, "成功", "保存成功")

    def load_structure(self):
        fname, _ = QFileDialog.getOpenFileName(self, "打开", "", "JSON (*.json)")
        if fname:
            from model import DataStructureManager
            obj = DataStructureManager.load_structure(fname)
            if obj: self.data_structure = obj; self.visual_area.set_data_structure(
                obj); self.update_display(); self.add_to_recent_files(fname)


class StackVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "栈 (Stack) 可视化工具")
        self.data_structure = Stack()
        self.visual_area.set_data_structure(self.data_structure)
        self.anim_timer = QTimer();
        self.anim_timer.timeout.connect(self.update_animation)

    def _create_input_layout(self):
        l = QHBoxLayout();
        self.push_input = QLineEdit();
        self.push_input.setStyleSheet(STYLES["input"]);
        self.push_input.setPlaceholderText("元素值")
        btn = QPushButton("入栈");
        btn.setStyleSheet(STYLES["btn_success"]);
        btn.clicked.connect(self.handle_push)
        l.addWidget(self.push_input);
        l.addWidget(btn);
        return l

    def _create_button_layout(self):
        l = QHBoxLayout();
        l.setSpacing(15)
        b1 = QPushButton("出栈");
        b1.clicked.connect(self.handle_pop);
        b1.setStyleSheet(STYLES["btn_warning"])
        b2 = QPushButton("随机生成");
        b2.clicked.connect(self.random_build);
        b2.setStyleSheet(STYLES["btn_random"])
        b3 = QPushButton("清空");
        b3.clicked.connect(self.handle_clear);
        b3.setStyleSheet(STYLES["btn_danger"])
        l.addWidget(b1);
        l.addWidget(b2);
        l.addWidget(b3);
        return l

    def handle_push(self):
        try:
            if self.push_input.text():
                self.data_structure.push(self.push_input.text());
                self.push_input.clear()
                self.visual_area.anim_state = {'type': 'push', 'index': self.data_structure.length() - 1, 'scale': 0.1}
                self.anim_timer.start(30);
                self.update_display()
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def handle_pop(self):
        try:
            if not self.data_structure.is_empty():
                self.visual_area.anim_state = {'type': 'highlight', 'index': self.data_structure.length() - 1,
                                               'offset_y': 0}
                self.update_display();
                QTimer.singleShot(500, self.start_pop_animation)
            else:
                QMessageBox.warning(self, "错误", "栈已空")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def start_pop_animation(self):
        self.visual_area.anim_state = {'type': 'pop', 'index': self.data_structure.length() - 1,
                                       'offset_y': 0}; self.anim_timer.start(30)

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state: self.anim_timer.stop(); return
        if state['type'] == 'push':
            state['scale'] += 0.1
            if state['scale'] >= 1.0: state['scale'] = 1.0; self.anim_timer.stop(); self.visual_area.anim_state = {}
        elif state['type'] == 'pop':
            state['offset_y'] -= 15
            if state[
                'offset_y'] < -300: self.anim_timer.stop(); self.visual_area.anim_state = {}; self.data_structure.pop(); self.status_label.setText(
                f"出栈完成, 当前栈深: {self.data_structure.length()}")
        self.update_display()

    def handle_clear(self):
        self.data_structure.clear(); self.update_display()

    def random_build(self):
        self.data_structure.clear();
        [self.data_structure.push(random.randint(1, 100)) for _ in range(random.randint(5, 10))]
        self.update_display();
        self.status_label.setText("已随机生成栈")

    def _update_status_text(self):
        self.status_label.setText(f"当前栈深: {self.data_structure.length()}")


class SequenceListVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "顺序表 (SequenceList) 可视化工具")
        self.data_structure = SequenceList();
        self.visual_area.set_data_structure(self.data_structure)
        self.anim_timer = QTimer();
        self.anim_timer.timeout.connect(self.update_animation)

    def _create_input_layout(self):
        l = QVBoxLayout();
        l.setSpacing(12);
        row1 = QHBoxLayout()
        self.input_val = QLineEdit();
        self.input_val.setStyleSheet(STYLES["input"]);
        self.input_val.setPlaceholderText("数值 (Value)")
        self.input_idx = QLineEdit();
        self.input_idx.setStyleSheet(STYLES["input"]);
        self.input_idx.setPlaceholderText("索引 (Index)");
        self.input_idx.setFixedWidth(100)
        row1.addWidget(QLabel("值:"));
        row1.addWidget(self.input_val);
        row1.addWidget(QLabel("下标:"));
        row1.addWidget(self.input_idx);
        l.addLayout(row1);
        return l

    def _create_button_layout(self):
        grid = QGridLayout();
        grid.setSpacing(12)
        btn_insert = QPushButton("插入");
        btn_insert.setStyleSheet(STYLES["btn_success"]);
        btn_insert.clicked.connect(self.handle_insert)
        btn_delete = QPushButton("删除");
        btn_delete.setStyleSheet(STYLES["btn_warning"]);
        btn_delete.clicked.connect(self.handle_delete)
        btn_locate = QPushButton("查找");
        btn_locate.setStyleSheet(STYLES["btn_primary"]);
        btn_locate.clicked.connect(self.handle_locate)
        btn_rand = QPushButton("随机生成");
        btn_rand.setStyleSheet(STYLES["btn_random"]);
        btn_rand.clicked.connect(self.random_build)
        btn_clear = QPushButton("清空");
        btn_clear.setStyleSheet(STYLES["btn_danger"]);
        btn_clear.clicked.connect(self.handle_clear)
        grid.addWidget(btn_insert, 0, 0);
        grid.addWidget(btn_delete, 0, 1);
        grid.addWidget(btn_locate, 1, 0);
        grid.addWidget(btn_rand, 1, 1);
        grid.addWidget(btn_clear, 2, 0, 1, 2);
        return grid

    def _get_val_from_input(self, text):
        try:
            return int(text)
        except:
            return text

    def handle_insert(self):
        try:
            text = self.input_val.text()
            if not text: QMessageBox.warning(self, "错误", "请输入数值"); return
            val = self._get_val_from_input(text);
            idx = int(self.input_idx.text()) if self.input_idx.text() else self.data_structure.length()
            self.data_structure.insert(idx, val);
            self.push_input_clear()
            self.visual_area.anim_state = {'type': 'push', 'index': idx, 'scale': 0.1}
            self.anim_timer.start(30);
            self.update_display();
            self.status_label.setText(f"已在索引 {idx} 插入 {val}")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def push_input_clear(self):
        self.input_val.clear(); self.input_idx.clear()

    def handle_delete(self):
        val_text = self.input_val.text().strip();
        idx_text = self.input_idx.text().strip()
        if val_text and idx_text: QMessageBox.warning(self, "错误", "请只填写【数值】或【索引】其中一项"); return
        if not val_text and not idx_text: QMessageBox.warning(self, "错误", "请填写【数值】或【索引】进行删除"); return
        target_idx = -1
        try:
            if idx_text:
                target_idx = int(idx_text)
                if target_idx < 0 or target_idx >= self.data_structure.length(): QMessageBox.warning(self, "错误",
                                                                                                     "索引越界"); return
            else:
                val = self._get_val_from_input(val_text);
                target_idx = self.data_structure.locate(val)
                if target_idx == -1: QMessageBox.warning(self, "错误", f"未找到数值: {val_text}"); return
            self.visual_area.anim_state = {'type': 'highlight', 'index': target_idx}
            self.update_display();
            QTimer.singleShot(500, lambda: self.start_pop_animation(target_idx))
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def start_pop_animation(self, idx):
        self.visual_area.anim_state = {'type': 'pop', 'index': idx, 'offset_y': 0}; self.anim_timer.start(30)

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state: self.anim_timer.stop(); return
        if state['type'] == 'push':
            state['scale'] += 0.1
            if state['scale'] >= 1.0: state['scale'] = 1.0; self.anim_timer.stop(); self.visual_area.anim_state = {}
        elif state['type'] == 'pop':
            state['offset_y'] -= 15
            if state['offset_y'] < -300:
                self.anim_timer.stop();
                idx = state['index']
                try:
                    self.data_structure.remove(idx)
                except:
                    pass
                self.visual_area.anim_state = {};
                self.status_label.setText(f"删除完成");
                self.push_input_clear()
        self.update_display()

    def handle_locate(self):
        text = self.input_val.text()
        if not text: QMessageBox.warning(self, "错误", "请输入要查找的值"); return
        val = self._get_val_from_input(text);
        idx = self.data_structure.locate(val)
        if idx != -1:
            self.highlighted_index = idx; self.update_display(); self.status_label.setText(
                f"找到元素 {val} 在索引: {idx}")
        else:
            self.highlighted_index = -1; self.update_display(); QMessageBox.information(self, "查找结果",
                                                                                        f"未找到元素: {val}")

    def handle_clear(self):
        self.data_structure.clear(); self.highlighted_index = -1; self.update_display()

    def random_build(self):
        self.data_structure.clear(); [self.data_structure.insert(i, random.randint(1, 100)) for i in
                                      range(random.randint(5, 10))]; self.update_display(); self.status_label.setText(
            "已随机生成顺序表")

    def _update_status_text(self):
        pass


class LinkedListVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "链表 (LinkedList) 可视化工具")
        self.data_structure = LinkedList();
        self.visual_area.set_data_structure(self.data_structure)
        self.anim_timer = QTimer();
        self.anim_timer.timeout.connect(self.update_animation)

    def _create_input_layout(self):
        l = QVBoxLayout();
        l.setSpacing(12);
        row1 = QHBoxLayout()
        self.input_val = QLineEdit();
        self.input_val.setStyleSheet(STYLES["input"]);
        self.input_val.setPlaceholderText("节点值")
        self.input_idx = QLineEdit();
        self.input_idx.setStyleSheet(STYLES["input"]);
        self.input_idx.setPlaceholderText("索引");
        self.input_idx.setFixedWidth(100)
        row1.addWidget(QLabel("值:"));
        row1.addWidget(self.input_val);
        row1.addWidget(QLabel("索引:"));
        row1.addWidget(self.input_idx);
        l.addLayout(row1);
        return l

    def _create_button_layout(self):
        grid = QGridLayout();
        grid.setSpacing(12)
        btn_head = QPushButton("头插");
        btn_head.setStyleSheet(STYLES["btn_success"]);
        btn_head.clicked.connect(self.handle_head_insert)
        btn_tail = QPushButton("尾插");
        btn_tail.setStyleSheet(STYLES["btn_success"]);
        btn_tail.clicked.connect(self.handle_tail_insert)
        btn_insert = QPushButton("指定插入");
        btn_insert.setStyleSheet(STYLES["btn_primary"]);
        btn_insert.clicked.connect(self.handle_insert_idx)
        btn_del = QPushButton("删除");
        btn_del.setStyleSheet(STYLES["btn_warning"]);
        btn_del.clicked.connect(self.handle_delete)
        btn_loc = QPushButton("查找");
        btn_loc.setStyleSheet(STYLES["btn_primary"]);
        btn_loc.clicked.connect(self.handle_locate)
        btn_rand = QPushButton("随机生成");
        btn_rand.setStyleSheet(STYLES["btn_random"]);
        btn_rand.clicked.connect(self.random_build)
        btn_clr = QPushButton("清空");
        btn_clr.setStyleSheet(STYLES["btn_danger"]);
        btn_clr.clicked.connect(self.handle_clear)
        grid.addWidget(btn_head, 0, 0);
        grid.addWidget(btn_tail, 0, 1);
        grid.addWidget(btn_insert, 1, 0);
        grid.addWidget(btn_del, 1, 1)
        grid.addWidget(btn_loc, 2, 0);
        grid.addWidget(btn_rand, 2, 1);
        grid.addWidget(btn_clr, 3, 0, 1, 2);
        return grid

    def _get_val_from_input(self, text):
        try:
            return int(text)
        except:
            return text

    def start_insert_animation(self, idx, val):
        start_phase = 'shift'
        if idx >= self.data_structure.length(): start_phase = 'appear'
        self.visual_area.anim_state = {'type': 'linked_insert', 'target_idx': idx, 'new_val': val, 'phase': start_phase,
                                       'progress': 0.0}
        self.anim_timer.start(20)

    def start_delete_animation(self, idx):
        self.visual_area.anim_state = {'type': 'linked_delete', 'target_idx': idx, 'phase': 'fade_prev_link',
                                       'progress': 0.0}
        self.anim_timer.start(20)

    def start_search_animation(self, val):
        self.visual_area.highlighted_index = -1
        self.visual_area.anim_state = {'type': 'linked_search', 'current_idx': 0, 'target_val': val,
                                       'phase': 'scanning', 'flash_time': 0}
        self.update_display()
        self.anim_timer.start(400)

    def update_animation(self):
        state = self.visual_area.anim_state
        if not state: self.anim_timer.stop(); return
        if state['type'] == 'linked_search':
            if state['phase'] == 'scanning':
                idx = state['current_idx']
                if idx < self.data_structure.length():
                    self.visual_area.highlighted_index = -1
                    curr_val = self.data_structure.get(idx)
                    if str(curr_val) == str(state['target_val']):
                        state['phase'] = 'found';
                        self.highlighted_index = idx
                        self.anim_timer.setInterval(100)
                    else:
                        state['current_idx'] += 1
                else:
                    self.highlighted_index = -1;
                    self.anim_timer.stop();
                    self.visual_area.anim_state = {}
                    QMessageBox.information(self, "提示", "未找到元素")
            elif state['phase'] == 'found':
                state['flash_time'] += 1
                if state[
                    'flash_time'] > 30: self.anim_timer.stop(); self.visual_area.anim_state = {}; self.highlighted_index = -1; self.update_display()
            self.update_display()
            # Manually set status text after update_display
            if state['phase'] == 'found':
                self.status_label.setText(f"找到元素 {state['target_val']} 在索引 {state['current_idx']}")
            return

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
                    self.visual_area.anim_state = {};
                    self.anim_timer.stop();
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
                    self.visual_area.anim_state = {};
                    self.anim_timer.stop();
                    self.status_label.setText(f"删除完成: {val}")
        self.update_display()

    def handle_head_insert(self):
        text = self.input_val.text()
        if text:
            val = self._get_val_from_input(text); self.start_insert_animation(0, val)
        else:
            QMessageBox.warning(self, "错误", "请输入值")

    def handle_tail_insert(self):
        text = self.input_val.text()
        if text:
            val = self._get_val_from_input(text); idx = self.data_structure.length(); self.start_insert_animation(idx,
                                                                                                                  val)
        else:
            QMessageBox.warning(self, "错误", "请输入值")

    def handle_insert_idx(self):
        try:
            text = self.input_val.text();
            val = self._get_val_from_input(text);
            idx = int(self.input_idx.text())
            if idx < 0 or idx > self.data_structure.length(): QMessageBox.warning(self, "错误", "索引越界"); return
            self.start_insert_animation(idx, val)
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def handle_delete(self):
        try:
            idx_text = self.input_idx.text();
            val_text = self.input_val.text()
            if idx_text:
                idx = int(idx_text)
                if idx < 0 or idx >= self.data_structure.length(): QMessageBox.warning(self, "错误", "索引越界"); return
                self.start_delete_animation(idx)
            elif val_text:
                val = self._get_val_from_input(val_text);
                idx = self.data_structure.locate(val)
                if idx == -1: QMessageBox.warning(self, "错误", "未找到值"); return
                self.start_delete_animation(idx)
            else:
                QMessageBox.warning(self, "错误", "请输入索引或值")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def handle_locate(self):
        text = self.input_val.text()
        if not text: QMessageBox.warning(self, "错误", "请输入值"); return
        val = self._get_val_from_input(text);
        self.start_search_animation(val)

    def handle_clear(self):
        self.data_structure.clear(); self.highlighted_index = -1; self.update_display()

    def random_build(self):
        self.data_structure.clear(); [self.data_structure.append(random.randint(1, 100)) for _ in
                                      range(random.randint(5, 10))]; self.update_display(); self.status_label.setText(
            "已随机生成链表")

    def _update_status_text(self):
        self.status_label.setText(f"链表长度: {self.data_structure.length()}")


# ... (BinaryTreeVisualizer, HuffmanTreeVisualizer, BinarySearchTreeVisualizer code remains same)

class BinaryTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "二叉树可视化工具")
        self.data_structure = BinaryTree()
        self.visual_area.set_data_structure(self.data_structure)
        self.current_traversal_result = []

    def _create_input_layout(self):
        layout = QVBoxLayout();
        layout.setSpacing(12);
        root_layout = QHBoxLayout()
        self.root_input = QLineEdit();
        self.root_input.setStyleSheet(STYLES["input"]);
        self.root_input.setPlaceholderText("根节点数据")
        btn_root = QPushButton("创建/重置根");
        btn_root.setStyleSheet(STYLES["btn_danger"]);
        btn_root.clicked.connect(self.create_root)
        root_layout.addWidget(QLabel("根:"));
        root_layout.addWidget(self.root_input);
        root_layout.addWidget(btn_root);
        layout.addLayout(root_layout)
        child_layout = QHBoxLayout()
        self.parent_idx_input = QLineEdit();
        self.parent_idx_input.setStyleSheet(STYLES["input"]);
        self.parent_idx_input.setPlaceholderText("父节点索引");
        self.parent_idx_input.setFixedWidth(80)
        self.child_val_input = QLineEdit();
        self.child_val_input.setStyleSheet(STYLES["input"]);
        self.child_val_input.setPlaceholderText("新节点数据")
        child_layout.addWidget(QLabel("父索引:"));
        child_layout.addWidget(self.parent_idx_input);
        child_layout.addWidget(QLabel("数据:"));
        child_layout.addWidget(self.child_val_input);
        layout.addLayout(child_layout);
        return layout

    def _create_button_layout(self):
        main_layout = QVBoxLayout();
        main_layout.setSpacing(10);
        add_layout = QHBoxLayout()
        btn_left = QPushButton("添加左节点");
        btn_left.setStyleSheet(STYLES["btn_success"]);
        btn_left.clicked.connect(self.handle_add_left)
        btn_right = QPushButton("添加右节点");
        btn_right.setStyleSheet(STYLES["btn_success"]);
        btn_right.clicked.connect(self.handle_add_right)
        add_layout.addWidget(btn_left);
        add_layout.addWidget(btn_right);
        main_layout.addLayout(add_layout)
        trav_layout = QHBoxLayout()
        btn_pre = QPushButton("前序");
        btn_pre.setStyleSheet(STYLES["btn_primary"]);
        btn_pre.clicked.connect(lambda: self.start_traversal('pre'))
        btn_in = QPushButton("中序");
        btn_in.setStyleSheet(STYLES["btn_primary"]);
        btn_in.clicked.connect(lambda: self.start_traversal('in'))
        btn_post = QPushButton("后序");
        btn_post.setStyleSheet(STYLES["btn_primary"]);
        btn_post.clicked.connect(lambda: self.start_traversal('post'))
        trav_layout.addWidget(btn_pre);
        trav_layout.addWidget(btn_in);
        trav_layout.addWidget(btn_post);
        main_layout.addLayout(trav_layout)
        btn_rand = QPushButton("随机生成");
        btn_rand.setStyleSheet(STYLES["btn_random"]);
        btn_rand.clicked.connect(self.random_build);
        main_layout.addWidget(btn_rand);
        return main_layout

    def create_root(self):
        if self.root_input.text():
            self.data_structure = BinaryTree(self.root_input.text()); self.visual_area.set_data_structure(
                self.data_structure); self.update_display(); self.status_label.setText("根节点已创建")
        else:
            QMessageBox.warning(self, "错误", "请输入根节点数据")

    def handle_add_left(self):
        try:
            if not self.parent_idx_input.text(): raise ValueError("请输入父节点索引")
            p_idx = int(self.parent_idx_input.text());
            val = self.child_val_input.text()
            if not val: raise ValueError("请输入新节点数据")
            self.data_structure.insert_left(p_idx, val);
            self.update_display();
            self.status_label.setText(f"已在索引 {p_idx} 左侧添加 {val}")
        except Exception as e:
            QMessageBox.warning(self, "添加失败", str(e))

    def handle_add_right(self):
        try:
            if not self.parent_idx_input.text(): raise ValueError("请输入父节点索引")
            p_idx = int(self.parent_idx_input.text());
            val = self.child_val_input.text()
            if not val: raise ValueError("请输入新节点数据")
            self.data_structure.insert_right(p_idx, val);
            self.update_display();
            self.status_label.setText(f"已在索引 {p_idx} 右侧添加 {val}")
        except Exception as e:
            QMessageBox.warning(self, "添加失败", str(e))

    def start_traversal(self, type_):
        if self.data_structure.is_empty(): QMessageBox.warning(self, "错误", "树为空"); return
        self.animation_steps = [];
        self.current_traversal_result = [];
        self.visual_area.traversal_text = ""
        if type_ == 'pre':
            self._get_preorder_nodes(self.data_structure.root, self.animation_steps); name = "前序"
        elif type_ == 'in':
            self._get_inorder_nodes(self.data_structure.root, self.animation_steps); name = "中序"
        else:
            self._get_postorder_nodes(self.data_structure.root, self.animation_steps); name = "后序"
        self.is_animating = True;
        self.status_label.setText(f"正在进行{name}遍历...");
        self._run_animation()

    def _get_preorder_nodes(self, node, res):
        if node: res.append(node); self._get_preorder_nodes(node.left_child, res); self._get_preorder_nodes(
            node.right_child, res)

    def _get_inorder_nodes(self, node, res):
        if node: self._get_inorder_nodes(node.left_child, res); res.append(node); self._get_inorder_nodes(
            node.right_child, res)

    def _get_postorder_nodes(self, node, res):
        if node: self._get_postorder_nodes(node.left_child, res); self._get_postorder_nodes(node.right_child,
                                                                                            res); res.append(node)

    def _run_animation(self):
        if not self.animation_steps:
            self.visual_area.highlighted_node = None;
            self.is_animating = False;
            QTimer.singleShot(5000, self.clear_traversal_text);
            self.update_display();
            self.status_label.setText("遍历完成");
            return
        node = self.animation_steps.pop(0);
        self.current_traversal_result.append(str(node.data));
        content = ", ".join(self.current_traversal_result);
        self.visual_area.traversal_text = f"[ {content} ]"
        self.visual_area.highlighted_node = node;
        self.visual_area.highlight_color = QColor(50, 205, 50);
        self.update_display();
        QTimer.singleShot(self.animation_speed, self._run_animation)

    def clear_traversal_text(self):
        self.visual_area.traversal_text = None; self.update_display()

    def random_build(self):
        self.data_structure = BinaryTree(str(random.randint(1, 100)))
        for i in range(random.randint(5, 10)):
            curr_len = self.data_structure.length();
            parent_idx = (curr_len - 1) // 2;
            val = str(random.randint(1, 100))
            if curr_len % 2 != 0:
                self.data_structure.insert_left(parent_idx, val)
            else:
                self.data_structure.insert_right(parent_idx, val)
        self.update_display();
        self.status_label.setText("已随机生成完全二叉树")

    def _update_status_text(self):
        self.status_label.setText(f"节点总数: {self.data_structure.length()}")


class HuffmanTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, lastwindow=None):
        super().__init__(main_window, lastwindow, "哈夫曼树可视化工具")
        self.data_structure = HuffmanTree();
        self.visual_area.set_data_structure(self.data_structure)

    def _create_input_layout(self):
        l = QVBoxLayout();
        l.setSpacing(10);
        self.weight_input = QTextEdit();
        self.weight_input.setStyleSheet(
            "border: 1px solid #d1d5db; border-radius: 6px; padding: 8px; background-color: #f9fafb;");
        self.weight_input.setMaximumHeight(70);
        self.weight_input.setPlaceholderText("例: A:5, B:10, C:3")
        l.addWidget(QLabel("输入权重 (Key:Weight):"));
        l.addWidget(self.weight_input);
        return l

    def _create_button_layout(self):
        l = QHBoxLayout();
        btn = QPushButton("构建哈夫曼树");
        btn.setStyleSheet(STYLES["btn_success"]);
        btn.clicked.connect(self.build)
        btn_rand = QPushButton("随机生成");
        btn_rand.setStyleSheet(STYLES["btn_random"]);
        btn_rand.clicked.connect(self.random_build)
        l.addWidget(btn);
        l.addWidget(btn_rand);
        return l

    def build(self):
        try:
            text = self.weight_input.toPlainText();
            d = {}
            for item in text.split(','): k, v = item.split(':'); d[k.strip()] = int(v.strip())
            self.data_structure = HuffmanTree(d);
            self.visual_area.set_data_structure(self.data_structure);
            self.update_display();
            self.status_label.setText("构建成功")
        except:
            QMessageBox.warning(self, "错误", "格式错误，请使用 Key:Value, Key:Value")

    def random_build(self):
        import string;
        d = {};
        chars = string.ascii_uppercase
        for i in range(random.randint(4, 8)): d[chars[i]] = random.randint(1, 50)
        self.data_structure = HuffmanTree(d);
        self.visual_area.set_data_structure(self.data_structure);
        self.update_display()
        txt = ", ".join([f"{k}:{v}" for k, v in d.items()]);
        self.weight_input.setText(txt);
        self.status_label.setText("已随机生成")

    def _update_status_text(self):
        pass


class BinarySearchTreeVisualizer(BaseVisualizer):
    def __init__(self, main_window=None, last_window=None):
        super().__init__(main_window, last_window, "二叉搜索树 (BST) 可视化工具")
        self.data_structure = BinarySearchTree();
        self.visual_area.set_data_structure(self.data_structure);
        self.animation_steps = [];
        self.is_animating = False
        for v in [50, 30, 70, 20, 40, 60, 80]: self.data_structure.insert(v)
        self.update_display()

    def _create_input_layout(self):
        l = QHBoxLayout();
        self.value_input = QLineEdit();
        self.value_input.setStyleSheet(STYLES["input"]);
        self.value_input.setPlaceholderText("整数值");
        self.value_input.returnPressed.connect(self.start_insert)
        l.addWidget(QLabel("数值:"));
        l.addWidget(self.value_input);
        return l

    def _create_button_layout(self):
        grid = QGridLayout();
        grid.setSpacing(12)
        btn_ins = QPushButton("插入");
        btn_ins.setStyleSheet(STYLES["btn_success"]);
        btn_ins.clicked.connect(self.start_insert)
        btn_sch = QPushButton("查找");
        btn_sch.setStyleSheet(STYLES["btn_primary"]);
        btn_sch.clicked.connect(self.start_search)
        btn_del = QPushButton("删除");
        btn_del.setStyleSheet(STYLES["btn_warning"]);
        btn_del.clicked.connect(self.start_delete)
        btn_rand = QPushButton("随机");
        btn_rand.setStyleSheet(STYLES["btn_random"]);
        btn_rand.clicked.connect(self.random_build)
        btn_clr = QPushButton("清空");
        btn_clr.setStyleSheet(STYLES["btn_danger"]);
        btn_clr.clicked.connect(self.clear_tree)
        grid.addWidget(btn_ins, 0, 0);
        grid.addWidget(btn_sch, 0, 1);
        grid.addWidget(btn_del, 1, 0);
        grid.addWidget(btn_rand, 1, 1);
        grid.addWidget(btn_clr, 2, 0, 1, 2);
        return grid

    def _get_value(self):
        try:
            return int(self.value_input.text().strip())
        except:
            return None

    def start_insert(self):
        if self.is_animating: return
        val = self._get_value();
        if val is None: QMessageBox.warning(self, "错误", "请输入有效整数"); return
        self.is_animating = True;
        self.current_operation = 'insert';
        self.operation_data = val;
        self.status_label.setText(f"插入: {val}...");
        self.animation_steps = self._generate_path(val);
        self._run_animation()

    def start_search(self):
        if self.is_animating: return
        val = self._get_value()
        if val is None: QMessageBox.warning(self, "错误", "请输入有效整数"); return
        self.is_animating = True;
        self.current_operation = 'search';
        self.operation_data = val;
        self.status_label.setText(f"查找: {val}...");
        self.animation_steps = self._generate_path(val);
        self._run_animation()

    def start_delete(self):
        if self.is_animating: return
        val = self._get_value()
        if val is None: QMessageBox.warning(self, "错误", "请输入有效整数"); return
        self.is_animating = True;
        self.current_operation = 'delete';
        self.operation_data = val;
        self.status_label.setText(f"删除: {val}...");
        self.animation_steps = self._generate_path(val);
        self._run_animation()

    def _generate_path(self, val):
        steps = [];
        curr = self.data_structure.root
        while curr:
            steps.append(curr)
            if val == curr.data:
                break
            elif val < curr.data:
                curr = curr.left_child
            else:
                curr = curr.right_child
        return steps

    def _run_animation(self):
        if not self.animation_steps: self._finish_operation(); return
        node = self.animation_steps.pop(0);
        self.visual_area.highlighted_node = node;
        self.visual_area.highlight_color = QColor(255, 215, 0)
        if not self.animation_steps:
            if self.current_operation == 'search':
                if node.data == self.operation_data:
                    self.visual_area.highlighted_color = QColor(50, 205, 50); self.status_label.setText(
                        f"找到: {self.operation_data}")
                else:
                    self.visual_area.highlight_color = QColor(255, 69, 0); self.status_label.setText("未找到")
        self.update_display();
        QTimer.singleShot(self.animation_speed, self._run_animation)

    def _finish_operation(self):
        val = self.operation_data
        if self.current_operation == 'insert':
            self.data_structure.insert(val)
        elif self.current_operation == 'delete':
            if self.data_structure.delete(val):
                self.status_label.setText(f"已删除 {val}")
            else:
                self.status_label.setText(f"删除失败 {val}")
        self.visual_area.highlighted_node = None;
        self.is_animating = False;
        self.update_display();
        self.value_input.clear();
        self.value_input.setFocus()

    def clear_tree(self):
        self.data_structure.clear(); self.update_display()

    def random_build(self):
        self.clear_tree(); [self.data_structure.insert(v) for v in
                            random.sample(range(1, 100), 7)]; self.update_display()

    def _update_status_text(self):
        self.status_label.setText(f"节点数: {self.data_structure.length()}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DS Visualizer")
    app.setStyle('Fusion')
    window = BinarySearchTreeVisualizer()  # Default to BST for testing
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())