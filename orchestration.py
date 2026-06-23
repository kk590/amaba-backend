"""
AMABA Multi-Agent Orchestration System
Manages multiple specialized agents for autonomous browser automation

Compatible with smolagents>=1.8 (where InferenceClientModel replaced the
deprecated HfApiModel). Note: the `ManagedAgent` wrapper class was removed
from smolagents in later versions - agents are now passed directly as
managed agents as long as they have a `name` and `description` set.
"""

from smolagents import CodeAgent
from smolagents import InferenceClientModel
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# =========================
# MODELS
# =========================
ceo_model = InferenceClientModel(
    model_id="Qwen/Qwen3-8B-Instruct"
)
browser_model = InferenceClientModel(
    model_id="microsoft/Phi-4-mini-instruct"
)
recovery_model = InferenceClientModel(
    model_id="deepseek-ai/DeepSeek-R1"
)
debug_model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-3B-Instruct"
)
critique_model = InferenceClientModel(
    model_id="microsoft/Phi-4-mini-instruct"
)

# =========================
# IMPORT TOOLS
# =========================
try:
    from browser_tools import (
        open_url,
        click,
        fill,
        press,
        scroll,
        extract_text,
        take_screenshot,
        verify_url,
        verify_text_exists,
        retry_action,
        refresh_page
    )
    TOOLS_AVAILABLE = True
except ImportError:
    logger.warning("browser_tools not available - running in stub mode")
    TOOLS_AVAILABLE = False
    # Stub tools for development/testing
    open_url = None
    click = None
    fill = None
    press = None
    scroll = None
    extract_text = None
    take_screenshot = None
    verify_url = None
    verify_text_exists = None
    retry_action = None
    refresh_page = None


class OrchestratorConfig:
    """Configuration for the orchestration system"""
    def __init__(self):
        self.max_steps = 15
        self.timeout = 300  # 5 minutes
        self.retry_attempts = 3
        self.enable_logging = True


class OrchestrationResult:
    """Result of a task orchestration"""
    def __init__(self, task_id: str, success: bool, result: Any, error: Optional[str] = None):
        self.task_id = task_id
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.now().isoformat()
        self.duration = 0


