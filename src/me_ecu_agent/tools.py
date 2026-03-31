"""Tools module."""

from langchain_core.tools.retriever import create_retriever_tool


def get_agent_tools(store_700, store_800):
    """
    Creates and returns a list of tools for the agent to use, based on the provided vector stores.
    """
    tools = []

    if store_700:
        retriever_700 = store_700.as_retriever(search_kwargs={"k": 3})
        tool_700 = create_retriever_tool(
            retriever_700,
            "search_ecu_700",
            "Searches and returns information about the ECU-700 series (including the ECU-750). Use this tool when the user asks questions regarding older/legacy ECU-700 series."
        )
        tools.append(tool_700)

    if store_800:
        retriever_800 = store_800.as_retriever(search_kwargs={"k": 4})
        tool_800 = create_retriever_tool(
            retriever_800,
            "search_ecu_800",
            "Searches and returns information about the ECU-800 series (including the ECU-850 and ECU-850b). Use this tool when the user asks questions regarding newer ECU-800 series."
        )
        tools.append(tool_800)

    return tools
