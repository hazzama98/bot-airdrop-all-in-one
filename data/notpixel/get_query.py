import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from telethon.sync import TelegramClient
from telethon import functions
from urllib.parse import unquote
import sqlite3

# Ensure all necessary imports are present here

def load_api_credentials():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(root_dir, 'env.txt')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            api_id = None
            api_hash = None
            for line in lines:
                if line.startswith('API_ID='):
                    api_id = line.split('=')[1].strip()
                elif line.startswith('API_HASH='):
                    api_hash = line.split('=')[1].strip()
            if api_id and api_hash:
                return api_id, api_hash
    print("[!] API credentials not found or incomplete in env.txt")
    return None, None

def get_available_sessions():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sessions_dir = os.path.join(root_dir, 'sessions')
    if not os.path.exists(sessions_dir):
        print(f"[!] Folder sessions tidak ditemukan di: {sessions_dir}")
        return []
    sessions = [f.split('.')[0] for f in os.listdir(sessions_dir) if f.endswith('.session')]
    if not sessions:
        print(f"[!] Tidak ada file .session ditemukan di folder: {sessions_dir}")
    return sessions

async def get_web_app_data(session_name):
    api_id, api_hash = load_api_credentials()
    if not api_id or not api_hash:
        print("[!] API credentials tidak ditemukan. Silakan periksa file env.txt Anda.")
        return None

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    session_path = os.path.join(root_dir, 'sessions', session_name)

    try:
        async with TelegramClient(session_path, api_id, api_hash) as client:
            try:
                notcoin = await client.get_entity("notpixel")
                msg = await client(functions.messages.RequestWebViewRequest(
                    peer=notcoin,
                    bot=notcoin,
                    platform="android",
                    url="https://notpx.app/"
                ))
                webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D","=").split('&tgWebAppVersion=')[0].replace("%26","&")
                user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
                webappdata_global = webappdata_global.replace(user_data, unquote(user_data))
                return webappdata_global
            except Exception as e:
                print(f"[!] Error: {str(e)}")
                return None
    except sqlite3.OperationalError as e:
        print(f"[!] Tidak dapat membuka file database sesi: {str(e)}")
        print(f"[!] Pastikan file sesi ada di: {session_path}")
        return None
    except Exception as e:
        print(f"[!] Error tidak terduga saat membuka sesi: {str(e)}")
        return None

async def create_query_id():
    api_id, api_hash = load_api_credentials()
    if not api_id or not api_hash:
        print("[!] API credentials tidak ditemukan. Silakan periksa file env.txt di direktori root.")
        return

    sessions = get_available_sessions()
    if not sessions:
        print("[!] Tidak ada sesi yang tersedia. Silakan buat sesi terlebih dahulu.")
        return

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    query_file_path = os.path.join(root_dir, 'query/notpixel.txt')
    
    all_webappdata = []

    for session_name in sessions:
        webappdata = await get_web_app_data(session_name)
        if webappdata:
            all_webappdata.append(webappdata)
            print(f"[+] Query ID untuk sesi {session_name} berhasil dibuat")
        else:
            print(f"[!] Gagal mengambil WebAppData untuk sesi {session_name}")

    if all_webappdata:
        os.makedirs(os.path.dirname(query_file_path), exist_ok=True)
        with open(query_file_path, 'w') as f:
            f.write('\n'.join(all_webappdata))
        print(f"[+] Semua Query ID telah berhasil disimpan ke {query_file_path}")
    else:
        print("[!] Tidak ada WebAppData yang berhasil diambil")

if __name__ == "__main__":
    asyncio.run(create_query_id())
