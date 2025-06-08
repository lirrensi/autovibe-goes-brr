import sys
import os

from mcp.server.fastmcp import FastMCP

from autovibe import AutoVibe, ToolReturn

# cause that damn thing lot loading env.
from dotenv import load_dotenv
load_dotenv()

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

mcp = FastMCP("AutoVibe")

@mcp.tool(description="Generates python code and automatically runs it with auto-retry and safety checks")
def auto_vibe(
      content: str, 
      max_retry: int = 1,
      auto_check: bool = False,
      exec_timeout: int = 120,
      ) -> dict:
    """Call VibeApi"""

    sys.stderr.write(f'autovibe called => {content}\n')

    autovibe = AutoVibe(
        max_retry=max_retry,
        auto_check=auto_check,
        exec_timeout=exec_timeout,
        )
    result = autovibe.as_tool(content)

    sys.stderr.write(f'autovibe result => {result}\n')


    # Handle errors by raising an exception, which FastMCP will convert to proper MCP error format
    if result.is_error:
        raise Exception(result.content)
    
    return result.content
    

if __name__ == "__main__":
    mcp.run()