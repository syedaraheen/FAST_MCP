#!/bin/bash

# FAST MCP Server Demo Script
# Demonstrates the complete functionality of the MCP server

echo "🚀 FAST MCP Server with Gemini Integration - Demo"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_section() {
    echo -e "${BLUE}📋 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if server is running
print_section "Checking Server Status"
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    print_success "MCP Server is running on port 5001"
    ./mcp_cli.sh health
else
    echo "❌ Server is not running. Please start it with: python server.py"
    exit 1
fi

echo ""
print_section "Available MCP Tools"
./mcp_cli.sh list

echo ""
print_section "Testing Tasks Management - Pending Tasks"
./mcp_cli.sh tasks pending

echo ""
print_section "Testing Tasks Management - Completed Tasks"
./mcp_cli.sh tasks done

echo ""
print_section "Testing Tasks Management - All Tasks"
./mcp_cli.sh tasks all

echo ""
print_section "Testing Gemini Integration"
print_info "Note: This will show Gemini CLI help (Gemini CLI not configured)"
./mcp_cli.sh gemini "Hello, how are you?"

echo ""
print_section "Query Logs"
print_info "Showing all logged requests and responses"
./mcp_cli.sh logs

echo ""
print_section "Demo Complete!"
print_success "All MCP server functionality demonstrated successfully!"
print_info "Server is running at: http://localhost:5001"
print_info "API Documentation: http://localhost:5001/docs"
print_info "Query logs saved to: query_log.json"