import io

import aiohttp
import interactions
from dotenv import dotenv_values

bot = interactions.Client()
config = dotenv_values(".env")

assert "TOKEN" in config
TOKEN = config["TOKEN"]
TARGET_CHANNEL = int(config["TARGET_CHANNEL"]) if "TARGET_CHANNEL" in config else None


@interactions.slash_command(
    name="upload",
    description="Upload Anonymously.",
    dm_permission=False,
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
    if TARGET_CHANNEL and ctx.channel.id != TARGET_CHANNEL:
        channel = await ctx.guild.fetch_channel(TARGET_CHANNEL)
        return await ctx.send(
            f"Please use this command in {channel.mention}!",
            ephemeral=True,
        )

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

    form_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(form)
    res = form_ctx.responses
    async with aiohttp.ClientSession() as session:
        async with session.get(image_attachment.url) as image_res:
            if image_res.status != 200:
                return await form_ctx.send("Could not download image", ephemeral=True)

            image_data = io.BytesIO(await image_res.read())

            await form_ctx.channel.send(
                content=res["description"],
                suppress_embeds=True,
                file=interactions.File(
                    file=image_data,
                    file_name=image_attachment.filename,
                    content_type=image_attachment.content_type,
                ),
            )
    await form_ctx.send("Uploaded!", ephemeral=True)


@interactions.listen(interactions.api.events.Startup)
async def on_startup(event: interactions.api.events.Startup):
    bot_name = event.bot.user.username
    print(f"[{bot_name}] Ready!")


bot.start(config["TOKEN"])
