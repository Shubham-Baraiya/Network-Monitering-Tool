// static/js/dashboard.js


async function updateDashboard() {

    try {

        const response = await fetch(
            "/api/status"
        );

        if (!response.ok) {
            throw new Error(
                "Unable to retrieve dashboard data"
            );
        }

        const data = await response.json();


        document.getElementById(
            "interface"
        ).textContent =
            data.interface || "Unknown";


        document.getElementById(
            "ip"
        ).textContent =
            data.ip || "Unknown";


        document.getElementById(
            "network"
        ).textContent =
            data.network || "Unknown";


        document.getElementById(
            "hosts"
        ).textContent =
            data.hosts ?? 0;


        document.getElementById(
            "download"
        ).textContent =
            `${(data.total_received_mb || 0).toFixed(2)} MB`;


        document.getElementById(
            "upload"
        ).textContent =
            `${(data.total_sent_mb || 0).toFixed(2)} MB`;


        document.getElementById(
            "packets-received"
        ).textContent =
            data.packets_received ?? 0;


        document.getElementById(
            "packets-sent"
        ).textContent =
            data.packets_sent ?? 0;


        const targetsElement =
            document.getElementById(
                "targets"
            );


        targetsElement.innerHTML = "";


        for (const target of data.targets || []) {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "target-card";


            const statusText =
                target.status === "UP"
                    ? "UP"
                    : "DOWN";


            const rttText =
                target.rtt !== null
                    ? `${target.rtt} ms`
                    : "-";


            card.innerHTML = `
                <h3>${target.target}</h3>

                <p>
                    Status:
                    <strong>
                        ${statusText}
                    </strong>
                </p>

                <p>
                    RTT:
                    ${rttText}
                </p>
            `;


            targetsElement.appendChild(
                card
            );
        }


        document.getElementById(
            "last-updated"
        ).textContent =
            "Last updated: " +
            new Date().toLocaleTimeString();


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }
}


// Initial update
updateDashboard();


// Auto-refresh every 3 seconds
setInterval(
    updateDashboard,
    3000
);