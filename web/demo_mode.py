"""
Demo Mode API Server - Without MLflow Model Dependency

This version simulates responses for demonstration purposes when the actual
MLflow model is not available.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Server startup time
start_time = time.time()


class QueryRequest(BaseModel):
    """Query request model."""
    query: str = Field(..., description="User query about ECU specifications", min_length=1)
    timeout: int = Field(default=30, description="Query timeout in seconds", ge=1, le=120)


class QueryResponse(BaseModel):
    """Query response model."""
    response: str = Field(..., description="Agent response")
    latency: float = Field(..., description="Response latency in seconds")
    detected_product_lines: list[str] = Field(..., description="Detected ECU product lines")
    timestamp: float = Field(..., description="Unix timestamp")


class MetricsResponse(BaseModel):
    """System metrics response."""
    accuracy: float = Field(..., description="Test accuracy (0-1)")
    avg_latency: float = Field(..., description="Average response time in seconds")
    code_quality: float = Field(..., description="Pylint code quality score (0-10)")
    tier_grade: str = Field(..., description="Overall tier grade")
    tier_score: float = Field(..., description="Overall score (0-100)")
    total_queries: int = Field(..., description="Total test queries")
    passed_queries: int = Field(..., description="Passed test queries")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether MLflow model is loaded")
    uptime: float = Field(..., description="Server uptime in seconds")
    demo_mode: bool = Field(..., description="Running in demo mode")


# Initialize FastAPI app
app = FastAPI(
    title="ME ECU Engineering Assistant API (Demo Mode)",
    description="Demo API for ECU technical documentation queries",
    version="1.0.0-demo",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Demo responses - More accurate and specific
DEMO_RESPONSES = {
    "ecu-750": """**ECU-750** is the primary model in the **ECU-700 Series**.

## Technical Specifications:

**Processor:**
- 300 MHz ARM Cortex-R5
- FPU (Floating Point Unit)

**Memory:**
- 1 MB Flash memory
- 192 KB RAM

**Operating Conditions:**
- **Maximum operating temperature: +85°C**
- Storage temperature: -55°C to +150°C
- Supply voltage: 4.5V to 36V

**Applications:**
- Engine control systems
- Powertrain applications
- Industrial automation""",

    "ecu-850": """**ECU-850** is the baseline model in the **ECU-800 Series** (next-generation platform).

## Technical Specifications:

**Processor:**
- Dual-core ARM Cortex-A53 @ 1.2 GHz
- 64-bit architecture

**Memory:**
- 2 GB LPDDR4 RAM
- 16 GB eMMC flash storage

**Operating Conditions:**
- **Maximum operating temperature: +105°C**
- Ambient temperature range: -40°C to +85°C
- Supply voltage: 9V to 36V

**Key Features:**
- CAN FD interfaces
- Ethernet connectivity
- Advanced powertrain control""",

    "ecu-850b": """**ECU-850b** is the enhanced model in the **ECU-800 Series** with AI capabilities.

## Key Specifications:

**Processor:**
- Quad-core ARM Cortex-A53 @ 1.5 GHz (enhanced from dual-core @ 1.2 GHz)
- **Neural Processing Unit (NPU) included**

**Memory:**
- 4 GB LPDDR4 RAM (upgraded from 2 GB)
- 32 GB eMMC flash storage (upgraded from 16 GB)

**Operating Conditions:**
- **Maximum operating temperature: +105°C**
- Higher power consumption (12W vs 8W) due to NPU

**AI Capabilities:**
- Hardware NPU acceleration
- Support for autonomous driving features
- Advanced machine learning inference""",

    "compare-850-850b": """## Comparison: **ECU-850 vs ECU-850b**

| Feature | ECU-850 | ECU-850b |
|---------|---------|----------|
| **Processor** | Dual-core ARM Cortex-A53 @ 1.2 GHz | Quad-core ARM Cortex-A53 @ 1.5 GHz |
| **RAM** | 2 GB LPDDR4 | 4 GB LPDDR4 |
| **Storage** | 16 GB eMMC | 32 GB eMMC |
| **NPU** | Not included | **Included** (Neural Processing Unit) |
| **Max Operating Temp** | +105°C | +105°C |
| **Power Consumption** | 8W typical | 12W typical |
| **AI Acceleration** | Software-based | Hardware NPU acceleration |
| **Applications** | Standard powertrain | AI-enabled autonomous features |

