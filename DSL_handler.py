import time
from PyQt5.QtWidgets import QMessageBox

# 导入必要的类，以便进行类型检查和方法调用
try:
    # 假设 model.py 中的类结构如下
    from model import Stack, SequenceList, LinkedList, BinaryTree, BinarySearchTree, HuffmanTree, HuffmanStructNode
except ImportError:
    # 如果 model.py 不存在，使用桩代码，确保 DSLHandler 可以运行
    class Stack:
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

            # 对于 BST/Tree，直接执行操作
            is_tree_visualizer = self.vis.__class__.__name__ in ['BinaryTreeVisualizer', 'BinarySearchTreeVisualizer',
                                                                 'HuffmanTreeVisualizer']

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
            raise ValueError("语法错误，缺少冒号 (格式: COMMAND: args)")

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
            elif structure_type == 'SequenceList':
                for i, val in enumerate(vals): self.ds.insert(self.ds.length(), val)  # 默认尾插
            elif structure_type == 'LinkedList':
                for val in vals: self.ds.append(val)
            elif structure_type in ['BinaryTree', 'BinarySearchTree']:
                if not vals: return

                # 对于 BinaryTree，第一个元素视为根节点
                if structure_type == 'BinaryTree':
                    # 重新初始化树并设置根节点
                    self.vis.data_structure = BinaryTree(vals[0])
                    self.ds = self.vis.data_structure  # 更新 ds 引用

                    # 尝试进行顺序完全二叉树插入 (简化处理)
                    for i, val in enumerate(vals[1:]):
                        parent_idx = (i + 1 - 1) // 2
                        try:
                            if (i + 1) % 2 != 0:  # 奇数索引为左子节点
                                self.ds.insert_left(parent_idx, val)
                            else:  # 偶数索引为右子节点
                                self.ds.insert_right(parent_idx, val)
                        except (IndexError, ValueError):
                            # 忽略插入失败 (如父节点不存在或位置被占用，通常不会发生于顺序插入)
                            pass

                # 对于 BinarySearchTree，视为批量 insert
                elif structure_type == 'BinarySearchTree':
                    for val in vals: self.ds.insert(val)

        # === 2. INSERT 指令 ===
        elif cmd == 'INSERT':
            if not args:
                raise ValueError("INSERT 缺少参数 (格式: INSERT: value[, index] 或 INSERT: p_idx, value, L/R)")

            # --- 线性结构：Stack, SequenceList, LinkedList ---
            if structure_type in ['Stack', 'SequenceList', 'LinkedList']:
                val = self._get_val_from_str(args[0])
                idx = -1  # 默认为尾插或栈顶操作

                if len(args) == 2:
                    try:
                        idx = int(args[1])
                    except ValueError:
                        raise ValueError("INSERT 索引参数必须为整数")

                if structure_type == 'Stack':
                    self.ds.push(val)  # 忽略索引参数
                elif structure_type in ['SequenceList', 'LinkedList']:
                    if idx == -1 or idx == self.ds.length():  # 尾插
                        self.ds.insert(self.ds.length(), val)
                    elif 0 <= idx < self.ds.length():
                        self.ds.insert(idx, val)
                    else:
                        raise IndexError(f"INSERT 索引 {idx} 超出范围")

            # --- 树结构：BinarySearchTree ---
            elif structure_type == 'BinarySearchTree':
                val = self._get_val_from_str(args[0])
                self.ds.insert(val)  # BST 忽略其他参数

            # --- 树结构：BinaryTree ---
            elif structure_type == 'BinaryTree':
                if len(args) != 3:
                    raise ValueError("BinaryTree INSERT 格式: INSERT: p_idx, value, L/R")

                try:
                    p_idx = int(args[0])
                except ValueError:
                    raise ValueError("父节点索引必须为整数")

                val = self._get_val_from_str(args[1])
                direction = args[2].strip().upper()

                if self.ds.is_empty():
                    # 允许通过 INSERT 0, value, L/R 创建根节点，但更推荐 BUILD
                    if p_idx == 0:
                        # 假设 BinaryTree 不为空，如果为空，则不允许插入子节点
                        raise ValueError("空树请使用 BUILD 命令创建根节点")

                if direction == 'L':
                    self.ds.insert_left(p_idx, val)
                elif direction == 'R':
                    self.ds.insert_right(p_idx, val)
                else:
                    raise ValueError("方向参数必须是 L 或 R")

        # === 3. DELETE/REMOVE 指令 ===
        elif cmd in ['DELETE', 'REMOVE']:
            if not args:
                raise ValueError(f"{cmd} 缺少参数")

            # --- 线性结构 ---
            if structure_type in ['Stack', 'SequenceList', 'LinkedList']:

                # Stack：只支持 pop (忽略所有参数)
                if structure_type == 'Stack':
                    if self.ds.is_empty():
                        raise IndexError("栈为空，无法 pop")
                    self.ds.pop()
                    return

                # SequenceList / LinkedList：支持按索引删除
                try:
                    idx = int(args[0])
                except ValueError:
                    raise ValueError("DELETE 索引参数必须为整数")

                if 0 <= idx < self.ds.length():
                    self.ds.remove(idx)
                else:
                    raise IndexError(f"DELETE 索引 {idx} 超出范围")

            # --- 树结构 ---
            elif structure_type == 'BinarySearchTree':
                val = self._get_val_from_str(args[0])
                if not self.ds.delete(val):
                    raise ValueError(f"BST 中未找到要删除的元素: {val}")

            elif structure_type == 'BinaryTree':
                # BinaryTree 删除通常按索引删除子树
                try:
                    idx = int(args[0])
                except ValueError:
                    raise ValueError("BinaryTree DELETE 索引参数必须为整数")

                node_to_del = self.ds._get_node(idx)
                if not node_to_del:
                    raise IndexError(f"BinaryTree 中索引 {idx} 节点不存在")

                if node_to_del == self.ds.root:
                    self.ds.clear()  # 删除根节点，清空树
                else:
                    if node_to_del.parent.left_child == node_to_del:
                        node_to_del.parent.left_child = None
                    else:
                        node_to_del.parent.right_child = None

                    # 简化处理：大小需要重新计算，这里仅减1
                    self.ds._size -= 1

        else:
            raise ValueError(f"未知指令: {cmd}")