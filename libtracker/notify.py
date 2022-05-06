import requests

from libtracker.constants import CONFIG_TELEGRAM_USERS, CONFIG_TELEGRAM_BOT_TOKEN

_USER_CACHE = []


def send_notification(device: str, config: dict) -> None:
    """
    Send an HTTP POST request to the Telegram messaging API.

    :param device: The device name that has returned home.
    :param config: Global configuration object.
    :return: None
    """
    if not _USER_CACHE:
        if users := config.setdefault(CONFIG_TELEGRAM_USERS, None):
            if not isinstance(users, list):
                users = [users]
            for user in users:
                _USER_CACHE.append(user)
        else:
            # Telegram users have not been added. Cancel sending the notification.
            return

    if not (token := config.setdefault(CONFIG_TELEGRAM_BOT_TOKEN, None)):
        # No token has been set. Cancel sending the notification.
        return

    message = f"Device: {device} has just returned home"
    for user in _USER_CACHE:
        url = "https://api.telegram.org/bot" + token + '/sendMessage?chat_id=' + user + "&text=" + message
        response = requests.post(url)
