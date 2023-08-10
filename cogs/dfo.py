import discord
from discord import app_commands
from discord.ext import commands
import requests
import typing
from copy import deepcopy

from cogs.utils.keywords import Keyword as ky


class DFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = bot.get_api_key("DFO-APIKey")[15:-2]
        self.error_thumbnail = "https://wiki.dfo-world.com/images/5/5a/Future_content.png"

    dfo = app_commands.Group(name = "dfo", description = "Pulls up information using the DFO Global API")

    def get_request(self, type: str):
        pass


    def __get_character_base_stats(self, embed, server_id, character_id):
        payload = f"https://api.dfoneople.com/df/servers/{server_id}/characters/{character_id}?apikey={self.api_key}"
        response = requests.get(payload).json()
        message = f"""
            {ky.BULLET.value} **Level:** {response['level']}
            {ky.BULLET.value} **Adventurer Club:** {response['adventureName']}
            {ky.BULLET.value} **Guild:** {response['guildName']}
        """
        return embed.add_field(name="**General Stats:**", value=message)

    
    def __get_character_equipment(self, embed, server_id, character_id):
        payload = f"https://api.dfoneople.com/df/servers/{server_id}/characters/{character_id}/equip/equipment?apikey={self.api_key}"
        response = requests.get(payload).json()
        equipped_equipment = []
        for equipment in response["equipment"]:
            reinforce = "" if equipment["reinforce"] == 0 else f"+{equipment['reinforce']}"
            option_level_total = f"(Option Lv.: **{equipment['growInfo']['total']['level']}**)" if "growInfo" in equipment else ""
            equipped_equipment.append(f"{ky.BULLET.value} **{equipment['slotName']}:** {equipment['itemName']} {option_level_total}")
        return embed.add_field(name="**Equipment:**", value="\n".join(equipped_equipment))


    def __get_character_stats(self, embed, server_id, character_id):
        payload = f"https://api.dfoneople.com/df/servers/{server_id}/characters/{character_id}/status?apikey={self.api_key}"
        response = requests.get(payload).json()
        if not response["status"]:
            return

        base_stats = []
        for i in range(8):
            stat_name = response['status'][i]['name']
            stat_value = f"{response['status'][i]['value']:,}"
            if "Crit" in stat_name:
                stat_value += "%"
            base_stats.append(f"{ky.BULLET.value} **{stat_name}**: {stat_value}")

        damage_stats = []
        for i in range(8, 13):
            stat_name = response['status'][i]['name']
            stat_value = f"{response['status'][i]['value']:,}"
            if "Crit" in stat_name:
                stat_value += "%"
            damage_stats.append(f"{ky.BULLET.value} **{stat_name}**: {stat_value}")

        for i in range(33, 35):
            stat_name = response['status'][i]['name']
            stat_value = f"{response['status'][i]['value']:,}"
            damage_stats.append(f"{ky.BULLET.value} **{stat_name}**: {stat_value}")

        elemental_stats = []
        for i in range(23,31):
            stat_name = response['status'][i]['name']
            stat_value = f"{response['status'][i]['value']:,}"
            elemental_stats.append(f"{ky.BULLET.value} **{stat_name}**: {stat_value}")

        embed.add_field(name="**Base Stats:**", value="\n".join(base_stats))
        embed.add_field(name="**Damage Stats:**", value="\n".join(damage_stats))
        embed.add_field(name="**Elemental Stats:**", value="\n".join(elemental_stats))
        return embed


    @dfo.command(name = "character", description = "Pulls up information about a specific character")
    @app_commands.describe(name = "The name of the character who you want to pull up information on.")
    async def get_character_info(self, interaction: discord.Interaction, name: str, server: typing.Literal["cain", "sirocco", "all"] = "all"):
        payload = f"https://api.dfoneople.com/df/servers/{server}/characters?characterName={name}&limit=1&apikey={self.api_key}"
        response = requests.get(payload).json()

        if not response or "error" in response or not response["rows"]:
            if server == "all":
                server = "DFO Global"
            embed = self.bot.create_error_response(message=f"No character named **{name}** on **{server.title()}** was found!")
            embed.set_thumbnail(url=self.error_thumbnail)
            await interaction.response.send_message(embed=embed)
            return

        print(response)
        response = response["rows"][0]
        server_id = response["serverId"]
        character_id = response["characterId"]
        description = response["jobGrowName"]
        if response["fame"]:
            description = f"{ky.FAME.value} **{response['fame']:,}** " + description

        embed = discord.Embed(title = f"{name}", description = description, color = interaction.user.color)
        embed.set_footer(text=f"Character ID: {character_id}")

        embeds = [
            self.__get_character_base_stats(deepcopy(embed), server_id, character_id),
            self.__get_character_equipment(deepcopy(embed), server_id, character_id),
            self.__get_character_stats(deepcopy(embed), server_id, character_id)
        ]
        embeds = list(filter(None,embeds))
        await self.bot.create_paginated_embed().start(interaction, pages=embeds)


    def get_item_description(self, item):
        descriptions = []
        if item["itemExplainDetail"]:
            descriptions.append(item["itemExplainDetail"])
        elif item["itemExplain"]:
            descriptions.append(item["itemExplain"])
        if item["itemFlavorText"]:
            descriptions.append(f"*{item['itemFlavorText']}*")
        return "\n".join(descriptions)


    def get_equipment_stats(self, item, embed):
        stats = []
        for stat in item["itemStatus"]:
            if stat["value"] != "none":
                stats.append(f"{ky.BULLET.value} **{stat['name'].title()}:** {stat['value']}")
        return "\n".join(stats)


    @dfo.command(name="item", description="Query for item information.")
    @app_commands.describe(
        name="The name of the item",
        pattern="The search pattern to use. Defaults to match, which will only look for a name that matches the given name."
    )
    async def get_item(self, interaction: discord.Interaction, name: str, pattern: typing.Literal["match", "front", "full"] = "match"):
        payload = f"https://api.dfoneople.com/df/items?itemName={name}&wordType={pattern}&limit=1&apikey={self.api_key}"
        response = requests.get(payload).json()

        if not response or "error" in response or not response["rows"]:
            embed = self.bot.create_error_response(message=f"Could not find any search results for **{name}**!")
            embed.set_thumbnail(url=self.error_thumbnail)
            await interaction.response.send_message(embed=embed)
            return

        item_id = response["rows"][0]["itemId"]
        detailed_payload = f"https://api.dfoneople.com/df/items/{item_id}?apikey={self.api_key}"
        item = requests.get(detailed_payload).json()

        embeds = []
        item_name = item["itemName"]
        item_img_url = f"https://img-api.dfoneople.com/df/items/{item_id}"
        embed = discord.Embed(title=f"**{item['itemName']}**", description=f"Level {item['itemAvailableLevel']} {item['itemTypeDetail']}")
        embed.set_footer(text=f"Item ID: {item_id}")
        embed.set_thumbnail(url=item_img_url)

        embed_1 = deepcopy(embed)
        if "itemStatus" in item:
            embed_1.add_field(name="**Stats:**", value=self.get_equipment_stats(item, embed_1), inline=False)

        description = self.get_item_description(item)
        if description:
            embed_1.add_field(name="**Description:**", value=description, inline=False)

        if "growInfo" in item:
            embed_2 = deepcopy(embed)
            growth_options = item["growInfo"]["options"]
            i = 1
            for growth_option in growth_options:
                damage_value = growth_option['damage']
                buff_power = growth_option['buff']
                option_detail = growth_option['explainDetail']
                embed_2.add_field(name=f"**Option {i}:**", value=f"**Damage Value:** {damage_value}\n**Buff Power:** {buff_power}\n{option_detail}", inline=False)
                i += 1
            await self.bot.create_paginated_embed().start(interaction, pages=[embed_1, embed_2])
        else:
            await interaction.response.send_message(embed = embed_1)

        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DFO(bot))