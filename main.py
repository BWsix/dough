import asyncio
import io

import aiohttp
import interactions
from dotenv import dotenv_values

bot = interactions.Client()
config = dotenv_values(".env")

assert "TOKEN" in config
TOKEN = config["TOKEN"]
assert "GUILD_ID" in config
GUILD_ID = int(config["GUILD_ID"])
assert "CHANNEL_ID" in config
CHANNEL_ID = int(config["CHANNEL_ID"])


@interactions.slash_command(
    name="upload",
    description="Upload Anonymously.",
)
@interactions.slash_option(
    name="image_attachment",
    description="Paste your image here!",
    required=True,
    opt_type=interactions.OptionType.ATTACHMENT,
)
async def upload_anonymously(
    ctx: interactions.SlashContext,
    image_attachment: interactions.Attachment = None,
):
    form = interactions.Modal(
        interactions.ParagraphText(
            label="Description",
            placeholder="Enter a description",
            custom_id="description",
            required=True,
        ),
        title="Upload Anonymously",
    )
    await ctx.send_modal(modal=form)

    form_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(
        form,
        author=ctx.author,
    )
    # must reply to the modal context
    loading_message: interactions.Message = await form_ctx.send(
        "Processing...",
        ephemeral=True,
    )

    description = form_ctx.responses["description"]
    image: interactions.File = None
    async with aiohttp.ClientSession() as session:
        async with session.get(image_attachment.url) as image_res:
            if image_res.status != 200:
                return await ctx.send(
                    "Could not download image",
                    ephemeral=True,
                )
            image_data = io.BytesIO(await image_res.read())
            image = interactions.File(
                file=image_data,
                file_name=image_attachment.filename,
                content_type=image_attachment.content_type,
            )

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)
    anonymous_post_message = await channel.send(
        content=description,
        file=image,
        suppress_embeds=True,
    )
    await loading_message.delete(context=ctx)

    delete_button = interactions.Button(
        style=interactions.ButtonStyle.RED,
        label="Delete Post",
    )
    delete_confirmation_message = await ctx.send(
        "The post has been uploaded to the server.\n"
        + f"Link: {anonymous_post_message.jump_url}\n"
        + "In case you want to delete your post, click the button below within 5 minutes.",
        components=delete_button,
        ephemeral=True,
    )

    try:
        await ctx.bot.wait_for_component(
            components=delete_button,
            timeout=60 * 5,
        )
        await anonymous_post_message.delete(context=ctx)
        await delete_confirmation_message.delete(context=ctx)
        await ctx.send(
            "Post deleted.",
            ephemeral=True,
        )
    except asyncio.TimeoutError:
        await delete_confirmation_message.delete(context=ctx)


@interactions.listen(interactions.api.events.Startup)
async def on_startup(event: interactions.api.events.Startup):
    bot_name = event.bot.user.username
    guild = await event.bot.fetch_guild(GUILD_ID)
    channel = await event.bot.fetch_channel(CHANNEL_ID)

    print(f"[{bot_name}] Ready")
    print(f"[{bot_name}] Guild: {guild.name}")
    print(f"[{bot_name}] Channel: {channel.name}")


bot.start(TOKEN)
