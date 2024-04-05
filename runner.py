from container import Container
from models.lama import Lama
from models.model import Model
from parser import parse_stack_trace, get_function_index

from dotenv import load_dotenv


def try_fix_code(container: Container, model: Model):
    while True:
        print("Running the code")
        output, status = container.run_python()

        if status == 0:
            return True

        stack_frames = parse_stack_trace(output)
        file_frames = filter(lambda f: f["file"] == container.container_paths["python"], stack_frames)
        frame = list(filter(lambda f: f["function"] is not None, file_frames))[0]

        if not frame:
            return False

        src = container.python_src
        function_start, function_end = get_function_index(src, frame)

        print(f"Error in {frame['function']} at line {frame['line'] + 1}")
        print(output)

        function_src = "".join(src[function_start:function_end])
        fixed_code = model.query(function_src, output)

        if not fixed_code:
            return False

        print("Fixed code:\n", fixed_code, "\n\n")

        if "def " + frame["function"] not in fixed_code:
            print("Function name changed. Skipping fix")
            model.feedback("Response rejected due to incorrect format. Please try again.")
            continue

        fixed_code = fixed_code if fixed_code.endswith("\n") else fixed_code + "\n"

        src = src[:function_start] + [fixed_code] + src[function_end:]
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
