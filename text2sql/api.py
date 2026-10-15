import os

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from text2sql.core import TextSQL
from text2sql.task_runtime import TaskStatus, TaskStore


app = FastAPI(title="Text-to-SQL Agent Harness")
task_store = TaskStore()


class CreateTaskRequest(BaseModel):
    question: str = Field(min_length=1)


def run_task(task_id: str) -> None:
    task = task_store.get(task_id)
    if task is None:
        return

    task_store.set_status(task_id, TaskStatus.RUNNING)

    try:
        database_url = os.getenv("TEXT2SQL_DB", "sqlite:///example.db")
        model = os.getenv("TEXT2SQL_MODEL", "openai:gpt-4o")

        engine = TextSQL(database_url, model=model)
        result = engine.ask(task.question)

        task_store.set_status(
            task_id,
            TaskStatus.SUCCEEDED,
            result=jsonable_encoder(result),
        )
    except Exception as exc:
        task_store.set_status(
            task_id,
            TaskStatus.FAILED,
            error=str(exc),
        )


@app.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
):
    task = task_store.create(request.question)
    background_tasks.add_task(run_task, task.task_id)
    return jsonable_encoder(task)


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    task = task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return jsonable_encoder(task)