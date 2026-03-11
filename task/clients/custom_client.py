import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role

class CustomDialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self.endpoint_url = f"{DIAL_ENDPOINT}/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        http_headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [msg.to_dict() for msg in messages]
        }
        print(f"\n--- CustomDialClient Request ---\nURL: {self.endpoint_url}\nHeaders: {http_headers}\nPayload: {json.dumps(payload, indent=2)}")
        http_response = requests.post(self.endpoint_url, headers=http_headers, json=payload)
        if http_response.status_code != 200:
            raise Exception(f"HTTP {http_response.status_code}: {http_response.text}")
        response_json = http_response.json()
        print(f"\n--- CustomDialClient Response ---\n{json.dumps(response_json, indent=2)}")
        completions = response_json.get("choices")
        if not completions:
            raise Exception("No choices in response found")
        assistant_content = completions[0]["message"]["content"]
        print("AI:", assistant_content)
        return Message(role=Role.AI, content=assistant_content)

    async def stream_completion(self, messages: list[Message]):
        http_headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        print(f"\n--- CustomDialClient Streaming Request ---\nURL: {self.endpoint_url}\nHeaders: {http_headers}\nPayload: {json.dumps(payload, indent=2)}")
        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint_url, headers=http_headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                async for data_line in response.content:
                    line_str = data_line.decode("utf-8").strip()
                    if not line_str.startswith("data: "):
                        continue
                    chunk_data = line_str[len("data: "):]
                    if chunk_data == "[DONE]":
                        break
                    content_piece = self.parse_stream_chunk(chunk_data)
                    print(content_piece, end="", flush=True)
                    yield content_piece
        print()

    def parse_stream_chunk(self, chunk_str: str) -> str:
        try:
            chunk_json = json.loads(chunk_str)
            return chunk_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
        except Exception as exc:
            print(f"Error parsing chunk: {exc}")
            return ""