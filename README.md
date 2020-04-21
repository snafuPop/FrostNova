<p align="center">
  <img width="870" height="550" src="https://i.imgur.com/kkXCoCg.png"><br>
</p>

# yvona Bot
Yvona Bot is a bot made for use with the VoIP platform [Discord](https://discordapp.com/). Features include an economy system, pulling information from select wikis and databases, and other fun commands.

This bot was mainly done as a fun side-project and to get my portfolio going, so it is amateur at best, in my opinion.

[![made-with-python](https://img.shields.io/badge/Language-Python%203.5.6-%234B8BBE.svg)](https://www.python.org/)
[![python-anywhere](https://img.shields.io/badge/Host-PythonAnywhere-%23139fd7.svg)](https://pythonanywhere.com/)
[![discord-rewrite](https://img.shields.io/badge/Discord.py-v1.0.0a-%232C2F33.svg)](https://github.com/Rapptz/discord.py/tree/rewrite)

## Getting Started
Simply [click here](https://discordapp.com/api/oauth2/authorize?client_id=547516876851380293&permissions=1861483585&scope=bot) to invite Yvona to your server. You must have server permission to invite bots in order to see your server on the drop-down menu.

## Commands
Commands are, by default, invoked by typing in `!` followed by a command's name. Typing in `!help` will cause y'shtola to direct message you a list of commands for you to browse. That list is dynamically updated based on the code and, therefore, will always be up to date.

Server administrators can choose to set a custom prefix to invoke commands. This custom prefix can be any string input, including emojis or mentions.

## Main Features
### DFO World Wiki Look-up
Yvona can look up item-pages on the [DFO World Wiki](http://wiki.dfo.world/view/Main_Page). This is helpful for when you need to look up an item outside of the game. This utilizes the [Media Wiki API](https://www.mediawiki.org/wiki/API:Main_page) in order to parse pages.

### Jisho.org Look-up
Yvona can search words on [Jisho](https://jisho.org/) using Jisho API. Returns up to 5 dictionary entries of the word, including part of speech, definition, kanji, furigana, and direct links to said entries.

### Adventure Economy
As a small side-game, Yvona also features an economy surrounding going on adventures. As you do more adventures, you can go on increasingly lucrative journeys and level-up! When you've accumulated enough coins, you can spend them on loot (WIP) or mini-games, such as slots.

This feature is heavily under work in order to make it more engaging for users — the goal is to encourage user activity within Discord channels.

You can even check the top 5 users in various categories. Aim to be the best!

### Notes
Users can write notes that can be viewed at any time. Notes are split into two categories: server-side and global, also known as announcements. Notes can only be accessed by members of that server, while announcements can be seen by all users who can access Yvona. You can use these to save information (such as ip addresses for multiplayer lobbies), write reminders, or remember funny moments between your friends.

## Feedback
If you have any questions, bug reports, feature requests, or need to get in touch with me, please use the [issue page](https://github.com/snafuPop/yvona/issues) to do so.

I would also greatly appreciate any donations. The cost of hosting is quite minimal, but would be helpful nonetheless. Go to to the [Patreon page](https://www.patreon.com/yvona) for more information.
