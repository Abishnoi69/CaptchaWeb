async function handlePost(request, env) {
    const body = await request.formData();
    // Turnstile injects a token in "cf-turnstile-response".
    const token = body.get('cf-turnstile-response');
    const ip = request.headers.get('CF-Connecting-IP');
    const verify_id = body.get('verify_id');

    // Validate the token by calling the "/siteverify" API.
    let formData = new FormData();
    formData.append('secret', env.SECRET_KEY);
    formData.append('response', token);
    formData.append('remoteip', ip);

    const result = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
        body: formData,
        method: 'POST',
    });

    const outcome = await result.json();
    outcome['verify_id'] = verify_id;
    const res = `
<!DOCTYPE html>
<html lang="en">
    <head>
        <style>
            body {
                --bg-color: var(--tg-theme-bg-color, #fff);
                font-family: sans-serif;
                background-color: var(--bg-color);
                color: var(--tg-theme-text-color, #222);
                font-size: 14px;
                margin: 0;
                padding: 0;
                color-scheme: var(--tg-color-scheme);
            }
        </style>
        <script src="https://telegram.org/js/telegram-web-app.js?1"></script>
        <script>
            function myFunction() {
                var data = document.getElementById("result").value;
                Telegram.WebApp.ready();
                Telegram.WebApp.sendData(data);
            }
        </script>
    </head>
    <body onload="myFunction()">
        <input type="hidden" id="result" value='`+JSON.stringify(outcome)+`' />
    </body>
</html>
    `
    return new Response(res, {
        headers: {
            'Content-Type': 'text/html',
        },
    });
}

export default {
    async fetch(request, env) {
        if (request.method === 'POST') {
            return await handlePost(request, env);
        }

        const url = new URL(request.url);
        let verify_id = url.searchParams.get('verify_id');
        let body = `
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Turnstile &dash;</title>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=_turnstileCb" async defer></script>
    <style>
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
    </style>
    <script src="https://telegram.org/js/telegram-web-app.js?1"></script>
    <script>
      function turnstile_callback () {
        document.getElementById("form").submit();
      }
    </script>
  </head>
  <body>
    <main class="form-signin">
      <form method="POST" action="/" id="form">
        <img src="https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f916.svg" height="40px" width="40px" alt="robot" /><br />
        <h1>Are you a human?</h1>
        <i>Complete CAPTCHA below to join the group chat!</i>
        <input type="hidden" name="verify_id" value="`+verify_id+`" />
        <div class="cf-turnstile" data-sitekey="`+env.SITE_KEY+`" data-callback="turnstile_callback"></div>
      </form>
    </main>
  </body>
</html>
        `;
        return new Response(body, {
            headers: {
                'Content-Type': 'text/html',
            },
        });
    },
};
