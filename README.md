# Skill-Cortex (Lite) / Skill-Cortex (精简版)

一个第三方 MCP 服务器：让所有 IDE 获得 Claude Code Skills 的能力。

A third-party MCP server: Enable all IDEs to access Claude Code Skills capabilities.

## Features / 特性

- **Skill Discovery & Indexing / 技能发现与索引**: Automatically scan and index SKILL.md files from multiple sources / 自动扫描和索引来自多个来源的 SKILL.md 文件
- **Flexible Configuration / 灵活配置**: Support for custom skill roots and cache paths / 支持自定义技能根目录和缓存路径
- **Tag Management / 标签管理**: Built-in tag validation and management system / 内置标签验证和管理系统
- **Skill Tree Navigation / 技能树导航**: Hierarchical browsing of skills by category / 按类别分层浏览技能
- **Search Functionality / 搜索功能**: Full-text search across all indexed skills / 对所有索引技能进行全文搜索
- **Skill Details / 技能详情**: Detailed information retrieval for each skill / 每个技能的详细信息检索
- **Enhanced Import Tools / 增强导入工具**: Advanced import script with configuration files, progress tracking, and robust error handling / 具有配置文件、进度跟踪和健壮错误处理的高级导入脚本
- **No Bundled Skills in Repo / 仓库不内置 Skills**: This repository does not ship skills by default; put your skills under `~/.claude/skills` or `./.skills` / 本仓库默认不内置 skills，请将 skills 放到 `~/.claude/skills` 或 `./.skills`
- **Context Compression / 上下文压缩**: Token-friendly skill retrieval with section-based extraction (summary, instructions, examples, full) / 支持按 section 提取技能内容，节省 token 消耗

## Prerequisites / 先决条件

- Python 3.11 or higher / Python 3.11 或更高版本
- pip package manager / pip 包管理器

## Key Technologies / 关键技术

- **MCP (Model Context Protocol)**: For server integration / 用于服务器集成
- **Python Standard Library**: File system operations and caching / 文件系统操作和缓存

## Project Structure / 项目结构

```
skill_cortex_server/
├── skill_cortex/              # Main package / 主包
│   ├── __init__.py           # Package initialization / 包初始化
│   ├── server.py             # MCP server implementation / MCP 服务器实现
│   ├── models.py             # Data models / 数据模型
│   ├── config.py             # Configuration management / 配置管理
│   ├── scanner.py            # Skill file scanner / 技能文件扫描器
│   ├── index_store.py        # Index storage and caching / 索引存储和缓存
│   ├── tags_registry.py      # Tag management system / 标签管理系统
│   └── frontmatter.py        # Frontmatter parsing / 前置元数据解析
├── config/                    # Configuration files / 配置文件
│   └── examples/             # Example configuration files / 示例配置文件
│       ├── skills-config.yaml # YAML configuration example / YAML配置示例
│       └── skills-config.json # JSON configuration example / JSON配置示例
├── .kiro/                     # Kiro specs and development files / Kiro规范和开发文件
│   └── specs/                # Feature specifications / 功能规范
├── .skill_cortex_cache/       # Cache directory / 缓存目录
│   └── index.json            # Skill index cache / 技能索引缓存
├── .skill_cortex_sources/     # Imported skills source / 导入的技能源
├── .skills/                   # Local skills directory / 本地技能目录
│   └── imported/             # Imported skills / 导入的技能
├── import_skills.py          # Enhanced skill import script / 增强的技能导入脚本
├── pyproject.toml            # Project configuration / 项目配置
├── README.md                 # This file / 本文件
└── tags.md                   # Allowed tags list / 允许的标签列表
```

## Quick Start / 快速开始

### Installation / 安装

```bash
# Install in editable mode / 以可编辑模式安装
pip install -e .

# Or install from PyPI (when available) / 或从 PyPI 安装（当可用时）
pip install skill-cortex-lite
```

### Run the Server / 运行服务器

```bash
# Run directly / 直接运行
skill-cortex

# Or use Python module / 或使用 Python 模块
python -m skill_cortex.server
```

## MCP Tools / MCP 工具

### 1. list_skill_tree / 列出技能树

Browse skills in a hierarchical tree structure / 以分层树结构浏览技能

**Parameters / 参数:**
- `path` (optional): Starting path in the skill tree / 技能树中的起始路径

**Example / 示例:**
```json
{
  "path": "coding"
}
```

**Response / 响应:**
Returns a hierarchical tree of skills with their metadata / 返回包含元数据的分层技能树

### 2. search_skills / 搜索技能

