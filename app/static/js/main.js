/**
 * CampusHub — Main JavaScript
 *
 * Handles:
 *   - Flash message auto-dismiss
 *   - Password show/hide toggle
 *   - Mobile navigation toggle
 *   - Client-side password confirmation check
 *   - Apply saved theme/text-size immediately (avoids flash of wrong theme)
 */

/* --------------------------------------------------------------------------
   Theme: apply data-theme before first paint (prevent flash)
   -------------------------------------------------------------------------- */
(function applyThemeEarly() {
  // The server already sets data-theme on <html> via Jinja, so this is a
  // no-op for first load. It helps if JS-driven theme switching is added later.
  const html = document.documentElement;
  const theme = html.getAttribute('data-theme');
  if (theme) {
    html.setAttribute('data-theme', theme);
  }
})();

/* --------------------------------------------------------------------------
   DOMContentLoaded — run after HTML is parsed
   -------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', function () {
  initFlashMessages();
  initPasswordToggles();
  initMobileNav();
  initPasswordConfirmation();
  initFormSubmitOnce();
});

/* --------------------------------------------------------------------------
   Flash messages: auto-dismiss after 5 seconds
   -------------------------------------------------------------------------- */
function initFlashMessages() {
  const flash = document.getElementById('flashMessage');
  if (!flash) return;

  // Auto-remove after 5 s with a fade-out
  setTimeout(function () {
    flash.style.transition = 'opacity 0.5s ease';
    flash.style.opacity = '0';
    setTimeout(function () {
      flash.remove();
    }, 500);
  }, 5000);
}

/* --------------------------------------------------------------------------
   Password show/hide toggle
   Finds all buttons with class .toggle-password and toggles their target input
   -------------------------------------------------------------------------- */
function initPasswordToggles() {
  document.querySelectorAll('.toggle-password').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
        btn.setAttribute('aria-label', 'Hide password');
      } else {
        input.type = 'password';
        btn.textContent = '👁';
        btn.setAttribute('aria-label', 'Show password');
      }
    });
  });
}

/* --------------------------------------------------------------------------
   Mobile navigation toggle
   -------------------------------------------------------------------------- */
function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const menu = document.getElementById('navMenu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', function () {
    const isOpen = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    toggle.textContent = isOpen ? '✕' : '☰';
  });

  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('open');
      toggle.textContent = '☰';
    }
  });
}

/* --------------------------------------------------------------------------
   Client-side password confirmation check on the register form.
   This is UX-only — the server always re-validates.
   -------------------------------------------------------------------------- */
function initPasswordConfirmation() {
  const confirmInput = document.getElementById('confirm_password');
  const passwordInput = document.getElementById('password');
  if (!confirmInput || !passwordInput) return;

  function checkMatch() {
    if (confirmInput.value && passwordInput.value !== confirmInput.value) {
      confirmInput.setCustomValidity('Passwords do not match.');
    } else {
      confirmInput.setCustomValidity('');
    }
  }

  confirmInput.addEventListener('input', checkMatch);
  passwordInput.addEventListener('input', checkMatch);
}

/* --------------------------------------------------------------------------
   Prevent double-form-submit (e.g. accidental double-click on Create button)
   -------------------------------------------------------------------------- */
function initFormSubmitOnce() {
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!submitBtn) return;
      // Disable after a short delay so the form data is sent first
      setTimeout(function () {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving…';
      }, 100);
    });
  });
}

/* --------------------------------------------------------------------------
   Utility: confirm before destructive actions (used via inline onsubmit,
   but also available as a helper for future JS-driven actions).
   -------------------------------------------------------------------------- */
function confirmAction(message) {
  return window.confirm(message || 'Are you sure?');
}
