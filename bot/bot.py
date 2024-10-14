import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import asyncio
import subprocess
from bot.utils import night_sleep, Colors, loading_animation, print_header, clear_terminal
from telethon.sync import TelegramClient
from data.notpixel.get_query import get_web_app_data
import random

async def process():
    while True:
        await clear_terminal()
        await print_header()
        print("\nMain Menu:")
        print("1. Add API ID and Hash")
        print("2. Add account session")
        print("3. Bot Menu")
        print("4. Bot All in One")  # Tambahkan opsi Bot All in One
        print("5. Setting")  # Tambahkan opsi Setting
        print("6. Exit")
        
        option = input("Enter your choice: ")
        
        if option == "1":
            await add_api_credentials()
        elif option == "2":
            await add_session()
        elif option == "3":
            await bot_menu()
        elif option == "4":
            await bot_all_in_one()  # Tambahkan fungsi untuk Bot All in One
        elif option == "5":
            await setting_menu()  # Tambahkan fungsi untuk menu Setting
        elif option == "6":
            print("Exiting...")
            break
        else:
            print("[!] Invalid option. Please try again.")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        await loading_animation("Returning to main menu", random.uniform(0.5, 2))

async def setting_menu():
    while True:
        await clear_terminal()
        await print_header()
        print("\nSetting Menu:")
        print("1. Reset API Credentials")
        print("2. Reset Session")
        print("3. Return to Main Menu")
        
        option = input("Enter your choice: ")
        
        if option == "1":
            await reset_api_credentials()
        elif option == "2":
            await reset_session()
        elif option == "3":
            return
        else:
            print("[!] Invalid option. Please try again.")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        await loading_animation("Processing choice", random.uniform(0.5, 2))

async def bot_all_in_one():
    # Implementasi untuk Bot All in One
    print("Bot All in One functionality is not yet implemented.")
    await asyncio.sleep(2)

async def bot_menu():
    # Periksa apakah ada sesi yang tersedia
    if not os.path.exists("sessions") or not any(f.endswith(".session") for f in os.listdir("sessions/")):
        print("[!] No sessions found. Please add a session first.")
        await asyncio.sleep(2)  # Beri waktu untuk membaca pesan
        return  # Kembali ke menu utama jika tidak ada sesi

    while True:
        await clear_terminal()
        await print_header()  # Tambahkan await di sini
        print("\nBot Menu:")
        print("1. NotPixel")
        print("2. BirdX")
        print("3. Tomarket")  # Tambahkan opsi Tomarket
        print("4. Return to Main Menu")
        
        option = input("Enter your choice: ")
        
        if option == "1":
            await notpixel_menu()
        elif option == "2":
            await birdx_menu()
        elif option == "3":
            await tomarket_menu()  # Tambahkan fungsi untuk menu Tomarket
        elif option == "4":
            return
        else:
            print("[!] Invalid option. Please try again.")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        await loading_animation("Processing choice", random.uniform(0.5, 2))

async def notpixel_menu():
    while True:
        await clear_terminal()
        await print_header()  # Tambahkan await di sini
        print("\nNotPixel Menu:")
        print("1. Create Query ID")
        print("2. Run BOT")
        print("3. Return to Bot Menu")
        
        option = input("Enter your choice: ")
        
        if option == "1":
            await create_query_id("notpixel")
        elif option == "2":
            await run_bot("notpixel")
        elif option == "3":
            return
        else:
            print("[!] Invalid option. Please try again.")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        await loading_animation("Processing choice", random.uniform(0.5, 2))

async def birdx_menu():
    while True:
        await clear_terminal()
        await print_header()  # Tambahkan await di sini
        print("\nBirdX Menu:")
        print("1. Create Query ID")
        print("2. Run BOT")
        print("3. Return to Bot Menu")
        
        option = input("Enter your choice: ")
        
        if option == "1":
            await create_query_id("birdx")
        elif option == "2":
            await run_bot("birdx")
        elif option == "3":
            return
        else:
            print("[!] Invalid option. Please try again.")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        await loading_animation("Processing choice", random.uniform(0.5, 2))

async def tomarket_menu():
    while True:
        await clear_terminal()
        await print_header()  # Tambahkan await di sini
        print("\nTomarket Menu:")
        print("1. Create Query ID")
        print("2. Run BOT")
        print("3. Return to Bot Menu")
        
        option = input("Enter your choice: ")
        
        if option == "1":
            await create_query_id("tomarket")
        elif option == "2":
            await run_bot("tomarket")
        elif option == "3":
            return
        else:
            print("[!] Invalid option. Please try again.")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        await loading_animation("Processing choice", random.uniform(0.5, 2))

async def create_query_id(bot_type):
    module = __import__("data.notpixel.get_query", fromlist=["create_query_id"])
    
    await loading_animation(f"Creating Query ID for {bot_type}", random.uniform(0.5, 2))
    await module.create_query_id()

async def run_bot(bot_type):
    core_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', bot_type, 'core.py')
    
    if not os.path.exists(core_path):
        print(f"[!] File core.py untuk {bot_type} tidak ditemukan di {core_path}")
        return

    await loading_animation(f"Menjalankan BOT {bot_type}", random.uniform(0.5, 2))
    subprocess.run([sys.executable, core_path])

# Other functions (add_api_credentials, add_session, reset_api_credentials, reset_session) 
# also need to be changed to async and add loading_animation

async def add_api_credentials():
    api_id = input("Enter API ID: ")
    api_hash = input("Enter API Hash: ")
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env.txt')
    with open(env_path, "w") as f:
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
    await loading_animation("Saving API credentials", random.uniform(0.5, 2))
    print("[+] API credentials successfully saved in env.txt file.")

async def add_session():
    name = input("\nEnter Session name: ")
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    if not any(name in i for i in os.listdir("sessions/")):
        api_id, api_hash = await load_api_credentials()
        if api_id and api_hash:
            client = TelegramClient("sessions/" + name, api_id, api_hash)
            await client.start()
            await client.disconnect()
            await loading_animation("Saving session", random.uniform(0.5, 2))
            print(f"[+] Session {name} {Colors.GREEN}successfully saved{Colors.END}.")
        else:
            print("[!] API credentials not found. Please add them first.")
    else:
        print(f"[x] Session {name} {Colors.RED}already exists{Colors.END}.")

async def load_api_credentials():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env.txt')
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            api_id = lines[0].strip().split("=")[1]
            api_hash = lines[1].strip().split("=")[1]
        return api_id, api_hash
    else:
        return None, None

async def reset_api_credentials():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env.txt')
    if os.path.exists(env_path):
        os.remove(env_path)
        await loading_animation("Resetting API credentials", random.uniform(0.5, 2))
        print("[+] API credentials successfully reset.")
    else:
        print("[!] env.txt file not found. Nothing to reset.")

async def reset_session():
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    sessions = [f for f in os.listdir("sessions/") if f.endswith(".session")]
    if not sessions:
        print("[!] No sessions found.")
        return
    print("Available sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session[:-8]}")
    choice = input("Enter the number of the session you want to reset: ")
    try:
        session_to_reset = sessions[int(choice) - 1]
        os.remove(os.path.join("sessions", session_to_reset))
        await loading_animation("Resetting session", random.uniform(0.5, 2))
        print(f"[+] Session {session_to_reset[:-8]} successfully reset.")
    except (ValueError, IndexError):
        print("[!] Invalid choice. Please try again.")

# Change main function to async
async def main():
    await process()

# Run main function with asyncio
if __name__ == "__main__":
    asyncio.run(main())
