from pydantic import BaseModel
from typing import Dict, Any, Optional


class GraphCreate(BaseModel):
    nodes: Dict[str, str]  # mapping of node names to code identifiers
    edges: Dict[str, str]  # mapping of node to next node


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Optional[Dict[str, Any]] = {}  # starting state for the graph