import io
import nextcord
import asyncio
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions, MissingPermissions, BadArgument
import os
import re


mails_channel_name = "wmodmail"
transcripts_folder = "transcripts"


class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversations = {}  # Stores conversation messages

    async def save_transcript(self, user_id):
            if user_id in self.conversations:
                conversation = self.conversations[user_id]
                os.makedirs(transcripts_folder, exist_ok=True)
                with open(f"{transcripts_folder}/{user_id}.txt", "w") as f:
                    for user, message in conversation:
                        f.write(f"{user}: {message}\n")
                del self.conversations[user_id]
    async def load_transcript(self, transcript_id):
        file_path = f'transcripts/{transcript_id}.txt'  # Change this to match where you saved the transcript files
        print(f"Looking for transcript at {file_path}")  # Debug print

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                transcript = file.read()
            return transcript
        else:
            print(f"Transcript not found at {file_path}")  # Debug print
            return None

    @commands.command(description="Sets up Wadder ModMail")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setupmodmail(self, ctx):
        await ctx.trigger_typing()
        await asyncio.sleep(2)
        channel = nextcord.utils.get(ctx.guild.channels, name=mails_channel_name)
        if channel is None:
            guild = ctx.guild
            overwrites = {
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                guild.me: nextcord.PermissionOverwrite(read_messages=True)
            }

            mod_channel = await guild.create_text_channel(mails_channel_name, overwrites=overwrites)
            embed = nextcord.Embed(
                title='Setup completed',
                description=f"{mod_channel.name} is created.",
                color = nextcord.Color.green(),
            )
        else:
            mod_channel = channel
            embed = nextcord.Embed(
                title='Setup completed',
                description=f"{mod_channel.name} exists",
                color = nextcord.Color.blue(),
            )
        
        await ctx.send(embed=embed)

        overwrites2 = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            guild.me: nextcord.PermissionOverwrite(read_messages=True)
        }
        try:
            mod_logs = await guild.create_text_channel("mod-logs", overwrites=overwrites2)
        except:
            print("couldn't create a mod-logs channel, maybe it exists")

    @setupmodmail.error
    async def setup_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = nextcord.Embed(
                title='Setup',
                description="You don't have permissions to manage mod mails",
                color = nextcord.Color.red(),
            )
            await ctx.send(embed=embed)
        # else:
        #     embed = nextcord.Embed(
        #         title='Server Only Command',
        #         description="You can't use this command here",
        #         color = nextcord.Color.red(),
        #     )
        #     await ctx.send(embed=embed)

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, nextcord.channel.DMChannel):
            user_id = message.author.id
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            # ... rest of your existing code for handling DMs ...

            if user_id not in self.conversations:
                self.conversations[user_id] = []

            self.conversations[user_id].append((message.author, message.content))

            # Create or get the user-specific channel
            guild = self.bot.get_guild(1101158751576264795)  # Replace with your guild/server ID
            channel_name = f'modmail-{user_id}'
            mails_channel = nextcord.utils.get(guild.text_channels, name=channel_name)

            if not mails_channel:
                overwrites = {
                    guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
                }
                mails_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

            try:
                # send to server
                embed_to = nextcord.Embed(
                    title='📨 Mod Mail Received',
                    color=nextcord.Color.orange(),
                    timestamp=message.created_at
                )
                embed_to.set_author(name=f"{message.author}", icon_url=message.author.avatar.url)
                embed_to.add_field(name='**User ID**', value=f"`{message.author.id}`", inline=False)
                embed_to.add_field(name='**Message**', value=f"```{message.content}```", inline=False)
                embed_to.set_footer(text="Type your response here", icon_url=self.bot.user.avatar.url)
                embed_to.set_thumbnail(url=message.author.avatar.url)

                await mails_channel.send(embed=embed_to)

                # report result to user
                embed_reply = nextcord.Embed(
                    title='✅ Mail Sent Successfully',
                    description="Your message has been sent to moderators. They'll get back to you soon.",
                    color=nextcord.Color.green(),
                    timestamp=message.created_at
                )
                embed_reply.set_author(name=f"{message.author}", icon_url=message.author.avatar.url)
                embed_reply.set_thumbnail(url=self.bot.user.avatar.url)
                await message.author.send(embed=embed_reply)
            except:
                # report result to user
                embed_reply = nextcord.Embed(
                    title='❌ Oops! Something went wrong',
                    description="I couldn't send your message to moderators. Please try again later.",
                    color=nextcord.Color.red(),
                    timestamp=message.created_at
                )
                embed_reply.set_author(name=f"{message.author}", icon_url=message.author.avatar.url)
                embed_reply.set_thumbnail(url=self.bot.user.avatar.url)
                await message.author.send(embed=embed_reply)

        elif message.channel.name.startswith("modmail-"):
            try:
                user_id = int(message.channel.name.split("-")[1])
            except ValueError:
                # Invalid channel name format, ignore
                return

            user = self.bot.get_user(user_id)
            if not user:
                return  # User not found

            if message.author.guild_permissions.administrator:
                try:
                    # send reply to user
                    embed_reply = nextcord.Embed(
                        title='🔔 Reply from Moderator',
                        description=f"```{message.content}```",
                        color=nextcord.Color.blue(),
                        timestamp=message.created_at
                    )
                    embed_reply.set_footer(text=f"Sent by {message.author}", icon_url=message.author.avatar.url)
                    await user.send(embed=embed_reply)

                    # send confirmation to moderator
                    embed_confirm = nextcord.Embed(
                        title='✅ Reply sent successfully',
                        description=f"Your reply has been sent to {user.name}",
                        color=nextcord.Color.green(),
                        timestamp=message.created_at
                    )
                    embed_confirm.set_thumbnail(url=self.bot.user.avatar.url)
                    await message.channel.send(embed=embed_confirm)
                except:
                    # send error message to moderator
                    embed_error = nextcord.Embed(
                        title='❌ Oops! Something went wrong',
                        description="I couldn't send your message to the user. Please try again later.",
                        color=nextcord.Color.red(),
                        timestamp=message.created_at
                    )
                    embed_error.set_thumbnail(url=self.bot.user.avatar.url)
                    await message.channel.send(embed=embed_error)
            else:
                # send error message to moderator
                embed_error = nextcord.Embed(
                    title='❌ Access denied',
                    description="You do not have permission to send a message to this user.",
                    color=nextcord.Color.red(),
                    timestamp=message.created_at
                )
                embed_error.set_thumbnail(url=self.bot.user.avatar.url)
                await message.channel.send(embed=embed_error)
    
    
    @commands.command()
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def end(self, ctx, user_id: int, channel_id: int):
        user = self.bot.get_user(user_id)
        transcript_channel = self.bot.get_channel(channel_id)
        if user is not None and transcript_channel is not None:
            if user_id in self.conversations:
                await self.save_transcript(user_id)
                transcript = await self.load_transcript(user_id)
                if transcript:
                    transcript_file = io.BytesIO(transcript.encode('utf-8'))
                    file = nextcord.File(transcript_file, filename=f"{user_id}_transcript.txt")
                    embed = nextcord.Embed(
                        title='✅ Transcript saved',
                        description=f"Conversation with {user.name} has been saved and closed.",
                        color=nextcord.Color.green(),
                        timestamp=ctx.message.created_at
                    )
                    await ctx.send(embed=embed)

                    # Send transcript to the specified channel
                    await transcript_channel.send(f"Transcript for conversation with {user.name}:", file=file)
                    
                    # Close the conversation channel
                    channel_name = f'modmail-{user_id}'
                    mails_channel = nextcord.utils.get(ctx.guild.text_channels, name=channel_name)
                    if mails_channel:
                        await mails_channel.delete()
                        del self.conversations[user_id]
                else:
                    embed = nextcord.Embed(
                        title='❌ Failed to save transcript',
                        description=f"Can't find user with the id {user_id}",
                        color=nextcord.Color.red(),
                        timestamp=ctx.message.created_at
                    )
                    await ctx.send(embed=embed)
            else:
                embed = nextcord.Embed(
                    title='❌ No active conversation',
                    description=f"There is no active conversation with {user.name}",
                    color=nextcord.Color.red(),
                    timestamp=ctx.message.created_at
                )
                await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title='❌ Failed to end conversation',
                description=f"Can't find user or transcript channel with the provided IDs",
                color=nextcord.Color.red(),
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)


    
    @commands.command(description="Loads a transcript for a user")
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def gtrans(self, ctx, user_id: int):
        transcript = await self.load_transcript(user_id)
        if transcript:
            # Send transcript as a file
            with io.StringIO(transcript) as fp:
                await ctx.send(f"Transcript for user {user_id}:", file=nextcord.File(fp, f"{user_id}.txt"))
        else:
            await ctx.send("Transcript not found.")

def setup(bot): 
    bot.add_cog(ModMail(bot))
    print('Mod Mail Cog LOADED')