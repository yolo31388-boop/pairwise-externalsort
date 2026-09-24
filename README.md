# Pair-wise GSB 基线：外部 k 路归并排序（真实磁盘文件版）

题目（feature 迭代）：实现真实磁盘文件版的外部 k 路归并排序：序列化、字节预算分块、文件生命周期管理。

- 骨架：`externalsort.py`（ExternalSorter 方法均 `raise NotImplementedError`）
- 验收：`python -m pytest tests/test_externalsort.py -q` 全绿
- 约束：只 import 标准库；必须真实落盘（禁止内存 list 冒充磁盘块）；元素类型 int/str
