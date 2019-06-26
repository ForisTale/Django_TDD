import random


secret_key = "".join(random.SystemRandom().choices(
    "abcdefghijklmnopqrstuvwxyz0123456789", k=50
))

print("DJANGO_SECRET_KEY="+secret_key)
