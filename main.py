from container import Container


def main():
    python_file_path = "test/test.py"
    with Container("test/requirements.txt", python_file_path) as container:
        # Run the Python script inside the container
        output, status = container.run_python()

        # Capture the output
        print("Python script output:", output, "Exit status:", status)


if __name__ == "__main__":
    main()
