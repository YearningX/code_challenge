# LangGraph Agent 架构可视化

## 1. Mermaid流程图

```mermaid
graph TD
    Start([用户查询]) --> Analyze[节点1: analyze_query]
    Analyze -->|LLM分析| Route{路由决策}

    Route -->|ECU-700| R700[节点2a: retrieve_ecu700]
    Route -->|ECU-800| R800[节点2b: retrieve_ecu800]
    Route -->|Both| RBoth[节点2c: parallel_retrieval]

    R700 -->|HyDE + Hybrid Search| R700_docs[检索10个chunks]
    R800 -->|HyDE + Hybrid Search| R800_docs[检索15个chunks]
    RBoth -->|并行检索| RBoth_docs[检索10+15个chunks]

    R700_docs --> Synthesize
    R800_docs --> Synthesize
    RBoth_docs --> Synthesize

    Synthesize[节点3: synthesize_response] -->|LLM合成| End([最终响应])

    style Analyze fill:#e1f5ff
    style R700 fill:#fff4e1
    style R800 fill:#fff4e1
    style RBoth fill:#fff4e1
    style Synthesize fill:#e1ffe1
```

## 2. 状态转换图

```mermaid
stateDiagram-v2
    [*] --> Initial: 用户提交查询
    Initial --> Analyzing: analyze_query节点
    Analyzing --> Routing: LLM分析完成

    Routing --> Retrieving_700: 检测到ECU-700
    Routing --> Retrieving_800: 检测到ECU-800
    Routing --> Retrieving_Both: 检测到Both

    Retrieving_700 --> Synthesizing: 检索完成(k=10)
    Retrieving_800 --> Synthesizing: 检索完成(k=15)
    Retrieving_Both --> Synthesizing: 检索完成(k=10+15)

    Synthesizing --> [*]: 响应生成完成

    note right of Analyzing
        使用LLM (gpt-4.1-mini)
        识别查询类型
    end note

    note right of Synthesizing
        使用LLM (gpt-4.1-mini)
        基于上下文合成答案
    end note
```

## 3. 数据流图

```mermaid
flowchart LR
    subgraph Input["输入层"]
        Query["用户查询"]
    end

    subgraph Analysis["分析层"]
        LLM1["LLM<br/>gpt-4.1-mini"]
        Class["产品线分类<br/>ECU-700/800/both"]
    end

    subgraph Retrieval["检索层"]
        HyDE["HyDE<br/>假设文档生成"]
        Hybrid["混合检索<br/>语义+关键词"]
        Expand["查询扩展<br/>多查询"]
        Vector["向量存储<br/>FAISS"]
    end

    subgraph Synthesis["合成层"]
        Context["检索上下文"]
        LLM2["LLM<br/>gpt-4.1-mini"]
        Prompt["合成提示词"]
    end

    subgraph Output["输出层"]
        Response["最终响应"]
    end

    Query --> LLM1
    LLM1 --> Class
    Class --> HyDE
    HyDE --> Expand
    Expand --> Hybrid
    Hybrid --> Vector
    Vector --> Context
    Context --> Prompt
    Prompt --> LLM2
    LLM2 --> Response

    style LLM1 fill:#ffe1e1
    style LLM2 fill:#ffe1e1
    style Vector fill:#e1f5ff
```

## 4. 系统架构层次图

```mermaid
graph TB
    subgraph ["应用层"]
        Agent["ECUQueryAgent<br/>LangGraph"]
    end

    subgraph ["编排层"]
        Graph["StateGraph<br/>工作流编排"]
        Nodes["5个节点<br/>analyze, retrieve, synthesize"]
        Routing["条件路由<br/>动态决策"]
    end

    subgraph ["LLM层"]
        GPT35["gpt-4.1-mini<br/>查询分析"]
        GPT35_2["gpt-4.1-mini<br/>响应合成"]
        Config["LLMConfig<br/>model_name: gpt-4.1-mini<br/>temperature: 0.0"]
    end

    subgraph ["检索增强层"]
        HyDE["HyDE<br/>假设文档"]
        Hybrid["Hybrid Search<br/>混合检索"]
        Expand["Query Expansion<br/>查询扩展"]
        Rerank["重排序"]
    end

    subgraph ["存储层"]
        FAISS1["FAISS Store<br/>ECU-700<br/>k=10"]
        FAISS2["FAISS Store<br/>ECU-800<br/>k=15"]
        Docs["文档集合<br/>3个MD文件"]
    end

    Agent --> Graph
    Graph --> Nodes
    Nodes --> Routing

    Nodes --> GPT35
    Nodes --> GPT35_2
    GPT35 --> Config
    GPT35_2 --> Config

    Nodes --> HyDE
    HyDE --> Hybrid
    Hybrid --> Expand
    Expand --> Rerank

    Rerank --> FAISS1
    Rerank --> FAISS2
    FAISS1 --> Docs
    FAISS2 --> Docs

    style Agent fill:#e1f5ff
    style GPT35 fill:#ffe1e1
    style GPT35_2 fill:#ffe1e1
    style FAISS1 fill:#e1ffe1
    style FAISS2 fill:#e1ffe1
```

