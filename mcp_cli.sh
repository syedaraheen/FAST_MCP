#!/bin/bash

# MCP CLI Helper Script
# Provides easy access to MCP server endpoints

# FIXES APPLIED:
# 1. Enhanced HTTP error handling with status code checking
# 2. Improved JSON formatting with fallback to python3 -m json.tool
# 3. Added new 'pending' command for direct endpoint access
# 4. Better error reporting and user feedback
# 5. Proper exit codes for script failure conditions

SERVER_URL="http://localhost:5001"
LOG_FILE="query_log.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if server is running
check_server() {
    if ! curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
        print_error "MCP Server is not running at $SERVER_URL"
        print_info "Please start the server with: python server.py"
        exit 1
    fi
}

# Function to make HTTP requests with improved error handling
make_request() {
    local method="$1"
    local url="$2"
    local data="$3"
    local response
    local http_code
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
             -H "Content-Type: application/json" \
             -d "$data" \
             "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" 2>/dev/null)
    fi
    
    # Check if curl failed
    if [ $? -ne 0 ]; then
        print_error "Failed to connect to server"
        return 1
    fi
    
    # Extract HTTP status code
    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | head -n -1)
    
    # Check for HTTP errors
    if [ "$http_code" -ge 400 ]; then
        print_error "HTTP Error $http_code"
        echo "$response" | head -c 200
        echo ""
        return 1
    fi
    
    # Check if response is empty
    if [ -z "$response" ]; then
        print_warning "Empty response from server"
        return 1
    fi
    
    echo "$response"
    return 0
}

# Function to format JSON output
format_json() {
    local input="$1"
    if [ -z "$input" ]; then
        print_warning "No response received"
        return 1
    fi
    
    if command -v jq > /dev/null 2>&1; then
        echo "$input" | jq .
    else
        # Basic JSON formatting without jq
        echo "$input" | python3 -m json.tool 2>/dev/null || echo "$input"
    fi
}

# Function to list available MCP tools
list_tools() {
    print_info "Available MCP Tools:"
    echo ""
    echo "📋 Tasks Management:"
    echo "  • tasks pending  - Get pending tasks"
    echo "  • tasks done     - Get completed tasks"
    echo "  • tasks all      - Get all tasks"
    echo "  • tasks in_progress - Get in-progress tasks"
    echo "  • pending        - Get pending tasks (direct endpoint)"
    echo ""
    echo "🤖 Gemini Integration:"
    echo "  • gemini \"<prompt>\" - Send prompt to Gemini AI"
    echo ""
    echo "📊 Server Information:"
    echo "  • health         - Check server health"
    echo "  • logs           - View query logs"
    echo ""
}

# Function to run MCP tools
run_tool() {
    local tool_name="$1"
    shift
    local args="$*"
    
    check_server
    
    case "$tool_name" in
        "tasks")
            print_info "Fetching tasks with query: $args"
            if ! make_request "POST" "$SERVER_URL/tasks" "{\"query\": \"$args\"}" | format_json; then
                print_error "Failed to fetch tasks"
                exit 1
            fi
            ;;
        "pending")
            print_info "Fetching pending tasks (direct endpoint)..."
            if ! make_request "GET" "$SERVER_URL/tasks/pending" | format_json; then
                print_error "Failed to fetch pending tasks"
                exit 1
            fi
            ;;
        "gemini")
            if [ -z "$args" ]; then
                print_error "Please provide a prompt for Gemini"
                echo "Usage: $0 gemini \"<your prompt>\""
                exit 1
            fi
            print_info "Sending prompt to Gemini: $args"
            if ! make_request "POST" "$SERVER_URL/gemini" "{\"prompt\": \"$args\"}" | format_json; then
                print_error "Failed to send prompt to Gemini"
                exit 1
            fi
            ;;
        "health")
            print_info "Checking server health..."
            if ! make_request "GET" "$SERVER_URL/health" | format_json; then
                print_error "Failed to check server health"
                exit 1
            fi
            ;;
        "logs")
            print_info "Fetching query logs..."
            if ! make_request "GET" "$SERVER_URL/logs" | format_json; then
                print_error "Failed to fetch logs"
                exit 1
            fi
            ;;
        *)
            print_error "Unknown tool: $tool_name"
            echo ""
            list_tools
            exit 1
            ;;
    esac
}

# Function to show help
show_help() {
    echo "MCP CLI Helper Script"
    echo ""
    echo "Usage:"
    echo "  $0 list                                    - List available MCP tools"
    echo "  $0 run <tool_name> <arguments>            - Run an MCP tool"
    echo "  $0 tasks <query>                          - Get tasks (pending/done/all)"
    echo "  $0 pending                                - Get pending tasks (direct)"
    echo "  $0 gemini \"<prompt>\"                      - Send prompt to Gemini"
    echo "  $0 health                             - Check server health"
    echo "  $0 logs                                   - View query logs"
    echo "  $0 help                                   - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 run tasks pending"
    echo "  $0 run gemini \"What is machine learning?\""
    echo "  $0 tasks done"
    echo "  $0 pending"
    echo "  $0 gemini \"Explain quantum computing\""
    echo ""
}

# Main script logic
case "$1" in
    "list")
        list_tools
        ;;
    "run")
        if [ $# -lt 3 ]; then
            print_error "Usage: $0 run <tool_name> <arguments>"
            exit 1
        fi
        run_tool "$2" "${@:3}"
        ;;
    "tasks")
        if [ $# -lt 2 ]; then
            print_error "Usage: $0 tasks <query>"
            echo "Available queries: pending, done, all, in_progress"
            exit 1
        fi
        run_tool "tasks" "$2"
        ;;
    "pending")
        run_tool "pending"
        ;;
    "gemini")
        if [ $# -lt 2 ]; then
            print_error "Usage: $0 gemini \"<prompt>\""
            exit 1
        fi
        run_tool "gemini" "$2"
        ;;
    "health")
        run_tool "health"
        ;;
    "logs")
        run_tool "logs"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        print_warning "No command provided"
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac