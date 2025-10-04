# FAST MCP Server with Google Gemini Integration

## 🎥 Demo Video

Watch the FastMCP Task demonstration video:

**[📹 Download and Watch: FastMCP_Task.mp4](FastMCP_Task.mp4)**

*Complete demonstration of the MCP server functionality*

> **💡 Tip**: Click the link above to download and view the video. For the best viewing experience, download the file and open it with your preferred video player.

---

A comprehensive Model Context Protocol (MCP) server demonstration featuring FastAPI, Excel-based To-Do list management, and Google Gemini CLI integration.

## 🚀 Features

- **FastAPI MCP Server** running on port 5000
- **Excel-based To-Do list management** with `tasks.xlsx`
- **Google Gemini CLI integration** for AI-powered responses
- **Comprehensive logging** with `query_log.json`
- **CLI helper script** for easy interaction
- **Production-ready code** with proper error handling

## 📁 Project Structure

```
FAST_MCP/
├── server.py              # FastAPI MCP server
├── requirements.txt       # Python dependencies
├── mcp_cli.sh            # CLI helper script
├── tasks.xlsx            # To-Do list Excel file
├── query_log.json        # Request/response logs
├── create_sample_data.py  # Script to generate sample data
└── README.md             # This file
```

## 🛠️ Setup Instructions

### 1. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Sample Data (if needed)

```bash
python create_sample_data.py
```

### 4. Install Gemini CLI (Optional)

To use the Gemini integration, install the Google Gemini CLI:

```bash
# Install Gemini CLI (follow official Google documentation)
# This is optional - the server will work without it
```

## 🚀 Running the Server

### Start the MCP Server

```bash
python server.py
```

The server will be available at:
- **API Server**: http://localhost:5000
- **Interactive Docs**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/health

## 📋 API Endpoints

### 1. Tasks Management

**GET/POST** `/tasks`

Query To-Do items based on status:

```bash
# Using curl
curl -X POST "http://localhost:5000/tasks" \
     -H "Content-Type: application/json" \
     -d '{"query": "pending"}'

# Available queries: "pending", "done", "all", "in_progress"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Complete project documentation",
      "description": "Write comprehensive documentation...",
      "status": "pending",
      "priority": "high",
      "assigned_to": "John Doe",
      "created_date": "2024-01-15",
      "due_date": "2024-01-20"
    }
  ],
  "count": 1,
  "query": "pending"
}
```

### 2. Gemini Integration

**POST** `/gemini`

Send prompts to Google Gemini CLI:

```bash
# Using curl
curl -X POST "http://localhost:5000/gemini" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What is machine learning?"}'
```

**Response:**
```json
{
  "success": true,
  "response": "Machine learning is a subset of artificial intelligence...",
  "error": null
}
```

### 3. Health Check

**GET** `/health`

Check server status and loaded data:

```bash
curl http://localhost:5000/health
```

### 4. Query Logs

**GET** `/logs`

View all logged requests and responses:

```bash
curl http://localhost:5000/logs
```

## 🖥️ CLI Helper Script

The `mcp_cli.sh` script provides easy access to all MCP tools:

### Basic Usage

```bash
# List available tools
./mcp_cli.sh list

# Run MCP tools
./mcp_cli.sh run <tool_name> <arguments>

# Direct commands
./mcp_cli.sh tasks <query>
./mcp_cli.sh gemini "<prompt>"
./mcp_cli.sh health
./mcp_cli.sh logs
```

### Examples

```bash
# List all available MCP tools
./mcp_cli.sh list

# Get pending tasks
./mcp_cli.sh tasks pending

# Get completed tasks
./mcp_cli.sh tasks done

# Get all tasks
./mcp_cli.sh tasks all

# Send prompt to Gemini
./mcp_cli.sh gemini "Explain quantum computing"

# Check server health
./mcp_cli.sh health

# View query logs
./mcp_cli.sh logs
```

## 📊 Sample Data

The `tasks.xlsx` file contains sample To-Do items with the following structure:

| Column | Description | Example |
|--------|-------------|---------|
| id | Unique identifier | 1, 2, 3... |
| title | Task title | "Complete project documentation" |
| description | Detailed description | "Write comprehensive documentation..." |
| status | Task status | "pending", "done", "in_progress" |
| priority | Task priority | "high", "medium", "low" |
| assigned_to | Assigned person | "John Doe" |
| created_date | Creation date | "2024-01-15" |
| due_date | Due date | "2024-01-20" |

## 📝 Logging

All requests and responses are automatically logged to `query_log.json`:

```json
[
  {
    "timestamp": "2024-01-17T10:30:00.000Z",
    "endpoint": "/tasks",
    "request": {"query": "pending"},
    "response": {
      "success": true,
      "data": [...],
      "count": 3,
      "query": "pending"
    }
  }
]
```

## 🧪 Testing the Application

### 1. Start the Server

```bash
python server.py
```

### 2. Test Tasks Endpoint

```bash
# Test in another terminal
./mcp_cli.sh tasks pending
./mcp_cli.sh tasks done
./mcp_cli.sh tasks all
```

### 3. Test Gemini Integration

```bash
# Test Gemini (requires Gemini CLI to be installed)
./mcp_cli.sh gemini "What is artificial intelligence?"
```

### 4. Check Logs

```bash
./mcp_cli.sh logs
```

## 🔧 Configuration

### Server Configuration

- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5000
- **CORS**: Enabled for all origins
- **Logging**: INFO level with timestamps

### Gemini CLI Configuration

The server expects the `gemini` command to be available in the system PATH. Configure your Gemini CLI according to Google's official documentation.

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 5000 is available
   - Ensure all dependencies are installed
   - Check Python version (3.8+ required)

2. **Tasks not loading**
   - Ensure `tasks.xlsx` exists in the project directory
   - Check file permissions
   - Run `python create_sample_data.py` to create sample data

3. **Gemini CLI not working**
   - Install and configure Gemini CLI
   - Check if `gemini` command is available in PATH
   - Verify API credentials

4. **CLI script not working**
   - Ensure script is executable: `chmod +x mcp_cli.sh`
   - Check if server is running
   - Verify curl is installed

### Debug Mode

Run the server with debug logging:

```bash
python server.py --log-level debug
```

## 📈 Performance

- **FastAPI**: High-performance async framework
- **Pandas**: Efficient Excel file processing
- **Subprocess**: Non-blocking Gemini CLI calls
- **JSON Logging**: Structured logging for analysis

## 🔒 Security Considerations

- CORS is enabled for development (restrict in production)
- Input validation with Pydantic models
- Error handling prevents information leakage
- Timeout protection for external CLI calls

## 🚀 Production Deployment

For production deployment:

1. **Environment Variables**: Use environment variables for configuration
2. **CORS**: Restrict CORS origins to your domain
3. **Logging**: Configure proper log rotation
4. **Monitoring**: Add health checks and monitoring
5. **Security**: Implement authentication and rate limiting

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🎯 Demo Script

For a complete demonstration, run these commands in sequence:

```bash
# 1. Start the server
python server.py &

# 2. Wait a moment for server to start
sleep 3

# 3. Test the CLI
./mcp_cli.sh list
./mcp_cli.sh tasks pending
./mcp_cli.sh tasks done
./mcp_cli.sh health

# 4. Test Gemini (if installed)
./mcp_cli.sh gemini "Hello, how are you?"

# 5. Check logs
./mcp_cli.sh logs

# 6. Stop the server
pkill -f "python server.py"
```

This demonstrates a complete MCP server with To-Do list management and AI integration! 🎉# FAST_MCP
