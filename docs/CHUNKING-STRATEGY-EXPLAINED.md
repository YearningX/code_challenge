# Chunk分块策略详解

**文档**: `src/me_ecu_agent/document_processor.py`
**更新日期**: 2026-03-30

---

## 📋 当前Chunking策略概述

### 核心方法：**Header-based Chunking**（基于标题的分块）

**不是传统的字符数分块，而是基于文档结构的智能分块！**

---

## 🎯 策略详解

### 1. 基于Markdown标题分块

**分块规则**：
```
# H1标题 (一级标题)
↓
## H2标题 (二级标题) ← ← 分割点：每个H2/H3标题开始新的chunk
↓
内容段落
↓
### H3标题 (三级标题) ← ← 分割点：每个H3标题开始新的chunk
↓
更多内容
```

**示例**：

**原始文档**：
```markdown
# ME Engineering Specs: ECU-800 Series

## Overview
The ECU-800 Series is our next-generation platform...

## Key Features
- Over-the-Air (OTA) Update Capability
- Secure Boot and Hardware Security Module (HSM)

## ECU-850 Technical Specifications

| Feature | Specification |
|---------|---------------|
| Processor | Dual-core ARM Cortex-A53 @ 1.2 GHz |
| RAM | 2 GB LPDDR4 |
```

**分块结果**：
```
Chunk 1: "# ME Engineering Specs: ECU-800 Series"
Chunk 2: "## Overview\nThe ECU-800 Series is..."
Chunk 3: "## Key Features\n- Over-the-Air (OTA)..."
Chunk 4: "## ECU-850 Technical Specifications\n| Feature |..."
```

### 2. 表格转换为自然语言

**重要特性**：Markdown表格不会被保留为表格格式，而是转换为句子！

**转换规则**：

**原始表格**：
```markdown
| Feature | Specification |
|---------|---------------|
| Processor | Dual-core ARM Cortex-A53 @ 1.2 GHz |
| Memory (RAM) | 2 GB LPDDR4 |
| Storage | 16 GB eMMC |
```

**转换为句子**：
```text
In ECU-850 Technical Specifications, Processor is Dual-core ARM Cortex-A53 @ 1.2 GHz.
In ECU-850 Technical Specifications, Memory (RAM) is 2 GB LPDDR4.
In ECU-850 Technical Specifications, Storage is 16 GB eMMC.
```

**优势**：
- ✅ 更适合向量搜索
- ✅ 更容易被LLM理解
- ✅ 保留所有关键信息

### 3. 保留完整逻辑单元

**不做递归字符分割**：
- ❌ 不使用 `RecursiveCharacterTextSplitter`
- ❌ 不按固定字符数（如300、500字符）分割
- ✅ 每个section是一个完整的逻辑单元

**原因**：
- 保持表格完整性
- 保持上下文完整性
- 避免信息碎片化

---

## 🔧 实现细节

### 配置参数

**`src/me_ecu_agent/config.py`**:
```python
@dataclass
class ChunkingConfig:
    chunk_size: int = 300        # ⚠️ 当前不使用
    chunk_overlap: int = 100      # ⚠️ 当前不使用
    headers_to_split_on: List[Tuple[str, str]] = None
```

**注意**：`chunk_size` 和 `chunk_overlap` 参数配置了，但**当前实现中不使用**！

**实际使用**：
```python
# document_processor.py 第22行
def __init__(
    self,
    chunk_size: int = 500,        # ← 定义了但未使用
    chunk_overlap: int = 50,      # ← 定义了但未使用
    use_llm_for_tables: bool = True,
    headers_to_split_on: List[tuple] = None
):
```

### 分块流程

**步骤1: 加载文档** (第66-105行)
```python
def load_markdown_files(directory: Path) -> List[Document]:
    # 加载所有.md文件
    # 添加元数据：source文件名
```

**步骤2: 按标题分割** (第229-320行)
```python
def split_by_headers(documents: List[Document]) -> List[Document]:
    # 识别H1/H2/H3标题
    # 每个标题后开始新chunk
    # 保留标题层级关系
```

**步骤3: 表格转换** (第156-227行)
```python
def _table_to_sentences(text: str, section_title: str = "") -> str:
    # 检测markdown表格
    # 转换为自然语言句子
    # 格式："In {section_title}, {key} is {value}."
```

**步骤4: 按产品线分类** (第325-353行)
```python
def separate_by_product_line(chunks: List[Document]) -> Dict:
    # 根据文件名分类
    # ECU-700_Series_Manual.md → ECU-700
    # ECU-800_Series_Base.md → ECU-800
    # ECU-800_Series_Plus.md → ECU-800
```

---

## 📊 当前分块结果

### 实际Chunks数量

```bash
$ python -c "
from me_ecu_agent.document_processor import DocumentProcessor
processor = DocumentProcessor()
chunks = processor.process_documents('data')
for pl, chunk_list in chunks.items():
    print(f'{pl}: {len(chunk_list)} chunks')
"

ECU-700: 6 chunks
ECU-800: 10 chunks
Total: 16 chunks
```

### Chunk结构示例

**Chunk元数据**：
```python
{
    'source': 'ECU-800_Series_Base.md',
    'file_path': 'F:/.../data/ECU-800_Series_Base.md',
    'Header 1': 'ME Engineering Specs: ECU-800 Series',
    'Header 2': 'ECU-850 Technical Specifications',
    'section_title': 'ECU-850 Technical Specifications',
    'chunk_type': 'section',
    'header_1': 'ME Engineering Specs: ECU-800 Series',
    'header_2': 'ECU-850 Technical Specifications'
}
```

