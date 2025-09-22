from abc import ABC, abstractmethod


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


class SequenceList(LinearList):
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


class Node:
    """链表节点类"""

    def __init__(self, data):
        self.data = data
        self.next = None

    def __str__(self):
        return str(self.data)


class LinkedList(LinearList):
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


class Stack(SequenceList):
    """栈类（继承自顺序表）"""

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


# 测试代码
if __name__ == "__main__":
    print("=== 测试顺序表 ===")
    seq_list = SequenceList()
    seq_list.insert(0, 10)
    seq_list.insert(1, 20)
    seq_list.insert(2, 30)
    seq_list.append(40)
    print("顺序表长度:", seq_list.length())
    print("位置1的元素:", seq_list.get(1))
    seq_list.display()

    print("\n=== 测试链表 ===")
    linked_list = LinkedList()
    linked_list.insert(0, 100)
    linked_list.insert(1, 200)
    linked_list.insert(2, 300)
    linked_list.append(400)
    print("链表长度:", linked_list.length())
    print("位置2的元素:", linked_list.get(2))
    linked_list.display()

    print("\n=== 测试栈 ===")
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    print("栈大小:", stack.length())
    print("栈顶元素:", stack.peek())
    print("弹出元素:", stack.pop())
    stack.display()

    print("\n=== 多态性测试 ===")
    lists = [seq_list, linked_list, stack]
    for lst in lists:
        print(f"{type(lst).__name__} 长度: {lst.length()}")
        print(f"{type(lst).__name__} 是否为空: {lst.is_empty()}")
        lst.display()
        print()