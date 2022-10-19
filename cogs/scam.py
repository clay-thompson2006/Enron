import datetime
import config.config as config
import json
from cogs.timeout import timeout


async def scam_check(message):
    with open('database/blocked_links.json', 'r') as f1:
        scam_links = json.load(f1)    
    scam_links = scam_links['domains']
    for links in scam_links:
        if links in message.content:
            await timeout(message,message.author,reason=f"Sent scam link in {message.channel.name}")