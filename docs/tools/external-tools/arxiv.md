# arXiv

## Overview

Searches papers on arXiv

## Use cases

## Usage with ADK

```python
root_agent = Agent(
    # ...
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "arxiv-mcp-server",
                    ]
                ),
            ),
        )
    ],
)
```

## Sample code

```python
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = Agent(
    model='gemini-2.5-pro',
    name='root_agent',
    description='A helpful assistant for searching papers on arXiv',
    instruction='Help the user search for papers on arXiv',
    tools=[
    MCPToolset(
        connection_params=StdioConnectionParams(
            server_params = StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "arxiv-mcp-server",
                ]
            ),
        ),
    )
],
)
```

## Additional resources
