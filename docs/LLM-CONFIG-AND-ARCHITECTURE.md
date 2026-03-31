# LLM模型配置与LangGraph架构可视化

## 1. LLM模型配置位置

### 主要配置文件
**文件**: `src/me_ecu_agent/config.py`

### LLMConfig类定义
```python
@dataclass
class LLMConfig:
    """Configuration for Large Language Model parameters."""
    model_name: str = "gpt-4.1-mini"      # 当前使用的模型
    temperature: float = 0.0                 # 温度参数（0=确定性输出）
    max_tokens: int = 1000                   # 最大token数
```

### 配置使用位置
**文件**: `src/me_ecu_agent/graph.py`

**第29行** - Agent初始化时创建LLM实例：
```python
class ECUQueryAgent:
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        # 在这里创建LLM实例
        self.llm = ChatOpenAI(
            model=self.config.model_name,      # 使用配置的模型名称
            temperature=self.config.temperature # 使用配置的温度参数
        )
```

### LLM使用场景

#### 1. 查询分析（Query Analysis）
**位置**: `graph.py` 第85行
```python
def _analyze_query(self, state: AgentState) -> AgentState:
    chain = self.query_analysis_prompt | self.llm
    result = chain.invoke({"query": query})
    # 用于识别查询应该路由到哪个产品线
```

#### 2. 响应合成（Response Synthesis）
**位置**: `graph.py` 第134行
```python
def _synthesize_response(self, state: AgentState) -> AgentState:
    chain = self.response_synthesis_prompt | self.llm
    result = chain.invoke({"query": state["query"], "context": state["retrieved_context"]})
    # 用于基于检索到的上下文生成最终答案
```

---

## 2. 如何修改LLM模型

### 方式1: 修改默认配置（推荐）
**文件**: `src/me_ecu_agent/config.py`

```python
@dataclass
class LLMConfig:
    model_name: str = "gpt-4"  # 从gpt-4.1-mini改为gpt-4
    temperature: float = 0.0
    max_tokens: int = 1000
```

### 方式2: 运行时传入配置
```python
from me_ecu_agent.config import LLMConfig
from me_ecu_agent.graph import ECUQueryAgent

# 自定义配置
custom_config = LLMConfig(
    model_name="gpt-4",
    temperature=0.0,
    max_tokens=2000
)

# 使用自定义配置创建agent
agent = ECUQueryAgent(config=custom_config)
```

### 方式3: 环境变量配置
```python
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    model_name: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
```

然后在`.env`文件中：
```
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000
```

---

## 3. LangGraph架构可视化

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        ECU Query Agent                          │
│                      (LangGraph Workflow)                       │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                          用户查询                                 │
│                   "What is ECU-750 max temp?"                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      节点1: analyze_query                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LLM (gpt-4.1-mini) + Query Analysis Prompt           │  │
│  │  任务: 识别查询属于哪个产品线                            │  │
│  │  输入: user_query                                        │  │
│  │  输出: detected_product_line                             │  │
│  │       (ECU-700 | ECU-800 | both | unknown)              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ 条件路由 (Routing)   │
                    │ _route_to_retriever │
                    └──────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
    │ ECU-700      │   │ ECU-800      │   │ Both (比较查询)   │
    │ detected     │   │ detected     │   │ detected         │
    └──────────────┘   └──────────────┘   └──────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────────┐
│ 节点2a:              │ │ 节点2b:              │ │ 节点2c:          │
│ retrieve_ecu700     │ │ retrieve_ecu800     │ │ parallel_retrieval│
│ ┌─────────────────┐ │ │ ┌─────────────────┐ │ │ ┌──────────────┐ │
│ │Hybrid Retriever │ │ │ │Hybrid Retriever │ │ ││ ECU-700      │ │
│ │+ HyDE           │ │ │ │+ HyDE           │ │ ││ + ECU-800    │ │
│ │+ Query Expansion│ │ │ │+ Query Expansion│ │ ││ Parallel     │ │
│ └─────────────────┘ │ │ └─────────────────┘ │ │└──────────────┘ │
│ k=10 chunks        │ │ k=15 chunks        │ │ k=10 + k=15     │
└─────────────────────┘ └─────────────────────┘ └──────────────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      节点3: synthesize_response                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LLM (gpt-4.1-mini) + Response Synthesis Prompt       │  │
│  │  任务: 基于检索到的上下文生成最终答案                   │  │
│  │  输入: query + retrieved_context                        │  │
│  │  输出: final_response                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        最终响应                                   │
│         "The ECU-750 has a maximum operating temperature       │
│          of +85°C with a range of -40°C to +85°C."             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 详细数据流

#### State (Agent State)
```python
class AgentState(TypedDict):
    query: str                      # 用户查询
    detected_product_line: Literal  # 检测到的产品线
    retrieved_context: str          # 检索到的上下文
    response: str                   # 生成的响应
    messages: List[BaseMessage]     # 消息历史
```

#### 流程详解

**1. 初始状态**
```python
{
    "query": "What is ECU-750 max temp?",
    "detected_product_line": "unknown",
    "retrieved_context": "",
    "response": "",
    "messages": [HumanMessage("What is ECU-750 max temp?")]
}
```

