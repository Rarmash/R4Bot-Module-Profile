import datetime
import platform
import sys
import time
from math import ceil

import discord
from discord.ext import commands
from .service import ProfileService

DATE_FORMAT = '%#d.%#m.%Y в %H:%M:%S'
CONFIG_NOT_INITIALIZED_MESSAGE = (
    'Сервер ещё не настроен. Владелец сервера может выполнить `/service initserver`.'
)


class BotLink(discord.ui.View):
    def __init__(self, application_id):
        super().__init__(timeout=None)
        invite_button = discord.ui.Button(
            label='Приглашение',
            style=discord.ButtonStyle.link,
            emoji='🤩',
            url=f'https://discord.com/oauth2/authorize?client_id={application_id}&permissions=8&scope=bot%20applications.commands',
        )
        self.add_item(invite_button)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.services = getattr(bot, 'r4_services', None)
        if self.services is None:
            raise RuntimeError('R4Bot runtime services are not available on bot.r4_services')

        self.application_id = self.services.config.application_id
        if not self.application_id:
            raise RuntimeError('APPLICATIONID is not configured for the bot core')
        self.service = ProfileService(self)

    def get_server_data(self, guild_id: int):
        return self.services.config.get_servers_data().get(str(guild_id))

    def is_module_enabled(self, module_id: str) -> bool:
        return self.services.module_state.is_module_enabled(module_id)

    @staticmethod
    def get_status_emoji(status):
        if status == discord.Status.online:
            return '🟢 в сети'
        if status == discord.Status.offline:
            return '⚪ не в сети'
        if status == discord.Status.idle:
            return '🌙 не активен'
        if status == discord.Status.dnd:
            return '⛔ не беспокоить'
        return '❔ неизвестно'

    @staticmethod
    def get_timestamp(value: datetime.datetime) -> int:
        return ceil(
            time.mktime(
                (
                    datetime.datetime.strptime(
                        str(value.strftime(DATE_FORMAT)),
                        '%d.%m.%Y в %H:%M:%S',
                    )
                    + datetime.timedelta(hours=3)
                ).timetuple()
            )
        )

    @staticmethod
    def format_voice_duration(total_seconds):
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f'{hours} ч {minutes} м'
        if minutes:
            return f'{minutes} м {seconds} с'
        return f'{seconds} с'

    @commands.slash_command(description='Посмотреть карточку профиля')
    @discord.option('user', description='Пользователь', required=False)
    async def profile(self, ctx: discord.ApplicationContext, user: discord.Member = None):
        server_data = self.get_server_data(ctx.guild.id)
        if not server_data:
            await ctx.respond(CONFIG_NOT_INITIALIZED_MESSAGE, ephemeral=True)
            return

        user = user or ctx.author
        await ctx.defer()

        status = self.get_status_emoji(user.status)
        user_data = self.services.firebase.get_from_record(str(ctx.guild.id), 'Users', str(user.id))

        if user.id != self.bot.user.id:
            timeout_suffix = '(в тайм-ауте)' if user.timed_out else ''
            embed = discord.Embed(
                title=f'Привет, я {user.name}',
                description=f'<@{user.id}> — {status} {timeout_suffix}'.strip(),
                color=int(server_data.get('accent_color'), 16),
            )
            embed.add_field(name='Регистрация', value=f'<t:{self.get_timestamp(user.created_at)}:f>')
            embed.add_field(name='На сервере с', value=f'<t:{self.get_timestamp(user.joined_at)}:f>')

            if not user.bot and user_data:
                if self.is_module_enabled('messages'):
                    embed.add_field(name='Сообщений', value=user_data.get('messages', 0))
                if self.is_module_enabled('timeouts'):
                    embed.add_field(name='Всего тайм-аутов', value=user_data.get('timeouts', 0))
                if self.is_module_enabled('voice'):
                    embed.add_field(name='Голосовая активность', value=self.format_voice_duration(user_data.get('voice', 0)))

                extra_fields = await self.service.collect_extra_fields(ctx, user, user_data, server_data)
                for field in extra_fields:
                    embed.add_field(
                        name=field['name'],
                        value=field['value'],
                        inline=field.get('inline', True),
                    )

            insider_role = discord.utils.get(ctx.guild.roles, id=server_data.get('insider_id'))
            if insider_role in user.roles:
                embed.set_footer(text='Принимает участие в тестировании и помогает серверу стать лучше')

            embed.set_thumbnail(url=user.avatar)
            await ctx.respond(embed=embed)
            return

        embed = discord.Embed(
            title=f'Привет, я {user.name}',
            description=f'Тег: <@{user.id}>',
            color=int(server_data.get('accent_color'), 16),
        )
        embed.add_field(name='Владелец', value=f"<@{server_data.get('admin_id')}>")
        embed.add_field(name='Сервер бота', value=ctx.guild.name)
        embed.add_field(name='Создан', value=f'<t:{self.get_timestamp(user.created_at)}:f>')
        embed.add_field(name='На сервере с', value=f'<t:{self.get_timestamp(user.joined_at)}:f>')
        embed.add_field(name='Статус', value=status)
        embed.add_field(name='ОС', value=sys.platform)
        embed.add_field(name='Версия бота', value=self.services.config.version)
        embed.add_field(name='Версия Python', value=platform.python_version())
        embed.add_field(name='Версия Pycord', value=discord.__version__)
        embed.set_thumbnail(url=user.avatar)
        await ctx.respond(embed=embed, view=BotLink(self.application_id))

    @commands.slash_command(description='Посмотреть карточку сервера')
    @discord.guild_only()
    async def server(self, ctx: discord.ApplicationContext):
        server_data = self.get_server_data(ctx.guild.id)
        if not server_data:
            await ctx.respond(CONFIG_NOT_INITIALIZED_MESSAGE, ephemeral=True)
            return

        guild = ctx.guild
        members = guild.members
        bot_count = len([member for member in members if member.bot])

        embed = discord.Embed(
            title=f'Информация о сервере {guild}',
            color=int(server_data.get('accent_color'), 16),
        )
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name='Описание', value=guild.description or 'Отсутствует')
        embed.add_field(name='Каналов', value=str(len(guild.channels)))
        embed.add_field(name='Ролей', value=str(len(guild.roles)))
        embed.add_field(name='Бустеров', value=str(len(guild.premium_subscribers)))
        embed.add_field(name='Участников', value=str(guild.member_count - bot_count))
        embed.add_field(name='Ботов', value=str(bot_count))
        embed.add_field(name='Создан', value=f'<t:{self.get_timestamp(guild.created_at)}:f>')
        embed.add_field(name='Владелец', value=f'<@{guild.owner.id}>')
        await ctx.respond(embed=embed)



def setup(bot):
    bot.add_cog(Profile(bot))