Search for skills by query text / 通过查询文本搜索技能

**Parameters / 参数:**
- `query` (optional): Search query string / 搜索查询字符串
- `tags` (optional): Array of tags to filter by / 用于筛选的标签数组

**Example / 示例:**
```json
{
  "query": "database",
  "tags": ["coding", "data"]
}
```

**Response / 响应:**
Returns matching skills with their details / 返回匹配的技能及其详细信息

### 3. get_skill_details / 获取技能详情

Get detailed information about a specific skill with context compression / 获取特定技能的详细信息，支持上下文压缩

**Parameters / 参数:**
- `skill_id` (required): Unique identifier of the skill / 技能的唯一标识符
- `section` (optional): What to return / 返回内容类型
  - `"summary"` (default): Frontmatter + description snapshot (token-friendly) / 仅元数据和描述摘要（节省token）
  - `"instructions"`: Main instructions section only / 仅主要指令部分
  - `"examples"`: Code examples section only / 仅代码示例部分
  - `"full"`: Complete SKILL.md content / 完整内容
- `max_lines` (optional): Limit output to N lines / 限制输出行数

**Example / 示例:**
```json
{
  "skill_id": "coding/database/query",
  "section": "summary"
}
```

```json
{
  "skill_id": "coding/database/query",
  "section": "instructions",
  "max_lines": 50
}
```

**Response / 响应:**
Returns skill information based on section parameter / 根据 section 参数返回技能信息

### 4. update_tags / 更新标签

Manage tags inside skills frontmatter / 管理 skills 的 frontmatter tags

**Parameters / 参数:**
- `mode` (required): "list" or "apply" / 操作模式："list" 或 "apply"
- `updates` (optional): required when mode is "apply" / 当 mode 为 "apply" 时需要提供

**Example / 示例:**
```json
{
  "mode": "list"
}
```

```json
{
  "mode": "apply",
  "updates": [
    {"skill_id": "...", "tags": ["python", "mcp"]}
  ]
}
```

**Response / 响应:**
Returns the current tags list or operation result / 返回当前标签列表或操作结果

## Configuration / 配置

### Environment Variables / 环境变量

- `SKILL_CORTEX_ROOTS`: Comma-separated list of skill root directories / 逗号分隔的技能根目录列表
  - Default: `~/.claude/skills,./.skills` / 默认值
  - Example: `/path/to/skills1,/path/to/skills2` / 示例

- `SKILL_CORTEX_CACHE_PATH`: Path to the index cache file / 索引缓存文件路径
  - Default: `./.skill_cortex_cache/index.json` / 默认值
  - Example: `/custom/path/cache.json` / 示例

- `SKILL_CORTEX_TAGS_PATH`: Path to the allowed tags file / 允许的标签文件路径
  - Default: `./tags.md` / 默认值
  - Example: `/custom/path/tags.md` / 示例

### Example Configuration / 配置示例

```json
{
  "mcpServers": {
    "skill-cortex-lite": {
      "command": "skill-cortex",
      "args": [],
      "env": {
        "SKILL_CORTEX_ROOTS": "/Users/username/skills1,/Users/username/skills2",
        "SKILL_CORTEX_CACHE_PATH": "/Users/username/.skill_cortex_cache/index.json",
        "SKILL_CORTEX_TAGS_PATH": "/Users/username/tags.md"
      }
    }
  }
}
```

## Importing Skills / 导入技能

The project includes an enhanced import script with advanced features for importing skills from public repositories / 项目包含一个增强的导入脚本，具有从公共仓库导入技能的高级功能

### Enhanced Import Features / 增强导入功能

#### 🔧 Configuration File Support / 配置文件支持
- **YAML/JSON Configuration**: Use configuration files to customize repository lists without modifying code / 使用配置文件自定义仓库列表，无需修改代码
- **Auto-discovery**: Automatically finds `skills-config.yaml`, `skills-config.yml`, or `skills-config.json` in current directory / 自动查找当前目录中的配置文件
- **Custom config path**: Use `--config` option to specify custom configuration file / 使用 `--config` 选项指定自定义配置文件

#### 📊 Progress Display / 进度显示
- **Real-time progress**: Shows current repository being processed with step-by-step feedback / 显示当前处理的仓库和逐步反馈
- **Skill counting**: Displays number of skills found in each repository / 显示每个仓库中找到的技能数量
- **Comprehensive summary**: Final report with statistics, timing, and success/failure counts / 包含统计、时间和成功/失败计数的最终报告

