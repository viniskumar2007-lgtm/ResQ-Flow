/* =========================================
   RESQ-FLOW VICTIM FRONTEND
========================================= */


/* =========================================
   ELEMENTS
========================================= */

const sosButton = document.getElementById("sosButton");

const sosModal = document.getElementById("sosModal");

const closeModal = document.getElementById("closeModal");

const cancelSOS = document.getElementById("cancelSOS");

const confirmSOS = document.getElementById("confirmSOS");

const successOverlay = document.getElementById("successOverlay");

const doneButton = document.getElementById("doneButton");

const locationButton = document.getElementById("locationButton");

const locationStatus = document.getElementById("locationStatus");

const coordinates = document.getElementById("coordinates");

const peopleInput = document.getElementById("people");

const emergencyType = document.getElementById("emergencyType");

const messageInput = document.getElementById("message");

const elderly = document.getElementById("elderly");

const children = document.getElementById("children");

const disabled = document.getElementById("disabled");

const medical = document.getElementById("medical");

const summaryPeople = document.getElementById("summaryPeople");

const summaryEmergency = document.getElementById("summaryEmergency");

const summaryLocation = document.getElementById("summaryLocation");

const sosHistory = document.getElementById("sosHistory");

const networkText = document.getElementById("networkText");

const connectionText = document.getElementById("connectionText");

const connectionStatus = document.getElementById("connectionStatus");


/* =========================================
   LOCATION VARIABLES
========================================= */

let userLatitude = null;
let userLongitude = null;


/* =========================================
   CONNECTION STATUS
========================================= */

function updateConnectionStatus() {

    if (navigator.onLine) {

        connectionStatus.style.background = "#ecfdf5";
        connectionStatus.style.color = "#15803d";

        connectionText.textContent = "Online";

    } else {

        connectionStatus.style.background = "#fff7ed";
        connectionStatus.style.color = "#c2410c";

        connectionText.textContent = "Offline";

    }

}

window.addEventListener("online", updateConnectionStatus);

window.addEventListener("offline", updateConnectionStatus);

updateConnectionStatus();


/* =========================================
   NETWORK SIMULATION
========================================= */

function simulateNetwork() {

    let count = 0;

    const messages = [
        "Searching for nearby emergency devices...",
        "Nearby relay device detected.",
        "Emergency mesh network available.",
        "Ready to transmit emergency requests."
    ];

    const interval = setInterval(() => {

        if (count < messages.length) {

            networkText.textContent = messages[count];

            count++;

        } else {

            clearInterval(interval);

        }

    }, 1800);

}

simulateNetwork();


/* =========================================
   LOCATION
========================================= */

locationButton.addEventListener("click", getLocation);


function getLocation() {

    locationStatus.innerHTML =
        `<span class="mini-dot"></span>
         <span>Detecting your location...</span>`;

    locationButton.disabled = true;

    if (!navigator.geolocation) {

        locationStatus.innerHTML =
            `<span class="mini-dot"></span>
             <span>Location is not supported.</span>`;

        locationButton.disabled = false;

        return;
    }


    navigator.geolocation.getCurrentPosition(

        function(position) {

            userLatitude = position.coords.latitude;
            userLongitude = position.coords.longitude;


            locationStatus.innerHTML =
                `<span class="mini-dot green"></span>
                 <span>Location detected successfully</span>`;


            coordinates.innerHTML =
                `Latitude: ${userLatitude.toFixed(6)}
                <br>
                Longitude: ${userLongitude.toFixed(6)}`;


            locationButton.textContent = "Location Detected";

            locationButton.style.color = "#15803d";

            locationButton.style.borderColor = "#86efac";

            locationButton.disabled = false;

        },

        function(error) {

            console.log(error);

            locationStatus.innerHTML =
                `<span class="mini-dot"></span>
                 <span>Unable to detect location.</span>`;

            locationButton.textContent = "Try Again";

            locationButton.disabled = false;

        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }

    );

}


/* =========================================
   OPEN SOS MODAL
========================================= */

sosButton.addEventListener("click", openSOSModal);


function openSOSModal() {

    summaryPeople.textContent =
        peopleInput.value || "1";

    summaryEmergency.textContent =
        emergencyType.value;


    if (userLatitude !== null) {

        summaryLocation.textContent =
            `${userLatitude.toFixed(4)}, ${userLongitude.toFixed(4)}`;

    } else {

        summaryLocation.textContent =
            "Not detected";

    }


    sosModal.classList.add("show");

}


/* =========================================
   CLOSE MODAL
========================================= */

function closeSOSModal() {

    sosModal.classList.remove("show");

}

closeModal.addEventListener("click", closeSOSModal);

cancelSOS.addEventListener("click", closeSOSModal);


/* =========================================
   SEND SOS
========================================= */

confirmSOS.addEventListener("click", sendSOS);


