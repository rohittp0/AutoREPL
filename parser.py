import re
from typing import List, TypedDict, Tuple


class StackFrame(TypedDict):
    file: str
    line: int
    function: str | None


def parse_stack_trace(stack_trace: str) -> List[StackFrame]:
    stack_trace = stack_trace.split("\n")
    stack_trace = [line.strip() for line in stack_trace if line.strip()]
    stack_frames = []

    header = re.compile(r'File "(.*)", line (\d+), in (.*)')

    for line in stack_trace:
        match = header.match(line)
        if match:
            stack_frames.append({
                "file": match.group(1),
                "line": int(match.group(2)) - 1,
                "function": match.group(3) if match.group(3) != "<module>" else None,
            })

    return list(reversed(stack_frames))


def get_function_index(src: List[str], stack_frame: StackFrame) -> Tuple[int, int]:
    function_start = None
    function_end = None
    function_def = f"def {stack_frame['function']}("
    contained_line = stack_frame["line"]

    if contained_line >= len(src):
        raise ValueError("Line number out of bounds "+str(contained_line))

    # Find the start of the function by looking for the line that
    # matches the function name starting from the line and going up

    for i in range(contained_line, -1, -1):
        if function_def in src[i]:
            function_start = i
            break

    # Find the end of the function by looking for end of indentation starting from the line
    intended_indentation = src[function_start].index("def")

    for i in range(contained_line, len(src)):
        stripped = src[i].strip()
        if stripped and src[i].index(stripped) <= intended_indentation:
            function_end = i
            break

    return function_start, function_end or len(src)