#### 🛡️ Robust Error Handling / 健壮错误处理
- **Continue on error**: Single repository failure doesn't stop the entire import process / 单个仓库失败不会停止整个导入过程
- **Detailed error reporting**: Clear error messages with specific failure reasons / 清晰的错误消息和具体失败原因
- **Error categorization**: Different handling for network, file system, and Git errors / 对网络、文件系统和Git错误的不同处理

#### 🔍 Enhanced Preview Mode / 增强预览模式
- **Detailed dry-run**: Shows repository URLs, skill paths, and counts before actual import / 在实际导入前显示仓库URL、技能路径和计数
- **Clear indicators**: Clearly shows when running in preview mode with no actual changes / 清楚显示预览模式，不进行实际更改

### Built-in Skills / 内置技能

This repository does not bundle skills by default. Use the import script (optional) to fetch skills from public repositories / 本仓库默认不内置 skills，可使用导入脚本（可选）从公共仓库拉取：

#### 1. [agentskills/agentskills](https://github.com/agentskills/agentskills)

A comprehensive collection of AI agent skills and capabilities / 一个全面的 AI 代理技能和能力集合

- **Features / 特性**: Provides a wide range of skills for AI agents, including coding, data analysis, and problem-solving / 为 AI 代理提供广泛的技能，包括编码、数据分析和问题解决
- **Skill Types / 技能类型**: Coding, debugging, testing, optimization, and more / 编码、调试、测试、优化等
- **Usage / 用途**: Enhances AI agent capabilities with practical, reusable skills / 通过实用的、可重用的技能增强 AI 代理能力

#### 2. [anthropics/skills](https://github.com/anthropics/skills)

Official skills repository from Anthropic / Anthropic 的官方技能仓库

- **Features / 特性**: Officially maintained skills optimized for Claude AI / 官方维护的针对 Claude AI 优化的技能
- **Skill Types / 技能类型**: Documentation, code generation, system administration, and more / 文档、代码生成、系统管理等
- **Usage / 用途**: Provides high-quality, tested skills for production use / 为生产环境提供高质量、经过测试的技能

#### 3. [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

Community-curated collection of Claude Skills resources / 社区策划的Claude Skills资源集合

- **Features / 特性**: Curated list of awesome Claude Skills, resources, and tools / 精选的Claude Skills、资源和工具列表
- **Skill Types / 技能类型**: Various community-contributed skills and resources / 各种社区贡献的技能和资源
- **Usage / 用途**: Access to community-driven skill collections / 访问社区驱动的技能集合

#### 4. [huggingface/skills](https://github.com/huggingface/skills)

Hugging Face's skills repository for AI and machine learning / Hugging Face 的 AI 和机器学习技能仓库

- **Features / 特性**: Skills and tools for working with Hugging Face ecosystem / 用于 Hugging Face 生态系统的技能和工具
- **Skill Types / 技能类型**: Machine learning, model training, dataset handling, and more / 机器学习、模型训练、数据处理等
- **Usage / 用途**: Enhances capabilities for AI/ML tasks and Hugging Face integrations / 增强 AI/ML 任务和 Hugging Face 集成的能力

### Import Script Usage / 导入脚本使用

#### Basic Usage / 基本使用

```bash
# Preview what would be imported (recommended first step) / 预览将要导入的内容（推荐第一步）
python import_skills.py --dry-run

# Actually import the skills / 实际导入技能
python import_skills.py

# Clean import (remove existing skills first) / 清理导入（先删除现有技能）
python import_skills.py --clean
```

#### Advanced Usage / 高级使用

```bash
# Use custom configuration file / 使用自定义配置文件
python import_skills.py --config my-config.yaml

# Import only specific repositories / 仅导入特定仓库
python import_skills.py --only anthropics_skills --only agentskills_agentskills

# Skip cloning (use existing local repositories) / 跳过克隆（使用现有本地仓库）
python import_skills.py --no-clone

# Don't update existing repositories / 不更新现有仓库
python import_skills.py --no-update
```

#### Configuration File Examples / 配置文件示例

**YAML Configuration (skills-config.yaml):**
```yaml
repositories:
  - name: "anthropics_skills"
    url: "https://github.com/anthropics/skills.git"
    enabled: true
    
  - name: "agentskills_agentskills"
    url: "https://github.com/agentskills/agentskills.git"
    enabled: true
    
  - name: "composio_awesome_skills"
    url: "https://github.com/ComposioHQ/awesome-claude-skills.git"
    enabled: true
    
  - name: "huggingface_skills"
    url: "https://github.com/huggingface/skills.git"
    enabled: true

settings:
  incremental: false
  validation: false
```

