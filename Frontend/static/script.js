const map = L.map('map').setView([42, 42],6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution:  '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


let currentRoute = null;

document.getElementById('gpx-upload').addEventListener('change', async function(event) {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:5000/gpx/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        
        if (currentRoute){
            map.removeLayer(currentRoute);
        }

        const routePoints = data.coordinates.map(coord => [coord.lat, coord.lon]);

        currentRoute = L.polyline(routePoints, {color: 'blue'}).addTo(map);

        map.fitBounds(currentRoute.getBounds());

    } catch (error) {
        console.error('Error uploading GPX file:', error);}
    });