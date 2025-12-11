TOOLS = {}


def register_tool(name):
    # decorator to register tools
    def _decorator(fn):
        TOOLS[name] = fn
        return fn
    return _decorator


@register_tool("detect_smells")
def detect_smells(code: str):
    # simple code smell detection
    issues = 0
    if "TODO" in code:
        issues += 1
    if "print(" in code:
        issues += 1
    return {"issues": issues}


@register_tool("measure_complexity")
def measure_complexity(code: str):
    # basic complexity measurement based on function count
    return {"complexity": code.count("def ") * 10}