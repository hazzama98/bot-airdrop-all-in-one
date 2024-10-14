import base64
import json
import sys
import os
import asyncio

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime
import subprocess
from bot.utils import loading_animation, clear_terminal, print_header, Colors
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

from birdx import Birdx

def log_message(message, status=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_icon = {
        "success": f"{Fore.GREEN}✓{Style.RESET_ALL}",
        "fail": f"{Fore.RED}✗{Style.RESET_ALL}",
        "info": f"{Fore.BLUE}ℹ{Style.RESET_ALL}",
        "warning": f"{Fore.YELLOW}⚠{Style.RESET_ALL}"
    }.get(status, "")
    
    print(f"{Fore.CYAN}[{current_time}]{Style.RESET_ALL} {status_icon} {message}")
 
def load_query():
    try:
        with open('query/birdx.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        if not queries:
            raise FileNotFoundError
        return queries
    except FileNotFoundError:
        log_message("birdx.txt file not found or empty. Generating new query...", status="info")
        create_new_query()
        return load_query()
    except Exception as e:
        log_message(f"Failed to retrieve Query: {str(e)}", status="error")
        return []

def create_new_query():
    log_message("Executing get_query.py to generate new query...", status="info")
    subprocess.run(["python", "data/birdx/get_query.py"])

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def format_remaining_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"Remaining Upgrade Time: {int(hours)}h {int(minutes)}m {int(seconds)}s"

async def main():
    await clear_terminal()
    await print_header()
    while True:
        birdx = Birdx()
        queries = load_query()
        total_accounts = len(queries)
        delay = int(2.5 * random.randint(3600, 3800))
        start_time = time.time()
        for index, query in enumerate(queries, start=1):
            
            log_message(f"Processing Account {index}/{total_accounts}", status="info")
            
            async def perform_action(action_name, action_func, *args):
                loading_task = asyncio.create_task(loading_animation(action_name, 3))
                try:
                    if asyncio.iscoroutinefunction(action_func):
                        result = await action_func(*args)
                    else:
                        result = action_func(*args)
                finally:
                    loading_task.cancel()
                    await asyncio.sleep(0.1)
                return result

            data_user_info = await perform_action("Retrieving User Details", birdx.get_user_info, query)
            
            if data_user_info is None:
                log_message('User Not Found or Query ID expired. Generating new query...', status="fail")
                create_new_query()
                return await main()  # Restart the main function with new queries
            
            username = data_user_info.get('telegramUserName', 'Unknown')
            telegram_id = data_user_info.get('telegramId', 'Unknown')
            telegram_age = data_user_info.get('telegramAge', 'Unknown')
            total_rewards = data_user_info.get('balance', 0)
            incubation_spent = data_user_info.get('incubationSpent', 0)
            log_message(f"Account Details | ID: {telegram_id} | Username: {username} | Account Age: {telegram_age} days | Total Rewards: {total_rewards}", status="info")

            if incubation_spent == 0:
                await perform_action("Performing Upgrade", birdx.upgraded, query)
            
            await perform_action("Acquiring Worm", birdx.mint_status, query)
            data_info = await perform_action("Retrieving Info", birdx.get_info, query)
            
            if data_info is not None:
                level = data_info.get('level', 0)
                status = data_info.get('status', 0)
                log_message(f"Level: {level} | Birds: {data_info.get('birds')}", status="info")
                upgraded_at = data_info.get('upgradedAt', 0) / 1000
                duration = data_info.get('duration', 0)
                now = time.time()
                upgrade_time = 3600 * duration
                if now >= (upgraded_at + upgrade_time):
                    if status == "confirmed":
                        await perform_action("Performing Upgrade", birdx.upgraded, query)
                    else:
                        await perform_action("Confirming Upgrade", birdx.confirm_upgrade, query)
                        if await perform_action("Retrieving Info", birdx.get_info, query) is not None:
                            log_message("Upgrade Confirmed", status="success")
                            await perform_action("Performing Upgrade", birdx.upgraded, query)
                else:
                    log_message(format_remaining_time((upgraded_at + upgrade_time) - now), status="info")
            
            await perform_action("Starting Task", birdx.clear_task, query)
            await perform_action("Playing Game", birdx.join_game, query)

        end_time = time.time()
        total_wait = delay - (end_time - start_time)
        if total_wait > 0:
            log_message(f"Processing completed for {total_accounts} accounts. Initiating cooldown period.", status="info")
            log_message(format_remaining_time(total_wait), status="info")
            await asyncio.sleep(total_wait)

if __name__ == "__main__":
    asyncio.run(main())
