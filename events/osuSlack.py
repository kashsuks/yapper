from osu import Client, GameModeStr
import os
from dotenv import load_dotenv

load_dotenv()


clientId = int(os.getenv("CLIENT_ID"))
secrete = os.getenv("CLIENT_SECRET")
redirect_url = None

client = Client.from_credentials(clientId, secrete, redirect_url)

user = client.get_user(os.getenv("OSU_ID"))
print(user)