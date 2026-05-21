"""
CLI runner as a fallback in case the web UI has issues during demo.
"""
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.coordinator import root_agent


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="travel_app", user_id="demo_user"
    )

    runner = Runner(
        agent=root_agent,
        app_name="travel_app",
        session_service=session_service,
    )

    print("Travel Intelligence System — type 'quit' to exit\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ("quit", "exit"):
            break

        message = types.Content(role="user", parts=[types.Part(text=query)])

        async for event in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                print(f"\nAgent: {event.content.parts[0].text}\n")


if __name__ == "__main__":
    asyncio.run(main())