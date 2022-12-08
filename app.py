import random
import string
from urllib import parse

import requests
from flask import Flask, request, redirect, session, url_for

import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SESSION_SECRET
FIVE_DON_BOT_SECRET = settings.FIVE_DON_BOT_SECRET
FIVE_DON_BOT_TOKEN = settings.FIVE_DON_BOT_TOKEN
DEVELOPMENT = settings.DEVELOPMENT

DISCORD_API_BASE_URL = 'https://discord.com/api/'
API_ENDPOINT = 'https://discord.com/api/v10'


@app.route('/neo-miyako/2fa')
def neo_miyako_auth():
    code = request.args.get("code")
    if code is None:
        state = random_strings(n=19)
        session['state'] = state
        if not DEVELOPMENT:
            return redirect(
                f'https://discord.com/api/oauth2/authorize?client_id=718034684533145605&redirect_uri=https%3A%2F%2Fauth'
                f'.alpaca131.com%2Fneo-miyako%2F2fa&response_type=code&scope=identify&state={state}')
        else:
            return redirect(f"https://discord.com/api/oauth2/authorize?client_id=718034684533145605&redirect_uri=http%"
                            f"3A%2F%2F100.85.179.122%3A5000%2Fneo-miyako%2F2fa&response_type=code&scope=identify&state={state}")
    if session["state"] != request.args.get("state"):
        return "Authorization failed.", 401
    res_token = exchange_code(code=code, redirect_url=url_for('neo_miyako_auth', _external=True),
                              client_id=718034684533145605, client_secret=FIVE_DON_BOT_SECRET, scope="identify")
    token = res_token['access_token']
    res_info = requests.get(DISCORD_API_BASE_URL + 'users/@me', headers={'Authorization': f'Bearer {token}'})
    res_dict = res_info.json()
    if res_dict["mfa_enabled"] is False:
        return "二段階認証を有効にしてから再度お試しください。"
    user_id = int(res_dict['id'])
    r = requests.get(DISCORD_API_BASE_URL + f"/guilds/484102468524048395/members/{user_id}",
                     headers={"authorization": f"Bot {FIVE_DON_BOT_TOKEN}"})
    r_dict = r.json()
    roles: list = r_dict["roles"]
    roles.append(873017896983482379)
    requests.patch(DISCORD_API_BASE_URL + f"/guilds/484102468524048395/members/{user_id}",
                   json={"roles": roles}, headers={"authorization": f"Bot {FIVE_DON_BOT_TOKEN}"})
    return "正常に付与されました。"


def exchange_code(code, redirect_url, client_id, client_secret, scope):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_url,
        'scope': scope
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('https://discord.com/api/oauth2/token', data=parse.urlencode(data), headers=headers)
    r.raise_for_status()
    return r.json()


def random_strings(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


if __name__ == '__main__':
    app.run(threaded=True)