**JSON Configuration (skills-config.json):**
```json
{
  "repositories": [
    {
      "name": "anthropics_skills",
      "url": "https://github.com/anthropics/skills.git",
      "enabled": true
    },
    {
      "name": "agentskills_agentskills",
      "url": "https://github.com/agentskills/agentskills.git",
      "enabled": true
    },
    {
      "name": "composio_awesome_skills",
      "url": "https://github.com/ComposioHQ/awesome-claude-skills.git",
      "enabled": true
    },
    {
      "name": "huggingface_skills",
      "url": "https://github.com/huggingface/skills.git",
      "enabled": true
    }
  ],
  "settings": {
    "incremental": false,
    "validation": false
  }
}
```

### Import Process / 导入过程

Skills are imported to: `./.skill_cortex_sources/` / 技能导入到：`./.skill_cortex_sources/`

Skills are copied to: `./.skills/imported/` / 技能拷贝到：`./.skills/imported/`

The import process includes:
1. **Repository cloning/updating** / 仓库克隆/更新
2. **Skill discovery** / 技能发现
3. **File copying** / 文件复制
4. **Progress reporting** / 进度报告
5. **Error handling** / 错误处理

## Troubleshooting / 故障排除

### ModuleNotFoundError / 模块未找到错误

**Problem / 问题:**
```
ModuleNotFoundError: No module named 'skill_cortex'
```

**Solution / 解决方案:**
Install the package in editable mode / 以可编辑模式安装包
```bash
pip install -e .
```

### Skills not appearing / 技能未显示

**Problem / 问题:**
Skills are not showing up in the tool results / 技能未在工具结果中显示

**Solution / 解决方案:**
1. Check that `SKILL_CORTEX_ROOTS` points to correct directories / 检查 `SKILL_CORTEX_ROOTS` 是否指向正确的目录
2. Verify that `SKILL.md` files exist in those directories / 验证这些目录中是否存在 `SKILL.md` 文件
3. Clear the cache by deleting the index.json file / 通过删除 index.json 文件清除缓存
4. Restart the server / 重启服务器

### Tag validation errors / 标签验证错误

**Problem / 问题:**
Tags are being rejected / 标签被拒绝

**Solution / 解决方案:**
1. Check the `tags.md` file for the allowed tags list / 检查 `tags.md` 文件中的允许标签列表
2. Use the `update_tags` tool to add missing tags / 使用 `update_tags` 工具添加缺失的标签
3. Ensure tag names match exactly (case-sensitive) / 确保标签名称完全匹配（区分大小写）

### Import script errors / 导入脚本错误

**Problem / 问题:**
Import script fails with configuration or repository errors / 导入脚本因配置或仓库错误而失败

**Solution / 解决方案:**
1. Use `--dry-run` first to preview what will be imported / 首先使用 `--dry-run` 预览将要导入的内容
2. Check configuration file syntax if using custom config / 如果使用自定义配置，检查配置文件语法
3. Verify repository URLs are accessible / 验证仓库URL是否可访问
4. Use `--no-clone` to skip cloning if repositories already exist locally / 如果仓库已存在本地，使用 `--no-clone` 跳过克隆
5. Check the detailed error report in the final summary / 检查最终摘要中的详细错误报告

## Development / 开发

### Project Setup / 项目设置

```bash
# Clone the repository / 克隆仓库
git clone <repository-url>
cd skill_cortex_server

# Install in development mode / 以开发模式安装
pip install -e .
```

### Running Tests / 运行测试

```bash
# Run all tests / 运行所有测试
pytest

# Run with coverage / 运行并生成覆盖率报告
pytest --cov=skill_cortex
```

## Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request / 欢迎贡献！请随时提交 Pull Request

1. Fork the repository / Fork 仓库
2. Create your feature branch / 创建功能分支
3. Commit your changes / 提交更改
4. Push to the branch / 推送到分支
5. Open a Pull Request / 打开 Pull Request

## License / 许可证

This project is licensed under the MIT License / 本项目采用 MIT 许可证

## Acknowledgments / 致谢

- Inspired by Claude Code Skills / 灵感来自 Claude Code Skills
- Built with MCP (Model Context Protocol) / 使用 MCP（模型上下文协议）构建
- Reference implementation based on mcp-sequential-thinking / 基于 mcp-sequential-thinking 的参考实现

## Contact / 联系方式

For questions and support, please open an issue on GitHub / 如有问题和支持需求，请在 GitHub 上提交 issue
