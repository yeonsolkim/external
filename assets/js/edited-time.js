(function () {
  function formatUpdatedTime(dateString, absoluteDate) {
    const updated = new Date(dateString);
    const now = new Date();

    if (Number.isNaN(updated.getTime())) {
      return null;
    }

    const diffMs = now - updated;
    const minute = 60 * 1000;
    const hour = 60 * minute;
    const day = 24 * hour;

    if (diffMs < 0) {
      return "updated just now";
    }

    if (diffMs < minute) {
      return "updated just now";
    }

    const minutes = Math.floor(diffMs / minute);
    if (minutes < 60) {
      return "updated " + minutes + " " + (minutes === 1 ? "minute" : "minutes") + " ago";
    }

    const hours = Math.floor(diffMs / hour);
    if (hours < 24) {
      return "updated " + hours + " " + (hours === 1 ? "hour" : "hours") + " ago";
    }

    const days = Math.floor(diffMs / day);
    if (days < 7) {
      return "updated " + days + " " + (days === 1 ? "day" : "days") + " ago";
    }

    return "updated " + absoluteDate;
  }

  document.querySelectorAll(".post-date-meta").forEach(function (el) {
    const createdText = el.getAttribute("data-created-display");
    const createdDay = el.getAttribute("data-created-day");
    const updatedAt = el.getAttribute("data-updated-at");
    const updatedDay = el.getAttribute("data-updated-day");
    const updatedText = el.getAttribute("data-updated-display");

    if (!createdText) {
      return;
    }

    if (!updatedAt || !updatedText || createdDay === updatedDay) {
      el.textContent = createdText;
      return;
    }

    const relativeUpdatedText = formatUpdatedTime(updatedAt, updatedText);
    const text = relativeUpdatedText
      ? createdText + " (" + relativeUpdatedText + ")"
      : createdText + " (updated " + updatedText + ")";

    if (text) {
      el.textContent = text;
    }
  });
})();
