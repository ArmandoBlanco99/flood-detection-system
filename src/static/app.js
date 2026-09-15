// Global variables
let map;
let marker;
let eventHistory = [];
const MAX_HISTORY = 50;

// Emojis for different statuses
const emojis = {
    VERDE: '🟢',
    AMARILLO: '🟡',
    ROJO: '🔴'
};

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    initializeUpdates();
    setupCoordsForm();
    fetchCoords();
});

// Initialize the Leaflet map
function initializeMap() {
    // Default coordinates: central Mexico City
    const initialCoordinates = [19.4326, -99.1332];
    
    map = L.map('map').setView(initialCoordinates, 13);
    
    // Add map tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Create the marker
    marker = L.marker(initialCoordinates, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    // Fetch initial data
    updateStatus();
}

// Update status every two seconds
function initializeUpdates() {
    updateStatus();
    setInterval(updateStatus, 2000);
}

// Update prediction status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update page elements
        updateUI(data);
        
        // Update the map
        if (data.coordenadas) {
            updateMap(data.coordenadas);
        }
        
        // Update connection status
        updateConnectionStatus('online');
    } catch (error) {
        console.error('Error al obtener estado:', error);
        updateConnectionStatus('offline');
    }
}

// Update interface elements
function updateUI(data) {
    const {
        alerta: alert,
        riesgo_zona: zoneRisk,
        riesgo_score: riskScore,
        nivel_sensor: sensorLevel,
        coordenadas: coordinates,
        mensaje: message
    } = data;
    
    // Update coordinates
    if (coordinates) {
        document.getElementById('lat').textContent = coordinates.latitud.toFixed(6);
        document.getElementById('lon').textContent = coordinates.longitud.toFixed(6);
    }
    
    // Update the sensor level
    if (sensorLevel !== undefined && sensorLevel >= 0) {
        document.getElementById('sensor-level').textContent = sensorLevel;
    } else {
        document.getElementById('sensor-level').textContent = '-';
    }
    
    // Update zone risk
    document.getElementById('zone-risk').textContent = zoneRisk || '--';
    document.getElementById('risk-score').textContent = riskScore || '--';
    
    // Update the alert indicator
    updateAlertIndicator(alert);
    
    // Update the last-updated time
    updateLastUpdatedTime();
    
    // Add a history event when the state changes
    addHistoryEvent(alert, sensorLevel, zoneRisk, riskScore);
}

// Update the alert indicator
function updateAlertIndicator(alert) {
    const circle = document.querySelector('.circle');
    const label = document.getElementById('alert-label');
    const description = document.getElementById('alert-description');
    
    // Remove previous classes
    circle.classList.remove('verde', 'amarillo', 'rojo', 'gris');
    
    // Apply the new class
    let colorClass = alert.toLowerCase();
    if (colorClass === 'gris') {
        circle.classList.add('gris');
    } else {
        circle.classList.add(colorClass);
    }
    
    // Update the label
    label.textContent = alert;
    
    // Update the description
    const descriptions = {
        'VERDE': '✅ Condiciones normales - No se requiere acción',
        'AMARILLO': '⚠️ Precaución - Monitoreo continuo recomendado',
        'ROJO': '🚨 Peligro - Tomar medidas de seguridad inmediatas',
        'GRIS': '⏳ Esperando datos...'
    };
    
    description.textContent = descriptions[alert] || 'Estado desconocido';
}

// Update the map with the new position
function updateMap(coordinates) {
    const latlng = [coordinates.latitud, coordinates.longitud];
    
    // Update the marker position
    marker.setLatLng(latlng);
    
    // Center the map only on the first update
    if (!map.hasBeenCentered) {
        map.setView(latlng, 13);
        map.hasBeenCentered = true;
    }
    
    // Update the marker popup
    const popupText = `
        <strong>Ubicación del Sensor</strong><br>
        Lat: ${coordinates.latitud.toFixed(6)}<br>
        Lon: ${coordinates.longitud.toFixed(6)}
    `;
    marker.bindPopup(popupText);
}

