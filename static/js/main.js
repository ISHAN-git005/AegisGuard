function sendSOS() {
    const btn = document.getElementById('sosBtn');
    const notice = document.getElementById('sosNotice');
    
    btn.disabled = true;
    notice.innerText = "Transmitting SOS and Geo-Coordinates...";

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => dispatchAlert(pos.coords.latitude, pos.coords.longitude),
            () => dispatchAlert(null, null)
        );
    } else {
        dispatchAlert(null, null);
    }
}

function dispatchAlert(lat, lon) {
    const notice = document.getElementById('sosNotice');
    const btn = document.getElementById('sosBtn');

    fetch('/api/sos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: lat, lon: lon })
    })
    .then(res => res.json())
    .then(data => {
        notice.innerText = "SOS Dispatched! Guardian notified.";
        notice.style.color = "#ef4444";
        setTimeout(() => {
            btn.disabled = false;
            notice.innerText = "Press in case of immediate danger or medical issue.";
            notice.style.color = "";
        }, 5000);
    })
    .catch(err => {
        notice.innerText = "Error dispatching alert. Re-trying...";
        btn.disabled = false;
    });
}