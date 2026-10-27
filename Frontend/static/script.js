const map = L.map('map').setView([42, 42],6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution:  '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


let currentRoute = null;
let currentRouteID = null;
let currentMarkers = [];

document.getElementById('gpx-upload').addEventListener('change', async function(event) {
    const file = this.files[0];
    document.getElementById('filename-display').textContent = file.name;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`http://localhost:5000/gpx/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            alert(data.detail || 'Upload failed.');
            return;
        }
        currentRouteID = data.route_id;
        
        if (currentRoute){
            map.removeLayer(currentRoute);
        }

        const routePoints = data.coordinates.map(coord => [coord.lat, coord.lon]);

        currentRoute = L.polyline(routePoints, {color: 'blue'}).addTo(map);

        map.fitBounds(currentRoute.getBounds());

        await loadPOIs();

    } catch (error) {
        console.error('Error uploading GPX file:', error);}
    });

function poiName(poi) {
    return poi.name ?? 'Unnamed';
}

async function loadPOIs() {
    try {
        const response = await fetch(`http://localhost:5000/pois/${currentRouteID}`);
        
        const data = await response.json();
        if (!response.ok) {
            alert(data.detail || 'Failed to load POIs.');
            return;
        }

        // Add markers to map
        data.pois.forEach(poi => {
            const newMarker = L.marker([poi.lat, poi.lon])
                .bindPopup(poiName(poi))
                .addTo(map);
            currentMarkers.push(newMarker);
        });


        // Update POI table
        const poiTableBody = document.getElementById('poi-tbody');
        poiTableBody.innerHTML = ''; 

        data.pois.forEach(poi => {
            const row = document.createElement('tr');
            // The API returns numbers; formatting is the client's job.
            // textContent (not innerHTML) so OSM names cannot inject markup.
            [
                `${poi.distance_on_route_km.toFixed(1)} km`,
                `${Math.round(poi.distance_to_route_m)} m`,
                poiName(poi),
            ].forEach(text => {
                const cell = document.createElement('td');
                cell.textContent = text;
                row.appendChild(cell);
            });
            poiTableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading POIs:', error);
        alert('Failed to load POIs. Please try again.');

    }
}

document.addEventListener('DOMContentLoaded', () => {
    const creditsModal = document.getElementById('credits-modal');
    const creditsBtn = document.getElementById('credits-btn');
    const closeModal = document.querySelector('.close-modal');

    creditsBtn.addEventListener('click', () => {
        creditsModal.style.display = 'block';
    });

    closeModal.addEventListener('click', () => {
        creditsModal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === creditsModal) {
            creditsModal.style.display = 'none';
        }
    });
});

