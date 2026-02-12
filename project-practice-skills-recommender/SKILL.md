---
name: project-practice-skills-recommender
description: "Use when the user asks to generate or update AGENTS.md (project rules) and wants Codex to enforce skill-based best practices based on the project's main tech stack."
---

# Project Practice Skills Recommender

## 目标

在你需要“生成/更新项目 `AGENTS.md`”时，按**主框架/主语言**（例如 Vue / React / .NET / Rust / Python / Node）：

1) 从聊天或代码库识别技术栈；  
2) 列出建议遵循的最佳实践 skills（先不安装）；  
3) 让用户确认后再安装缺失 skills（必要时先安装并使用 `find-skills`）；  
4) 将最终的 skills 清单作为**项目规则**（不是推荐）**去重写入** `AGENTS.md`，且不覆盖用户已有规则。

## 强制工作流（不要跳步）

### Step 0：确认是否真的要动 `AGENTS.md`

仅在用户明确提出如下诉求时继续：

- “生成/更新 `AGENTS.md`”
- “初始化项目规范/约束”
- “让 Codex 在这个项目遵循最佳实践”

否则不要主动写 `AGENTS.md`。

### Step 1：识别项目主技术栈（优先级：聊天 > 代码）

1) 先从聊天记录提取主框架/主语言关键词（只要主框架级别即可，不要细到每个库）。  
2) 若聊天里没提：扫描代码库做推断，并给出**证据文件**：

- Vue/Node：`package.json`（`dependencies` / `devDependencies`）、`vite.config.*`、`nuxt.config.*`
- .NET：`*.sln` / `*.csproj`
- Rust：`Cargo.toml`
- Python：`pyproject.toml` / `requirements.txt`
- Go：`go.mod`

3) 把推断结果用一句话问用户确认：  
“我判断这个项目是 `<stack>`（证据：`<file>`），对吗？”

**硬规则：**如果用户明确回答“不是”，立刻停止，不创建/不更新 `AGENTS.md`。

### Step 2：生成“候选 skills 清单”（先列出，别安装）

根据确认后的主技术栈，生成候选 skills 列表，至少包含：

- `skill_name`（例如 `vue-best-practices`）
- 是否已安装（检查 `~/.codex/skills/<skill_name>` 是否存在）
- 本地路径（若已安装）
- 1 行用途说明（让用户知道为什么要加）
- 规则性质说明：这些 skills 将写入 `AGENTS.md` 作为“本项目 Codex 必须遵循的协作规则”

**目标**：让用户能一句话确认“是否把这些 skills 作为本项目规则写入 `AGENTS.md`，以及是否需要安装缺失项”。

### Step 3：若缺失对应 skill，先确保有 `find-skills`

当“候选清单”里出现缺失 skill 时：

1) 检查 `~/.codex/skills/find-skills` 是否存在。  
2) 如果不存在，先安装它（全局）：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/vercel-labs/skills/tree/main/skills/find-skills
```

3) 然后显式调用 `$find-skills` 并按其流程搜索“最贴近该主技术栈的 best-practices 类 skill”，输出建议安装项。

> 选择策略（默认）：优先选择名称或描述里明确包含 `best-practices` / `development-guides` / “MUST use for <stack>” 等强约束表述的 skill。

### Step 4：让用户确认后再安装

把“将要安装”的 skills 清单再次展示给用户，要求用户确认（例如回复 “确认安装”）。

用户确认后，再执行安装（使用 `skill-installer` 或对应 skill 的安装方式）。

### Step 5：更新 `AGENTS.md`（去重、最小侵入）

1) 若仓库根目录不存在 `AGENTS.md`：创建。  
2) 若已存在：只追加/更新一个独立小节，不覆盖其他内容。  
3) 写入前先检测：`AGENTS.md` 是否已经包含对应 skill 名称；包含就跳过，不重复写。

写入格式必须体现“规则/强约束”，不要写成“推荐”。推荐写入格式（示例）：

```md
## Codex Skills Policy（必须遵循）

以下为本项目协作规则：当任务命中这些 skills 的触发条件时，Codex **必须先加载并遵循对应 skill 的流程**，不得跳过。

<!-- codex-skill-policy:start -->

- vue-best-practices: /Users/xxx/.codex/skills/vue-best-practices/SKILL.md — Vue 3 最佳实践

<!-- codex-skill-policy:end -->
```

> 注意：只写“主框架级别”的强约束即可；不要把无关 skill 塞进来。

## 常见澄清（必须问）

- “你希望以当前代码为准，还是以你准备迁移后的目标技术栈为准？”
- “这些 skills 我先列候选，你确认后我再安装，可以吗？”（默认是“需要确认”）

## 成功标准

- 用户确认了主技术栈  
- 候选 skills 已列出，且用户确认后才安装  
- `AGENTS.md` 中出现去重后的 skills 推荐清单，且不覆盖用户已有规范  