function sendSOS() {

    closeSOSModal();

    successOverlay.classList.add("show");


    const sosId =
        "RQ-" +
        Math.floor(1000 + Math.random() * 9000);


    const sosData = {

        id: sosId,

        people:
            Number(peopleInput.value) || 1,

        emergency:
            emergencyType.value,

        latitude:
            userLatitude,

        longitude:
            userLongitude,

        elderly:
            elderly.checked,

        children:
            children.checked,

        mobilityIssue:
            disabled.checked,

        medicalCondition:
            medical.checked,

        message:
            messageInput.value,

        timestamp:
            new Date().toISOString(),

        status:
            "Transmitting"

    };


    /* Save SOS locally */

    localStorage.setItem(
        "resq_latest_sos",
        JSON.stringify(sosData)
    );


    /* Update success message */

    document.getElementById("successMessage").textContent =
        `Emergency request ${sosId} has been created and is being transmitted through the ResQ-Flow network.`;


    simulateTransmission(sosData);

}


/* =========================================
   TRANSMISSION SIMULATION
========================================= */

function simulateTransmission(sosData) {

    const status =
        document.getElementById("transmissionStatus");


    status.textContent =
        "Searching for nearby relay devices...";


    setTimeout(() => {

        status.textContent =
            "Relay device found. Forwarding SOS...";

    }, 1500);


    setTimeout(() => {

        status.textContent =
            "SOS successfully added to rescue network.";

        sosData.status =
            "Sent";

        localStorage.setItem(
            "resq_latest_sos",
            JSON.stringify(sosData)
        );

    }, 3500);


    setTimeout(() => {

        displaySOSHistory(sosData);

    }, 3700);

}


/* =========================================
   DISPLAY SOS HISTORY
========================================= */

function displaySOSHistory(data) {

    const locationText =
        data.latitude !== null
            ? `${data.latitude.toFixed(4)}, ${data.longitude.toFixed(4)}`
            : "Location unavailable";


    sosHistory.innerHTML = `

        <div class="history-item">

            <div class="history-top">

                <span class="history-id">
                    ${data.id}
                </span>

                <span class="priority">
                    EMERGENCY
                </span>

            </div>


            <div class="history-details">

                <span>
                    👥 ${data.people} people
                </span>

                <span>
                    🚨 ${data.emergency}
                </span>

                <span>
                    📍 ${locationText}
                </span>

                <span>
                    📡 ${data.status}
                </span>

            </div>

        </div>

    `;

}


/* =========================================
   LOAD PREVIOUS SOS
========================================= */

function loadPreviousSOS() {

    const saved =
        localStorage.getItem("resq_latest_sos");


    if (!saved) {
        return;
    }


    try {

        const data =
            JSON.parse(saved);

        displaySOSHistory(data);

    } catch (error) {

        console.log(
            "Could not load previous SOS."
        );

    }

}

loadPreviousSOS();


/* =========================================
   DONE BUTTON
========================================= */

doneButton.addEventListener("click", function() {

    successOverlay.classList.remove("show");

});


/* =========================================
   CLOSE MODAL BY CLICKING OUTSIDE
========================================= */

sosModal.addEventListener("click", function(event) {

    if (event.target === sosModal) {

        closeSOSModal();

    }

});


/* =========================================
   EMERGENCY PRIORITY PREVIEW
========================================= */

function calculatePriority() {

    let score = 0;


    const people =
        Number(peopleInput.value) || 1;


    /* Number of people */

    if (people >= 5) {

        score += 10;

    } else if (people >= 3) {

        score += 6;

    } else {

        score += 2;

    }


    /* Emergency type */

    if (
        emergencyType.value ===
        "Medical Emergency"
    ) {

        score += 10;

    }

    if (
        emergencyType.value ===
        "Fire"
    ) {

        score += 9;

    }

    if (
        emergencyType.value ===
        "Trapped"
    ) {

        score += 8;

    }

    if (
        emergencyType.value ===
        "Flood"
    ) {

        score += 6;

    }


    /* Vulnerable people */

    if (elderly.checked) {

        score += 5;

    }

    if (children.checked) {

        score += 5;

    }

    if (disabled.checked) {

        score += 5;

    }

    if (medical.checked) {

        score += 7;

    }


    return score;

}


/* =========================================
   FORM MONITORING
========================================= */

peopleInput.addEventListener(
    "change",
    calculatePriority
);

emergencyType.addEventListener(
    "change",
    calculatePriority
);

elderly.addEventListener(
    "change",
    calculatePriority
);

children.addEventListener(
    "change",
    calculatePriority
);

disabled.addEventListener(
    "change",
    calculatePriority
);

medical.addEventListener(
    "change",
    calculatePriority
);


/* =========================================
   KEYBOARD SOS
   CTRL + ALT + S
   FOR DEMO ONLY
========================================= */

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.ctrlKey &&
            event.altKey &&
            event.key.toLowerCase() === "s"
        ) {

            openSOSModal();

        }

    }
);