"""Skill management utilities for creating and deleting skills."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from skill_cortex.frontmatter import normalize_tags


def validate_skill_name_part(name: str) -> tuple[bool, str]:
    """Validate a single part of a skill name.
    
    Args:
        name: Name part to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Name cannot be empty"
    
    if len(name) > 64:
        return False, f"Name too long (max 64 chars): {len(name)}"
    
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, "Name must contain only lowercase letters, numbers, and hyphens"
    
    if name.startswith("-") or name.endswith("-"):
        return False, "Name cannot start or end with a hyphen"
    
    if "--" in name:
        return False, "Name cannot contain consecutive hyphens"
    
    return True, ""


def parse_skill_path(path: str) -> tuple[tuple[str, ...], str, str | None]:
    """Parse a skill path into category and name components.
    
    Args:
        path: Skill path (e.g., "coding/python-helper" or "simple-skill")
        
    Returns:
        Tuple of (category_path, skill_name, error_message)
    """
    if not path:
        return (), "", "Path cannot be empty"
    
    parts = [p.strip() for p in path.split("/") if p.strip()]
    if not parts:
        return (), "", "Path cannot be empty"
    
    # Validate each part
    for part in parts:
        is_valid, error = validate_skill_name_part(part)
        if not is_valid:
            return (), "", f"Invalid path component '{part}': {error}"
    
    # Last part is the skill name, rest is category
    skill_name = parts[-1]
    category_path = tuple(parts[:-1])
    
    return category_path, skill_name, None


def generate_skill_markdown(
    name: str,
    description: str,
    tags: tuple[str, ...],
    instructions: str | None = None,
    license: str | None = None,
    metadata: dict[str, str] | None = None,
) -> str:
    """Generate SKILL.md content.
    
    Args:
        name: Skill name
        description: Skill description
        tags: Skill tags
        instructions: Optional custom instructions
        license: Optional license
        metadata: Optional metadata dict
        
    Returns:
        Complete SKILL.md content
    """
    # Build frontmatter
    frontmatter_lines = ["---"]
    frontmatter_lines.append(f"name: {name}")
    frontmatter_lines.append(f"description: {description}")
    
    if tags:
        tags_str = "[" + ", ".join(tags) + "]"
        frontmatter_lines.append(f"tags: {tags_str}")
    
    if license:
        frontmatter_lines.append(f"license: {license}")
    
    if metadata:
        frontmatter_lines.append("metadata:")
        for key, value in metadata.items():
            frontmatter_lines.append(f"  {key}: {value}")
    
    frontmatter_lines.append("---")
    frontmatter = "\n".join(frontmatter_lines)
    
    # Build body
    if instructions:
        body = f"\n\n{instructions}"
    else:
        # Generate template
        body = """

## Instructions

[Provide detailed step-by-step instructions for using this skill]

## Examples

[Add examples of how to use this skill]

## Notes

[Add any additional notes or considerations]
"""
    
    return frontmatter + body


