from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from app.agents.state import AgentState
from app.agents.planner import planner_node
from app.agents.workers.pattern_agent import pattern_node
from app.agents.workers.anomaly_agent import anomaly_node
from app.agents.workers.goal_agent import goal_node
from app.agents.workers.subscription_agent import subscription_node
from app.agents.workers.transfer_agent import transfer_node
from app.agents.fact_checker import fact_checker_node
from app.agents.writer import writer_node
from app.mcp.memory_client import load_memory, save_memory


async def load_memory_node(state: AgentState) -> AgentState:
    memory = await load_memory(state["user_id"])
    return {"memory_context": memory}


async def save_memory_node(state: AgentState) -> AgentState:
    await save_memory(state["user_id"], state["memory_updates"])
    return {}


def route_to_workers(state: AgentState):
    """Fan out to all 4 parallel workers."""
    return [
        Send("pattern_worker", state),
        Send("anomaly_worker", state),
        Send("goal_worker", state),
        Send("subscription_worker", state),
    ]


def build_pipeline() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("load_memory", load_memory_node)
    graph.add_node("planner", planner_node)
    graph.add_node("transfer_detector", transfer_node)
    graph.add_node("pattern_worker", pattern_node)
    graph.add_node("anomaly_worker", anomaly_node)
    graph.add_node("goal_worker", goal_node)
    graph.add_node("subscription_worker", subscription_node)
    graph.add_node("fact_checker", fact_checker_node)
    graph.add_node("writer", writer_node)
    graph.add_node("save_memory", save_memory_node)

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "planner")
    graph.add_edge("planner", "transfer_detector")
    graph.add_conditional_edges("transfer_detector", route_to_workers)
    graph.add_edge("pattern_worker", "fact_checker")
    graph.add_edge("anomaly_worker", "fact_checker")
    graph.add_edge("goal_worker", "fact_checker")
    graph.add_edge("subscription_worker", "fact_checker")
    graph.add_edge("fact_checker", "writer")
    graph.add_edge("writer", "save_memory")
    graph.add_edge("save_memory", END)

    return graph.compile()


pipeline = build_pipeline()
