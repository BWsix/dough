import io
import re
from typing import Annotated, Union

import aiohttp
import interactions

from app import config


class ImageAttachmentConverter(interactions.Converter):
    async def convert(
        self,
        ctx: interactions.BaseContext,
        image_attachment: interactions.Attachment,
    ) -> interactions.File:
        """Downloads the image from the attachment and returns it as a interactions.File object"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_attachment.url) as image_res:
                if image_res.status != 200:
                    return False

                return interactions.File(
                    file=io.BytesIO(await image_res.read()),
                    file_name=image_attachment.filename,
                    content_type=image_attachment.content_type,
                )


class UploadExtension(interactions.Extension):
    bot: interactions.Client
    config = config.Config()

    guild: interactions.Guild
    upload_request_channel: interactions.TYPE_GUILD_CHANNEL
    upload_form_modal = interactions.Modal(
        interactions.ParagraphText(
            label="Description",
            placeholder="Description of the upload",
            custom_id="description",
            required=True,
        ),
        title="Upload Anonymously",
    )
    confirmation_message_action_row = interactions.ActionRow(
        interactions.Button(
            style=interactions.ButtonStyle.RED,
            label="Delete Post",
            custom_id="btn:delete_post",
        ),
    )

    @interactions.listen(interactions.api.events.Startup)
    async def on_startup(self, event: interactions.api.events.Startup):
        self.bot = event.bot
        self.guild = self.bot.get_guild(self.config.guild_id)
        self.upload_request_channel = self.guild.get_channel(
            self.config.upload_request_channel_id
        )
        print("Upload Extension Loaded")

    @interactions.slash_command(
        name="upload",
        description="Upload Anonymously.",
        options=[
            interactions.SlashCommandOption(
                name="upload_channel",
                description="Select a channel to upload to",
                required=True,
                type=interactions.OptionType.STRING,
                choices=[
                    interactions.SlashCommandChoice(
                        "#upload-sharing", "#upload-sharing"
                    ),
                    interactions.SlashCommandChoice("#ost-sharing", "#ost-sharing"),
                    interactions.SlashCommandChoice("#misc-sharing", "#misc-sharing"),
                ],
            ),
            interactions.SlashCommandOption(
                name="image_attachment",
                description="Paste your image here!",
                required=True,
                type=interactions.OptionType.ATTACHMENT,
            ),
            interactions.SlashCommandOption(
                name="fulfilled_request_link",
                description="Paste the link to the fulfilled request here",
                required=False,
                type=interactions.OptionType.STRING,
            ),
        ],
    )
    async def upload_anonymously(
        self,
        ctx: interactions.SlashContext,
        upload_channel: str,
        image_attachment: Annotated[interactions.File, ImageAttachmentConverter],
        fulfilled_request_link: Union[str, None] = None,
    ):
        # form handler
        await ctx.send_modal(modal=self.upload_form_modal)
        upload_form_ctx = await ctx.bot.wait_for_modal(
            self.upload_form_modal,
            author=ctx.author,
        )
        form_loading_message = await upload_form_ctx.send(
            "Processing...", ephemeral=True
        )

        # build and publish anonymous post
        description = upload_form_ctx.responses["description"]
        target_channel = self.guild.get_channel(self.config.channels[upload_channel])
        try:
            users_to_ping = await self.fetch_requested_users(fulfilled_request_link)
        except Exception:
            users_to_ping = ""
            await ctx.send(
                "Invalid fulfilled request link provided, will skip pinging users.",
                ephemeral=True,
            )
        anonymous_post_message = await target_channel.send(
            content=f"{description}\n{users_to_ping}",
            file=image_attachment,
            suppress_embeds=True,
        )

        # delete form loading message
        try:
            await form_loading_message.delete(context=ctx)
        except interactions.errors.NotFound:
            pass

        # send confirmation message
        await ctx.send(
            "The post has been uploaded to the server."
            + f"\nLink: {anonymous_post_message.jump_url}"
            + "\nYou can delete the post by clicking the button below.",
            components=[self.confirmation_message_action_row],
            ephemeral=True,
        )

    @interactions.component_callback("btn:delete_post")
    async def delete_post(self, ctx: interactions.ComponentContext):
        link = re.search(r"(?P<url>https?://[^\s]+)", ctx.message.content).group("url")
        channel_id = int(link.split("/")[-2])
        message_id = int(link.split("/")[-1])
        upload_channel = self.guild.get_channel(channel_id)

        anonymous_post_message = await upload_channel.fetch_message(message_id)
        if anonymous_post_message:
            await anonymous_post_message.delete(context=ctx)
            await ctx.send("Post deleted.", ephemeral=True)
        else:
            await ctx.send(
                "Post not found, it may have already been deleted by admins.",
                ephemeral=True,
            )

        await ctx.message.delete(context=ctx)

    async def fetch_requested_users(self, fulfilled_request_link: str) -> str:
        """Fetches and composes a string of users to ping from the fulfilled request link."""
        if not fulfilled_request_link:
            return ""

        request_message_id = int(fulfilled_request_link.split("/")[-1])
        request_message = await self.upload_request_channel.fetch_message(
            request_message_id
        )
        reacted_users: interactions.ReactionUsers = {
            r.emoji.name: r.users for r in request_message.reactions
        }["pingme"]()
        users = await reacted_users.fetch()
        return "".join([u.mention for u in users])


def setup(bot: interactions.Client):
    UploadExtension(bot)
