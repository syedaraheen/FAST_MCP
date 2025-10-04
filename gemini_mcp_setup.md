# Connecting Gemini CLI to Your MCP Server

## Method 1: Direct MCP Connection

Your MCP server is running on `http://localhost:5001`. To connect Gemini CLI to it:

```bash
# In a new terminal, navigate to your project directory
cd /home/raheen/FAST_MCP

# Connect Gemini CLI to your MCP server
gemini mcp connect http://localhost:5001
```

## Method 2: Using Gemini CLI with MCP Tools

You can also use Gemini CLI to interact with your MCP tools directly:

```bash
# List available MCP tools
gemini mcp list

# Use your MCP server's tasks tool
gemini mcp call tasks --query="pending"
gemini mcp call tasks --query="done"
gemini mcp call tasks --query="all"
```

## Method 3: Interactive Mode with MCP

Start Gemini CLI in interactive mode with MCP support:

```bash
gemini --experimental-acp
```

This will start Gemini CLI with MCP support, and you can then ask it to use your local MCP server.

## Testing the Connection

Once connected, you can ask Gemini CLI things like:

- "Show me all pending tasks from my MCP server"
- "What tasks are completed?"
- "List all my tasks"
- "Help me organize my tasks"

The Gemini CLI will use your MCP server's `/tasks` endpoint to fetch the data from your Excel file.

## Server Endpoints Available

Your MCP server provides these endpoints:
- `GET /health` - Server health check
- `POST /tasks` - Get tasks (pending/done/all)
- `POST /gemini` - Send prompts to Gemini CLI
- `GET /logs` - View all query logs

## Example Usage

```bash
# Start your MCP server (already running)
python server.py

# In another terminal, connect Gemini CLI
gemini mcp connect http://localhost:5001

# Now you can ask Gemini to use your tasks
gemini "Show me my pending tasks"
gemini "What tasks are due today?"
gemini "Help me prioritize my tasks"
```