"""
Skill-Cortex (Lite) - MCP server for Claude Code Skills

A third-party MCP server that enables all IDEs to access Claude Code Skills capabilities.
"""

__version__ = "0.1.1"
__author__ = "Skill-Cortex Contributors"

from skill_cortex.models import ScanResult, SkillFrontmatter, SkillRecord, TreeNode
from skill_cortex.config import AppConfig, load_config
from skill_cortex.scanner import scan_skills
from skill_cortex.tags_registry import TagsRegistry, load_tags_registry
from skill_cortex.index_store import load_index, save_index
from skill_cortex.frontmatter import ParsedFrontmatter, parse_skill_markdown, normalize_tags

__all__ = [
    "__version__",
    # Models
    "ScanResult",
    "SkillFrontmatter", 
    "SkillRecord",
    "TreeNode",
    # Config
    "AppConfig",
    "load_config",
    # Scanner
    "scan_skills",
    # Tags
    "TagsRegistry",
    "load_tags_registry",
    # Index
    "load_index",
    "save_index",
    # Frontmatter
    "ParsedFrontmatter",
    "parse_skill_markdown",
    "normalize_tags",
]
