import os
import requests

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')


def verify_recaptcha(token, secret_key=None):
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': secret_key or RECAPTCHA_SECRET_KEY,
        'response': token
    }
    response = requests.post(url, data=payload)
    result = response.json()
    return result.get('success', False), result.get('score', 0.0), result.get('action', '')
