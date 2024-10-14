import sys
import os
import asyncio
import json
import random
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bot.utils import loading_animation, clear_terminal, print_header, log_message, Fore
from get_query import create_query_id

from urllib.parse import parse_qs, unquote
from colorama import Style, init, Fore
from tomarket import Tomarket, print_timestamp


async def load_credentials():
    try:
        with open('query/tomarket.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        if not queries:
            raise FileNotFoundError
        return queries
    except FileNotFoundError:
        log_message("File 'tomarket.txt' not found or empty. Generating new query ID...", status="info")
        await create_query_id()
        return await load_credentials()
    except Exception as e:
        log_message(f"An error occurred while loading credentials: {str(e)}", status="error")
        return []

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def get(id):
    try:
        with open("data/tomarket/tokens.json", "r") as file:
            tokens = json.load(file)
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]
    except FileNotFoundError:
        log_message("File 'tokens.json' not found.", status="error")
        return None

def save(id, token):
    try:
        with open("data/tomarket/tokens.json", "r") as file:
            tokens = json.load(file)
    except FileNotFoundError:
        tokens = {}
    tokens[str(id)] = token
    with open("data/tomarket/tokens.json", "w") as file:
        json.dump(tokens, file, indent=4)

async def generate_token():
    tom = Tomarket()
    queries = await load_credentials()
    total = len(queries)
    for index, query in enumerate(queries, 1):
        parse = parse_query(query)
        user = parse.get('user')
        await clear_terminal()
        await print_header()
        log_message(f"Processing Account {index}/{total}: {user.get('username', '')}", status="info")
        token = get(user['id'])
        if token is None:
            await loading_animation("Generating token...", 2)
            token = tom.user_login(query)
            save(user.get('id'), token)
            log_message("Token generation completed successfully.", status="success")

async def main():
    init(autoreset=True)
    tom = Tomarket()
    
    auto_task = 'y'
    auto_game = 'y'
    random_number = 'y'
    free_raffle = 'y'
    used_stars = '1'
    
    while True:
        queries = await load_credentials()
        if not queries:
            log_message("No valid queries found. Generating new query ID...", status="warning")
            await create_query_id()
            queries = await load_credentials()
            if not queries:
                log_message("Failed to generate query ID. Exiting program.", status="error")
                return

        total = len(queries)
        delay = int(3 * random.randint(3700, 3750))
        start_time = time.time()
        
        await generate_token()
        
        for index, query in enumerate(queries, 1):
            mid_time = time.time()
            remaining = delay - (mid_time - start_time)
            parse = parse_query(query)
            user = parse.get('user')
            token = get(user['id'])
            if token is None:
                token = tom.user_login(query)
                if token is None:
                    log_message(f"Invalid token for account {user.get('username', '')}. Generating new query ID...", status="warning")
                    await create_query_id()
                    break
                save(user.get('id'), token)
                time.sleep(2)
            log_message(f"Processing Account {index}/{total}: {parse.get('user')['username']}", status="info")
            tom.rank_data(token=token, selector=used_stars)
            await loading_animation("Processing...", 2)
            tom.claim_daily(token=token)
            await loading_animation("Processing...", 2)
            tom.start_farm(token=token)
            await loading_animation("Processing...", 2)
            if free_raffle == "y":
                tom.free_spin(token=token, query=query)
            await loading_animation("Processing...", 2)
        
        if auto_task == 'y':
            for index, query in enumerate(queries, 1):
                mid_time = time.time()
                remaining = delay - (mid_time - start_time)
                if remaining <= 0:
                    break
                parse = parse_query(query)
                user = parse.get('user')
                token = get(user['id'])
                if token is None:
                    token = tom.user_login(query)
                log_message(f"Processing Account {index}/{total}: {user.get('username', '')}", status="info")
                tom.list_tasks(token=token, query=query)
                time.sleep(2)   
                
        if auto_game == 'y':
            for index, query in enumerate(queries, 1):
                mid_time = time.time()
                remaining = delay - (mid_time - start_time)
                if remaining <= 0:
                    break
                parse = parse_query(query)
                user = parse.get('user')
                token = get(user['id'])
                if token is None:
                    token = tom.user_login(query)
                log_message(f"Processing Account {index}/{total}: {user.get('username', '')}", status="info")
                tom.user_balance(token=token, random_number=random_number)
                time.sleep(2)

        end_time = time.time()
        remaining = delay - (end_time - start_time)
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        log_message(f"Restarting in {int(hours)}h {int(minutes)}m {int(seconds)}s", status="info")
        if remaining > 0:
            await loading_animation(f"Waiting for restart...", remaining)

async def start():
    await clear_terminal()
    await print_header()
    
    log_message("Initializing process...", status="info")
    log_message("Generating query ID...", status="info")
    await create_query_id()
    
    log_message("Executing main function...", status="info")
    await main()

if __name__ == '__main__':
    try:
        asyncio.run(start())
    except Exception as e:
        log_message(f"An error occurred: {e}", status="error")
    except KeyboardInterrupt:
        log_message("Process terminated by user.", status="info")
        sys.exit(0)
