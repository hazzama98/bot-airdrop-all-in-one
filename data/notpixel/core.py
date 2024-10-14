import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
import json
import time
import random
from setproctitle import setproctitle
from convert import get
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse
import subprocess
import asyncio
from bot.utils import loading_animation, clear_terminal, print_header

url = "https://notpx.app/api/v1"

# Activity parameters
WAIT = 180 * 3
DELAY = 1

# Image dimensions
WIDTH = 1000
HEIGHT = 1000
MAX_HEIGHT = 50

# Initialize colorama for colored output
init(autoreset=True)

setproctitle("notpixel")

# Retrieve image configuration
image = get("")

# Define color mapping
c = {
    '#': "#000000",
    '.': "#3690EA",
    '*': "#ffffff"
}

def log_message(message, color=Style.RESET_ALL, status=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_color = Fore.GREEN if status == "success" else Fore.RED if status == "fail" else color
    status_text = f"[{status.upper()}]" if status else ""
    print(f"{Fore.CYAN}[{current_time}]{Style.RESET_ALL} {status_color}{status_text:<10}{Style.RESET_ALL} {message}")

def get_session_with_retries(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = get_session_with_retries()

def get_color(pixel, header):
    try:
        response = session.get(f"{url}/image/get/{str(pixel)}", headers=header, timeout=10)
        if response.status_code == 401:
            return -1
        return response.json()['pixel']['color']
    except KeyError:
        return "#000000"
    except requests.exceptions.Timeout:
        log_message("Request timed out. The server did not respond within the allocated time frame.", status="fail")
        return "#000000"
    except requests.exceptions.ConnectionError as e:
        log_message(f"A connection error occurred: {e}. Please check your network connectivity.", status="fail")
        return "#000000"
    except requests.exceptions.RequestException as e:
        log_message(f"An unexpected error occurred during the request: {e}. Please try again later.", status="fail")
        return "#000000"

async def claim(header):
    await loading_animation("Memulai proses klaim sumber daya", 3)
    try:
        response = session.get(f"{url}/mining/claim", headers=header, timeout=10)
        if response.status_code == 200:
            log_message("Operasi klaim sumber daya berhasil dilakukan.", status="success")
            return 0
        elif response.status_code == 401:
            log_message("Kesalahan otorisasi saat melakukan klaim.", status="fail")
            return -1
        else:
            log_message(f"Operasi klaim sumber daya gagal. Kode status: {response.status_code}", status="fail")
            return -1
    except requests.exceptions.RequestException as e:
        log_message(f"Operasi klaim sumber daya mengalami kesalahan: {e}. Silakan coba lagi.", status="fail")
        return -1

def get_pixel(x, y):
    return y * 1000 + x + 1

def get_pos(pixel, size_x):
    return pixel % size_x, pixel // size_x

def get_canvas_pos(x, y):
    return get_pixel(start_x + x - 1, start_y + y - 1)

start_x = 920
start_y = 386

async def paint(canvas_pos, color, header):
    data = {
        "pixelId": canvas_pos,
        "newColor": color
    }

    await loading_animation("Executing paint operation", 2)
    try:
        response = session.post(f"{url}/repaint/start", data=json.dumps(data), headers=header, timeout=10)
        x, y = get_pos(canvas_pos, 1000)

        if response.status_code == 400:
            log_message("Insufficient energy resources available for the paint operation.", status="fail")
            return False
        if response.status_code == 401:
            return -1

        log_message(f"Paint operation successfully executed at coordinates: {x},{y}", status="success")
        return True
    except requests.exceptions.RequestException as e:
        log_message(f"Paint operation encountered an error: {e}. Please attempt the operation again.", status="fail")
        return False

def extract_username_from_initdata(init_data):
    decoded_data = urllib.parse.unquote(init_data)
    username_start = decoded_data.find('"username":"') + len('"username":"')
    username_end = decoded_data.find('"', username_start)
    
    if username_start != -1 and username_end != -1:
        return decoded_data[username_start:username_end]
    
    return "Unknown"

def load_accounts_from_file(filename):
    try:
        with open(filename, 'r') as file:
            accounts = [f"initData {line.strip()}" for line in file if line.strip()]
        return accounts
    except FileNotFoundError:
        log_message(f"The file {filename} could not be located. Proceeding to create a new file...", status="info")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            pass  # Create an empty file
        return []

async def fetch_mining_data(header):
    await loading_animation("Mengambil statistik penambangan", 3)
    try:
        response = session.get(f"https://notpx.app/api/v1/mining/status", headers=header, timeout=10)
        if response.status_code == 200:
            data = response.json()
            user_balance = data.get('userBalance', 'Tidak diketahui')
            log_message(f"Saldo akun saat ini: {user_balance}", status="success")
            return 0
        elif response.status_code == 401:
            log_message("Tidak dapat mengambil data penambangan. Kesalahan otorisasi.", status="fail")
            return -1
        else:
            log_message(f"Tidak dapat mengambil data penambangan. Server merespons dengan kode status: {response.status_code}", status="fail")
            return -1
    except requests.exceptions.RequestException as e:
        log_message(f"Terjadi kesalahan saat mengambil data penambangan: {e}", status="fail")
        return -1

async def main(auth, account):
    headers = {'authorization': auth}

    try:
        mining_status = await fetch_mining_data(headers)
        if mining_status == -1:  # Menandakan kesalahan otorisasi
            log_message("Kesalahan otorisasi terdeteksi. Memperbarui query...", status="fail")
            return -1

        claim_status = await claim(headers)
        if claim_status == -1:  # Menandakan kesalahan otorisasi
            log_message("Kesalahan otorisasi terdeteksi saat mengklaim. Memperbarui query...", status="fail")
            return -1

        size = len(image) * len(image[0])
        order = [i for i in range(size)]
        random.shuffle(order)

        for pos_image in order:
            x, y = get_pos(pos_image, len(image[0]))
            await asyncio.sleep(0.05 + random.uniform(0.01, 0.1))
            try:
                await loading_animation("Analyzing pixel data", 1)
                color = get_color(get_canvas_pos(x, y), headers)
                if color == -1:
                    log_message("The session has been terminated unexpectedly.", status="fail")
                    break

                if image[y][x] == ' ' or color == c[image[y][x]]:
                    log_message(f"Pixel at coordinates {start_x + x - 1},{start_y + y - 1} has been skipped.", status="success")
                    continue

                result = await paint(get_canvas_pos(x, y), c[image[y][x]], headers)
                if result == -1:
                    log_message("The session has been terminated unexpectedly.", status="fail")
                    break
                elif result:
                    continue
                else:
                    break

            except IndexError:
                log_message(f"An index out of range error occurred at pos_image: {pos_image}, y: {y}, x: {x}", status="fail")

    except requests.exceptions.RequestException as e:
        log_message(f"Terjadi kesalahan jaringan pada akun {account}: {e}", status="fail")
        return -1

async def process_accounts(accounts):
    first_account_start_time = datetime.now()

    for account in accounts:
        username = extract_username_from_initdata(account)
        log_message(f"Memproses akun: {username}", status="info")
        log_message("=" * 50)

        result = await main(account, account)
        if result == -1:  # Sesi berakhir secara tidak terduga
            log_message("Sesi telah berakhir secara tidak terduga. Memulai proses pembaruan query_id...", status="info")
            await update_query_id()
            # Muat ulang akun setelah pembaruan
            accounts = load_accounts_from_file('query/notpixel.txt')
            if not accounts:
                log_message("Tidak ada akun yang dimuat setelah pembaruan query. Menghentikan proses.", status="fail")
                break
            log_message("Query telah diperbarui. Memulai ulang dengan akun baru.", status="info")
            return await process_accounts(accounts)  # Mulai ulang proses dengan akun yang baru dimuat
        
        log_message("=" * 50)

    time_elapsed = datetime.now() - first_account_start_time
    time_to_wait = timedelta(hours=1) - time_elapsed

    if time_to_wait.total_seconds() > 0:
        await loading_animation(f"Initiating cooldown period for {int(time_to_wait.total_seconds() // 60)} minutes", time_to_wait.total_seconds())
    else:
        log_message("Cooldown period is not necessary as processing time exceeded 1 hour", status="info")

async def update_query_id():
    log_message("Menjalankan get_query.py untuk memperbarui query_id...", status="info")
    try:
        result = subprocess.run(['python', 'data/notpixel/get_query.py'], check=True, capture_output=True, text=True)
        if "Query ID berhasil diperbarui" in result.stdout:
            log_message("Query ID telah berhasil diperbarui", status="success")
        else:
            log_message("Pembaruan Query ID gagal: " + result.stdout, status="fail")
    except subprocess.CalledProcessError as e:
        log_message(f"Upaya memperbarui Query ID gagal: {e.output}", status="fail")

def check_query_file():
    query_file = 'query/notpixel.txt'
    if not os.path.exists(query_file) or os.path.getsize(query_file) == 0:
        log_message("The query file is either non-existent or empty. Initiating the generation of a new query...", status="info")
        create_new_query()
    else:
        log_message("The query file has been located and contains data", status="info")
        
def create_new_query():
    try:
        subprocess.run(['python', 'data/notpixel/get_query.py'], check=True)
        log_message("A new query has been successfully generated", status="success")
    except subprocess.CalledProcessError:
        log_message("The attempt to generate a new query has failed", status="fail")
        exit(1)

def reset_query():
    query_file = 'query/notpixel.txt'
    if os.path.exists(query_file):
        os.remove(query_file)
    log_message("Query has been reset. Initiating the generation of a new query...", status="info")
    create_new_query()

if __name__ == "__main__":
    asyncio.run(clear_terminal())
    asyncio.run(print_header())
    log_message("Initializing NotPixel Bot", status="info")
    log_message("=" * 50)
    
    check_query_file()
    
    accounts = load_accounts_from_file('query/notpixel.txt')

    if not accounts:
        log_message("No accounts have been loaded. Please add accounts to query/notpixel.txt", status="fail")
    else:
        log_message(f"Successfully loaded {len(accounts)} accounts", status="success")
        while True:
            try:
                asyncio.run(process_accounts(accounts))
            except Exception as e:
                if "401 Unauthorized" in str(e):
                    log_message("An invalid query has been detected. Resetting and generating a new query...", status="fail")
                    reset_query()
                    accounts = load_accounts_from_file('query/notpixel.txt')
                else:
                    log_message(f"An error has occurred: {str(e)}", status="fail")
                    break
    
    log_message("Terminating NotPixel Bot", status="info")
    log_message("=" * 50)