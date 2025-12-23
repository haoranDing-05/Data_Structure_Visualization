# Data_Structure_Visualization
Design for the class Data Structure
Beijing university of technology -- bjut

## DSL 脚本语法说明 (DSL Script Syntax)

本项目支持通过自定义脚本语言（DSL）来批量执行数据结构操作。你可以在可视化界面的脚本区域输入指令，点击运行即可。

### 基础规则
* **格式：** `COMMAND: arg1, arg2, ...`
* **分隔符：** 指令与参数之间用冒号 (`:`) 分隔，参数之间用逗号 (`,`) 分隔。
* **注释：** 以 `#` 开头的行将被忽略。
* **大小写：** 指令不区分大小写 (例如 `insert` 和 `INSERT` 等效)。

### 支持的指令详解

#### 1. BUILD (批量构建)
初始化数据结构并填入数据。执行此命令通常会先清空当前结构。

* **线性结构 (Stack, SequenceList, LinkedList):**
    * 依次插入提供的值。
    * **语法:** `BUILD: value1, value2, value3`
    * **示例:** `BUILD: 10, 20, 30, 40`

* **二叉搜索树 (BinarySearchTree) / AVL树 (AVLTree):**
    * 按照顺序依次插入数值。对于 AVL 树，插入过程中会自动进行平衡旋转。
    * **语法:** `BUILD: value1, value2, ...`
    * **示例:** `BUILD: 50, 30, 70, 20, 40`

* **普通二叉树 (BinaryTree):**
    * 第一个参数作为根节点，后续参数按层序遍历（完全二叉树顺序）插入。
    * **语法:** `BUILD: root_val, child_val1, child_val2...`
    * **示例:** `BUILD: A, B, C, D, E`

* **哈夫曼树 (HuffmanTree):**
    * 根据字符和对应的权重构建。
    * **语法:** `BUILD: Key:Weight, Key:Weight, ...`
    * **示例:** `BUILD: A:10, B:15, C:20, D:5`

#### 2. INSERT (插入元素)
向结构中插入单个元素。

* **栈 (Stack):**
    * 将元素压入栈顶。
    * **语法:** `INSERT: value`
    * **示例:** `INSERT: 99`

* **顺序表/链表 (SequenceList / LinkedList):**
    * 插入一个值。可选指定索引（如果省略索引，默认插到末尾）。
    * **注意:** 参数顺序为先值后索引。
    * **语法:** `INSERT: value` 或 `INSERT: value, index`
    * **示例:** `INSERT: 99, 2` (在索引 2 的位置插入 99)

* **二叉搜索树 (BST) / AVL树 (AVLTree):**
    * 按照 BST 规则插入值。AVL树插入后会自动平衡。
    * **语法:** `INSERT: value`
    * **示例:** `INSERT: 65`

* **普通二叉树 (BinaryTree):**
    * 将节点插入到指定父节点的左侧或右侧。
    * **语法:** `INSERT: parent_index, value, Direction(L/R)`
    * **示例:** `INSERT: 0, X, L` (将 'X' 插入到索引为 0 的节点左侧)

#### 3. DELETE / REMOVE (删除元素)
从结构中移除元素。

* **栈 (Stack):**
    * 弹出栈顶元素 (无需参数)。
    * **语法:** `DELETE`

* **顺序表/链表 (SequenceList / LinkedList):**
    * 删除指定**索引**处的元素。
    * **语法:** `DELETE: index`
    * **示例:** `DELETE: 0` (删除头部元素)

* **二叉搜索树 (BST) / AVL树 (AVLTree):**
    * 查找并删除包含指定**数值**的节点。AVL树删除后会自动平衡。
    * **语法:** `DELETE: value`
    * **示例:** `DELETE: 30`

* **普通二叉树 (BinaryTree):**
    * 删除指定**节点索引**及其子树。
    * **语法:** `DELETE: node_index`
    * **示例:** `DELETE: 2` (删除索引 2 的节点及其子节点)

### 脚本示例

**AVL树操作:**
```text
# 批量构建 (将会自动触发旋转)
BUILD: 10, 20, 30, 40, 50
# 插入新元素
INSERT: 25
# 删除元素
DELETE: 40