// Add an event to the history
function addHistoryEvent(alert, sensorLevel, zoneRisk, riskScore) {
    const now = new Date();
    const time = now.toLocaleTimeString('es-MX', {
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    
    // Avoid consecutive duplicates
    if (eventHistory.length > 0) {
        const lastEvent = eventHistory[0];
        if (lastEvent.alerta === alert &&
            lastEvent.nivel_sensor === sensorLevel) {
            return;
        }
    }
    
    const event = {
        time,
        alerta: alert,
        nivel_sensor: sensorLevel,
        riesgo_zona: zoneRisk,
        riesgo_score: riskScore,
        timestamp: now.getTime()
    };
    
    eventHistory.unshift(event);
    
    // Limit the history length
    if (eventHistory.length > MAX_HISTORY) {
        eventHistory = eventHistory.slice(0, MAX_HISTORY);
    }
    
    // Update the history view
    updateHistoryView();
}

// Update the history view
function updateHistoryView() {
    const container = document.getElementById('history');
    
    if (eventHistory.length === 0) {
        container.innerHTML = '<p class="empty-state">No hay eventos registrados aún...</p>';
        return;
    }
    
    let html = '';
    for (const event of eventHistory) {
        const emoji = emojis[event.alerta] || '⚪';
        const colorClass = event.alerta.toLowerCase();
        
        html += `
            <div class="event">
                <span class="event-time">${event.time}</span>
                <span class="event-text">
                    ${emoji} Alerta ${event.alerta} |\x20
                    Sensor: ${event.nivel_sensor} |\x20
                    Riesgo: ${event.riesgo_zona} (${event.riesgo_score})
                </span>
                <span class="event-level ${colorClass}">${event.alerta}</span>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Update the last-updated time
function updateLastUpdatedTime() {
    const now = new Date();
    const time = now.toLocaleTimeString('es-MX', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    document.getElementById('last-update').textContent = time;
}

// Update connection status
function updateConnectionStatus(status) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (status === 'online') {
        statusIndicator.classList.remove('offline');
        statusIndicator.classList.add('online');
        statusText.textContent = 'En línea';
    } else {
        statusIndicator.classList.remove('online');
        statusIndicator.classList.add('offline');
        statusText.textContent = 'Sin conexión';
    }
}

// Show notifications, optionally, in supported browsers
function showNotification(title, options) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, options);
    }
}

// Fetch saved coordinates and update the inputs and map
async function fetchCoords() {
    try {
        const resp = await fetch('/api/coords');
        if (!resp.ok) return;
        const coords = await resp.json();
        const latEl = document.getElementById('input-lat');
        const lonEl = document.getElementById('input-lon');
        if (latEl && lonEl && coords) {
            latEl.value = coords.latitud;
            lonEl.value = coords.longitud;
            // Update the interface and map with the current coordinates
            document.getElementById('lat').textContent = coords.latitud.toFixed(6);
            document.getElementById('lon').textContent = coords.longitud.toFixed(6);
            updateMap(coords);
        }
    } catch (err) {
        console.warn('No se pudieron obtener coordenadas:', err);
    }
}

// Set up the coordinate form and save coordinates to the server
function setupCoordsForm() {
    const btn = document.getElementById('save-coords');
    if (!btn) return;

    btn.addEventListener('click', async (ev) => {
        ev.preventDefault();
        const latEl = document.getElementById('input-lat');
        const lonEl = document.getElementById('input-lon');
        const msg = document.getElementById('coords-message');
        const lat = parseFloat(latEl.value);
        const lon = parseFloat(lonEl.value);

        if (!isFinite(lat) || !isFinite(lon)) {
            msg.textContent = 'Latitud/Longitud inválidas';
            return;
        }

        try {
            const resp = await fetch('/api/coords', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat, lon })
            });
            const data = await resp.json();
            if (resp.ok && data.ok) {
                msg.textContent = 'Coordenadas guardadas correctamente';
                setTimeout(() => { msg.textContent = ''; }, 3000);

                // Update the local interface and request the latest status
                const coords = { latitud: lat, longitud: lon };
                document.getElementById('lat').textContent = lat.toFixed(6);
                document.getElementById('lon').textContent = lon.toFixed(6);
                updateMap(coords);
                updateStatus();
            } else {
                msg.textContent = data.error || 'Error al guardar coordenadas';
            }
        } catch (err) {
            console.error(err);
            msg.textContent = 'Error de red al guardar coordenadas';
        }
    });
}
