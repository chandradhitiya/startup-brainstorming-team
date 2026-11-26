# Chinese → English Translation Instructions for MiroFish

## Files to Translate (Priority Order)

### HIGH PRIORITY — Log Output (What You See in Terminal)
These produce the logs you're trying to read:

| File | Lines | Type |
|------|-------|------|
| `backend/scripts/run_twitter_simulation.py` | ~200 | Print statements, CLI help |
| `backend/scripts/run_parallel_simulation.py` | ~150 | Print statements, CLI help |
| `backend/scripts/run_reddit_simulation.py` | ~150 | Print statements, CLI help |
| `backend/scripts/action_logger.py` | ~80 | Docstrings, log messages |
| `backend/app/services/report_agent.py` | ~300 | ReACT logs, tool names, prompts |
| `backend/app/services/zep_graph_memory_updater.py` | ~100 | Batch processing logs |
| `backend/app/services/simulation_runner.py` | ~80 | Runner status messages |
| `backend/app/api/graph.py` | ~120 | Task progress, error messages |
| `backend/app/services/simulation_manager.py` | ~80 | Preparation stage logs |

### MEDIUM PRIORITY — API Error Messages & Docstrings
| File | Type |
|------|------|
| `backend/app/api/report.py` | Error responses, docstrings |
| `backend/app/api/simulation.py` | Error responses, docstrings |
| `backend/app/services/ontology_generator.py` | System prompt (LLM sees this), docstrings |
| `backend/app/services/oasis_profile_generator.py` | Prompts, log messages |
| `backend/app/services/simulation_config_generator.py` | Prompts, log messages |
| `backend/app/services/zep_entity_reader.py` | Log messages |
| `backend/app/services/zep_tools.py` | Tool descriptions, log messages |
| `backend/app/services/graph_builder.py` | Log messages |
| `backend/app/services/text_processor.py` | Docstrings |

### LOW PRIORITY — Config, Models, Utils, Tests
| File | Type |
|------|------|
| `backend/app/config.py` | Comments, defaults |
| `backend/app/models/project.py` | Docstrings |
| `backend/app/models/task.py` | Docstrings |
| `backend/app/utils/locale.py` | **Contains the translation function `t()`** |
| `backend/app/utils/logger.py` | Docstrings |
| `backend/app/utils/llm_client.py` | Error messages |
| `backend/tests/*.py` | Test data, assertions |

---

## Translation Strategy

### 1. Use the `t()` Function (Already Exists!)
The codebase has `backend/app/utils/locale.py` with a `t(key, **kwargs)` function for i18n. **Use it for all user-facing strings.**

Example:
```python
# Before
logger.info(f"模拟准备失败: {simulation_id}, error={str(e)}")

# After
logger.info(t('simulation.prepareFailed', simulation_id=simulation_id, error=str(e)))
```

### 2. Add Translation Keys to `backend/app/utils/locale.py`
The locale file has `TRANSLATIONS = {"en": {}, "zh": {}}`. Add English keys there.

