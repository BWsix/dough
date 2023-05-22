import asyncio
import io
from typing import Union

import aiohttp
import interactions
from dotenv import dotenv_values

bot = interactions.Client()
config = dotenv_values(".env")

assert "TOKEN" in config
TOKEN = config["TOKEN"]
assert "GUILD_ID" in config
GUILD_ID = int(config["GUILD_ID"])

assert "UPLOAD_SHARING_CHANNEL_ID" in config
assert "OST_SHARING_CHANNEL_ID" in config
assert "MISC_SHARING_CHANNEL_ID" in config
assert "UPLOAD_REQUEST_CHANNEL_ID" in config
CHANNELS = {
    "#upload-sharing": int(config["UPLOAD_SHARING_CHANNEL_ID"]),
    "#ost-sharing": int(config["OST_SHARING_CHANNEL_ID"]),
    "#misc-sharing": int(config["MISC_SHARING_CHANNEL_ID"]),
    "#upload-request": int(config["UPLOAD_REQUEST_CHANNEL_ID"]),
}


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
@interactions.slash_option(
    name="upload_channel",
    description="Select a channel to upload to",
    required=True,
    opt_type=interactions.OptionType.STRING,
    choices=[
        interactions.SlashCommandChoice(
            name="#upload-sharing",
            value="#upload-sharing",
        ),
        interactions.SlashCommandChoice(
            name="#ost-sharing",
            value="#ost-sharing",
        ),
        interactions.SlashCommandChoice(
            name="#misc-sharing",
            value="#misc-sharing",
        ),
    ],
)
@interactions.slash_option(
    name="fulfilled_request_link",
    description="Paste the link to the fulfilled request here",
    required=False,
    opt_type=interactions.OptionType.STRING,
)
async def upload_anonymously(
    ctx: interactions.SlashContext,
    image_attachment: interactions.Attachment,
    upload_channel: str,
    fulfilled_request_link: Union[str, None] = None,
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
    channel = guild.get_channel(CHANNELS[upload_channel])
    request_channel = guild.get_channel(CHANNELS["#upload-request"])

    users_to_ping = ""
    if fulfilled_request_link:
        try:
            request_message_id = int(fulfilled_request_link.split("/")[-1])
            request_message = await request_channel.fetch_message(request_message_id)
            reacted_users: interactions.ReactionUsers = {
                r.emoji.name: r.users for r in request_message.reactions
            }["pingme"]()
            users = await reacted_users.fetch()
            users_to_ping = "".join([u.mention for u in users])
        except Exception as error:
            print("Error while parsing the link.")
            print(error)
            await ctx.send(
                "Error while parsing the link. Skip pinging users and continue with the upload.\n"
                + f"Link you provided: {fulfilled_request_link}",
                ephemeral=True,
            )

    anonymous_post_message = await channel.send(
        content=f"{description}\n{users_to_ping}",
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
    print(f"[{bot_name}] Ready")

    guild = await event.bot.fetch_guild(GUILD_ID)
    assert guild
    print(f"[{bot_name}] Server: {guild.name}")

    assert guild.get_channel(CHANNELS["#upload-request"])
    assert guild.get_channel(CHANNELS["#upload-sharing"])
    assert guild.get_channel(CHANNELS["#misc-sharing"])
    assert guild.get_channel(CHANNELS["#upload-request"])
    print(f"[{bot_name}] Found all target channels")

    emojis = await guild.fetch_all_custom_emojis()
    assert "pingme" in [emoji.name for emoji in emojis]
    print(f"[{bot_name}] Found :pingme: emoji")


bot.start(TOKEN)