**Key Differences:**
- **ECU-850**: Baseline next-generation ECU
- **ECU-850b**: Enhanced version with NPU for AI/ML workloads""",

    "overview": """## ME ECU Product Lines Overview

We currently support **two main ECU product lines**:

### **ECU-700 Series** (Legacy Platform)
- **Models**: ECU-750
- **Processor**: ARM Cortex-R5 @ 300 MHz
- **Max Operating Temp**: +85°C
- **Target**: Traditional powertrain applications
- **Features**: Basic I/O, CAN/LAN connectivity
- **Status**: Mature, production-proven

### **ECU-800 Series** (Next-Generation)
- **Models**: ECU-850, ECU-850b
- **Processor**: ARM Cortex-A53 (dual/quad-core)
- **Max Operating Temp**: +105°C
- **Target**: Advanced powertrain & autonomous driving
- **Features**: CAN FD, Ethernet, NPU (850b only)
- **Status**: Latest generation, AI-capable"""
}


def get_demo_response(query: str) -> tuple[str, list[str]]:
    """Get demo response based on query keywords - more intelligent matching."""
    query_lower = query.lower()

    # Temperature questions
    if "temperature" in query_lower:
        if "ecu-750" in query_lower:
            return "The **maximum operating temperature for the ECU-750 is +85°C**.\n\nThis temperature rating makes it suitable for automotive under-hood applications where high ambient temperatures are common.", ["ECU-700"]
        elif "ecu-850" in query_lower and "850b" not in query_lower:
            return "The **maximum operating temperature for the ECU-850 is +105°C**.\n\nThe ECU-800 series is designed for more demanding applications with higher thermal requirements.", ["ECU-800"]
        elif "ecu-850b" in query_lower:
            return "The **maximum operating temperature for the ECU-850b is +105°C**.\n\nDespite having the additional NPU which generates more heat, the enhanced model maintains the same thermal performance as the base ECU-850.", ["ECU-800"]
        elif "ecu-800" in query_lower:
            return "The **ECU-800 series** has a maximum operating temperature of **+105°C** for both ECU-850 and ECU-850b models.\n\nThis is higher than the ECU-700 series (+85°C), making it suitable for more demanding applications.", ["ECU-800"]

    # Memory questions
    if "memory" in query_lower or "ram" in query_lower:
        if "ecu-750" in query_lower:
            return "**ECU-750 Memory Specifications:**\n- 1 MB Flash memory\n- 192 KB RAM\n\nThe memory configuration is optimized for embedded control applications.", ["ECU-700"]
        elif "ecu-850" in query_lower and "850b" not in query_lower:
            return "**ECU-850 Memory Specifications:**\n- 2 GB LPDDR4 RAM\n- 16 GB eMMC flash storage\n\nThe significantly higher memory capacity supports advanced algorithms and data logging.", ["ECU-800"]
        elif "ecu-850b" in query_lower:
            return "**ECU-850b Memory Specifications:**\n- 4 GB LPDDR4 RAM (doubled from ECU-850)\n- 32 GB eMMC flash storage (doubled from ECU-850)\n\nThe enhanced memory is necessary for AI/ML workloads and NPU operations.", ["ECU-800"]

    # Processor questions
    if "processor" in query_lower or "cpu" in query_lower:
        if "ecu-750" in query_lower:
            return "**ECU-750 Processor:**\n- 300 MHz ARM Cortex-R5\n- Includes FPU (Floating Point Unit)\n\nThis is a proven automotive-grade processor optimized for real-time control.", ["ECU-700"]
        elif "ecu-850" in query_lower and "850b" not in query_lower:
            return "**ECU-850 Processor:**\n- Dual-core ARM Cortex-A53 @ 1.2 GHz\n- 64-bit architecture\n\nThe modern ARM Cortex-A53 provides significantly more processing power than the ECU-700 series.", ["ECU-800"]
        elif "ecu-850b" in query_lower:
            return "**ECU-850b Processor:**\n- Quad-core ARM Cortex-A53 @ 1.5 GHz\n- **Includes Neural Processing Unit (NPU)**\n\nThe enhanced processor with NPU enables AI and machine learning inference for autonomous driving features.", ["ECU-800"]

    # Interface questions
    if "interface" in query_lower or "can" in query_lower or "ethernet" in query_lower:
        if "ecu-750" in query_lower:
            return "**ECU-750 Interfaces:**\n- 2x CAN interfaces\n- 2x LIN interfaces\n- 1x Ethernet (100 Mbps)\n- 5x ADC channels\n\nStandard automotive communication interfaces for powertrain applications.", ["ECU-700"]
        elif "ecu-850" in query_lower and "850b" not in query_lower:
            return "**ECU-850 Interfaces:**\n- 2x CAN FD interfaces (next-gen CAN)\n- 2x Ethernet (1 Gbps)\n- 6x ADC channels\n- 2x USB 3.0 interfaces\n\nAdvanced interfaces supporting high-speed data transfer and external connectivity.", ["ECU-800"]

    # Specific model queries
    if "ecu-750" in query_lower or "ecu-700" in query_lower:
        return DEMO_RESPONSES["ecu-750"], ["ECU-700"]
    elif "ecu-850" in query_lower and "ecu-850b" in query_lower:
        return DEMO_RESPONSES["compare-850-850b"], ["ECU-800"]
    elif "ecu-850b" in query_lower:
        return DEMO_RESPONSES["ecu-850b"], ["ECU-800"]
    elif "ecu-850" in query_lower:
        return DEMO_RESPONSES["ecu-850"], ["ECU-800"]
    elif "ecu-800" in query_lower or "overview" in query_lower or "product" in query_lower:
        return DEMO_RESPONSES["overview"], ["ECU-700", "ECU-800"]
    else:
        return f"Demo response for query: \"{query}\"\n\nNote: This is a simulated response. In production, the MLflow model would provide accurate technical documentation from the knowledge base.", ["Unknown"]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface."""
    try:
        index_path = Path(__file__).parent / "index.html"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return HTMLResponse(content="<h1>Error loading page</h1>", status_code=500)


