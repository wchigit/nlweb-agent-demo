# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

from typing import Dict, Any, Callable, Awaitable

class OutputResponse:
    def __init__(self):
        self.responses = []

    def create_output_method(self, response: Any) -> Callable[[Dict[str, Any]], Awaitable[None]]:
        async def output_method(data: Dict[str, Any]) -> None:
            """Callback for handler output."""
            await self.send_response(response, data)

        return output_method

    def create_collector_output_method(self) -> Callable[[Dict[str, Any]], Awaitable[None]]:
        async def output_method(data: Dict[str, Any]) -> None:
            """Callback that collects output."""
            self.responses.append(data)

        return output_method

    def get_collected_responses(self) -> list:
        responses = self.responses
        self.responses = []
        return responses

    def build_json_response(self, responses: list) -> Dict[str, Any]:
        # Separate _meta and content items
        meta = {}
        content = []

        for response in responses:
            if '_meta' in response:
                # Merge meta information (first one wins for duplicates)
                for key, value in response['_meta'].items():
                    if key not in meta:
                        meta[key] = value
            if 'content' in response:
                # Collect all content items
                content.extend(response['content'])

        # Build final response
        result = {}
        if meta:
            result['_meta'] = meta
        if content:
            result['content'] = content

        return result
