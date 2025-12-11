What this project does

This is a small FastAPI-based workflow engine that runs a series of steps in order.
Each step (called a node) is just a Python function that updates a shared dictionary called state.
The workflow can move forward, branch, or loop based on what the state contains.

A basic example workflow is included that pretends to analyze code by extracting functions, checking complexity, detecting issues, and giving suggestions.

How to run it
1. Install requirements
pip install fastapi uvicorn pydantic

2. Start the server
uvicorn app.main:app --reload --port 8000


The server will print a default graph_id you can use.

3. Open the API docs

Go to:

http://127.0.0.1:8000/docs


You can run everything from here.

4. Run the workflow

Use POST /graph/run with:

{
  "graph_id": "<printed_graph_id>",
  "initial_state": {
    "code": "def foo(): print('TODO')",
    "quality_score": 60,
    "quality_threshold": 90,
    "complexity_threshold": 50
  }
}

5. Check progress

Use:

GET /graph/state/{run_id}


to see the state, logs, and final output.
