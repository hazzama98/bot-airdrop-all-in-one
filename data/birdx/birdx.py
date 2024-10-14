import base64
import json
import os
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime

import asyncio
from bot.utils import loading_animation, Colors

def log_message(message):
    timestamp = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{timestamp}] {message}")

def make_request(method, url, headers, json=None, data=None):
    retry_count = 0
    while True:
        time.sleep(2)
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, json=json)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json, data=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json, data=data)
        else:
            raise ValueError("Invalid HTTP method.")
        
        if response.status_code >= 420:
            if retry_count > 5:
                log_message(f"Error: Status Code {response.status_code} | Response: {response.text}")
                return None
            retry_count += 1
        elif response.status_code >= 400:
            log_message(f"Error: Status Code {response.status_code} | Response: {response.text}")
            return None
        elif response.status_code >= 200:
            return response.json()

class Birdx():
    def __init__(self):
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            # "telegramauth": f"tma {token}",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127", "Microsoft Edge WebView2";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "Referer": "https://birdx.birds.dog/home",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def get_user_info(self, query):
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        url = "https://api.birds.dog/user"
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def get_info(self, query):
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        url = 'https://api.birds.dog/minigame/incubate/info'
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    async def upgraded(self, query):
        url = 'https://api.birds.dog/minigame/incubate/upgrade'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            if response is not None:
                sec = 3600
                log_message(f"Upgrade successful. New level: {response.get('level',0)} | Estimated waiting time: {round(sec*response.get('duration',1))} seconds")
                await loading_animation("Waiting for upgrade completion", sec*response.get('duration',1))
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def confirm_upgrade(self, query):
        url = 'https://api.birds.dog/minigame/incubate/confirm-upgraded'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('post', url, headers)
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def clear_task(self, query):
        url = "https://api.birds.dog/project"
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            list_task_complete = self.check_task_completion(query)
            if response is not None:
                for task in response:
                    if task.get('is_enable'):
                        log_message(f"Task Name: {task.get('name','')}")
                        detail_task = task.get('tasks',[])
                        for detail in detail_task:
                            id = detail.get('_id',"")
                            if id in list_task_complete:
                                log_message(f"Task '{detail.get('title')}' status: Completed")
                            else:
                                log_message(f"Initiating task: {detail.get('title')}")
                                self.join_task(query, detail)

        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def check_task_completion(self, query):
        url = "https://api.birds.dog/user-join-task/"
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            list = []
            response = make_request('get', url, headers)
            if response is not None:
                for data in response:
                    task_id = data.get('taskId','')
                    list.append(task_id)
                return list
            else:
                return None
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def join_task(self, query, detail):
        url = 'https://api.birds.dog/project/join-task'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        payload = {"taskId":detail.get('_id'),
                   "channelId":detail.get('channelId'),
                   "slug":detail.get('slug'),
                   "point":detail.get('point')}
        try:
            list = []
            response = make_request('post', url, headers, json=payload)
            if response is not None:
                log_message(f"Task '{detail.get('title')}' status: {response.get('msg')}")
            return list
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def join_game(self, query):
        url = 'https://api.birds.dog/minigame/egg/join'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            if response is not None:
                data_turn = self.turn_game(query)
                turn = data_turn.get('turn')
                while True:
                    if turn <= 0:
                        data_claim_game = self.claim_game(query)
                        if data_claim_game is not None:
                            log_message("Total reward successfully claimed")
                        break
                    else:
                        data_play = self.play_game(query)
                        if data_play is not None:
                            result = data_play.get('result')
                            data_turn = self.turn_game(query)
                            if data_turn is not None:
                                total = data_turn.get('total')
                                turn = data_turn.get('turn')
                                log_message(f"Game round completed. Reward: {result} | Total accumulated reward: {total}")


        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def turn_game(self, query):
        url = 'https://api.birds.dog/minigame/egg/turn'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            return response

        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def play_game(self, query):
        url = 'https://api.birds.dog/minigame/egg/play'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def claim_game(self, query):
        url = 'https://api.birds.dog/minigame/egg/claim'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def mint_status(self, query):
        url = 'https://worm.birds.dog/worms/mint-status'
        headers = self.headers
        headers['authorization'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            if response is not None:
                data = response.get('data',{})
                nextMintTime = data.get('nextMintTime')
                status = data.get('status','')
                log_message(f"Worm minting status: {status}")
                if status == "MINT_OPEN":
                    data_mint = self.mint_worm(query)
                    if data_mint is not None:
                        minted = data_mint.get('minted',{})
                        message = data_mint.get('message','')
                        if message == 'SUCCESS':
                            log_message(f"Worm minting details: Type - {minted.get('type','')} | Reward - {minted.get('reward',0)}")
                        else:
                            log_message(f"Worm minting result: {message}")

                else:
                    if nextMintTime is not None:
                        dt_object = datetime.fromisoformat(nextMintTime.replace("Z", "+00:00"))
                        unix_time = int(dt_object.timestamp())
                        remaining = unix_time - time.time()
                        log_message(f'Time remaining until next worm minting opportunity: {round(remaining)} seconds')
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
    
    def mint_worm(self, query):
        url = 'https://worm.birds.dog/worms/mint'
        headers = self.headers
        headers['authorization'] = f"tma {query}"
        try:
            response = make_request('post', url, headers)
            return response
        except requests.RequestException as e:
            log_message(f"Error: Failed to fetch user data. Details: {e}")
            return None
