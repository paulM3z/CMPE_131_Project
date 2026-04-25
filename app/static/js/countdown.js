/**
 * Live event countdowns for detail and dashboard views.
 * Event timestamps are provided in UTC via data-event-time attributes.
 */
(function initCountdowns() {
  function parseEventDate(isoLikeString) {
    if (!isoLikeString) {
      return null;
    }

    if (isoLikeString.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(isoLikeString)) {
      const utcDate = new Date(isoLikeString);
      return Number.isNaN(utcDate.getTime()) ? null : utcDate;
    }

    const match = isoLikeString.match(
      /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/
    );
    if (!match) {
      const fallbackDate = new Date(isoLikeString);
      return Number.isNaN(fallbackDate.getTime()) ? null : fallbackDate;
    }

    const [, year, month, day, hour, minute, second = '00'] = match;
    return new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
      Number(hour),
      Number(minute),
      Number(second)
    );
  }

  function formatLocalTime(date) {
    return new Intl.DateTimeFormat(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    }).format(date);
  }

  function isSameLocalDay(a, b) {
    return (
      a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate()
    );
  }

  function setStateClass(node, state) {
    node.classList.remove('countdown-ended', 'countdown-live', 'countdown-soon');
    if (state === 'ended') {
      node.classList.add('countdown-ended');
    } else if (state === 'live') {
      node.classList.add('countdown-live');
    } else if (state === 'soon') {
      node.classList.add('countdown-soon');
    }
  }

  function buildDetailMessage(eventDate, now) {
    const diffMs = eventDate.getTime() - now.getTime();
    const liveWindowMs = 15 * 60 * 1000;

    if (Math.abs(diffMs) <= liveWindowMs) {
      return { text: '🔴 LIVE NOW! Join now!', state: 'live' };
    }

    if (diffMs < -liveWindowMs) {
      return { text: '✅ This event has ended', state: 'ended' };
    }

    const totalMinutes = Math.max(Math.floor(diffMs / 60000), 0);
    const days = Math.floor(totalMinutes / (60 * 24));
    const hours = Math.floor((totalMinutes % (60 * 24)) / 60);
    const minutes = totalMinutes % 60;

    if (diffMs < 60 * 60 * 1000) {
      return {
        text: `⚡ STARTS SOON! In ${minutes} minute${minutes === 1 ? '' : 's'}`,
        state: 'soon',
      };
    }

    if (diffMs < 24 * 60 * 60 * 1000 || isSameLocalDay(eventDate, now)) {
      return {
        text: `🔥 TODAY! Starts in ${hours} hours ${minutes} minutes`,
        state: 'default',
      };
    }

    return {
      text: `${days} DAYS ${hours} HOURS ${minutes} MINUTES`,
      state: 'default',
    };
  }

  function buildMiniMessage(eventDate, now) {
    const diffMs = eventDate.getTime() - now.getTime();
    const liveWindowMs = 15 * 60 * 1000;

    if (Math.abs(diffMs) <= liveWindowMs) {
      return { text: '🔴 Live now', state: 'live' };
    }

    if (diffMs < -liveWindowMs) {
      return { text: 'Ended', state: 'ended' };
    }

    if (isSameLocalDay(eventDate, now)) {
      return { text: `Today at ${formatLocalTime(eventDate)}`, state: 'default' };
    }

    const totalHours = Math.max(Math.floor(diffMs / (1000 * 60 * 60)), 0);
    const days = Math.floor(totalHours / 24);
    const hours = totalHours % 24;
    return { text: `Starts in ${days}d ${hours}h`, state: 'default' };
  }

  function renderCountdown(node) {
    const isoTime = node.dataset.eventTime;
    const style = node.dataset.countdownStyle || 'mini';
    if (!isoTime) {
      return;
    }

    const eventDate = parseEventDate(isoTime);
    if (!eventDate || Number.isNaN(eventDate.getTime())) {
      if (style === 'detail') {
        const value = node.querySelector('.countdown-value');
        if (value) {
          value.textContent = 'Countdown unavailable';
        }
      } else {
        node.textContent = 'Countdown unavailable';
      }
      return;
    }

    const message = style === 'detail'
      ? buildDetailMessage(eventDate, new Date())
      : buildMiniMessage(eventDate, new Date());

    if (style === 'detail') {
      const value = node.querySelector('.countdown-value');
      if (!value) {
        return;
      }
      value.textContent = message.text;
      setStateClass(value, message.state);
      return;
    }

    node.textContent = message.text;
    setStateClass(node, message.state);
  }

  function updateCountdowns() {
    document.querySelectorAll('[data-event-time]').forEach(renderCountdown);
  }

  document.addEventListener('DOMContentLoaded', function () {
    updateCountdowns();
    window.setInterval(updateCountdowns, 1000);
  });

  window.updateCountdowns = updateCountdowns;
})();
