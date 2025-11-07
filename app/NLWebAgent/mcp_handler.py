import json
from typing import Dict, Any
from nlweb_core.NLWebVectorDBRankingHandler import NLWebVectorDBRankingHandler
from output_response import OutputResponse

class MCPHandler:

    MCP_VERSION = "2024-11-05"
    SERVER_NAME = "nlweb-mcp-server"
    SERVER_VERSION = "0.5.0"

    def __init__(self):
        pass

    async def handle_request(self, request_data: dict) -> Dict[str, Any]:
        method = request_data.get("method")
        params = request_data.get("params")
        request_id = request_data.get("id")

        if method == "initialize":
            return self.build_initialize_response(request_data)
        elif method == "tools/list":
            return self.build_tools_list_response(request_data)
        # Handle tools/call
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name != "ask":
                response = self.build_error_response(
                    request_id,
                    -32602,
                    f"Unknown tool: {tool_name}"
                )
                return response

            # MCP calls default to non-streaming
            if "streaming" not in arguments:
                arguments["streaming"] = False

            query_params = arguments

            if 'query' not in query_params:
                response = self.build_error_response(
                    request_id,
                    -32602,
                    "Missing required parameter: query"
                )
                return response

            output_response = OutputResponse()
            output_method = output_response.create_collector_output_method()
            handler = NLWebVectorDBRankingHandler(query_params, output_method)
            await handler.runQuery()
            responses = output_response.get_collected_responses()
            result = output_response.build_json_response(responses)
            response = self.build_tool_call_response(request_id, result)
            return response        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }

    def build_initialize_response(self, request_data: dict) -> Dict[str, Any]:
        request_id = request_data.get("id")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.MCP_VERSION,
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.SERVER_NAME,
                    "version": self.SERVER_VERSION
                }
            }
        }

    def build_tools_list_response(self, request_data: dict) -> Dict[str, Any]:
        request_id = request_data.get("id")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "ask",
                        "description": "Search and answer natural language queries using NLWeb's vector database and LLM ranking",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Natural language query"
                                },
                                "site": {
                                    "type": "string",
                                    "description": "Target site identifier"
                                },
                                "num_results": {
                                    "type": "integer",
                                    "description": "Number of results to return"
                                },
                                "streaming": {
                                    "type": "boolean",
                                    "description": "Enable streaming response",
                                    "default": False
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }

    def build_error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """
        Build JSON-RPC 2.0 error response.

        Args:
            request_id: JSON-RPC request ID
            code: Error code (JSON-RPC standard codes)
            message: Error message

        Returns:
            JSON-RPC 2.0 error response dict
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def build_tool_call_response(self, request_id: Any, nlweb_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build MCP tools/call response from NLWeb result.

        Args:
            request_id: JSON-RPC request ID
            nlweb_result: Result from NLWeb handler

        Returns:
            JSON-RPC 2.0 response dict
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(nlweb_result, indent=2)
                    }
                ]
            }
        }
