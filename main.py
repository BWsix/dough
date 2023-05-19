import interactions
from dotenv import dotenv_values

bot = interactions.Client()

config = dotenv_values(".env")
assert "TOKEN" in config


@interactions.slash_command(name="upload", description="Upload Anonymously")
async def my_command_function(ctx: interactions.SlashContext):
    form = interactions.Modal(
        interactions.ParagraphText(
            label="Description",
            placeholder="Enter a description",
            custom_id="description",
            required=True,
        ),
        interactions.ShortText(
            label="Image URL",
            placeholder="Enter an image URL",
            custom_id="image_url",
            required=False,
        ),
        title="Upload Anonymously",
    )
    await ctx.send_modal(modal=form)

    form_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(form)
    res = form_ctx.responses
    await form_ctx.channel.send(
        embed=interactions.Embed(
            description=res["description"],
            images=[interactions.EmbedAttachment(url=res["image_url"])],
        )
    )
    await form_ctx.send("Uploaded!", ephemeral=True)


@interactions.listen(interactions.api.events.Startup)
async def on_startup(event: interactions.api.events.Startup):
    bot_name = event.bot.user.username
    print(f"[{bot_name}] Ready!")


bot.start(config["TOKEN"])
