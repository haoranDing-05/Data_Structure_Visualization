from abc import ABC, abstractmethod
import json
import pickle


class Serializable(ABC):
    """可序列化接口"""

    @abstractmethod
    def to_dict(self):
        """将对象转换为字典"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        pass


class LinearList(ABC):
    """线性表抽象基类"""

    @abstractmethod
    def is_empty(self):
        """检查线性表是否为空"""
        pass

    @abstractmethod
    def length(self):
        """返回线性表的长度"""
        pass

    @abstractmethod
    def clear(self):
        """清空线性表"""
        pass

    @abstractmethod
    def display(self):
        """显示线性表内容"""
        pass

    def __len__(self):
        """支持len()函数"""
        return self.length()

    def __str__(self):
        """支持str()函数"""
        return f"{self.__class__.__name__}对象，长度: {self.length()}"


class SequenceList(LinearList, Serializable):
    """顺序表实现（基于Python列表）"""

    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def length(self):
        return len(self.items)

    def get(self, index):
        """获取指定位置的元素"""
        if 0 <= index < len(self.items):
            return self.items[index]
        raise IndexError("索引超出范围")

    def insert(self, index, item):
        """在指定位置插入元素"""
        if 0 <= index <= len(self.items):
            self.items.insert(index, item)
        else:
            raise IndexError("索引超出范围")

    def remove(self, index):
        """移除指定位置的元素"""
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        raise IndexError("索引超出范围")

    def locate(self, item):
        """查找元素的位置"""
        for i in range(len(self.items)):
            if self.items[i] == item:
                return i
        return -1

    def clear(self):
        """清空顺序表（修正：清空items列表）"""
        self.items = []

    def display(self):
        print(self.items)

    def append(self, item):
        """在末尾添加元素"""
        self.items.append(item)

    def __getitem__(self, index):
        """支持索引访问"""
        return self.get(index)

    def __setitem__(self, index, value):
        """支持索引赋值"""
        if 0 <= index < len(self.items):
            self.items[index] = value
        else:
            raise IndexError("索引超出范围")

    def to_dict(self):
        return {
            'type': 'SequenceList',
            'items': self.items.copy()
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.items = data['items'].copy()
        return obj


class Node:
    """链表节点类"""

    def __init__(self, data):
        self.data = data
        self.next = None

    def __str__(self):
        return str(self.data)


class LinkedList(LinearList, Serializable):
    """链表实现"""

    def __init__(self):
        self.head = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    def length(self):
        return self.size

    def insert(self, index, item):
        """在指定位置插入元素"""
        if index < 0 or index > self.size:
            raise IndexError("索引超出范围")

        new_node = Node(item)

        if index == 0:  # 插入到头部
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            for _ in range(index - 1):
                current = current.next
            new_node.next = current.next
            current.next = new_node

        self.size += 1

    def remove(self, index):
        """移除指定位置的元素"""
        if index < 0 or index >= self.size:
            raise IndexError("索引超出范围")

        if index == 0:  # 移除头部
            removed_item = self.head.data
            self.head = self.head.next
        else:
            current = self.head
            for _ in range(index - 1):
                current = current.next
            removed_item = current.next.data
            current.next = current.next.next

        self.size -= 1
        return removed_item

    def get(self, index):
        """获取指定位置的元素"""
        if index < 0 or index >= self.size:
            raise IndexError("索引超出范围")

        current = self.head
        for _ in range(index):
            current = current.next
        return current.data

    def locate(self, item):
        """查找元素的位置"""
        current = self.head
        index = 0
        while current:
            if current.data == item:
                return index
            current = current.next
            index += 1
        return -1

    def clear(self):
        """清空链表（修正：重置头节点和大小）"""
        self.head = None
        self.size = 0

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        print(elements)

    def append(self, item):
        """在末尾添加元素"""
        self.insert(self.size, item)

    def __getitem__(self, index):
        """支持索引访问"""
        return self.get(index)

    def to_dict(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next

        return {
            'type': 'LinkedList',
            'elements': elements
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        for element in data['elements']:
            obj.append(element)
        return obj


class Stack(SequenceList, Serializable):
    """栈类"""

    def push(self, item):
        """压入元素到栈顶"""
        self.append(item)

    def pop(self):
        """弹出栈顶元素"""
        if self.is_empty():
            raise IndexError("栈为空")
        return self.remove(self.length() - 1)

    def peek(self):
        """查看栈顶元素但不弹出"""
        if self.is_empty():
            raise IndexError("栈为空")
        return self.get(self.length() - 1)

    def display(self):
        """显示栈内容（从栈底到栈顶）"""
        print("栈内容:", self.items)

    def to_dict(self):
        return {
            'type': 'Stack',
            'items': self.items.copy()
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.items = data['items'].copy()
        return obj


class BinaryTreeNode:
    """二叉树节点类"""

    def __init__(self, data):
        self.data = data
        self.left_child = None  # 左子节点
        self.right_child = None  # 右子节点
        self.parent = None  # 父节点（可选）

    def __str__(self):
        return str(self.data)


class BinaryTree(LinearList, Serializable):
    """二叉树的链式存储实现"""

    def __init__(self, root_data=None):
        self.root = BinaryTreeNode(root_data) if root_data is not None else None
        self._size = 0 if root_data is None else 1

    def is_empty(self):
        return self.root is None

    def length(self):
        return self._size

    def clear(self):
        self.root = None
        self._size = 0

    def _preorder_traversal(self, node, result):
        """前序遍历辅助函数"""
        if node:
            result.append(node.data)
            self._preorder_traversal(node.left_child, result)
            self._preorder_traversal(node.right_child, result)

    def _inorder_traversal(self, node, result):
        """中序遍历辅助函数"""
        if node:
            self._inorder_traversal(node.left_child, result)
            result.append(node.data)
            self._inorder_traversal(node.right_child, result)

    def _postorder_traversal(self, node, result):
        """后序遍历辅助函数"""
        if node:
            self._postorder_traversal(node.left_child, result)
            self._postorder_traversal(node.right_child, result)
            result.append(node.data)

    def display(self):
        """显示二叉树的三种遍历结果"""
        preorder = []
        inorder = []
        postorder = []
        self._preorder_traversal(self.root, preorder)
        self._inorder_traversal(self.root, inorder)
        self._postorder_traversal(self.root, postorder)
        print(f"前序遍历: {preorder}")
        print(f"中序遍历: {inorder}")
        print(f"后序遍历: {postorder}")

    def _get_node(self, index):
        """根据索引获取节点（层序索引）"""
        if index < 0 or index >= self._size:
            # 允许传入 -1 或其他超出范围的值进行查找，但如果找到的节点不存在则返回None
            if index < 0:
                return None

        queue = [self.root]
        current_index = 0

        while queue:
            node = queue.pop(0)
            if current_index == index:
                return node
            current_index += 1
            if node.left_child:
                queue.append(node.left_child)
            if node.right_child:
                queue.append(node.right_child)
        return None

    def get(self, index):
        """获取指定索引位置的元素（层序索引）"""
        node = self._get_node(index)
        return node.data if node else None

    def insert_left(self, parent_index, data):
        """在指定父节点左侧插入新节点"""
        parent_node = self._get_node(parent_index)
        if not parent_node:
            # 允许通过索引查找父节点，如果父节点不存在，应该抛出索引错误
            if parent_index >= 0:
                raise IndexError("父节点索引无效")
            # 如果父节点为None（空树），无法执行插入操作（除了创建根节点）
            raise ValueError("当前树为空，无法插入子节点")

        if parent_node.left_child:
            raise ValueError("左子节点已存在")

        new_node = BinaryTreeNode(data)
        parent_node.left_child = new_node
        new_node.parent = parent_node
        self._size += 1

    def insert_right(self, parent_index, data):
        """在指定父节点右侧插入新节点"""
        parent_node = self._get_node(parent_index)
        if not parent_node:
            if parent_index >= 0:
                raise IndexError("父节点索引无效")
            raise ValueError("当前树为空，无法插入子节点")

        if parent_node.right_child:
            raise ValueError("右子节点已存在")

        new_node = BinaryTreeNode(data)
        parent_node.right_child = new_node
        new_node.parent = parent_node
        self._size += 1

    def to_dict(self):
        def node_to_dict(node):
            if not node:
                return None
            return {
                'data': node.data,
                'left_child': node_to_dict(node.left_child),
                'right_child': node_to_dict(node.right_child)
            }

        return {
            'type': 'BinaryTree',
            'root': node_to_dict(self.root),
            'size': self._size
        }

    @classmethod
    def from_dict(cls, data):
        def dict_to_node(node_dict):
            if not node_dict:
                return None
            node = BinaryTreeNode(node_dict['data'])
            node.left_child = dict_to_node(node_dict['left_child'])
            node.right_child = dict_to_node(node_dict['right_child'])

            # 恢复父节点连接 (复杂，为简化序列化通常省略)
            # 这里保持原样，因为 from_dict 不会恢复 parent 属性

            return node

        obj = cls()
        obj.root = dict_to_node(data['root'])
        # 简单地从 dict 中读取 size
        obj._size = data['size']
        return obj


class BinarySearchTree(BinaryTree, Serializable):
    """二叉搜索树实现"""

    def __init__(self):
        # 显式调用 BinaryTree 的 __init__ 但不设置根节点
        super().__init__(None)
        self._size = 0

    def _insert_recursive(self, node, data):
        """递归插入辅助函数"""
        # 数据类型检查，确保可比较
        if not isinstance(data, (int, float)) or not isinstance(node.data, (int, float)):
            # 尝试转换为可比较类型，否则报错
            try:
                data = float(data)
                node_data = float(node.data)
            except (ValueError, TypeError):
                # 如果不能转换为数字，则使用默认的 Python 比较（如果数据结构中混合了类型，这会很危险）
                node_data = node.data

        if data < node.data:
            if node.left_child is None:
                node.left_child = BinaryTreeNode(data)
                node.left_child.parent = node
                self._size += 1
            else:
                self._insert_recursive(node.left_child, data)
        elif data > node.data:
            if node.right_child is None:
                node.right_child = BinaryTreeNode(data)
                node.right_child.parent = node
                self._size += 1
            else:
                self._insert_recursive(node.right_child, data)
        # 如果 data == node.data，则不执行任何操作（BST 不允许重复元素）

    def insert(self, data):
        """插入元素"""
        if self.root is None:
            self.root = BinaryTreeNode(data)
            self._size = 1
        else:
            self._insert_recursive(self.root, data)

    def _search_recursive(self, node, data):
        """递归搜索辅助函数"""
        if node is None:
            return None

        # 数据类型检查和转换
        if not isinstance(data, (int, float)) or not isinstance(node.data, (int, float)):
            try:
                data = float(data)
                node_data = float(node.data)
            except (ValueError, TypeError):
                node_data = node.data

        if node.data == data:
            return node
        elif data < node.data:
            return self._search_recursive(node.left_child, data)
        else:
            return self._search_recursive(node.right_child, data)

    def search(self, data):
        """搜索元素是否存在并返回节点"""
        return self._search_recursive(self.root, data)

    def _find_min_node(self, node):
        """找到以node为根的子树中的最小值节点"""
        current = node
        while current.left_child:
            current = current.left_child
        return current

    def delete(self, data):
        """删除指定元素"""
        node = self._search_recursive(self.root, data)
        if not node:
            return False  # 元素不存在

        # 情况1：叶子节点
        if node.left_child is None and node.right_child is None:
            if node.parent:
                if node.parent.left_child == node:
                    node.parent.left_child = None
                else:
                    node.parent.right_child = None
            else:  # 根节点
                self.root = None

        # 情况2：只有一个子节点
        elif node.left_child is None or node.right_child is None:
            child = node.left_child if node.left_child else node.right_child
            if node.parent:
                if node.parent.left_child == node:
                    node.parent.left_child = child
                else:
                    node.parent.right_child = child
            else:  # 根节点
                self.root = child
            child.parent = node.parent

        # 情况3：有两个子节点
        else:
            # 找到中序后继（右子树最小值）
            successor = self._find_min_node(node.right_child)
            # 交换数据
            node.data = successor.data

            # 删除后继节点（后继节点最多只有一个右子节点）
            if successor.parent.left_child == successor:
                successor.parent.left_child = successor.right_child
            else:
                successor.parent.right_child = successor.right_child
            if successor.right_child:
                successor.right_child.parent = successor.parent

        self._size -= 1
        return True

    def display(self):
        """显示二叉搜索树（中序遍历结果为有序序列）"""
        inorder = []
        self._inorder_traversal(self.root, inorder)
        print(f"二叉搜索树（中序遍历）: {inorder}")

    def to_dict(self):
        data = super().to_dict()
        data['type'] = 'BinarySearchTree'
        return data

    @classmethod
    def from_dict(cls, data):
        temp = BinaryTree.from_dict(data)
        obj = cls()
        obj.root = temp.root
        obj._size = data['size']
        return obj


class HuffmanNode(BinaryTreeNode):
    """哈夫曼树节点类（继承自二叉树节点，增加权重属性）"""

    def __init__(self, data=None, weight=0):
        super().__init__(data)
        self.weight = weight  # 权重


class HuffmanTree(BinaryTree, Serializable):
    """哈夫曼树实现"""

    def __init__(self, weight_dict=None):
        super().__init__(None)
        self._size = 0
        if weight_dict:
            self.build_from_weights(weight_dict)

    def build_from_weights(self, weight_dict):
        """根据权重字典构建哈夫曼树"""
        nodes = [HuffmanNode(data, weight) for data, weight in weight_dict.items()]
        self._size = len(nodes)

        while len(nodes) > 1:
            nodes.sort(key=lambda x: x.weight)

            left = nodes.pop(0)
            right = nodes.pop(0)

            parent = HuffmanNode(weight=left.weight + right.weight)
            parent.left_child = left
            parent.right_child = right
            left.parent = parent
            right.parent = parent

            nodes.append(parent)
            self._size += 1

        self.root = nodes[0] if nodes else None

    def get_huffman_code(self):
        """生成哈夫曼编码（左0右1）"""
        if not self.root:
            return {}

        codes = {}
        self._generate_code(self.root, "", codes)
        return codes

    def _generate_code(self, node, current_code, codes):
        """递归生成哈夫曼编码辅助函数"""
        if node is None:
            return

        if node.data is not None:
            codes[node.data] = current_code
            return

        self._generate_code(node.left_child, current_code + "0", codes)
        self._generate_code(node.right_child, current_code + "1", codes)

    def display(self):
        """显示哈夫曼树及编码"""
        if not self.root:
            print("哈夫曼树为空")
            return

        codes = self.get_huffman_code()
        print("哈夫曼编码:")
        for data, code in codes.items():
            print(f"{data}: {code}")

    def to_dict(self):
        def node_to_dict(node):
            if not node:
                return None
            return {
                'data': node.data,
                'weight': node.weight,
                'left_child': node_to_dict(node.left_child),
                'right_child': node_to_dict(node.right_child)
            }

        return {
            'type': 'HuffmanTree',
            'root': node_to_dict(self.root),
            'size': self._size
        }

    @classmethod
    def from_dict(cls, data):
        def dict_to_node(node_dict):
            if not node_dict:
                return None
            # 必须使用 HuffmanNode 来实例化，以保持 weight 属性
            node = HuffmanNode(node_dict['data'], node_dict['weight'])
            node.left_child = dict_to_node(node_dict['left_child'])
            node.right_child = dict_to_node(node_dict['right_child'])
            return node

        obj = cls()
        obj.root = dict_to_node(data['root'])
        obj._size = data['size']
        return obj


# HuffmanTree的结构体节点 用于存储和实现哈夫曼树的动画
class HuffmanStructNode:
    def __init__(self, data=None, weight=0, index=-1):
        self.data = data  # 字符名称
        self.weight = weight  # 权重
        self.index = index  # 在数组中的自身下标
        self.parent = -1  # 父节点下标，-1表示无
        self.left = -1  # 左孩子下标，-1表示无
        self.right = -1  # 右孩子下标，-1表示无


class DataStructureManager:
    """数据结构管理器，负责保存和加载"""

    @staticmethod
    def save_structure(structure, filename):
        """保存数据结构到文件"""
        try:
            data = structure.to_dict()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            # 捕获异常时，打印更详细的错误信息
            print(f"保存失败: {e}")
            return False

    @staticmethod
    def load_structure(filename):
        """从文件加载数据结构"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            structure_type = data.get('type')
            if structure_type == 'SequenceList':
                return SequenceList.from_dict(data)
            elif structure_type == 'LinkedList':
                return LinkedList.from_dict(data)
            elif structure_type == 'Stack':
                return Stack.from_dict(data)
            elif structure_type == 'BinaryTree':
                return BinaryTree.from_dict(data)
            elif structure_type == 'BinarySearchTree':
                return BinarySearchTree.from_dict(data)
            elif structure_type == 'HuffmanTree':
                return HuffmanTree.from_dict(data)
            else:
                raise ValueError(f"不支持的数据结构类型: {structure_type}")

        except Exception as e:
            print(f"加载失败: {e}")
            return None

    @staticmethod
    def get_structure_type(filename):
        """获取文件中数据结构的类型"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('type')
        except Exception as e:
            print(f"获取结构类型失败: {e}")
            return None