class AgentOrchestrator:
    """
    Main orchestrator managing specialized agents for autonomous browser automation.
    Follows a CEO -> Specialized Managers architecture.

    In smolagents>=1.8, an agent becomes a "managed agent" simply by being
    constructed with a `name` and `description`, and then passed into a
    parent agent's `managed_agents` list. There is no separate wrapper class.
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.agents: Dict[str, CodeAgent] = {}
        self.execution_history = []
        self._initialize_agents()
        logger.info("AgentOrchestrator initialized successfully")

    def _initialize_agents(self):
        """Initialize all specialized agent managers"""
        logger.info("Initializing agent managers...")

        # Browser Manager
        browser_tools = [
            open_url, click, fill, press, scroll, extract_text, take_screenshot
        ] if TOOLS_AVAILABLE else []

        self.agents['browser'] = CodeAgent(
            tools=browser_tools,
            model=browser_model,
            name="browser_manager",
            description="""
            Responsible for browser navigation,
            interaction, extraction and page operations.
            """,
            max_steps=self.config.max_steps
        )

        # Recovery Manager
        recovery_tools = [retry_action, refresh_page] if TOOLS_AVAILABLE else []

        self.agents['recovery'] = CodeAgent(
            tools=recovery_tools,
            model=recovery_model,
            name="recovery_manager",
            description="""
            Handles browser failures,
            retries and workflow recovery.
            """,
            max_steps=self.config.max_steps
        )

        # Debug Manager
        self.agents['debug'] = CodeAgent(
            tools=[],
            model=debug_model,
            name="debug_manager",
            description="""
            Debugs automation failures,
            analyzes errors and generates fixes.
            """,
            max_steps=self.config.max_steps
        )

        # Critique Manager
        critique_tools = [verify_url, verify_text_exists] if TOOLS_AVAILABLE else []

        self.agents['critique'] = CodeAgent(
            tools=critique_tools,
            model=critique_model,
            name="critique_manager",
            description="""
            Validates workflow output,
            checks task completion,
            detects hallucinations.
            """,
            max_steps=self.config.max_steps
        )

        # CEO Orchestrator - sub-agents are passed directly as managed_agents
        # since each already has a `name` and `description`.
        managed_agents_list = [
            self.agents['browser'],
            self.agents['recovery'],
            self.agents['debug'],
            self.agents['critique'],
        ]

        self.ceo = CodeAgent(
            tools=[],
            managed_agents=managed_agents_list,
            model=ceo_model,
            name="ceo_orchestrator",
            description="Multi-agent orchestrator",
            max_steps=self.config.max_steps
        )

        logger.info("\u2705 All agents initialized")
        logger.info(f"   - Browser Manager: {'ready' if TOOLS_AVAILABLE else 'stub mode'}")
        logger.info(f"   - Recovery Manager: {'ready' if TOOLS_AVAILABLE else 'stub mode'}")
        logger.info("   - Debug Manager: ready")
        logger.info(f"   - Critique Manager: {'ready' if TOOLS_AVAILABLE else 'stub mode'}")
        logger.info("   - CEO Orchestrator: ready")

    def run_task(self, task: str, task_id: Optional[str] = None) -> OrchestrationResult:
        """
        Execute a task through the orchestration system.

        Args:
            task: Task description/instruction
            task_id: Optional task identifier

        Returns:
            OrchestrationResult: Execution result
        """
        task_id = task_id or f"task_{datetime.now().timestamp()}"
        start_time = datetime.now()

        logger.info(f"[{task_id}] Starting task execution: {task[:50]}...")

        try:
            # Execute through CEO
            result = self.ceo.run(task)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            execution_result = OrchestrationResult(
                task_id=task_id,
                success=True,
                result=result
            )
            execution_result.duration = duration

            logger.info(f"[{task_id}] Task completed successfully in {duration:.2f}s")
            self.execution_history.append(execution_result)

            return execution_result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            error_msg = str(e)
            logger.error(f"[{task_id}] Task failed: {error_msg}")

            execution_result = OrchestrationResult(
                task_id=task_id,
                success=False,
                result=None,
                error=error_msg
            )
            execution_result.duration = duration

            self.execution_history.append(execution_result)

            return execution_result

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            'ceo': 'active',
            'agents': list(self.agents.keys()),
            'execution_history': len(self.execution_history),
            'timestamp': datetime.now().isoformat()
        }

    def get_execution_history(self, limit: int = 10) -> list:
        """Get recent execution history"""
        history = []
        for result in self.execution_history[-limit:]:
            history.append({
                'task_id': result.task_id,
                'success': result.success,
                'duration': result.duration,
                'timestamp': result.timestamp,
                'error': result.error
            })
        return history


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(config: Optional[OrchestratorConfig] = None) -> AgentOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(config)
    return _orchestrator


def init_orchestrator(config: Optional[OrchestratorConfig] = None):
    """Initialize the global orchestrator"""
    global _orchestrator
    _orchestrator = AgentOrchestrator(config)


# =========================
# ENTRYPOINT FOR CLI
# =========================
if __name__ == "__main__":
    import sys

    # Initialize orchestrator
    orchestrator = get_orchestrator()

    # Get task from input or command line
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("AMABA Task > ")

    # Execute task
    result = orchestrator.run_task(task)

    # Output result
    print(f"\n{'='*60}")
    print(f"Task ID: {result.task_id}")
    print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Duration: {result.duration:.2f}s")
    if result.error:
        print(f"Error: {result.error}")
    if result.result:
        print(f"Result:\n{result.result}")
    print(f"{'='*60}\n")
