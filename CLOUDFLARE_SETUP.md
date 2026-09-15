# Cloudflare Tunnel setup

Cloudflare Tunnel connects a local service to Cloudflare through the `cloudflared`
client. It does not add application authentication automatically. This project's
Flask app exposes mutable readings and coordinate configuration, so restrict access
when sharing outside a controlled demonstration.

## Install and verify

Install **cloudflared**, not Cloudflare WARP, using the
[official downloads](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/).
Then verify:

```bash
cloudflared --version
```

## Temporary URL

Follow [the quickstart](PUBLIC_SERVER_QUICKSTART.md): run `python wsgi.py` from an
activated environment, then in another terminal:

```bash
cloudflared tunnel --url http://localhost:5000
```

A Quick Tunnel does not need a managed domain and prints a temporary public URL.
It has no fixed 30-minute lifetime or permanent-address guarantee. See
[Quick Tunnel limitations](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).

## Named tunnel with your domain

A locally managed named tunnel requires a Cloudflare account and a domain configured
with Cloudflare. Follow the [official local-tunnel guide](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/create-local-tunnel/).
The following names are examples:

```bash
cloudflared tunnel login
cloudflared tunnel create sistema-inundaciones
```

Keep the generated certificate and tunnel credentials in the cloudflared user
configuration directory, outside this repository. Create its `config.yml` with your
actual tunnel UUID, credential-file path, and hostname:

```yaml
tunnel: <TUNNEL_UUID>
credentials-file: <ABSOLUTE_PATH_TO_TUNNEL_CREDENTIALS_JSON>
ingress:
  - hostname: flood-demo.example.com
    service: http://localhost:5000
  - service: http_status:404
```

Create the DNS route using a hostname on your own domain:

```bash
cloudflared tunnel route dns sistema-inundaciones flood-demo.example.com
```

Start the local app with `python wsgi.py`, then run the tunnel in another terminal:

```bash
cloudflared tunnel run sistema-inundaciones
```

A named tunnel's hostname depends on your DNS configuration. Neither an example
hostname printed by a launcher nor the existence of a tunnel guarantees that the
application is reachable. Both the app and tunnel must remain running.

For restricted demos, configure [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/access-controls/)
and account for how the ESP32 will authenticate before placing Access in its path.
The current firmware does not implement Access authentication.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `cloudflared` not found | Confirm the Tunnel client is installed and on PATH; reopen the terminal |
| Origin connection refused | Open http://localhost:5000 locally and confirm the configured port |
| Named tunnel missing | Confirm the account, tunnel name, and local configuration; use `cloudflared tunnel list` |
| Dashboard waiting for data | Send a sample `/ingest` request from the root README |

Stop the app and cloudflared with Ctrl+C in their terminals. Avoid terminating
unrelated Python processes.

The Windows launchers in `scripts/` are conveniences for the named tunnel above. They use the
direct Flask entry point, whose default is debug mode; set `FLASK_ENV=production`
before starting them. Their example hostname and old download hint are not account
configuration. See the [quickstart](PUBLIC_SERVER_QUICKSTART.md#existing-launch-scripts).
