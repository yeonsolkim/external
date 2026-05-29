(function () {
  function formatEditedTime(dateString) {
    const edited = new Date(dateString);
    const now = new Date();

    if (Number.isNaN(edited.getTime())) {
      return null;
    }

    const diffMs = now - edited;
    const minute = 60 * 1000;
    const hour = 60 * minute;
    const day = 24 * hour;

    if (diffMs < 0) {
      return "edited just now";
    }

    if (diffMs < minute) {
      return "edited just now";
    }

    const minutes = Math.floor(diffMs / minute);
    if (minutes < 60) {
      return "edited " + minutes + " " + (minutes === 1 ? "minute" : "minutes") + " ago";
    }

    const hours = Math.floor(diffMs / hour);
    if (hours < 24) {
      return "edited " + hours + " " + (hours === 1 ? "hour" : "hours") + " ago";
    }

    const days = Math.floor(diffMs / day);
    if (days < 7) {
      return "edited " + days + " " + (days === 1 ? "day" : "days") + " ago";
    }

    return "edited on " + edited.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  }

  document.querySelectorAll(".post-edited-time").forEach(function (el) {
    const editedAt = el.getAttribute("data-edited-at");
    const text = formatEditedTime(editedAt);

    if (text) {
      el.textContent = text;
    }
  });
})();