### 3. For Print Statements in Scripts
Replace Chinese `print()` with English directly (scripts don't use `t()`).

---

## Key String Mappings (Start Here)

### Simulation Scripts (`run_twitter_simulation.py`, `run_parallel_simulation.py`)
| Chinese | English |
|---------|---------|
| "OASIS Twitter模拟" | "OASIS Twitter Simulation" |
| "配置文件:" | "Config file:" |
| "模拟ID:" | "Simulation ID:" |
| "等待命令模式:" | "Wait for commands mode:" |
| "模拟参数:" | "Simulation parameters:" |
| "总模拟时长:" | "Total simulation duration:" |
| "每轮时间:" | "Time per round:" |
| "总轮数:" | "Total rounds:" |
| "Agent数量:" | "Agent count:" |
| "初始化LLM模型..." | "Initializing LLM model..." |
| "加载Agent Profile..." | "Loading Agent Profiles..." |
| "创建OASIS环境..." | "Creating OASIS environment..." |
| "环境初始化完成" | "Environment initialized" |
| "开始模拟循环..." | "Starting simulation loop..." |
| "模拟循环完成!" | "Simulation loop completed!" |
| "总耗时:" | "Total elapsed:" |
| "进入等待命令模式" | "Entering wait-for-commands mode" |
| "支持的命令:" | "Supported commands:" |
| "收到中断信号" | "Received interrupt signal" |
| "任务被取消" | "Task cancelled" |
| "关闭环境..." | "Shutting down environment..." |
| "环境已关闭" | "Environment closed" |

### Report Agent (`report_agent.py`)
| Chinese | English |
|---------|---------|
| "报告生成任务已启动" | "Report generation task started" |
| "规划开始" | "Planning started" |
| "规划完成" | "Planning completed" |
| "章节生成开始" | "Section generation started" |
| "章节生成完成" | "Section generation completed" |
| "ReACT思考" | "ReACT thought" |
| "工具调用" | "Tool call" |
| "工具结果" | "Tool result" |
| "报告生成完成" | "Report generation completed" |
| "报告生成失败" | "Report generation failed" |
| "获取模拟上下文" | "Fetching simulation context" |
| "调用LLM生成大纲" | "Calling LLM to generate outline" |
| "正在生成章节" | "Generating section" |

### Graph Build (`graph.py`)
| Chinese | English |
|---------|---------|
| "图谱构建任务已启动" | "Graph build task started" |
| "初始化图谱服务" | "Initializing graph service" |
| "文本分块" | "Text chunking" |
| "创建Zep图谱" | "Creating Zep graph" |
| "设置本体" | "Setting ontology" |
| "添加文本块" | "Adding text chunks" |
| "等待Zep处理" | "Waiting for Zep processing" |
| "获取图谱数据" | "Fetching graph data" |
| "图谱构建完成" | "Graph build completed" |
| "构建失败" | "Build failed" |

### Simulation Manager (`simulation_manager.py`)
| Chinese | English |
|---------|---------|
| "连接Zep图谱" | "Connecting to Zep graph" |
| "读取节点数据" | "Reading node data" |
| "读取完成" | "Reading completed" |
| "开始生成人设" | "Starting profile generation" |
| "保存人设" | "Saving profiles" |
| "人设生成完成" | "Profile generation completed" |
| "分析模拟需求" | "Analyzing simulation requirements" |
| "调用LLM生成配置" | "Calling LLM to generate config" |
| "保存配置文件" | "Saving config files" |
| "配置生成完成" | "Config generation completed" |

### Zep Memory Updater (`zep_graph_memory_updater.py`)
| Chinese | English |
|---------|---------|
| "ZepGraphMemoryUpdater 已停止" | "ZepGraphMemoryUpdater stopped" |
| "批量发送到Zep失败" | "Batch send to Zep failed" |
| "清理模拟失败" | "Simulation cleanup failed" |
| "部分模拟未安全完成清理" | "Some simulations not cleaned up safely" |

---

## How to Apply

### Option 1: Batch Replace (Fastest)
Use a script to replace known strings across files.

### Option 2: Manual Per File (Safer)
Edit each file, replacing Chinese strings with English or `t()` calls.

### Option 3: Use Locale System (Best Long-term)
1. Add all keys to `backend/app/utils/locale.py` under `"en": {}`
2. Replace Chinese strings with `t('key')` calls
3. Set `LOCALE=en` in `.env` or code

---

## Quick Test
After translation, run:
```bash
cd backend && uv run python run.py
```
Then trigger a simulation or report — logs should be in English.

---

## Files NOT to Touch
- `backend/.venv/` — virtual environment (third-party code)
- `backend/.git/` — git history
- `README-ZH.md` — Chinese README (keep for Chinese users)
- Test data files with Chinese content (e.g., `validate_zep_cloud_integration.py` test cases) — these are test fixtures