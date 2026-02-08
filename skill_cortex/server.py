from __future__ import annotations

import logging
import sys
import threading
import time
from pathlib import Path

from skill_cortex.config import AppConfig, load_config
from skill_cortex.frontmatter import normalize_tags
from skill_cortex.index_store import load_index, save_index
from skill_cortex.scanner import scan_skills
from skill_cortex.skill_manager import create_skill, delete_skill
from skill_cortex.tags_registry import TagsRegistry, load_tags_registry


_logger = logging.getLogger("skill_cortex")


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _not_implemented(name: str) -> dict:
    return {
        "ok": False,
        "error": "not_implemented",
        "tool": name,
    }


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _ensure_state_loaded(
    config: AppConfig,
    state: dict[str, object],
    state_lock: threading.Lock,
) -> None:
    with state_lock:
        if state.get("registry") is not None and state.get("scan") is not None:
            return

        start = time.perf_counter()
        registry = load_tags_registry(config.tags_path)
        scan = load_index(config.cache_path)
        if scan is None:
            scan = scan_skills(config.roots, tags_registry=registry)
            save_index(config.cache_path, scan)

        state["registry"] = registry
        state["scan"] = scan
        duration = time.perf_counter() - start
        _logger.info("Index ready in %.2fs (skills=%s)", duration, len(scan.skills))


def _parse_path_arg(path: str | None) -> tuple[str, ...]:
    if not path:
        return ()
    return tuple(p for p in path.split("/") if p)


def _find_node(tree, path: tuple[str, ...]):
    node = tree
    for part in path:
        node = node.children.get(part)
        if node is None:
            return None
    return node


def _apply_max_lines(text: str, max_lines: int | None) -> str:
    """Truncate text to max_lines if specified."""
    if max_lines is None or max_lines <= 0:
        return text
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + f"\n... [truncated, {len(lines) - max_lines} more lines]"


def _extract_section(content: str, section: str) -> str:
    """Extract a specific section from SKILL.md content.
    
    Sections are identified by markdown headers (## or ###).
    Common sections: instructions, examples, notes, usage, parameters
    """
    lines = content.splitlines()
    
    # Skip frontmatter
    start_idx = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start_idx = i + 1
                break
    
    # Find section boundaries
    section_lower = section.lower()
    section_start = None
    section_end = None
    
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        # Check for header lines
        if line.startswith("#"):
            header_text = line.lstrip("#").strip().lower()
            if section_start is None:
                # Looking for section start
                if section_lower in header_text:
                    section_start = i
            else:
                # Found next section, mark end
                section_end = i
                break
    
    if section_start is None:
        # Section not found, return body without frontmatter
        if section_lower == "instructions":
            # Default: return everything after frontmatter until first ## header
            body_lines = []
            for i in range(start_idx, len(lines)):
                line = lines[i].strip()
                if line.startswith("## "):
                    break
                body_lines.append(lines[i])
            return "\n".join(body_lines).strip() or "[No instructions section found]"
        return f"[Section '{section}' not found]"
    
    section_end = section_end or len(lines)
    return "\n".join(lines[section_start:section_end]).strip()


def _summarize_skill(skill) -> dict:
    return {
        "skill_id": skill.skill_id,
        "title": skill.frontmatter.title,
        "description_snapshot": skill.description_snapshot,
        "tags": list(skill.frontmatter.tags),
        "tag_issues": list(skill.tag_issues),
        "category_path": list(skill.category_path),
    }


def _format_tags_inline(tags: tuple[str, ...]) -> str:
    return "[" + ", ".join(tags) + "]"


def _update_tags_in_skill_md(skill_md_path: Path, new_tags: tuple[str, ...]) -> None:
    text = skill_md_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines:
        raise ValueError("empty_file")
    if lines[0].strip() != "---":
        raise ValueError("missing_frontmatter")

    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
    if end_index is None:
        raise ValueError("unterminated_frontmatter")

    open_delim = lines[0]
    front = lines[1:end_index]
    close_delim = lines[end_index]
    body = lines[end_index + 1 :]

    new_tags_line = "tags: " + _format_tags_inline(new_tags) + "\n"
    found = False
    updated_front: list[str] = []
    for raw in front:
        if raw.lstrip().lower().startswith("tags:"):
            updated_front.append(new_tags_line)
            found = True
            continue
        updated_front.append(raw)
    if not found:
        updated_front.append(new_tags_line)

    skill_md_path.write_text(
        open_delim + "".join(updated_front) + close_delim + "".join(body),
        encoding="utf-8",
    )