def create_skill(
    roots: tuple[Path, ...],
    path: str,
    description: str,
    tags: list[str] | None = None,
    instructions: str | None = None,
    license: str | None = None,
    metadata: dict[str, str] | None = None,
    create_scripts_dir: bool = False,
    create_references_dir: bool = False,
    create_assets_dir: bool = False,
) -> dict[str, Any]:
    """Create a new skill.
    
    Args:
        roots: Skill root directories
        path: Skill path (e.g., "coding/python-helper" or "simple-skill")
        description: Skill description
        tags: Optional list of tags
        instructions: Optional custom instructions
        license: Optional license
        metadata: Optional metadata dict
        create_scripts_dir: Whether to create scripts/ directory
        create_references_dir: Whether to create references/ directory
        create_assets_dir: Whether to create assets/ directory
        
    Returns:
        Result dict with ok status and details
    """
    # Parse and validate path
    category_path, skill_name, error = parse_skill_path(path)
    if error:
        return {"ok": False, "error": "invalid_path", "detail": error}
    
    # Validate description
    if not description or len(description) > 1024:
        return {"ok": False, "error": "invalid_description", "detail": "Description must be 1-1024 characters"}
    
    # Normalize and validate tags
    normalized_tags = normalize_tags(tags or [])
    
    # Find the first writable root (prefer .skills/)
    target_root = None
    for root in roots:
        if root.name == ".skills" or root.name == "skills":
            target_root = root
            break
    
    if target_root is None and roots:
        target_root = roots[0]
    
    if target_root is None:
        return {"ok": False, "error": "no_root", "detail": "No skill root directory configured"}
    
    # Build skill directory path
    skill_dir = target_root
    for part in category_path:
        skill_dir = skill_dir / part
    skill_dir = skill_dir / skill_name
    
    # Check if skill already exists
    skill_md_path = skill_dir / "SKILL.md"
    if skill_md_path.exists():
        return {"ok": False, "error": "skill_exists", "detail": f"Skill already exists at {skill_md_path}"}
    
    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        return {"ok": False, "error": "mkdir_failed", "detail": str(exc)}
    
    # Generate and write SKILL.md
    try:
        markdown_content = generate_skill_markdown(
            name=skill_name,
            description=description,
            tags=normalized_tags,
            instructions=instructions,
            license=license,
            metadata=metadata,
        )
        skill_md_path.write_text(markdown_content, encoding="utf-8")
    except Exception as exc:
        # Clean up on failure
        shutil.rmtree(skill_dir, ignore_errors=True)
        return {"ok": False, "error": "write_failed", "detail": str(exc)}
    
    # Create optional directories
    try:
        if create_scripts_dir:
            (skill_dir / "scripts").mkdir(exist_ok=True)
        if create_references_dir:
            (skill_dir / "references").mkdir(exist_ok=True)
        if create_assets_dir:
            (skill_dir / "assets").mkdir(exist_ok=True)
    except Exception as exc:
        return {"ok": False, "error": "mkdir_optional_failed", "detail": str(exc)}
    
    return {
        "ok": True,
        "skill_path": str(skill_md_path),
        "skill_dir": str(skill_dir),
        "skill_name": skill_name,
        "category_path": list(category_path),
        "message": f"Skill created successfully at {skill_md_path}",
    }


def is_deletable_skill(skill_path: Path, roots: tuple[Path, ...]) -> tuple[bool, str]:
    """Check if a skill can be deleted.
    
    Only allows deletion of skills in .skills/ directory (not imported skills).
    
    Args:
        skill_path: Path to SKILL.md file
        roots: Skill root directories
        
    Returns:
        Tuple of (is_deletable, reason)
    """
    # Check if skill is in a deletable root
    for root in roots:
        try:
            rel_path = skill_path.relative_to(root)
            # Allow deletion from .skills/ but not .skills/imported/
            if root.name in (".skills", "skills"):
                if "imported" in rel_path.parts:
                    return False, "Cannot delete imported skills"
                return True, ""
            # Don't allow deletion from .skill_cortex_sources/
            if root.name == ".skill_cortex_sources":
                return False, "Cannot delete skills from source repositories"
        except ValueError:
            # Not relative to this root, continue
            continue
    
    return False, "Skill not in a deletable directory"


def delete_skill(
    skill_path: Path,
    roots: tuple[Path, ...],
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a skill.
    
    Args:
        skill_path: Path to SKILL.md file
        roots: Skill root directories
        confirm: Must be True to actually delete
        
    Returns:
        Result dict with ok status and details
    """
    if not skill_path.exists():
        return {"ok": False, "error": "skill_not_found", "detail": f"Skill not found at {skill_path}"}
    
    # Check if deletable
    is_deletable, reason = is_deletable_skill(skill_path, roots)
    if not is_deletable:
        return {"ok": False, "error": "not_deletable", "detail": reason}
    
    skill_dir = skill_path.parent
    
    # If not confirmed, return preview
    if not confirm:
        return {
            "ok": False,
            "error": "confirmation_required",
            "detail": "Set confirm=true to delete this skill",
            "skill_path": str(skill_path),
            "skill_dir": str(skill_dir),
            "message": "Preview mode: skill will NOT be deleted",
        }
    
    # Delete the skill directory
    try:
        shutil.rmtree(skill_dir)
    except Exception as exc:
        return {"ok": False, "error": "delete_failed", "detail": str(exc)}
    
    return {
        "ok": True,
        "skill_path": str(skill_path),
        "skill_dir": str(skill_dir),
        "message": f"Skill deleted successfully from {skill_dir}",
    }
