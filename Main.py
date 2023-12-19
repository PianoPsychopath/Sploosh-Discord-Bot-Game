import subprocess
import discord
from discord.ext import commands
import csv
import random 
import asyncio
from sploosh_game.variables import board_size, ship_sizes, empty, ship, hit, miss
from sploosh_game.sploosh_game import SplooshGame

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True  # Enable MESSAGE_CONTENT intent
intents.guilds = True  # Enable GUILD_MESSAGES intent


bot = commands.Bot(command_prefix='!', intents=intents)
bot_owner_id = 0#BOTOWNER ID
# Function to create or update user's dogtag in the rupees.csv file

def add_rupees(user_id, rupees):
    rows = []
    updated = False

    try:
        with open('rupees.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user_id):
                    row[1] = str(int(row[1]) + rupees)
                    updated = True
                rows.append(row)

        if not updated:
            rows.append([str(user_id), str(rupees)])

        with open('rupees.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    except FileNotFoundError:
        with open('rupees.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['User_ID', 'rupees'])
            writer.writerow([str(user_id), str(rupees)])

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
@bot.event
async def on_connect():
    print('Bot connected to Discord')

@bot.event
async def on_disconnect():
    print('Bot disconnected from Discord')


@bot.event  
async def is_bot_owner(ctx):
    if ctx.author.id == bot_owner_id:
        return True
    else:
        await ctx.send("You don't have permission to run this command.")
        return False

@bot.command()
@commands.check(is_bot_owner)  # Ensure only the bot owner can run this command
async def shutdown(ctx):
    await ctx.send("```Shutting down...```")
    await ctx.message.delete()
    await bot.close()

def get_rupees(user_id):
    try:
        with open('rupees.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['User_ID'] == str(user_id):
                    return int(row['rupees'])
    except FileNotFoundError:
        pass
    return 0  # Return 0 if user doesn't exist or CSV file doesn't exist

@bot.command()
async def rupees(ctx, member: discord.Member = None):
    try:
        if member is None:
            user_id = ctx.author.id
            rupees = get_rupees(user_id)
            await ctx.send(f'You have {rupees} rupees!')
        else:
            user_id = member.id
            rupees = get_rupees(user_id)
            await ctx.send(f'{member.display_name} has {rupees} rupees!')
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


# Command to give rupees to a user
@bot.command()
@commands.check(is_bot_owner)
async def give_rupees(ctx, member: discord.Member, rupees: int):
    add_rupees(member.id, rupees)
    await ctx.send(f'{rupees} rupees given to {member.display_name}!')
@bot.command()
async def sploosh(ctx):
    user_id = ctx.author.id
    
    user_rupees = get_rupees(user_id)
    
    # Check if the user has at least 20 rupees
    if user_rupees < 20:
        await ctx.send("Sorry, you need at least 20 rupees to play this game.")
        return
    add_rupees(user_id, -20)# Deduct 20 rupees from the user initiating the game
    game = SplooshGame()
    shots = 20
    message = await ctx.send(f"🦑Welcome to Sploosh💣! It costs 20 rupees to play! You have {shots}💣 shots. Say the coordinate like `A1` to aim at the enemy🦑.")
    board_message = await ctx.send(game.print_board())  # Display initial board
    shots_message = await ctx.send(f"Remaining shots: {shots}💣. Fire! Enter your target coordinates (e.g., A1):")
    game.print_ship_positions()

    while shots > 0:
        def check(message):
            return message.author == ctx.author and message.content.upper() in [f"{chr(65 + i)}{j + 1}" for i in range(board_size) for j in range(board_size)]

        try:
            shot = await bot.wait_for('message', check=check, timeout=30)
            shot_content = shot.content.upper()
            x, y = ord(shot_content[0]) - 65, int(shot_content[1:]) - 1  # Corrected x and y for proper matching with board labels
            result, shot_result = game.shoot(x, y)
            shots -= 1
            await shot.delete()
            await shots_message.edit(content=f"Remaining shots: {shots}. Fire!\n{shot_result}")  # Update remaining shots message
            if result:
                await board_message.edit(content=game.print_board())  # Update the board message with the current state
            if not game.ships:  # All ships destroyed
                await ctx.send("Congratulations! All enemies have been eliminated!")
                game.reveal_ships()  # Reveal the remaining ships
                await board_message.edit(content=game.print_board())  # Update the board message to reveal ships

                # Calculate and award rupees
                prize = game.get_total_prize(shots)
                add_rupees(ctx.author.id, prize)
                await ctx.send(f"You won {prize} rupees!")
                return  # End the game here
        except asyncio.TimeoutError:
            await ctx.send("Time's up! Game over.")
            break

    if shots == 0:
        await ctx.send("Out of shots! Game over.")
        game.reveal_ships()  # Reveal the remaining ships
        await board_message.edit(content=game.print_board())  # Update the board message

        # Calculate and award rupees
        prize = game.get_total_prize(shots)
        add_rupees(ctx.author.id, prize)
        await ctx.send(f"You won {prize} rupees!")



bot.run('BOT_TOKEN')
