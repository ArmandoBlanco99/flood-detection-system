# Web dashboard

The dashboard presents the latest prediction from the Flask API, a Leaflet map,
a coordinate form, and a browser-local history of alert changes.

## Start and send a reading

Follow the [root setup guide](../README.md), then run from the repository root:

```bash
python wsgi.py
```

Open http://localhost:5000. In a second terminal, simulate a device reading:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/ingest -ContentType 'application/json' -Body '{"v":0.8,"pct":75}'
```

```bash
curl -X POST http://localhost:5000/ingest \
  -H 'Content-Type: application/json' -d '{"v":0.8,"pct":75}'
```

The page polls `/api/status`; no frontend package installation or build is needed.
Internet access is needed for the Leaflet CDN and map tiles.

## Configuration and state

- The coordinate form reads/writes `/api/coords`. Saving it updates
  `src/coords_config.json`; the setting is shared by all incoming readings.
- The API retains the latest prediction in memory. Restarting the server clears it.
- Event history is kept in the page's JavaScript memory. Reloading clears it.
- The firmware sends voltage and percentage, without a sensor identifier or location.
  Multiple independently located sensors are not implemented.

## Implementation

| File | Responsibility |
| --- | --- |
| `templates/index.html` | Page structure and external Leaflet assets |
| `static/styles.css` | Responsive layout and alert appearance |
| `static/app.js` | API polling, map, coordinates, and page-local history |
| `flask_server.py` | Dashboard route and JSON endpoints |

The root README contains the [API reference](../README.md#api-and-repository-map).
If the page stays in its waiting state, confirm `/ingest` received numeric `v` and
`pct` values. If the map is missing, check network access and browser console errors.
