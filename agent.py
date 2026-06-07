from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import google

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful voice AI assistant",
            tools=[google.tools.GoogleSearch()],
            )

server = AgentServer()

@server.rtc_session(agent_name="gemini-native-audio")
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-3.1-flash-audio-eap",
            voice="Puck"
        )
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )