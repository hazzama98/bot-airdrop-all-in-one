import random
import sys
import os
import asyncio
import subprocess  # Import subprocess untuk menjalankan script eksternal

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bot.utils import loading_animation, clear_terminal, print_header, Colors

import requests
import time
import urllib.parse
import json
import base64
import socket
from datetime import datetime
from colorama import Fore, Style



headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
    'Origin': 'https://major.bot',
    'Priority': 'u=1, i',
}

def make_request(method, url, headers, json=None, params=None, data=None):
    retry_count = 0
    while True:
        time.sleep(2)
        if method.upper() == "GET":
            if params:
                response = requests.get(url, headers=headers, params=params)
            elif json:
                response = requests.get(url, headers=headers, json=json)
            else:
                response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            if json:
                response = requests.post(url, headers=headers, json=json)
            elif data:
                response = requests.post(url, headers=headers, data=data)
            else:
                response = requests.post(url, headers=headers)
        elif method.upper() == "PUT":
            if json:
                response = requests.put(url, headers=headers, json=json)
            elif data:
                response = requests.put(url, headers=headers, data=data)
            else:
                response = requests.put(url, headers=headers)
        else:
            raise ValueError("Invalid method. Only GET, PUT and POST are supported.")
        if response.status_code >= 500:
            if retry_count >= 4:
                print_(f"Status Code : {response.status_code} | Server Down/Something")
                return None
            retry_count += 1
        elif response.status_code >= 400:
            print_(f"Status Code : {response.status_code} | Failed to get Coin")
            return None
        elif response.status_code >= 200:
            return response.json()

