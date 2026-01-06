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
- **Import Tools / 导入工具**: Built-in script to import skills from public repositories / 内置从公共仓库导入技能的脚本
- **Built-in Skills from Open Source Projects / 内置开源项目技能**: Includes skills from [agentskills/agentskills](https://github.com/agentskills/agentskills) and [anthropics/skills](https://github.com/anthropics/skills) repositories / 包含来自 agentskills/agentskills 和 anthropics/skills 仓库的技能

## Prerequisites / 先决条件

- Python 3.11 or higher / Python 3.11 或更高版本
- pip package manager / pip 包管理器

## Key Technologies / 关键技术

- **MCP (Model Context Protocol)**: For server integration / 用于服务器集成
- **Pydantic**: For data validation and serialization / 用于数据验证和序列化
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
├── .skill_cortex_cache/       # Cache directory / 缓存目录
│   └── index.json            # Skill index cache / 技能索引缓存
├── .skill_cortex_sources/     # Imported skills source / 导入的技能源
├── import_skills.py          # Skill import script / 技能导入脚本
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

Get detailed information about a specific skill / 获取特定技能的详细信息

**Parameters / 参数:**
- `skill_id` (required): Unique identifier of the skill / 技能的唯一标识符

**Example / 示例:**
```json
{
  "skill_id": "coding/database/query"
}
```

**Response / 响应:**
Returns complete skill information including content, tags, and metadata / 返回完整的技能信息，包括内容、标签和元数据

### 4. update_tags / 更新标签

Manage the allowed tags list / 管理允许的标签列表

**Parameters / 参数:**
- `mode` (required): Operation mode - "list", "add", "remove", or "update" / 操作模式 - "list"、"add"、"remove" 或 "update"
- `updates` (optional): Array of tag updates / 标签更新数组

**Example / 示例:**
```json
{
  "mode": "list"
}
```

```json
{
  "mode": "add",
  "updates": [
    {"tag": "ai", "description": "Artificial Intelligence"}
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

The project includes a built-in script to import skills from public repositories / 项目包含一个内置脚本，用于从公共仓库导入技能

### Built-in Skills / 内置技能

This project includes skills from the following open-source repositories / 本项目包含以下开源仓库的技能：

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

### Import Script / 导入脚本

```bash
# Preview what would be imported / 预览将要导入的内容
python import_skills.py --dry-run

# Actually import the skills / 实际导入技能
python import_skills.py
```

Skills are imported to: `./.skill_cortex_sources/` / 技能导入到：`./.skill_cortex_sources/`

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
