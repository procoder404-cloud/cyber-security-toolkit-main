/* =====================================================
   Cyber Security Toolkit
   Professional Script - Fixed Terminal Clash
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // Fade In Page
    // ===============================
    document.body.style.opacity = "0";
    setTimeout(() => {
        document.body.style.transition = "opacity .8s";
        document.body.style.opacity = "1";
    }, 100);

    // ===============================
    // Live Clock
    // ===============================
    function updateClock() {
        const clock = document.getElementById("clock");
        const date = document.getElementById("date");
        if (!clock || !date) return;

        const now = new Date();
        clock.innerHTML = now.toLocaleTimeString();
        date.innerHTML = now.toDateString();
    }
    updateClock();
    setInterval(updateClock, 1000);

    // ===============================
    // Animated Counter
    // ===============================
    document.querySelectorAll(".stat-card h2").forEach(counter => {
        const targetText = counter.innerText.replace("%", "");
        const target = parseInt(targetText);
        if (isNaN(target)) return;

        let count = 0;
        const speed = Math.max(10, Math.floor(2000 / target));

        function update() {
            if (count < target) {
                count++;
                if (counter.innerText.includes("%")) {
                    counter.innerText = count + "%";
                } else {
                    counter.innerText = count;
                }
                setTimeout(update, speed);
            }
        }
        update();
    });

    // =====================================================
    // Hacker Terminal & Live Threat Feed Sequential Logic
    // =====================================================
    const terminal = document.getElementById("terminal-text");
    const threatLogs = [
        "🟢 Firewall Active",
        "🟢 Antivirus Updated",
        "🔵 QR Scanner Ready",
        "🟢 Port Scanner Loaded",
        "🔵 Monitoring Network...",
        "🟢 Database Connected",
        "🟡 Checking URL Reputation...",
        "🟢 IP Lookup Online",
        "🔵 File Hash Module Ready",
        "🟢 Security Score: 100%",
        "🟢 No Active Threats",
        "🔵 Waiting for User Scan..."
    ];
    
    if (terminal) {
        const initMessages = [
            "Initializing Security Toolkit...",
            "Loading Firewall...",
            "Checking Malware Protection...",
            "Monitoring Network...",
            "Scanning Active Sessions...",
            "System Status : SECURE ✔"
        ];
        let initIndex = 0;
        terminal.innerHTML = "";

        function printLine() {
            if (initIndex < initMessages.length) {
                terminal.innerHTML += initMessages[initIndex] + "<br>";
                initIndex++;
                setTimeout(printLine, 600);
            } else {
                // Once typewriter sequence finishes, clear and launch the rolling threat feed loop safely
                setTimeout(() => {
                    let logIndex = 0;
                    function updateThreatFeed(){
                        terminal.innerHTML = threatLogs[logIndex];
                        logIndex = (logIndex + 1) % threatLogs.length;
                    }
                    updateThreatFeed();
                    setInterval(updateThreatFeed, 2500);
                }, 1500);
            }
        }
        printLine();
    }

    // ===============================
    // Card Hover Effect
    // ===============================
    document.querySelectorAll(".card").forEach(card => {
        card.addEventListener("mouseenter", function () {
            this.style.transform = "translateY(-10px) scale(1.02)";
        });
        card.addEventListener("mouseleave", function () {
            this.style.transform = "translateY(0) scale(1)";
        });
    });

    // ===================================
    // Live Security Meter Animation Loop
    // ===================================
    function updateSecurityMeter(){
        const bar = document.getElementById("securityBar");
        if(!bar) return;
        let randomScore = Math.floor(Math.random() * 6) + 95;
        bar.style.width = randomScore + "%";
        bar.innerHTML = randomScore + "%";
    }
    updateSecurityMeter();
    setInterval(updateSecurityMeter, 3000);
});

// ===============================
// Show / Hide Password
// ===============================
function togglePassword() {
    const password = document.getElementById("password");
    const eye = document.getElementById("eye");
    if (!password || !eye) return;

    if (password.type === "password") {
        password.type = "text";
        eye.classList.remove("fa-eye");
        eye.classList.add("fa-eye-slash");
    } else {
        password.type = "password";
        eye.classList.remove("fa-eye-slash");
        eye.classList.add("fa-eye");
    }
}

// ===============================
// Copy Text
// ===============================
function copyText(id) {
    const text = document.getElementById(id);
    if (!text) return;
    navigator.clipboard.writeText(text.value);
    alert("Copied Successfully!");
}

// ===============================
// Scroll to Top
// ===============================
function scrollTopPage() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

// ===============================
// Loading Button Form Submit Accent
// ===============================
document.querySelectorAll("button").forEach(button => {
    button.addEventListener("click", function () {
        if (this.type === "submit" && this.form && this.form.checkValidity()) {
            this.innerHTML = "Please Wait...";
        }
    });
});