const map = L.map('map').setView([42, 42],6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution:  '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


let currentRoute = null;
let currentRouteID = null;

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

async function loadPOIs() {
    try {
        const response = await fetch(`http://localhost:5000/pois/${currentRouteID}`);
        
        const data = await response.json();
        
        // Add markers to map
        data.markers.forEach(marker => {
            L.marker([marker.lat, marker.lon])
                .bindPopup(marker.name)
                .addTo(map);
        });


        // Update POI table
        const poiTableBody = document.getElementById('poi-tbody');
        poiTableBody.innerHTML = ''; 

        data.table.forEach(poi => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${poi.distance}</td>
                <td>${poi.deviation}</td>
                <td>${poi.name}</td>
            `;
            poiTableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading POIs:', error);
        alert('Failed to load POIs. Please try again.');

    }
}

const creditsModal = document.getElementById('credits-modal');
const creditsBtn = document.getElementById('credits-btn');
const closeModal = document.querySelector('.close-modal');

// Show modal when clicking the credits button
creditsBtn.addEventListener('click', () => {
    creditsModal.style.display = 'block';
});

// Close modal when clicking the X
closeModal.addEventListener('click', () => {
    creditsModal.style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    if (event.target === creditsModal) {
        creditsModal.style.display = 'none';
    }
});

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