@app.get("/api")
async def api_info():
    """API information endpoint."""
    uptime = time.time() - start_time
    return {
        "message": "ME ECU Engineering Assistant API (Demo Mode)",
        "version": "1.0.0-demo",
        "status": "running",
        "demo_mode": True,
        "uptime_seconds": uptime,
        "endpoints": {
            "query": "/api/query",
            "metrics": "/api/metrics",
            "health": "/api/health",
            "docs": "/api/docs"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - start_time
    return HealthResponse(
        status="healthy",
        model_loaded=False,
        demo_mode=True,
        uptime=uptime
    )


@app.post("/api/query", response_model=QueryResponse)
async def query_ecu(request: QueryRequest):
    """
    Process ECU query using demo mode.

    Args:
        request: Query request with user question

    Returns:
        Query response with demo answer and metadata
    """
    logger.info(f"Received query: {request.query[:100]}...")

    # Simulate processing time
    query_start = time.time()
    time.sleep(2.5)  # Simulate 2.5s processing time
    latency = time.time() - query_start

    # Get demo response
    response_text, detected_lines = get_demo_response(request.query)

    logger.info(f"Query completed in {latency:.2f}s")

    return QueryResponse(
        response=response_text,
        latency=latency,
        detected_product_lines=detected_lines,
        timestamp=time.time()
    )


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system performance metrics."""
    return MetricsResponse(
        accuracy=0.85,
        avg_latency=3.80,
        code_quality=8.61,
        tier_grade="A",
        tier_score=90.0,
        total_queries=10,
        passed_queries=8
    )


@app.get("/api/demo-queries")
async def get_demo_queries():
    """Get predefined demo queries for presentation."""
    return {
        "demo_mode": True,
        "message": "Using demo responses - MLflow model not loaded",
        "queries": [
            {
                "id": 1,
                "name": "ECU-700 Basic Query",
                "query": "What is ECU-750?",
                "description": "Tests ECU-700 series knowledge and basic specifications",
                "category": "ECU-700"
            },
            {
                "id": 2,
                "name": "ECU-800 Basic Query",
                "query": "What is ECU-850?",
                "description": "Tests ECU-800 series knowledge and detailed specifications",
                "category": "ECU-800"
            },
            {
                "id": 3,
                "name": "Comparison Query",
                "query": "Compare ECU-850 and ECU-850b",
                "description": "Tests cross-product-line comparison capability",
                "category": "Comparison"
            },
            {
                "id": 4,
                "name": "Overview Query",
                "query": "What ECU product lines are available?",
                "description": "Tests general product line knowledge",
                "category": "Overview"
            }
        ]
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )


def main():
    """Run the API server."""
    logger.info("Starting ME ECU Assistant API Server (DEMO MODE)...")
    logger.info("Demo mode: Using simulated responses")
    logger.info("Server: 0.0.0.0:8000")
    logger.info("API Documentation: http://localhost:8000/api/docs")

    uvicorn.run(
        "demo_mode:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
