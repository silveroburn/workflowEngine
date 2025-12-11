import asyncio
import uuid
from typing import Dict, Any, Optional
from .workflows import NODES


class GraphEngine:
    def __init__(self):
        # storing all the runs here
        self.runs: Dict[str, Dict[str, Any]] = {}

    async def run_graph(self, graph_id: str, graph_def: Dict[str, Any], initial_state: Dict[str, Any]):
        # generate unique run id
        run_id = str(uuid.uuid4())
        run = {
            "id": run_id,
            "state": dict(initial_state),
            "log": [],
            "status": "running",
            "current_node": None,
        }
        self.runs[run_id] = run
        
        # get nodes from graph
        nodes = graph_def.get("nodes", {})
        if not nodes:
            run["status"] = "failed"
            run["log"].append("empty graph")
            return run
            
        # start from first node
        start_node = list(nodes.keys())[0]
        next_node = start_node

        try:
            # keep running until no more nodes
            while next_node:
                run["current_node"] = next_node
                run["log"].append(f"running {next_node}")
                
                # find the node function
                node_fn = NODES.get(next_node)
                if node_fn is None:
                    run["log"].append(f"node {next_node} not found")
                    break
                
                # execute node (check if async or not)
                res = await node_fn(run["state"]) if asyncio.iscoroutinefunction(node_fn) else node_fn(run["state"])
                
                # check what node returned
                if isinstance(res, dict) and res.get("next"):
                    next_node = res.get("next")
                else:
                    # use edges to find next node
                    edges = graph_def.get("edges", {})
                    edge = edges.get(next_node)
                    
                    if not edge:
                        next_node = None
                    else:
                        # handle pipe separated edges
                        next_node = edge.split("|")[0]
                
                # small delay for async
                await asyncio.sleep(0)

            run["status"] = "finished"
            run["log"].append("finished run")
        except Exception as e:
            # something went wrong
            run["status"] = "error"
            run["log"].append(str(e))
            
        return run

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        # retrieve run by id
        return self.runs.get(run_id)