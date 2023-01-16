from fastapi import APIRouter, Request, HTTPException
from wmtf.wm.client import Client
import logging

router = APIRouter()


@router.get("/api/user", tags=["api"])
def get_user():
    return {}


@router.get("/api/report", tags=["api"])
def get_report():
    days = Client.report()
    return [d.dict() for d in days]


@router.get("/api/tasks", tags=["api"])
def get_tasks():
    tasks = Client.tasks()
    return [t.dict() for t in tasks]


@router.get("/api/task/{task_id}", tags=["api"])
def get_task(task_id: int):
    try:
        task = Client.task(id)
        return task.dict()
    except Exception:
        raise HTTPException(404, f"Task {id} not found")


@router.post("/api/clock", tags=["api"])
async def post_clock(request: Request):
    raise HTTPException(500)
