# Share a temporary demo

First complete the [local setup](README.md#local-setup). Use a Cloudflare Quick
Tunnel for a short demonstration; its URL is temporary and is not a permanent
deployment address.

The app has no authentication. A public URL allows visitors to submit readings and
change the shared coordinates. Only expose a demo when that access is intended;
use access controls for a restricted audience.

## Two terminals

Install **cloudflared**, the Tunnel client, from
[Cloudflare's downloads](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/).
Cloudflare WARP is a different product.

In an activated Python environment, from the repository root:

```bash
# Terminal 1: local server, debug disabled
python wsgi.py
```

```bash
# Terminal 2: temporary public tunnel
cloudflared tunnel --url http://localhost:5000
```

Open the `https://...trycloudflare.com` URL printed by cloudflared. Keep both
processes running; stop each with Ctrl+C after the demonstration. The URL may
change when the tunnel restarts. Quick Tunnels have no uptime guarantee and are
intended for testing: [official Quick Tunnel documentation](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).

If you set a different `PORT` for `wsgi.py`, pass the same port to cloudflared.
If a Quick Tunnel fails while a local cloudflared configuration exists, consult
the official guide; existing configuration files can interfere with Quick Tunnels.

## Existing launch scripts

`scripts/Start-PublicServer.ps1` and `scripts/start_with_cloudflare.bat` run the preconfigured named
tunnel `sistema-inundaciones`; they do not create a Quick Tunnel. They start
`src/Flask_Server.py`, so set `FLASK_ENV=production` in the shell first to disable
debug mode. That entry point always uses port 5000.

The launchers still contain an example public hostname and a legacy WARP download
link. Use the cloudflared link above and the hostname actually configured in your
Cloudflare account. The two-terminal commands above are the documented demo path.

See [the detailed guide](CLOUDFLARE_SETUP.md) for named tunnels.