## 5. 节点详细流程

### 5.1 analyze_query节点

```mermaid
flowchart TD
    Start([用户查询输入]) --> Input[接收查询]
    Input --> Expand[查询扩展<br/>Query Expansion]
    Expand --> LLM[LLM调用<br/>gpt-4.1-mini]
    LLM --> Prompt1[查询分析提示词]
    Prompt1 --> Classify{产品线分类}
    Classify -->|包含ECU-750| P700["ECU-700"]
    Classify -->|包含ECU-850/850b| P800["ECU-800"]
    Classify -->|比较/all/both| PBoth["Both"]
    Classify -->|无法识别| PUnknown["Unknown"]
    P700 --> Update1[更新State]
    P800 --> Update1
    PBoth --> Update1
    PUnknown --> Update1
    Update1 --> End([返回更新后的State])

    style LLM fill:#ffe1e1
```

### 5.2 retrieve节点（以ECU-800为例）

```mermaid
flowchart TD
    Start([接收State]) --> Check{检查<br/>retriever}
    Check -->|未注册| Error["返回错误"]
    Check -->|已注册| HyDE[HyDE转换<br/>生成假设文档]
    HyDE --> Expand[查询扩展<br/>生成多个查询]
    Expand --> Retrieve[向量检索<br/>FAISS k=15]
    Retrieve --> Hybrid[混合检索<br/>+关键词匹配]
    Hybrid --> Rerank[重排序<br/>相关性评分]
    Rerank --> Format[格式化上下文<br/>添加元数据]
    Format --> Update[更新State<br/>retrieved_context]
    Update --> End([返回更新后的State])

    style HyDE fill:#ffe1ff
    style Retrieve fill:#e1f5ff
    style Rerank fill:#fff4e1
```

### 5.3 synthesize_response节点

```mermaid
flowchart TD
    Start([接收State]) --> Get[获取查询和上下文]
    Get --> LLM[LLM调用<br/>gpt-4.1-mini]
    LLM --> Prompt[合成提示词<br/>+ 相关性指令]
    Prompt --> Generate[生成响应]
    Generate --> Validate{验证响应}
    Validate -->|通过| Update[更新State<br/>response]
    Validate -->|失败| Retry[重试<br/>最多3次]
    Retry --> LLM
    Update --> Log[记录消息<br/>messages列表]
    Log --> End([返回最终State])

    style LLM fill:#ffe1e1
    style Prompt fill:#fff4e1
```

## 6. 完整工作流程示例

### 场景: 用户询问ECU-750的最大温度

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as Agent
    participant Q as analyze_query
    participant L1 as LLM (gpt-3.5)
    participant R as retrieve_ecu700
    participant V as FAISS Store
    participant S as synthesize_response
    participant L2 as LLM (gpt-3.5)

    U->>A: "What is ECU-750 max temp?"
    A->>Q: 分析查询
    Q->>L1: 分类请求
    L1-->>Q: "ECU-700"
    Q->>A: 路由到retrieve_ecu700

    A->>R: 检索ECU-700文档
    R->>V: HyDE + 混合检索 (k=10)
    V-->>R: 10个chunks
    R->>R: 格式化上下文
    R->>A: 返回上下文

    A->>S: 合成响应
    S->>L2: 生成答案
    L2-->>S: "The ECU-750 max temp is +85°C"
    S->>A: 最终响应
    A->>U: 返回答案

    Note over L1: 温度: 0.0<br/>模型: gpt-4.1-mini
    Note over L2: 温度: 0.0<br/>模型: gpt-4.1-mini
```

## 7. 配置文件结构

```mermaid
graph LR
    subgraph AgentConfig["AgentConfig"]
        Chunking["ChunkingConfig<br/>chunk_size: 300<br/>chunk_overlap: 100"]
        Retrieval["RetrievalConfig<br/>ecu700_k: 10<br/>ecu800_k: 15"]
        LLM["LLMConfig<br/>model_name: gpt-4.1-mini<br/>temperature: 0.0<br/>max_tokens: 1000"]
        Perf["PerformanceConfig<br/>timeout: 10s"]
        MLflow["MLflowConfig<br/>experiment: me-ecu-agent"]
    end

    subgraph Usage["使用位置"]
        Agent["ECUQueryAgent.__init__"]
        Graph["create_graph"]
    end

    Chunking --> Agent
    Retrieval --> Agent
    LLM --> Agent
    Perf --> Agent
    MLflow --> Agent

    Agent --> Graph

    style LLM fill:#ffe1e1
```

---

## 使用说明

### 查看图形
1. 复制上述Mermaid代码
2. 访问 https://mermaid.live
3. 粘贴代码查看可视化图形

### 修改LLM模型
编辑 `src/me_ecu_agent/config.py` 第52行：
```python
model_name: str = "gpt-4"  # 改为gpt-4或其他模型
```

### 调整检索参数
编辑 `src/me_ecu_agent/config.py` 第41-42行：
```python
ecu700_k: int = 10  # 调整ECU-700检索数量
ecu800_k: int = 15  # 调整ECU-800检索数量
```

---

*创建日期: 2026-03-30*
*项目: Bosch ECU Code Challenge*
