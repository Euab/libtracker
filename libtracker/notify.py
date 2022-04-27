import requests

from libtracker.constants import CONFIG_TELEGRAM_USERS, CONFIG_TELEGRAM_BOT_TOKEN


def send_notification(device, config):
    users = [user for user in config[CONFIG_TELEGRAM_USERS]]
    token = config[CONFIG_TELEGRAM_BOT_TOKEN]

    message = f"Device: {device} has just returned home"
    for user in users:
        url = "https://api.telegram.org/bot" + token + '/sendMessage?chat_id=' + user + "&text=" + message
        response = requests.post(url)
