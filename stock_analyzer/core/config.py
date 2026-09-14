"""Configuration Loader and Source Registry Engine."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field


class SourceDefinition(BaseModel):
    """Metadata and capability definition for a registered data provider."""
    id: str
    name: str
    kind: str
    url: str
    enabled: bool = True
    priority: int = 99
    api_key_env: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    best_for: str = ""
    notes: str = ""

    def is_authenticated(self) -> bool:
        """Check whether the necessary API key exists in environment variables."""
        if not self.api_key_env:
            return True  # No key required (e.g. SEC EDGAR or public open sources)
        val = os.environ.get(self.api_key_env, "")
        return bool(val.strip())


class SourceRegistry:
    """Registry managing data sources, capabilities, and priority selection."""

    def __init__(self, sources: List[SourceDefinition]):
        self.sources: Dict[str, SourceDefinition] = {s.id: s for s in sources}

    def get_source(self, source_id: str) -> Optional[SourceDefinition]:
        return self.sources.get(source_id)

    def get_sources_for_capability(self, capability: str) -> List[SourceDefinition]:
        """Return all enabled sources supporting a capability, sorted by priority (1 is highest)."""
        matching = [
            s for s in self.sources.values()
            if s.enabled and capability in s.capabilities
        ]
        return sorted(matching, key=lambda s: s.priority)

    def get_primary_source_for_capability(self, capability: str) -> Optional[SourceDefinition]:
        """Get the highest priority authenticated source for a given capability."""
        sources = self.get_sources_for_capability(capability)
        for s in sources:
            if s.is_authenticated():
                return s
        return sources[0] if sources else None


class ConfigLoader:
    """Loads authoritative project configuration YAML files and builds registries."""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Default to <workspace_root>/config
            root = Path(__file__).resolve().parent.parent.parent
            self.config_dir = root / "config"
        else:
            self.config_dir = Path(config_dir)

    def load_main_config(self) -> Dict[str, Any]:
        """Load stock_market_data_config.yaml."""
        path = self.config_dir / "stock_market_data_config.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_source_registry(self) -> SourceRegistry:
        """Construct the SourceRegistry from stock_market_data_config.yaml."""
        cfg = self.load_main_config()
        priority_map = cfg.get("source_priority", {
            "authoritative": 1,
            "licensed_api": 2,
            "exchange_or_broker": 3,
            "reputable_aggregator": 4,
            "social_or_crowd": 5,
            "unofficial_library": 6,
        })

        source_list: List[SourceDefinition] = []
        sources_block = cfg.get("sources", {})

        for category, items in sources_block.items():
            for item in items:
                kind = item.get("kind", "other")
                prio = priority_map.get(kind, 99)
                source_def = SourceDefinition(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    kind=kind,
                    url=item.get("url", ""),
                    enabled=item.get("enabled", True),
                    priority=prio,
                    api_key_env=item.get("api_key_env"),
                    capabilities=item.get("capabilities", []),
                    best_for=item.get("best_for", ""),
                    notes=item.get("notes", ""),
                )
                source_list.append(source_def)

        return SourceRegistry(source_list)
