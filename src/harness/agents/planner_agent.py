import json

from harness.agents.base_agent import BaseAgent
from harness.config.agents.planner_instructions import PLAN_REQUIREMENT_INSTRUCTIONS
from harness.domain.message import Message
from harness.models.response import ModelResponse


class PlannerAgent(BaseAgent):
    def check_if_plan_needed(self, user_request: str, task_context: str | None = None) -> ModelResponse:
        if not user_request.strip():
            raise ValueError("User request is required.")

        request_content = f"User request:\n{user_request.strip()}"
        if task_context and task_context.strip():
            request_content = f"{request_content}\n\nRelevant task context:\n{task_context.strip()}"

        messages = [
            Message(role="system", type="system_instruction", content=PLAN_REQUIREMENT_INSTRUCTIONS),
            Message(role="user", type="user_message", content=request_content)
        ]
        response = self._model_client.generate(messages, tools=[])

        if response.tool_calls:
            raise ValueError("Plan requirement analysis must not call tools.")

        try:
            decision = json.loads(response.text)
        except json.JSONDecodeError as error:
            raise ValueError("Plan requirement analysis returned invalid JSON.") from error

        if not isinstance(decision, dict) or set(decision) != {"requires_plan"}:
            raise ValueError("Plan requirement analysis must return only requires_plan.")

        if not isinstance(decision["requires_plan"], bool):
            raise ValueError("requires_plan must be a boolean.")

        return ModelResponse(text=json.dumps(decision))

    def plan(self, task: str | None, task_context: str | None = None) -> Message:
        if task is None or not task.strip():
            return self.loop(task)

        decision = self.check_if_plan_needed(task, task_context)
        requires_plan = json.loads(decision.text)["requires_plan"]

        if not requires_plan:
            return Message(role="assistant", type="assistant_message", content=decision.text)

        planning_task = task
        if task_context and task_context.strip():
            planning_task = f"User request:\n{task.strip()}\n\nRelevant task context:\n{task_context.strip()}"

        return self.loop(planning_task)