def main() -> None:
    _setup_logging()
    try:
        sys.stdout.reconfigure(line_buffering=True, write_through=True)
    except Exception:
        pass

    try:
        sys.stderr.reconfigure(line_buffering=True, write_through=True)
    except Exception:
        pass

    config = load_config()
    _logger.info("Starting Skill-Cortex (Lite)")
    _logger.info("roots=%s", ",".join(str(p) for p in config.roots))
    _logger.info("cache_path=%s", str(config.cache_path))
    _logger.info("tags_path=%s", str(config.tags_path))

    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        _logger.error("Missing dependency 'mcp': %s", exc)
        print(
            "Missing dependency 'mcp'. Install dependencies first, e.g. `pip install -e .`\n"
            + f"Import error: {exc}",
            file=sys.stderr,
        )
        raise

    mcp = FastMCP("skill-cortex-lite")

    state_lock = threading.Lock()
    state: dict[str, object] = {
        "registry": None,
        "scan": None,
    }

    @mcp.tool()
    def list_skill_tree(path: str | None = None) -> dict:
        _ensure_state_loaded(config, state, state_lock)
        parts = _parse_path_arg(path)
        node = _find_node(state["scan"].tree, parts)
        if node is None:
            return {"ok": False, "error": "path_not_found", "path": list(parts)}
        return {
            "ok": True,
            "path": list(parts),
            "categories": sorted(node.children.keys()),
            "skills": [_summarize_skill(s) for s in node.skills],
        }

    @mcp.tool()
    def search_skills(query: str | None = None, tags: list[str] | None = None) -> dict:
        _ensure_state_loaded(config, state, state_lock)
        q = (query or "").strip().lower()
        filter_tags = normalize_tags(tags or [])
        results = []
        for s in state["scan"].skills:
            if q:
                hay = " ".join(
                    [
                        s.skill_id,
                        s.frontmatter.title,
                        s.description_snapshot,
                        "/".join(s.category_path),
                    ]
                ).lower()
                if q not in hay:
                    continue
            if filter_tags:
                if not set(filter_tags).issubset(set(s.frontmatter.tags)):
                    continue
            results.append(_summarize_skill(s))
        return {"ok": True, "count": len(results), "results": results}

    @mcp.tool()
    def get_skill_details(
        skill_id: str,
        section: str = "summary",
        max_lines: int | None = None,
    ) -> dict:
        """Get skill details with context compression options.
        
        Args:
            skill_id: Unique identifier of the skill
            section: What to return - "summary" (default, frontmatter + snippet), 
                     "instructions" (main instructions only),
                     "examples" (code examples only),
                     "full" (complete content)
            max_lines: Optional line limit for the content
        """
        _ensure_state_loaded(config, state, state_lock)
        for s in state["scan"].skills:
            if s.skill_id == skill_id:
                content = s.skill_path.read_text(encoding="utf-8")
                
                result = {
                    "ok": True,
                    "skill_id": s.skill_id,
                    "title": s.frontmatter.title,
                    "description": s.frontmatter.description,
                    "tags": list(s.frontmatter.tags),
                }
                
                section_lower = (section or "summary").strip().lower()
                
                if section_lower == "summary":
                    # Just metadata + description snapshot, no full content
                    result["description_snapshot"] = s.description_snapshot
                    result["hint"] = "Use section='instructions' or 'full' for complete content"
                elif section_lower == "full":
                    result["content"] = _apply_max_lines(content, max_lines)
                else:
                    # Extract specific section
                    extracted = _extract_section(content, section_lower)
                    result["section"] = section_lower
                    result["content"] = _apply_max_lines(extracted, max_lines)
                
                return result
        return {"ok": False, "error": "skill_not_found", "skill_id": skill_id}

    @mcp.tool()
    def update_tags(mode: str = "list", updates: list[dict] | None = None) -> dict:
        _ensure_state_loaded(config, state, state_lock)
        m = (mode or "list").strip().lower()
        if m == "list":
            bad = [s for s in state["scan"].skills if s.tag_issues]
            return {"ok": True, "count": len(bad), "skills": [_summarize_skill(s) for s in bad]}

        if m != "apply":
            return {"ok": False, "error": "invalid_mode", "mode": mode}

        if not updates:
            return {"ok": False, "error": "missing_updates"}

        allowed = state["registry"].allowed_tags
        results = []
        for upd in updates:
            skill_id = str(upd.get("skill_id", "")).strip()
            tags_tuple = normalize_tags(upd.get("tags", []))
            if not skill_id:
                results.append({"ok": False, "error": "missing_skill_id"})
                continue
            if not tags_tuple:
                results.append({"ok": False, "skill_id": skill_id, "error": "missing_tags"})
                continue
            invalid = [t for t in tags_tuple if t not in allowed]
            if invalid:
                results.append({"ok": False, "skill_id": skill_id, "error": "invalid_tags", "invalid": invalid})
                continue

            skill = next((s for s in state["scan"].skills if s.skill_id == skill_id), None)
            if skill is None:
                results.append({"ok": False, "skill_id": skill_id, "error": "skill_not_found"})
                continue

            try:
                _update_tags_in_skill_md(skill.skill_path, tags_tuple)
                results.append({"ok": True, "skill_id": skill_id, "tags": list(tags_tuple)})
            except Exception as exc:
                results.append({"ok": False, "skill_id": skill_id, "error": "write_failed", "detail": str(exc)})

        state["scan"] = scan_skills(config.roots, tags_registry=state["registry"])
        save_index(config.cache_path, state["scan"])
        return {"ok": True, "results": results}

    @mcp.tool()
    def create_new_skill(
        path: str,
        description: str,
        tags: list[str] | None = None,
        instructions: str | None = None,
        license: str | None = None,
        metadata: dict[str, str] | None = None,
        create_scripts_dir: bool = False,
        create_references_dir: bool = False,
        create_assets_dir: bool = False,
    ) -> dict:
        """Create a new skill.
        
        Args:
            path: Skill path (e.g., "coding/python-helper" or "simple-skill")
            description: Skill description (1-1024 characters)
            tags: Optional list of tags
            instructions: Optional custom instructions (if not provided, a template will be generated)
            license: Optional license information
            metadata: Optional metadata dict (e.g., {"author": "example", "version": "1.0"})
            create_scripts_dir: Whether to create scripts/ directory
            create_references_dir: Whether to create references/ directory
            create_assets_dir: Whether to create assets/ directory
            
        Returns:
            Result dict with ok status and skill details
        """
        _ensure_state_loaded(config, state, state_lock)
        
        result = create_skill(
            roots=config.roots,
            path=path,
            description=description,
            tags=tags,
            instructions=instructions,
            license=license,
            metadata=metadata,
            create_scripts_dir=create_scripts_dir,
            create_references_dir=create_references_dir,
            create_assets_dir=create_assets_dir,
        )
        
        # If successful, rescan and update index
        if result.get("ok"):
            state["scan"] = scan_skills(config.roots, tags_registry=state["registry"])
            save_index(config.cache_path, state["scan"])
        
        return result

    @mcp.tool()
    def delete_existing_skill(
        skill_id: str,
        confirm: bool = False,
    ) -> dict:
        """Delete a skill (requires confirmation).
        
        Only allows deletion of user-created skills in .skills/ directory.
        Imported skills and source repository skills cannot be deleted.
        
        Args:
            skill_id: Unique identifier of the skill to delete
            confirm: Must be True to actually delete (False shows preview only)
            
        Returns:
            Result dict with ok status and details
        """
        _ensure_state_loaded(config, state, state_lock)
        
        # Find the skill
        skill = next((s for s in state["scan"].skills if s.skill_id == skill_id), None)
        if skill is None:
            return {"ok": False, "error": "skill_not_found", "skill_id": skill_id}
        
        result = delete_skill(
            skill_path=skill.skill_path,
            roots=config.roots,
            confirm=confirm,
        )
        
        # If successfully deleted, rescan and update index
        if result.get("ok"):
            state["scan"] = scan_skills(config.roots, tags_registry=state["registry"])
            save_index(config.cache_path, state["scan"])
        
        return result

    mcp.run()


if __name__ == "__main__":
    main()
