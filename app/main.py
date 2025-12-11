from fastapi import FastAPI, HTTPException, BackgroundTasks
from .models import GraphCreate, GraphRunRequest
from .workflows import GRAPH_TEMPLATE
from .engine import GraphEngine
import uuid


app = FastAPI()
engine = GraphEngine()

# in-memory storage for graphs
GRAPHS = {}


@app.post("/graph/create")
async def create_graph(payload: GraphCreate):
    # create new graph with unique id
    graph_id = str(uuid.uuid4())
    GRAPHS[graph_id] = {"nodes": payload.nodes, "edges": payload.edges}
    return {"graph_id": graph_id}


@app.post("/graph/run")
async def run_graph(req: GraphRunRequest, background_tasks: BackgroundTasks):
    # check if graph exists
    graph_def = GRAPHS.get(req.graph_id)
    if graph_def is None:
        raise HTTPException(status_code=404, detail="graph not found")
    
    # add to background tasks
    task = background_tasks.add_task(_run_background, req.graph_id, graph_def, req.initial_state)
    
    # create placeholder run id for now
    placeholder_run_id = str(uuid.uuid4())
    engine.runs[placeholder_run_id] = {
        "id": placeholder_run_id, 
        "state": req.initial_state, 
        "log": ["queued"], 
        "status": "queued", 
        "current_node": None
    }
    return {"run_id": placeholder_run_id}


async def _run_background(graph_id, graph_def, initial_state):
    # actually run the graph in background
    run = await engine.run_graph(graph_id, graph_def, initial_state)
    # update the run in engine
    engine.runs[run["id"]] = run


@app.get("/graph/state/{run_id}")
async def get_state(run_id: str):
    # get run status and state
    run = engine.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "id": run_id, 
        "status": run.get("status"), 
        "state": run.get("state"), 
        "log": run.get("log"), 
        "current_node": run.get("current_node")
    }


@app.on_event("startup")
async def startup_event():
    # create default graph on startup
    default_id = str(uuid.uuid4())
    GRAPHS[default_id] = GRAPH_TEMPLATE
    print("registered default graph", default_id)