import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from uuid import uuid4

from runner import run

app = FastAPI()
load_dotenv()

volume_path = os.getenv("VOLUME_PATH")


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class CreatePayload(BaseModel):
    code: str
    requirements: str


class TaskResult(BaseModel):
    code: str
    requirements: str


async def process_task(task_id: str, code: str, requirements: str):
    python_file_path = os.path.join(volume_path, f"{task_id}.py")
    requirements_file_path = os.path.join(volume_path, f"{task_id}.txt")
    status_file_path = os.path.join(volume_path, f"{task_id}.status")

    with open(status_file_path, "w") as f:
        f.write(TaskStatus.PENDING)

    with open(python_file_path, "w") as f:
        f.write(code)

    with open(requirements_file_path, "w") as f:
        f.write(requirements)

    result = run(python_file_path, requirements_file_path)

    with open(status_file_path, "w") as f:
        if result:
            f.write(TaskStatus.COMPLETED)
        else:
            f.write(TaskStatus.ERROR)


@app.post("/create")
async def create_task(payload: CreatePayload, background_tasks: BackgroundTasks):
    task_id = str(uuid4())
    background_tasks.add_task(process_task, task_id, payload.code, payload.requirements)
    return {"task_id": task_id}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status_file_path = os.path.join(volume_path, f"{task_id}.status")
    if not os.path.exists(status_file_path):
        raise HTTPException(status_code=404, detail="Task not found")
    with open(status_file_path) as f:
        return f.read()


@app.get("/result/{task_id}", response_model=TaskResult)
async def get_result(task_id: str):
    python_file_path = os.path.join(volume_path, f"{task_id}.py")
    requirements_file_path = os.path.join(volume_path, f"{task_id}.txt")
    if not os.path.exists(python_file_path) or not os.path.exists(requirements_file_path):
        raise HTTPException(status_code=404, detail="Task not found")
    with open(python_file_path) as f:
        code = f.read()
    with open(requirements_file_path) as f:
        requirements = f.read()
    return TaskResult(code=code, requirements=requirements)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
