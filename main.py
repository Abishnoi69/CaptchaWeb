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
async def verify(chat_id: str = None):
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
  function onSubmit(token) {
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
		<script src="https://www.google.com/recaptcha/api.js"></script>
		<script>{redirect}</script>
	</head>
	<body>
		<form action="/validate_captcha" method="post" id="form">
			<img src="https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f916.svg" height="20px" width="20px" alt="robot" /><br />
			<h1>Are you a human?</h1><br />
			<i>Click button below to join the group chat!</i>
			<input type="hidden" name="chat_id" value="{chat_id}" />
			<button class="g-recaptcha" data-sitekey="{config['recaptchav3']['SITE_KEY']}" data-callback='onSubmit' data-action='submit'>Submit</button>
		</form>
	</body>
</html>
	'''
	return HTMLResponse(text)

@app.post("/validate_captcha")
async def validate_captcha(r: Request):
	token = (await r.form())['g-recaptcha-response']
	chat_id = (await r.form())['chat_id']
	ip = r.client.host
	url = 'https://www.google.com/recaptcha/api/siteverify'
	body = {'response': token, 'secret': config['recaptchav3']['SECRET_KEY'], 'remote_ip': ip}
	result = requests.post(url, data=body).json()
	result["chat_id"] = chat_id
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