**2. analyze_query节点**
```python
# 使用LLM分析查询
LLM Input:
    System: "You are a Bosch ECU product line classifier..."
    User: "What is ECU-750 max temp?"

LLM Output: "ECU-700"

# 更新状态
{
    "detected_product_line": "ECU-700",
    "messages": [HumanMessage(...), AIMessage("Detected: ECU-700")]
}
```

**3. 路由决策**
```python
def _route_to_retriever(state):
    if state["detected_product_line"] == "ECU-700":
        return "retrieve_ecu700"  # → 节点retrieve_ecu700
    elif state["detected_product_line"] == "ECU-800":
        return "retrieve_ecu800"  # → 节点retrieve_ecu800
    else:
        return "parallel_retrieval"  # → 节点parallel_retrieval
```

**4. retrieve_ecu700节点**
```python
# 使用混合检索器
docs = self.ecu700_retriever.invoke(query)
# k=10, 使用HyDE + Hybrid Search + Query Expansion

# 检索结果示例
retrieved_context = """
[ECU-700: ECU-700_Series_Manual.md]
| **Operating Temperature** | -40°C to **+85°C** |
"""

# 更新状态
{
    "retrieved_context": retrieved_context,
    "messages": [..., AIMessage("Retrieved 10 from ECU-700")]
}
```

**5. synthesize_response节点**
```python
# 使用LLM合成响应
LLM Input:
    System: "You are a Bosch ECU technical assistant..."
    Context: "[ECU-700] | **Operating Temperature** | -40°C to **+85°C** |"
    User: "What is ECU-750 max temp?"

LLM Output:
    "The maximum operating temperature for the ECU-750 is +85°C."

# 更新状态
{
    "response": "The maximum operating temperature for the ECU-750 is +85°C.",
    "messages": [..., AIMessage("The maximum...")]
}
```

**6. 最终状态**
```python
{
    "query": "What is ECU-750 max temp?",
    "detected_product_line": "ECU-700",
    "retrieved_context": "[ECU-700]...",
    "response": "The maximum operating temperature for the ECU-750 is +85°C.",
    "messages": [HumanMessage(...), AIMessage(...), ...]
}
```

### 3.3 图结构定义

**文件**: `src/me_ecu_agent/graph.py` 第148-165行

```python
def create_graph(self) -> StateGraph:
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("analyze_query", self._analyze_query)
    workflow.add_node("retrieve_ecu700", self._retrieve_ecu700)
    workflow.add_node("retrieve_ecu800", self._retrieve_ecu800)
    workflow.add_node("parallel_retrieval", self._parallel_retrieval)
    workflow.add_node("synthesize_response", self._synthesize_response)

    # 设置入口点
    workflow.set_entry_point("analyze_query")

    # 添加条件边（路由）
    workflow.add_conditional_edges(
        "analyze_query",
        self._route_to_retriever,
        {
            "retrieve_ecu700": "retrieve_ecu700",
            "retrieve_ecu800": "retrieve_ecu800",
            "parallel_retrieval": "parallel_retrieval"
        }
    )

    # 添加普通边
    workflow.add_edge("retrieve_ecu700", "synthesize_response")
    workflow.add_edge("retrieve_ecu800", "synthesize_response")
    workflow.add_edge("parallel_retrieval", "synthesize_response")
    workflow.add_edge("synthesize_response", END)

    return workflow.compile()
```

---

## 4. 关键优化技术

### 4.1 HyDE (Hypothetical Document Embeddings)
```python
# 生成假设性答案
hypothetical = generate_hypothetical_answer(query)
# 使用假设性答案进行检索
docs = retrieve_with_hypothetical(hypothetical)
```

### 4.2 Hybrid Retrieval
```python
# 结合语义搜索和关键词匹配
semantic_docs = semantic_search(query, k)
keyword_docs = keyword_search(query, k)
# 重排序和合并
final_docs = rerank_and_merge(semantic_docs, keyword_docs)
```

### 4.3 Query Expansion
```python
# 生成多个相关查询
expanded_queries = [
    "original query",
    "query alternative 1",
    "query alternative 2"
]
# 对每个查询进行检索
all_docs = [retrieve(q) for q in expanded_queries]
```

---

## 5. 快速参考

### 修改模型
```python
# 在 src/me_ecu_agent/config.py 第52行
model_name: str = "gpt-4"  # 改为您需要的模型
```

### 修改温度参数
```python
# 在 src/me_ecu_agent/config.py 第53行
temperature: float = 0.0  # 0=确定性，0.7=创造性
```

### 修改检索数量
```python
# 在 src/me_ecu_agent/config.py 第41-42行
ecu700_k: int = 10  # ECU-700检索chunks数
ecu800_k: int = 15  # ECU-800检索chunks数
```

### 查看当前配置
```python
from me_ecu_agent.config import AgentConfig

config = AgentConfig()
print(f"Model: {config.llm.model_name}")
print(f"Temperature: {config.llm.temperature}")
print(f"ECU-700 k: {config.retrieval.ecu700_k}")
print(f"ECU-800 k: {config.retrieval.ecu800_k}")
```

---

*文档创建日期: 2026-03-30*
*项目: Bosch ECU Code Challenge*
