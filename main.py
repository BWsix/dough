import interactions
import app.config


config = app.config.Config()
bot = interactions.Client(
    send_command_tracebacks=config.dev,
    send_not_ready_messages=True,
)


@interactions.listen(interactions.api.events.Startup)
async def on_startup(event: interactions.api.events.Startup):
    """Global startup configuration"""
    bot_name = event.bot.user.username
    print(f"{bot_name} Ready")

    guild = await event.bot.fetch_guild(config.guild_id)
    assert guild
    print(f"Server: {guild.name}")

    assert guild.get_channel(config.channels["#upload-request"])
    assert guild.get_channel(config.channels["#upload-sharing"])
    assert guild.get_channel(config.channels["#misc-sharing"])
    assert guild.get_channel(config.channels["#upload-request"])
    print("Found all target channels")

    emojis = await guild.fetch_all_custom_emojis()
    assert "pingme" in [emoji.name for emoji in emojis]
    print("Found :pingme: emoji")


bot.load_extension("app.upload")
bot.start(config.bot_token)
