import json
import asyncio
from typing import Dict, Any

from smolagents import Tool


tasks_db: Dict[str, Dict[str, Any]] = {}
logs_db: Dict[str, list] = {}
artifacts_db: Dict[str, Dict[str, Any]] = {}


def _now():
    return asyncio.get_event_loop().time()


class CreateTaskTool(Tool):
    name = "create_task"
    description = "Create a new task."
    inputs = {
        "description": {"type": "string", "description": "Task description"},
        "priority": {"type": "string", "description": "Task priority (low, medium, high)"},
    }
    output_type = "string"

    async def forward(self, description: str = "", priority: str = "medium") -> str:
        import random
        import time

        task_id = f"task_{int(time.time())}_{random.randint(1000,9999)}"
        tasks_db[task_id] = {
            "id": task_id,
            "created_at": _now(),
            "status": "pending",
            "steps": [],
            "data": {"description": description, "priority": priority},
            "updated_at": _now(),
        }
        logs_db[task_id] = []
        return f"Task created successfully with ID: {task_id}"


class CreateStepTool(Tool):
    name = "create_step"
    description = "Create a new step under a task."
    inputs = {
        "task_id": {"type": "string", "description": "Parent task id"},
        "description": {"type": "string", "description": "Step description"},
        "action": {"type": "string", "description": "Action to perform"},
    }
    output_type = "string"

    async def forward(self, task_id: str, description: str = "", action: str = "") -> str:
        if task_id not in tasks_db:
            return f"Error creating step: unknown task_id {task_id}"
        import random
        import time

        step_id = f"step_{int(time.time())}_{random.randint(1000,9999)}"
        tasks_db[task_id]["steps"].append(
            {
                "id": step_id,
                "task_id": task_id,
                "status": "pending",
                "created_at": _now(),
                "data": {"description": description, "action": action},
                "updated_at": _now(),
            }
        )
        return f"Step created successfully with ID: {step_id} for task {task_id}"


class SaveLogTool(Tool):
    name = "save_log"
    description = "Save a log entry for a task."
    inputs = {
        "task_id": {"type": "string", "description": "Task id"},
        "message": {"type": "string", "description": "Log message"},
        "level": {"type": "string", "description": "Log level"},
    }
    output_type = "string"

    async def forward(self, task_id: str, message: str, level: str = "info") -> str:
        logs_db.setdefault(task_id, [])
        logs_db[task_id].append({"timestamp": _now(), "level": level, "message": message})
        return f"Log saved successfully for task {task_id}: {message}"


class GetTaskStateTool(Tool):
    name = "get_task_state"
    description = "Get task state as JSON string."
    inputs = {"task_id": {"type": "string", "description": "Task id"}}
    output_type = "string"

    async def forward(self, task_id: str) -> str:
        if task_id not in tasks_db:
            return json.dumps({"error": f"Task {task_id} not found"})
        return json.dumps(tasks_db[task_id], indent=2, default=str)


class UpdateTaskStateTool(Tool):
    name = "update_task_state"
    description = "Update task status."
    inputs = {
        "task_id": {"type": "string", "description": "Task id"},
        "status": {"type": "string", "description": "New status"},
    }
    output_type = "string"

    async def forward(self, task_id: str, status: str) -> str:
        if task_id not in tasks_db:
            return f"update_task_state: unknown task_id {task_id}"
        tasks_db[task_id]["status"] = status
        tasks_db[task_id]["updated_at"] = _now()
        return f"Task {task_id} status updated to {status}"


class UpdateStepStatusTool(Tool):
    name = "update_step_status"
    description = "Update step status by step id."
    inputs = {
        "step_id": {"type": "string", "description": "Step id"},
        "status": {"type": "string", "description": "pending/running/completed/failed"},
    }
    output_type = "string"

    async def forward(self, step_id: str, status: str) -> str:
        valid = {"pending", "running", "completed", "failed"}
        if status not in valid:
            return f"Invalid status. Valid options are: {sorted(valid)}"
        for _task_id, task in tasks_db.items():
            for step in task.get("steps", []):
                if step.get("id") == step_id:
                    step["status"] = status
                    step["updated_at"] = _now()
                    return f"Step {step_id} status updated to {status} successfully"
        return f"Error updating step status: unknown step_id {step_id}"


class GetExecutionLogsTool(Tool):
    name = "get_execution_logs"
    description = "Get execution logs for a task as JSON string."
    inputs = {"task_id": {"type": "string", "description": "Task id"}}
    output_type = "string"

    async def forward(self, task_id: str) -> str:
        if task_id in logs_db:
            return json.dumps(logs_db[task_id], indent=2, default=str)
        return json.dumps({"error": f"No logs found for task {task_id}"})


class AssignManagerTool(Tool):
    name = "assign_manager"
    description = "Assign a manager to a task."
    inputs = {
        "task_id": {"type": "string", "description": "Task id"},
        "manager": {"type": "string", "description": "Manager name"},
    }
    output_type = "string"

    async def forward(self, task_id: str, manager: str = "") -> str:
        if not task_id:
            return "assign_manager: missing task_id"
        tasks_db.setdefault(task_id, {"id": task_id, "steps": [], "status": "pending", "data": {}})
        tasks_db[task_id].setdefault("data", {})
        tasks_db[task_id]["data"]["manager"] = manager
        tasks_db[task_id]["updated_at"] = _now()
        return f"Assigned manager '{manager}' to task {task_id}"


class RequestApprovalTool(Tool):
    name = "request_approval"
    description = "Request approval (auto-approves in this demo)."
    inputs = {"message": {"type": "string", "description": "Approval message"}}
    output_type = "string"

    async def forward(self, message: str = "") -> str:
        return f"approved: {message}"


class MarkTaskCompleteTool(Tool):
    name = "mark_task_complete"
    description = "Mark task as completed."
    inputs = {"task_id": {"type": "string", "description": "Task id"}}
    output_type = "string"

    async def forward(self, task_id: str) -> str:
        if task_id not in tasks_db:
            return f"mark_task_complete: unknown task_id {task_id}"
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["updated_at"] = _now()
        return f"Task {task_id} marked completed"


class MarkTaskFailedTool(Tool):
    name = "mark_task_failed"
    description = "Mark task as failed."
    inputs = {
        "task_id": {"type": "string", "description": "Task id"},
        "reason": {"type": "string", "description": "Failure reason"},
    }
    output_type = "string"

    async def forward(self, task_id: str, reason: str = "") -> str:
        if task_id not in tasks_db:
            return f"mark_task_failed: unknown task_id {task_id}"
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["updated_at"] = _now()
        return f"Task {task_id} marked failed"


# Instantiate for main.py imports
create_task = CreateTaskTool()
create_step = CreateStepTool()
save_log = SaveLogTool()
get_task_state = GetTaskStateTool()
update_task_state = UpdateTaskStateTool()
update_step_status = UpdateStepStatusTool()
get_execution_logs = GetExecutionLogsTool()
assign_manager = AssignManagerTool()
request_approval = RequestApprovalTool()
mark_task_complete = MarkTaskCompleteTool()
mark_task_failed = MarkTaskFailedTool()

