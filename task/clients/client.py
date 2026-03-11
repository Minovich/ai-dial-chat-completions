from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role

class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self.dial_sync = Dial(
            base_url=DIAL_ENDPOINT,
            api_key=self._api_key,
        )
        self.dial_async = AsyncDial(
            base_url=DIAL_ENDPOINT,
            api_key=self._api_key,
        )

    def get_completion(self, messages: list[Message]) -> Message:
        result = self.dial_sync.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=[msg.to_dict() for msg in messages],
        )

        if completions := result.choices:
            if assistant_message := completions[0].message:
                print(assistant_message.content)
                return Message(Role.AI, assistant_message.content)

        raise Exception("No choices in response found")

    async def stream_completion(self, messages: list[Message]) -> Message:
        stream_chunks = await self.dial_async.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages],
            stream=True,
        )

        response_parts = []
        async for chunk in stream_chunks:
            if chunk.choices and len(chunk.choices) > 0:
                delta_part = chunk.choices[0].delta
                if delta_part and delta_part.content:
                    print(delta_part.content, end='')
                    response_parts.append(delta_part.content)

        print()
        return Message(Role.AI, ''.join(response_parts))