import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

try:
	import tomllib
except ImportError:
	import tomli as tomllib

app = FastAPI()

config_path = "config.toml"
if not os.path.isfile(config_path):
	config = None
else:
	with open(config_path, 'rb') as f:
		config = tomllib.load(f)

@app.get("/")
async def verify(verify_id: str = None):
	css = '''
			body {
				--bg-color: var(--tg-theme-bg-color, #fff);
				font-family: sans-serif;
				background-color: var(--bg-color);
				color: var(--tg-theme-text-color, #222);
				font-size: 14px;
				margin: 0;
				padding: 0;
				color-scheme: var(--tg-color-scheme);
				text-align: center;
			}
	'''

	redirect = '''
  function turnstile_callback () {
	document.getElementById("form").submit();
  }
    '''

	text = f'''
<!DOCTYPE html>
<html>
	<head>
		<style>
			{css}
		</style>
		<script src="https://telegram.org/js/telegram-web-app.js?1"></script>
		<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" defer></script>
		<script>{redirect}</script>
	</head>
	<body>
		<form action="/validate_turnstile" method="post" id="form">
			<img src="https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f916.svg" height="20px" width="20px" alt="robot" /><br />
			<h1>Are you a human?</h1><br />
			<i>Complete CAPTCHA below to join the group chat!</i>
			<input type="hidden" name="verify_id" value="{verify_id}" />
			<div class="cf-turnstile" data-sitekey="{config['turnstile']['SITE_KEY']}" data-callback="turnstile_callback"></div>
		</form>
	</body>
</html>
	'''
	return HTMLResponse(text)

@app.post("/validate_turnstile")
async def con(r: Request):
	token = (await r.form())['cf-turnstile-response']
	verify_id = (await r.form())['verify_id']
	ip = r.client.host
	url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
	body = {'secret': config['turnstile']['SECRET_KEY'], 'response': token, 'remoteip': ip}
	result = requests.post(url, json=body).json()
	result["verify_id"] = verify_id
	text = '''
<!DOCTYPE html>
<html>
	<head>
        <script src="https://telegram.org/js/telegram-web-app.js?1"></script>
        <script>
            function myFunction() {
                Telegram.WebApp.ready();
                Telegram.WebApp.sendData("'''+str(result)+'''");
            }
        </script>
	</head>
	<body onload="myFunction()">
	</body>
</html>
	'''
	return HTMLResponse(text)
