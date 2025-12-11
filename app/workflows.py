from typing import Dict, Any
from .tools import TOOLS


async def extract_functions(state: Dict[str, Any]):
    # extract function definitions from code
    code = state.get("code", "")
    # split by "def " and get first line of each
    funcs = [p.split("\n", 1)[0] if "\n" in p else p for p in code.split("def ") if p.strip()]
    state["functions"] = funcs
    state.setdefault("log", []).append("extracted {} functions".format(len(funcs)))
    return {"next": "check_complexity"}


async def check_complexity(state: Dict[str, Any]):
    # measure code complexity
    code = state.get("code", "")
    res = TOOLS["measure_complexity"](code)
    state["complexity"] = res["complexity"]
    state.setdefault("log", []).append(f"measured complexity={res['complexity']}")
    
    # branch based on complexity
    if res["complexity"] > state.get("complexity_threshold", 50):
        return {"next": "detect_issues"}
    return {"next": "suggest_improvements"}


async def detect_issues(state: Dict[str, Any]):
    # detect code smells and issues
    code = state.get("code", "")
    res = TOOLS["detect_smells"](code)
    state["issues"] = res["issues"]
    state.setdefault("log", []).append(f"detected issues={res['issues']}")
    
    # reduce quality score based on issues found
    qs = state.get("quality_score", 100)
    qs -= res["issues"] * 10
    state["quality_score"] = qs
    return {"next": "suggest_improvements"}


async def suggest_improvements(state: Dict[str, Any]):
    # generate improvement suggestions
    suggestions = []
    if state.get("issues", 0) > 0:
        suggestions.append("Remove TODOs and prints.")
    if state.get("complexity", 0) > 50:
        suggestions.append("Refactor long functions into smaller ones.")
    
    state["suggestions"] = suggestions
    state.setdefault("log", []).append("suggested {} improvements".format(len(suggestions)))
    
    # check if quality is good enough
    if state.get("quality_score", 100) >= state.get("quality_threshold", 90):
        return {"next": None}  # done
    
    # simulate applying improvements
    state["quality_score"] = state.get("quality_score", 100) + 20
    state.setdefault("log", []).append("applied suggestions, improved quality to {}".format(state["quality_score"]))
    return {"next": "check_complexity"}  # loop back


# map node names to their functions
NODES = {
    "extract": extract_functions,
    "check_complexity": check_complexity,
    "detect_issues": detect_issues,
    "suggest_improvements": suggest_improvements,
}


# default graph template
GRAPH_TEMPLATE = {
    "nodes": {name: name for name in NODES.keys()},
    "edges": {
        "extract": "check_complexity",
        "check_complexity": "detect_issues|suggest_improvements",  # conditional branching
        "detect_issues": "suggest_improvements",
        "suggest_improvements": "check_complexity",  # loop back
    },
}