
async function toggleFavorite(event, btn) {
    event.preventDefault();
    const gameId = btn.getAttribute("data-game-id");
    const response = await fetch(`/add-favorite/${gameId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });
    const data = await response.json();
    if (data.status === "added") {
        btn.innerHTML = '<i class="fa-solid fa-heart text-red-500"></i>';
    } else {
        btn.innerHTML = '<i class="fa-regular fa-heart text-slate-400"></i>';
    }
}
function getCookie(name) {

    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.split("=")[1]);
                break;
            }
        }
    }
    return cookieValue;
}


document.addEventListener("DOMContentLoaded", function () {
    let activeGenre = "all";

    const searchInput = document.getElementById("searchInput");
    const countBadge = document.getElementById("countBadge");
    const noResults = document.getElementById("noResults");

    function getCards() {
        return document.querySelectorAll("#gamesGrid [data-title]");
    }

    function applyFilters() {
        const q = searchInput ? searchInput.value.toLowerCase().trim() : "";
        const cards = getCards();
        let visible = 0;

        cards.forEach(function (card) {
            const titleMatch = card.dataset.title.includes(q);
            const descMatch = card.dataset.description.includes(q);
            const genreMatch = activeGenre === "all" || card.dataset.genre === activeGenre;

            const show = (titleMatch || descMatch) && genreMatch;
            card.style.display = show ? "" : "none";
            if (show) visible++;
        });

        if (countBadge) countBadge.textContent = visible + " games";
        if (noResults) noResults.classList.toggle("hidden", visible > 0);
    }

    window.setGenre = function (genre) {
        activeGenre = genre;
        document.querySelectorAll(".filter-btn").forEach(function (btn) {
            const isActive = btn.dataset.filter === genre;
            btn.className = "filter-btn text-xs font-semibold px-3.5 py-1.5 rounded-full border transition-all "
                + (isActive
                    ? "bg-[#7c6aff]/15 text-[#a89fff] border-[#7c6aff]/30"
                    : "bg-[#1e2535] text-[#7b82a0] border-[#2a3147] hover:border-[#7c6aff]/40 hover:text-[#a89fff]");
        });
        applyFilters();
    };

    if (searchInput) {
        searchInput.addEventListener("input", applyFilters);
    }
});

function updateNotificationBadge(count) {
    var badge = document.getElementById("notif-badge");
    var link = document.getElementById("notif-link");

    if (count > 0) {
        if (!badge) {
            badge = document.createElement("span");
            badge.id = "notif-badge";
            badge.className = "text-[10px] font-bold bg-[#7c6aff] text-white px-1.5 py-0.5 rounded-full min-w-[18px] text-center";
            link.appendChild(badge);
        }
        badge.textContent = count;
    } else {
        if (badge) badge.remove();
    }
}

function fetchUnreadCount() {
    fetch("/api/notifications/unread/")
        .then(function (res) { return res.json(); })
        .then(function (data) { updateNotificationBadge(data.count); })
        .catch(function () { });
}

fetchUnreadCount();
setInterval(fetchUnreadCount, 20000);

function toggleReplyForm(commentId) {
    const form = document.getElementById(`reply-form-${commentId}`);

    if (form) {
        form.classList.toggle("hidden");
    }
}

function toggleReplies(commentId) {
    const replies = document.getElementById(`replies-${commentId}`);
    const chevron = document.getElementById(`chevron-${commentId}`);

    if (!replies) return;

    replies.classList.toggle("hidden");

    if (chevron) {
        chevron.classList.toggle("fa-chevron-down");
        chevron.classList.toggle("fa-chevron-up");
    }
}