def load_credentials():
    try:
        with open('query/major.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        if not queries:  # Jika file ada tapi kosong atau query tidak valid
            print_("File query/major.txt kosong atau query tidak valid. Mencoba generate ulang query...")
            generate_query()
            return load_credentials()  # Memuat ulang setelah generate
        return queries
    except FileNotFoundError:
        print_("File query/major.txt tidak ditemukan. Mencoba generate query...")
        generate_query()
        return load_credentials()  # Memuat ulang setelah generate
    except Exception as e:
        print_("Terjadi kesalahan saat memuat token:", str(e))
        return []

def generate_query():
    # Jalankan script get_query.py untuk generate query baru
    try:
        subprocess.run(['python', 'data/major/get_query.py'], check=True)
    except subprocess.CalledProcessError as e:
        print_(f"Error saat menjalankan script generate query: {e}")

def getuseragent(index):
    try:
        with open('useragent.txt', 'r') as f:
            useragent = [line.strip() for line in f.readlines()]
        if index < len(useragent):
            return useragent[index]
        else:
            return "Index out of range"
    except FileNotFoundError:
        return 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
    except Exception as e:
        return 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'



def postauth(query):
    url = 'https://major.bot/api/auth/tg/'
    data = {
        'init_data': query,
    }
    try:
        response = make_request('post', url, headers, json=data)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None
    
def getdaily(token):
    url ='https://major.bot/api/tasks/?is_daily=true'
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('get', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def gettask(token):
    url ='https://major.bot/api/tasks/?is_daily=false'
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('get', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def donetask(token, payload):
    url = 'https://major.bot/api/tasks/'
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('post', url, headers, json=payload)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def visit(token):
    url = 'https://major.bot/api/user-visits/visit/?'
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('post', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None
    
def donate(token, amount):
    url = 'https://major.bot/api/invoices/'
    payload = {"amount":amount, 
               "buy_for_user_id":6057140648}
    headers['Authorization'] = f"Bearer {token}"
    try:
        response_codes_done = range(200, 241)
        response_code_failed = range(500, 540)
        response_code_notfound = range(400, 440)
        response = requests.post(url, headers, payload)
        if response.status_code in response_codes_done:
            return response.json()
        elif response.status_code in response_code_failed:
            print_(f"Response Code : {response.status_code} | Server Down")
            return None
        elif response.status_code in response_code_notfound:
            print_(response.text)
            return None
        else:
            raise Exception(f'Unexpected status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def roulette(token):
    url ='https://major.bot/api/roulette/'
    headers['Authorization'] = f"Bearer {token}"

    try:
        response = make_request('post', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def join_squad(token):
    url = 'https://major.bot/api/squads/5373988314/join/?'
    headers['Authorization'] = f"Bearer {token}"

    try:
        response = make_request('post', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def get_squad(token):
    url = 'https://major.bot/api/squads/5373988314?'
    headers['Authorization'] = f"Bearer {token}"

    try:
        response = make_request('get', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def claim_coins(token):
    url = 'https://major.bot/api/bonuses/coins/'
    coins = 915
    payload = {"coins":coins}
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('post', url, headers, json=payload)
        if response is not None:
            if response.get('success') == True:
                print_(f"Success Claim Hold Coin {coins} Coins ")
            return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def swipe_coin(token):
    url = 'https://major.bot/api/swipe_coin/'
    coins = random.randint(2500,3000)
    payload = {"coins":coins}
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('post', url, headers, json=payload)
        if response is not None:
            if response.get('success') == True:
                print_(f"Success Claim Swipe Coin {coins} Coins ")
            return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None
    
def get_detail(token, tgid):
    url = f'https://major.bot/api/users/{tgid}/'
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('get', url, headers)
        return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def durev_combo(token, payload):
    url = 'https://major.bot/api/durov/'
    headers['Authorization'] = f"Bearer {token}"
    try:
        response = make_request('post', url, headers, json=payload)
        if response is not None:
            correct = response.get('correct',[])
            ds = len(correct)
            if ds == 4:
                print_(f'Combo Done !! Reward 5000')
            else:
                print_(f'Combo Failed !! combo : {correct}')
            return response
    except requests.exceptions.RequestException as e:
        print_(f'Error making request: {e}')
        return None

def print_(word):
    symbol = "[+]" if "Success" in word else "[-]" if "Error" in word or "Failed" in word else "[*]" if "Task" in word or "Status" in word else "[!]"
    print(f"{symbol} {word}")

def convert_time(unix_time):
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(unix_time))
    return formatted_time

async def main():
    selector_task = input("auto clear single task y/n : ").strip().lower()
    selector_daily = input("auto clear daily task y/n : ").strip().lower()
    while True:
        majors = 0
        delay_time = (8 * 3900)
        start_time = time.time()
        queries = load_credentials()
        sum = len(queries)
        for index, query in enumerate(queries):
            useragent = getuseragent(index)
            headers['User-Agent'] = useragent
            await clear_terminal()
            await print_header()
            print(f"""{Fore.BLUE}
╔═══════════════════════════════════════════╗
                  Account {index+1}   {Style.RESET_ALL}""")
            await loading_animation("Refreshing token...", 2) # Mengganti time.sleep(2)
            data_auth = postauth(query)
            if data_auth is not None:
                token = data_auth.get('access_token')
                user = data_auth.get('user')
                ratings = user.get('rating')
                id = user.get('id')
                squad_id = user.get('squad_id')

                detail = get_detail(token, id)
                if detail is not None:
                    ratings = detail.get('rating', 0)
                print(f"""{Fore.BLUE}
    {user.get('id')} | {user.get('first_name')} | {ratings}

╚═══════════════════════════════════════════╝{Style.RESET_ALL}""")                          
                majors += ratings

                await loading_animation("Checking squad membership...", 2) # Menambahkan loading baru
                if squad_id == None:
                    print_('No Have Squad')
                    await loading_animation("Joining squad...", 2) # Menambahkan loading baru
                    data_squad = join_squad(token)
                    if data_squad is not None:
                        print_("Join Squad Done")
                else:
                    data_squad = get_squad(token)
                    if data_squad is not None:
                        print_(f"Squad : {data_squad.get('name')} | Member : {data_squad.get('members_count')} | Ratings : {data_squad.get('rating')}")

                await loading_animation("Claiming coins...", 2) # Menambahkan loading baru
                claim_coins(token)
                await loading_animation("Swiping coins...", 2) # Menambahkan loading baru
                swipe_coin(token)

                await loading_animation("Spinning roulette...", 3) # Menambahkan loading baru
                data_roulette = roulette(token)
                if data_roulette is not None:
                    reward = data_roulette.get('rating_award')
                    if reward is not None:
                        print_(f"Success Reward Roulette : {data_roulette.get('rating_award')}")

                if selector_daily == "y":
                    print_('Get daily Task')
                    data_daily = getdaily(token)
                    if data_daily is not None:
                        if len(data_daily) > 0:
                            for daily in reversed(data_daily):
                                id = daily.get('id')
                                type = daily.get('type')
                                title = daily.get('title')
                                is_completed = daily.get('is_completed')
                                if 'stars' in title.lower():
                                    print_(f"Skip Task : {title}")
                                    continue
                                if 'promote' in title.lower():
                                    print_(f"Skip Task : {title}")
                                    continue
                                if title not in ["Donate rating", "Invite more Friends", "Boost Major channel", "Boost Roxman channel"]:
                                    if is_completed == False:
                                        await loading_animation("Completing task...", 2) # Menambahkan loading baru
                                        payload = {
                                            'task_id': id
                                        }
                                        data_done = donetask(token, payload)
                                        if data_done is not None:
                                            print_(f"Task : {daily.get('title')} | Reward : {daily.get('award')} | Status: {data_done.get('is_completed')}")
                        else:
                            print_('No have daily task')

                if selector_task == "y":
                    print_('Get Single Task')
                    data_task = gettask(token)
                    if data_task is not None:
                        if len(data_task) > 0:
                            for task in data_task:
                                id = task.get('id')
                                type = task.get('type')
                                title = task.get('title')
                                if title not in ["One-time Stars Purchase", "Binance x TON", "Status Purchase"]:
                                    await loading_animation("Processing task...", 2) # Menambahkan loading baru
                                    if type == 'code':
                                        payload = {"task_id":id,"payload":{"code":""}}
                                    else:
                                        payload = {
                                                    'task_id': id
                                                }
                                    data_done = donetask(token, payload)
                                    if data_done is not None:
                                            print_(f"Task : {title} | Reward : {task.get('award')} | Status: {data_done.get('is_completed')}")
                        else:
                            print_('No have single task')
                await loading_animation("Preparing next account...", 3) # Menambahkan loading baru
        end_time = time.time()
        total_time = delay_time - (end_time-start_time)
        print_(" ======================================================")
        print_(f"Total Account : {sum} | Total Ratings Majors: {majors}")
        print_(" ======================================================")
        print_delay(total_time)

def print_delay(delay):
    while delay > 0:
        now = datetime.now().isoformat(" ").split(".")[0]
        hours, remainder = divmod(delay, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\r{now} | Waiting Time: {round(hours)} hours, {round(minutes)} minutes, and {round(seconds)} seconds")
        sys.stdout.flush()
        time.sleep(1)
        delay -= 1
    print_("\nWaiting Done, Starting....\n")

def quest_main():
    queries = load_credentials()
    input_string = input("input number (ex:14,2,3,4) : ").strip().lower()
    input_youtube = input("input code from youtube : ").strip().lower()
    if input_string != 'n':
        input_data = [int(x) for x in input_string.split(",")]
        payload = {"choice_{}".format(i+1): value for i, value in enumerate(input_data)}
    for index, query in enumerate(queries):
        useragent = getuseragent(index)
        headers['User-Agent'] = useragent
        print(f"""{Fore.BLUE}
╔═══════════════════════════════════════════╗
                  Account {index+1}   {Style.RESET_ALL}""")
        time.sleep(1)
        data_auth = postauth(query)
        print_(f"refresh token....")
        time.sleep(2)
        if data_auth is not None:
            token = data_auth.get('access_token')
            user = data_auth.get('user')
            ratings = user.get('rating')
            id = user.get('id')
            squad_id = user.get('squad_id')
            detail = get_detail(token, id)
            if detail is not None:
                ratings = detail.get('rating', 0)
            print(f"""{Fore.BLUE}
    {user.get('id')} | {user.get('first_name')} {user.get('last_name')} | point : {ratings}

╚═══════════════════════════════════════════╝{Style.RESET_ALL}""")
            if input_string != 'n' :
                data_combo = durev_combo(token, payload)
            if input_youtube != 'n':
                print_('Get Single Task')
                data_task = gettask(token)
                if data_task is not None:
                    if len(data_task) > 0:
                        for task in data_task:
                            id = task.get('id')
                            type = task.get('type')
                            title = task.get('title')
                            if title not in ["One-time Stars Purchase", "Binance x TON", "Status Purchase"]:
                                time.sleep(2)
                                if type == 'code':
                                        payload = {"task_id":id,"payload":{"code":input_youtube}}
                                else:
                                    payload = {
                                                'task_id': id
                                            }
                                if 'youtube' in title.lower():
                                    data_done = donetask(token, payload)
                                    if data_done is not None:
                                            print_(f"Task : {title} | Reward : {task.get('award')} | Status: {data_done.get('is_completed')}")
                else:
                    print_('No have single task')

async def start():
    await clear_terminal()
    await print_header()
    print("\nCheat Bot Major:")
    print("1. Claim Daily")
    print("2. Quest Game")
    print("3. Return to Main Menu")
    selector = input("Select the one  : ").strip().lower()

    if selector == '1':
        await main()  # Menggunakan await di sini
    elif selector == '2':
        await quest_main()  # Pastikan quest_main juga adalah coroutine jika perlu
    else:
        from bot.menu import major_menu
        await major_menu()  # Pastikan major_menu juga adalah coroutine jika perlu

if __name__ == "__main__":
    asyncio.run(start())