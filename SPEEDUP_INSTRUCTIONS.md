# Report Agent Speedup Instructions

## Problem
Report Agent chat and report generation take ~10 minutes per request because:
1. Large context (graph + simulation data) sent to Qwen-plus via Alibaba Bailian
2. Zep Cloud read timeouts on large graphs
3. No fast-model fallback configured

## Solution: Add LLM_BOOST Configuration

### 1. Update `.env` (add these lines)
```env
# ===== LLM加速配置（可选，用于Report Agent对话和报告生成提速）=====
# 建议使用快速模型如 gpt-4o-mini、claude-3-haiku 等
# 配置后 Report Agent 对话和报告生成将自动使用此配置
LLM_BOOST_API_KEY=your_boost_api_key_here
LLM_BOOST_BASE_URL=https://api.openai.com/v1
LLM_BOOST_MODEL_NAME=gpt-4o-mini
```

### 2. Code Changes Required

#### File: `backend/app/utils/llm_client.py`
Add classmethod `create_boost()` to `LLMClient` class (after `__init__`):

```python
    @classmethod
    def create_boost(cls) -> Optional["LLMClient"]:
        """Create a boost LLMClient from LLM_BOOST_* env vars if configured."""
        import os
        boost_api_key = os.environ.get("LLM_BOOST_API_KEY", "").strip()
        if not boost_api_key:
            return None
        boost_base_url = os.environ.get("LLM_BOOST_BASE_URL", "").strip()
        boost_model = os.environ.get("LLM_BOOST_MODEL_NAME", "").strip()
        return cls(
            api_key=boost_api_key,
            base_url=boost_base_url or None,
            model=boost_model or None
        )
```

#### File: `backend/app/api/report.py`
1. Add import at top:
```python
from ..utils.llm_client import LLMClient
```

2. In `generate_report()` background task (around line 257), pass boost client:
```python
agent = ReportAgent(
    graph_id=graph_id,
    simulation_id=simulation_id,
    simulation_requirement=simulation_requirement,
    llm_client=LLMClient.create_boost()
)
```

3. In `chat_with_report_agent()` (around line 665), pass boost client:
```python
boost_llm = LLMClient.create_boost()
agent = ReportAgent(
    graph_id=graph_id,
    simulation_id=simulation_id,
    simulation_requirement=simulation_requirement,
    llm_client=boost_llm
)
```

### 3. Update `.env.example`
Replace the LLM_BOOST section with:
```
# ===== LLM加速配置（可选，用于Report Agent对话和报告生成提速）=====
# 建议使用快速模型如 gpt-4o-mini、claude-3-haiku 等
# 配置后 Report Agent 对话和报告生成将自动使用此配置
LLM_BOOST_API_KEY=your_boost_api_key_here
LLM_BOOST_BASE_URL=https://api.openai.com/v1
LLM_BOOST_MODEL_NAME=gpt-4o-mini
```

## How It Works
- If `LLM_BOOST_API_KEY` is set → ReportAgent uses fast model (gpt-4o-mini)
- If not set → Falls back to main LLM (Qwen-plus) — current behavior
- No breaking changes; fully backward compatible

## Expected Improvement
- Chat response: ~10 min → ~10-30 seconds
- Report generation: proportionally faster

## To Apply
1. Edit the 2 Python files as shown above
2. Add LLM_BOOST_* to your `.env` with valid credentials
3. Restart backend: `cd backend && uv run python run.py`