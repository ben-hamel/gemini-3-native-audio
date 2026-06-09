import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    function_tool,
)
from livekit.plugins import openai
from openai import AsyncOpenAI

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        self.openai_client = AsyncOpenAI()
        super().__init__(
            instructions=(
                "You are a helpful voice AI assistant. Use search_web when the "
                "user asks for current information or something you are unsure "
                "about. Briefly identify the sources in your spoken answer."
            ),
        )

    @function_tool
    async def search_web(self, query: str) -> str:
        """Search the web for current information.

        Args:
            query: A focused web search query.
        """
        response = await self.openai_client.responses.create(
            model=os.getenv("SEARCH_MODEL", "gpt-5-mini"),
            tools=[{"type": "web_search"}],
            input=(
                f"Search the web for: {query}\n"
                "Return a concise answer for a voice assistant. Include the "
                "names of the most important sources and their URLs."
            ),
        )
        return response.output_text


server = AgentServer()


@server.rtc_session(agent_name="openai-realtime")
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime",
            voice="marin",
        )
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(server)
