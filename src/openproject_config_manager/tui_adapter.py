"""
Compatibility adapter for legacy TUI Form Engine usages.

Provides a FormRenderer-like interface backed by tui_form_designer.FlowEngine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

try:
    from tui_form_designer.core.flow_engine import FlowEngine
    from tui_form_designer.core.exceptions import (
        FlowExecutionError,
        FlowValidationError,
    )
except ImportError as e:  # pragma: no cover
    # Re-raise with clearer guidance
    raise ImportError(
        "tui_form_designer not available. Ensure the submodule is present and installed,"
        " e.g., `pip install -e external/tui-form-designer/`."
    ) from e


class FormRenderer:
    """
    Minimal compatibility wrapper exposing a `render_flow` method compatible with
    the legacy `tui_form_engine.renderer.FormRenderer` API used by this repo.

    The method accepts a full file path to the YAML layout and returns a dict with
    a `responses` key, matching the previous engine's return shape.
    """

    def __init__(self, flows_dir: Optional[Path | str] = None) -> None:
        self._flows_dir = Path(flows_dir) if flows_dir else None

    def render_flow(
        self,
        flow_path: str,
        mock_responses: Optional[Dict[str, Any]] = None,
        quiet: bool = False,  # kept for API compatibility; not used directly
    ) -> Dict[str, Any]:
        flow_file = Path(flow_path)
        flows_dir = flow_file.parent
        flow_id = flow_file.stem  # e.g., "config_tui.layout" -> file name without .yml

        engine = FlowEngine(flows_dir=flows_dir)
        responses = engine.execute_flow(
            flow_id=flow_id, context={}, mock_responses=mock_responses
        )
        return {"responses": responses}


__all__ = [
    "FormRenderer",
    "FlowExecutionError",
    "FlowValidationError",
]
