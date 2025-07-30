import random
import threading
import time
from collections import deque
from typing import Dict, Tuple

import config as const
from linkedin_api import Linkedin
from tqdm import tqdm


class APIClientManager:
    def __init__(self, apis: Dict[str, 'Linkedin'], cooldown_time=5):
        self.all_clients = apis
        self.available_clients = deque(apis.items())
        self.cooldown_time = cooldown_time
        self.lock = threading.Lock()
        self.client_available = threading.Condition(self.lock)

    def get_client(self) -> Tuple[str, 'Linkedin']:
        with self.client_available:
            while not self.available_clients:
                self.client_available.wait()
            email, client = random.choice(self.available_clients)
            self.available_clients.remove((email, client))
            return email, client

    def release_client(self, email: str, client: 'Linkedin'):
        def add_back_to_pool():
            time.sleep(random.randint(abs(self.cooldown_time - 5), self.cooldown_time + 5))
            with self.client_available:
                self.available_clients.append((email, client))
                self.client_available.notify()

        threading.Thread(target=add_back_to_pool).start()

def createClients() -> APIClientManager:
    apis = {}
    print("Creating clients...")
    pbar = tqdm(zip(const.LINKEDIN_EMAIL, const.LINKEDIN_PASSWORD))
    for uname, passwd in pbar:
        pbar.set_description(f"Logging in to {uname}")
        api = Linkedin(uname, passwd)
        time.sleep(5)
        apis[uname] = api

    apiManager = APIClientManager(apis, cooldown_time=const.COOLDOWN if const.COOLDOWN is not None else 5)
    return apiManager