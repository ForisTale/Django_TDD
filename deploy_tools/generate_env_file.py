import random
import os


secret_key = "".join(random.SystemRandom().choices(
    "abcdefghijklmnopqrstuvwxyz0123456789", k=50
))

path = os.getcwd()
path = path[:-13]
host = os.path.basename(path)

with open(f"{path}/.env", "w+") as env_file:
    env_file.write("DJANGO_SECRET_KEY="+secret_key+"\n")
    env_file.write("SITE_NAME="+host+"\n")
