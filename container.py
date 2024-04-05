import os

import docker
from docker import DockerClient


class Container:
    container_paths = {
        "requirements": "/app/requirements.txt",
        "python": "/app/test.py",
    }

    client: DockerClient = None

    def __new__(cls, *args, **kwargs):
        if cls.client is None:
            cls.client = docker.from_env()
        return super().__new__(cls)

    def __init__(self, requirements_path, python_path, version="3.11"):
        self.requirements_path = os.path.abspath(requirements_path)
        self.python_path = os.path.abspath(python_path)
        self.python_file = open(self.python_path, "r+")
        self.version = version
        self.container = None

    def dispose(self):
        if self.container:
            self.container.stop()
            self.container.remove()

        self.python_file.close()

    def __enter__(self):
        volumes = {
            self.requirements_path: {'bind': self.container_paths["requirements"], 'mode': 'ro'},
            self.python_path: {'bind': self.container_paths["python"], 'mode': 'ro'},
        }

        self.container = self.client.containers.run(f"python:{self.version}",
                                                    command="tail -f /dev/null",
                                                    volumes=volumes,
                                                    working_dir="/app",
                                                    detach=True)

        exec_log = self.container.exec_run(f"pip install -r {self.container_paths['requirements']}")
        if exec_log.exit_code != 0:
            self.dispose()
            raise Exception(f"Failed to install requirements.\n{exec_log.output.decode()}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()
        return False

    def run_python(self):
        exec_log = self.container.exec_run(f"python {self.container_paths['python']}")
        return exec_log.output.decode(), exec_log.exit_code

    @property
    def python_src(self):
        return self.python_file.readlines()

    @python_src.setter
    def python_src(self, value: str):
        self.python_file.seek(0)
        self.python_file.writelines(value)
        self.python_file.truncate()
        self.python_file.flush()
