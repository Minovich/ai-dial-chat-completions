import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

async def run_chat(stream_mode: bool) -> None:
    # Initialize clients
    main_llm = DialClient(deployment_name='gpt-4o')
    backup_llm = DialClient(deployment_name='gpt-4o')

    # Start conversation
    chat_history = Conversation()

    # System prompt setup
    print("Enter a system prompt or press Enter to use the default.")
    system_prompt_input = input("> ").strip()
    if system_prompt_input:
        chat_history.add_message(Message(Role.SYSTEM, system_prompt_input))
        print("System prompt added.")
    else:
        chat_history.add_message(Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT))
        print(f"Default system prompt used: '{DEFAULT_SYSTEM_PROMPT}'")
    print()

    # Chat loop
    print("Ask your question or type 'exit' to leave.")
    while True:
        user_query = input("> ").strip()
        if user_query.lower() == "exit":
            print("Chat ended. Goodbye!")
            break

        chat_history.add_message(Message(Role.USER, user_query))

        print("AI:")
        if stream_mode:
            ai_response = await backup_llm.stream_completion(chat_history.get_messages())
        else:
            ai_response = backup_llm.get_completion(chat_history.get_messages())

        chat_history.add_message(ai_response)

if __name__ == "__main__":
    asyncio.run(run_chat(True))