import time
from PyQt5.QtWidgets import QMessageBox

# 导入必要的类，以便进行类型检查和方法调用
try:
    # 假设 model.py 中的类结构如下
    from model import Stack, Queue, SequenceList, LinkedList, BinaryTree, BinarySearchTree, HuffmanTree, \
        HuffmanStructNode, \
        AVLTree
except ImportError:
    # 如果 model.py 不存在，使用桩代码，确保 DSLHandler 可以运行
    class Stack:
        pass


    class Queue:
        pass


    class SequenceList:
        pass


    class LinkedList:
        pass


    class BinaryTree:
        pass


    class BinarySearchTree:
        pass


    class HuffmanTree:
        pass


    class HuffmanStructNode:
        pass


    class AVLTree:
        pass


class DSLHandler:
    def __init__(self, visualizer):
        """
        :param visualizer: 当前激活的可视化窗口实例 (如 StackVisualizer, BinaryTreeVisualizer)
        """
        self.vis = visualizer
        self.ds = visualizer.data_structure

    def execute_script(self, script_text, flag):
        lines = script_text.strip().split('\n')
        errors = []

        # flag=1 表示禁用动画 (由 BaseVisualizer.run_dsl 传入)
        if flag == 1:
            # 暂停动画计时器
            if hasattr(self.vis, 'anim_timer'):
                self.vis.anim_timer.stop()
                self.vis.visual_area.anim_state = {}

            # 对于 BST/Tree/AVL，直接执行操作
            is_tree_visualizer = self.vis.__class__.__name__ in ['BinaryTreeVisualizer', 'BinarySearchTreeVisualizer',
                                                                 'HuffmanTreeVisualizer', 'AVLTreeVisualizer']

            # 对于线性结构，需要清空动画状态，否则绘图会出错
            if hasattr(self.vis.visual_area, 'anim_state'):
                self.vis.visual_area.anim_state = {}

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                self._parse_and_run_line(line)
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")

        # 确保执行完毕后刷新显示
        self.vis.update_display()

        if errors:
            return "\n".join(errors)
        return "执行成功"

    def _get_val_from_str(self, val_str):
        """尝试将字符串转换为数字，否则保留为字符串"""
        val_str = val_str.strip()
        try:
            return int(val_str)
        except ValueError:
            return val_str

    def _parse_and_run_line(self, line):
        # 分割指令和参数，例如 "INSERT: 50" -> ["INSERT", "50"]
        if ':' not in line:
            # 特殊情况：DEQUEUE 可能没有参数，但为了统一格式，建议还是带冒号
            # 或者在这里做一个宽容处理，如果指令是 DEQUEUE 且没冒号，视为无参
            if line.strip().upper() == 'DEQUEUE':
                cmd = 'DEQUEUE'
                args = []
            else:
                raise ValueError("语法错误，缺少冒号 (格式: COMMAND: args)")
        else:
            cmd, args_str = line.split(':', 1)
            cmd = cmd.strip().upper()
            # 移除空参数，并保留所有参数，包括可能的空格
            args = [x.strip() for x in args_str.split(',')]

        structure_type = self.ds.__class__.__name__

        # === 1. BUILD 指令 (批量构建/初始化) ===
        if cmd == 'BUILD':
            if hasattr(self.ds, 'clear'):
                self.ds.clear()

            # HuffmanTree 需要特殊处理：BUILD: A:10, B:20
            if structure_type == 'HuffmanTree':
                weight_dict = {}
                for item in args:
                    if ':' in item:
                        k, v = item.split(':', 1)
                        try:
                            weight_dict[k.strip()] = int(v.strip())
                        except ValueError:
                            raise ValueError(f"BUILD 参数错误: 哈夫曼树权重必须为整数 ({item})")
                if weight_dict:
                    self.ds.build_from_weights(weight_dict)
                return

            # 其他线性结构和树结构视为批量插入
            vals = [self._get_val_from_str(val) for val in args if val]

            if structure_type == 'Stack':
                for val in vals: self.ds.push(val)
            elif structure_type == 'Queue':  # [新增] 队列批量构建
                for val in vals: self.ds.enqueue(val)
            elif structure_type == 'SequenceList':
                for i, val in enumerate(vals): self.ds.insert(self.ds.length(), val)  # 默认尾插
            elif structure_type == 'LinkedList':
                for val in vals: self.ds.append(val)

            elif structure_type in ['BinaryTree', 'BinarySearchTree', 'AVLTree']:
                if not vals: return

                # 对于 BinaryTree，第一个元素视为根节点
                if structure_type == 'BinaryTree':
                    self.vis.data_structure = BinaryTree(vals[0])
                    self.ds = self.vis.data_structure
                    for i, val in enumerate(vals[1:]):
                        parent_idx = (i + 1 - 1) // 2
                        try:
                            if (i + 1) % 2 != 0:
                                self.ds.insert_left(parent_idx, val)
                            else:
                                self.ds.insert_right(parent_idx, val)
                        except (IndexError, ValueError):
                            pass

                elif structure_type in ['BinarySearchTree', 'AVLTree']:
                    for val in vals: self.ds.insert(val)

        # === 2. ENQUEUE 指令 (Queue 专用) ===
        elif cmd == 'ENQUEUE':
            if structure_type != 'Queue':
                raise ValueError("ENQUEUE 指令仅适用于队列 (Queue)")

            for item in args:
                if not item: continue
                val = self._get_val_from_str(item)
                self.ds.enqueue(val)

        # === 3. DEQUEUE 指令 (Queue 专用) ===
        elif cmd == 'DEQUEUE':
            if structure_type != 'Queue':
                raise ValueError("DEQUEUE 指令仅适用于队列 (Queue)")

            # 默认出队 1 次，如果指定了参数 (如 DEQUEUE: 2)，则出队 n 次
            count = 1
            if args and args[0]:
                try:
                    count = int(args[0])
                except ValueError:
                    pass  # 如果参数不是数字，忽略，默认1次

            for _ in range(count):
                if self.ds.is_empty():
                    # 队列空时停止或报错，这里选择安全停止
                    break
                self.ds.dequeue()

        # === 4. INSERT 指令 ===
        elif cmd == 'INSERT':
            if not args:
                raise ValueError("INSERT 缺少参数")

            # --- 线性结构 ---
            if structure_type in ['Stack', 'SequenceList', 'LinkedList']:
                val = self._get_val_from_str(args[0])
                idx = -1

                if len(args) == 2:
                    try:
                        idx = int(args[1])
                    except ValueError:
                        raise ValueError("INSERT 索引参数必须为整数")

                if structure_type == 'Stack':
                    self.ds.push(val)
                elif structure_type in ['SequenceList', 'LinkedList']:
                    if idx == -1 or idx == self.ds.length():
                        self.ds.insert(self.ds.length(), val)
                    elif 0 <= idx < self.ds.length():
                        self.ds.insert(idx, val)
                    else:
                        raise IndexError(f"INSERT 索引 {idx} 超出范围")

            # --- 树结构 ---
            elif structure_type in ['BinarySearchTree', 'AVLTree']:
                for item in args:
                    val = self._get_val_from_str(item)
                    self.ds.insert(val)

            elif structure_type == 'BinaryTree':
                if len(args) != 3:
                    raise ValueError("BinaryTree INSERT 格式: INSERT: p_idx, value, L/R")
                try:
                    p_idx = int(args[0])
                except ValueError:
                    raise ValueError("父节点索引必须为整数")
                val = self._get_val_from_str(args[1])
                direction = args[2].strip().upper()

                if self.ds.is_empty() and p_idx == 0:
                    raise ValueError("空树请使用 BUILD 命令创建根节点")

                if direction == 'L':
                    self.ds.insert_left(p_idx, val)
                elif direction == 'R':
                    self.ds.insert_right(p_idx, val)
                else:
                    raise ValueError("方向参数必须是 L 或 R")

        # === 5. DELETE/REMOVE 指令 ===
        elif cmd in ['DELETE', 'REMOVE']:
            if not args and structure_type != 'Stack':
                # Stack DELETE 可以无参(Pop)，其他通常需要参数
                if structure_type not in ['Stack', 'Queue']:  # Queue has DEQUEUE, handled above
                    raise ValueError(f"{cmd} 缺少参数")

            if structure_type in ['Stack', 'SequenceList', 'LinkedList']:
                if structure_type == 'Stack':
                    if self.ds.is_empty():
                        raise IndexError("栈为空，无法 pop")
                    self.ds.pop()
                    return

                try:
                    idx = int(args[0])
                except ValueError:
                    raise ValueError("DELETE 索引参数必须为整数")

                if 0 <= idx < self.ds.length():
                    self.ds.remove(idx)
                else:
                    raise IndexError(f"DELETE 索引 {idx} 超出范围")

            elif structure_type in ['BinarySearchTree', 'AVLTree']:
                for item in args:
                    val = self._get_val_from_str(item)
                    if not self.ds.delete(val):
                        raise ValueError(f"BST/AVL 中未找到要删除的元素: {val}")

            elif structure_type == 'BinaryTree':
                try:
                    idx = int(args[0])
                except ValueError:
                    raise ValueError("BinaryTree DELETE 索引参数必须为整数")
                node_to_del = self.ds._get_node(idx)
                if not node_to_del:
                    raise IndexError(f"BinaryTree 中索引 {idx} 节点不存在")
                if node_to_del == self.ds.root:
                    self.ds.clear()
                else:
                    if node_to_del.parent.left_child == node_to_del:
                        node_to_del.parent.left_child = None
                    else:
                        node_to_del.parent.right_child = None
                    self.ds._size -= 1

        else:
            raise ValueError(f"未知指令: {cmd}")