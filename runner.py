from container import Container
from models.lama import Lama
from parser import parse_stack_trace, get_function_index

from dotenv import load_dotenv


def try_fix_code(container, model):
    while True:
        output, status = container.run_python()

        if status == 0:
            return True

        stack_frames = parse_stack_trace(output)
        for frame in stack_frames:
            if frame["file"] == container.container_paths["python"]:
                src = container.python_src
                function_start, function_end = get_function_index(src, frame)

                print(f"Error in {frame['function']} at line {frame['line'] + 1}")

                function_src = "".join(src[function_start:function_end])
                fixed_code = model.query(function_src, output)

                if not fixed_code:
                    return False

                src = src[:function_start] + fixed_code.split("\n") + src[function_end:]
                container.python_src = src


def run(python_file_path, requirements_file_path):
    model = Lama(True)

    with Container(requirements_file_path, python_file_path) as container:
        ret = try_fix_code(container, model)

        if not ret:
            print("Failed to fix the code")
        else:
            print("Code fixed successfully")

        return ret


if __name__ == "__main__":
    load_dotenv()
    run("volume/test.py", "volume/requirements.txt")
