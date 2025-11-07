# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

import json
import ast

def is_json_rpc_message(msg: str | dict) -> bool:
    try:
        # Parse string to dict if needed
        if isinstance(msg, str):
            try:
                parsed_msg = json.loads(msg)
            except json.JSONDecodeError:
                return False
        elif isinstance(msg, dict):
            parsed_msg = msg
        else:
            return False
        
        # Check required jsonrpc version
        if parsed_msg.get("jsonrpc") != "2.0":
            return False
        if parsed_msg.get("method") == None:
            return False       
        return True        
    except Exception:
        return False

def safe_parse(s: str) -> dict | list | None:
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return None

def extract_text(data: str | list[str | dict]) -> str | None:
    def get_text_from_item(item: str | dict) -> str | None:
        if isinstance(item, str):
            item = safe_parse(item)
        if isinstance(item, dict):
            return item.get("text")
        return None

    def get_text_from_item_list(data: list) -> str | None:
        for item in data:
            text = get_text_from_item(item)
            if text is not None:
                return text
        return None

    if isinstance(data, str):
        parsed = safe_parse(data)
        if is_json_rpc_message(parsed):
            return data # return original string if it's JSON-RPC
        if isinstance(parsed, dict):
            return parsed.get("text")
        if isinstance(parsed, list):
            return get_text_from_item_list(parsed)
        return data  # return original string if no JSON found

    if isinstance(data, list):
        return get_text_from_item_list(data)

    return None