**Chunk内容**：
```text
**ECU-850 Technical Specifications**
| Feature | Specification |
|---------|---------------|
| Processor | Dual-core ARM Cortex-A53 @ 1.2 GHz |
| Memory (RAM) | 2 GB LPDDR4 |
| Storage | 16 GB eMMC |

转换为：
In ECU-850 Technical Specifications, Processor is Dual-core ARM Cortex-A53 @ 1.2 GHz.
In ECU-850 Technical Specifications, Memory (RAM) is 2 GB LPDDR4.
In ECU-850 Technical Specifications, Storage is 16 GB eMMC.
```

---

## 🎨 策略优缺点

### ✅ 优点

1. **保持语义完整性**
   - 每个chunk是完整的逻辑单元
   - 不会切断表格或列表
   - 保留上下文关系

2. **表格转换为句子**
   - 更适合向量搜索
   - LLM更容易理解
   - 保留所有数值和单位

3. **基于文档结构**
   - 利用markdown标题
   - 符合人类阅读习惯
   - 保留层级信息

### ⚠️ 缺点

1. **Chunks大小不均**
   - 有些section很短（2-3行）
   - 有些section很长（整个大表格）
   - 不利于token利用

2. **可能丢失跨section信息**
   - 相关信息在不同section
   - 检索时可能只找到部分
   - 需要LLM合成能力

3. **Chunks数量少**
   - 只有16个chunks（3个文档）
   - 检索覆盖面有限
   - 影响召回率

---

## 🔍 与传统方法的对比

### 传统方法：RecursiveCharacterTextSplitter

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(documents)
```

**特点**：
- 按固定字符数分割
- 保持overlap以保证连续性
- 可能在句子中间或表格中间分割

### 当前方法：Header-based Splitting

```python
class DocumentProcessor:
    def split_by_headers(self, documents):
        # 按H1/H2/H3标题分割
        # 每个section一个chunk
        # 表格转换为句子
```

**特点**：
- 按文档结构分割
- 不递归分割
- 保持语义完整性

---

## 📈 性能影响

### 检索质量

**优点**：
- ✅ 语义完整，相关性高
- ✅ 表格信息可搜索
- ✅ 层级信息丰富

**缺点**：
- ❌ Chunks少，覆盖面窄
- ❌ 可能错过跨section信息
- ❌ 大chunks可能影响精度

### 准确率影响

**当前准确率**: 93% (GPT-3.5 + GPT-4评估)

**影响分析**：
- ✅ Header-based分块保持了完整性 → 93%准确率
- ⚠️ 如果用字符分块，可能在表格中间切断 → 准确率可能更低

---

## 🚀 优化建议

### 短期优化（保持当前策略）

1. **增加Chunks数量**
   - 将大section进一步细分
   - 按段落或列表项分割
   - 目标：每个chunk 200-400字符

2. **改进表格处理**
   - 为每个表格行创建独立chunk
   - 添加表格标题到每个chunk
   - 提高表格信息的召回率

### 中期优化（混合策略）

1. **两级分块**
   ```python
   # 第一级：按标题分块（当前）
   header_chunks = split_by_headers(documents)

   # 第二级：大chunks进一步细分
   final_chunks = []
   for chunk in header_chunks:
       if len(chunk) > 500:
           sub_chunks = split_large_chunk(chunk, size=300)
           final_chunks.extend(sub_chunks)
       else:
           final_chunks.append(chunk)
   ```

2. **父子chunks**
   - 父chunk：整个section（用于上下文）
   - 子chunk：段落/表格行（用于检索）
   - 结合使用提升召回率和精度

### 长期优化（完全重构）

1. **语义分块**
   - 使用embedding计算段落相似度
   - 将相关段落组成chunk
   - 更智能的边界选择

2. **自适应分块**
   - 根据内容类型选择策略
   - 表格：每行独立chunk
   - 列表：每项独立chunk
   - 段落：合并相关段落

---

## 📝 配置示例

### 如果想切换到传统方法

```python
# 修改 document_processor.py
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        # 使用传统字符分块
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def process_documents(self, data_dir: str):
        documents = self.load_markdown_files(Path(data_dir))
        chunks = self.text_splitter.split_documents(documents)
        return self.separate_by_product_line(chunks)
```

### 如果想优化当前策略

```python
# 保持header-based，但添加大小限制
class DocumentProcessor:
    MAX_CHUNK_SIZE = 500  # 字符

    def split_by_headers(self, documents):
        # ... 现有代码 ...

        for chunk in header_chunks:
            if len(chunk.page_content) > self.MAX_CHUNK_SIZE:
                # 大chunk进一步细分
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
```

---

## 🎯 总结

### 当前策略

**Header-based Chunking + Table-to-Sentence Conversion**

- ✅ 保持语义完整性
- ✅ 适合技术文档
- ✅ 表格可搜索
- ⚠️ Chunks数量少（16个）
- ⚠️ 大小不均

### 适用场景

**适合**：
- 结构化技术文档
- Markdown格式
- 表格密集型文档

**不适合**：
- 非结构化文本
- 纯段落文本
- 需要大量小chunks的场景

### 当前状态

**工作良好**：93%准确率证明策略有效

**可优化**：增加chunks数量、改进大section处理

**不建议**：完全切换到字符分块（会降低质量）

---

*文档日期: 2026-03-30*
*相关文件: src/me_ecu_agent/document_processor.py*
*策略类型: Header-based Chunking*
