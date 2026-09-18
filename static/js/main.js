/* Aurora Goods — frontend behaviour (no frameworks, no build step). */
(function () {
  "use strict";

  /* ------------------------------------------------------------------ *
   * Mobile nav toggle
   * ------------------------------------------------------------------ */
  var navToggle = document.getElementById("nav-toggle");
  var navLinks = document.getElementById("nav-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      var open = navLinks.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ------------------------------------------------------------------ *
   * "Continue with Google" button injection (Requirement 3)
   * Rendered on login + signup pages via the official-branding partial.
   * ------------------------------------------------------------------ */
  var googleSlots = document.querySelectorAll(".google-slot");
  if (googleSlots.length) {
    var wrap = document.createElement("div");
    wrap.className = "google-btn-holder";
    wrap.innerHTML = [
      '<form method="post" action="/accounts/google/login/" class="google-btn-form">',
      '  <input type="hidden" name="csrfmiddlewaretoken" value="', getCookie("csrftoken"), '">',
      '  <button type="submit" class="google-btn" aria-label="Continue with Google">',
      '    <span class="google-btn__logo" aria-hidden="true">',
      // Official Google "G" logo (four colors, per branding guidelines)
      '      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20" height="20">',
      '        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>',
      '        <path fill="#4285F4" d="M46.98 24.55c0-.79-.07-1.54-.19-2.27H24v9.32h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.23z"/>',
      '        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>',
      '        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>',
      "      </svg>",
      "    </span>",
      '    <span class="google-btn__text">Continue with Google</span>',
      "  </button>",
      "</form>",
    ].join("");
    googleSlots.forEach(function (slot) { slot.appendChild(wrap.cloneNode(true)); });
  }

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : "";
  }

  /* ------------------------------------------------------------------ *
   * Product gallery (product detail page)
   * ------------------------------------------------------------------ */
  var gallery = document.querySelector("[data-gallery]");
  if (gallery) {
    var mainImg = document.getElementById("pdp-main-img");
    gallery.addEventListener("click", function (event) {
      var thumb = event.target.closest("[data-gallery-thumb]");
      if (!thumb || !mainImg) return;
      mainImg.src = thumb.getAttribute("data-src");
      gallery.querySelectorAll(".pdp-thumb").forEach(function (t) {
        t.classList.remove("is-active");
      });
      thumb.classList.add("is-active");
    });
  }

  /* ------------------------------------------------------------------ *
   * Cart badge pulse (feedback after add-to-cart redirects)
   * ------------------------------------------------------------------ */
  var cartCount = document.querySelector("[data-cart-count]");
  if (cartCount && !cartCount.classList.contains("is-empty")) {
    cartCount.classList.add("just-changed");
  }

  /* ------------------------------------------------------------------ *
   * Toasts — flash messages that dismiss themselves
   * - role="status" toasts (add-to-cart, order placed…): auto-dismiss
   *   after ~3.5s with a 550ms fade-out (CSS handles the transition).
   * - role="alert" toasts (form errors): manual dismissal only.
   * - The X button dismisses immediately, no fade wait.
   * ------------------------------------------------------------------ */
  var TOAST_AUTO_DISMISS_MS = 3500;
  var TOAST_FADE_MS = 550; // keep in sync with the .alert CSS transition
  var toastTimers = new WeakMap();

  function dismissToast(alert, immediate) {
    var pending = toastTimers.get(alert);
    if (pending) {
      clearTimeout(pending);
      toastTimers.delete(alert);
    }
    if (immediate) {
      alert.remove();
      return;
    }
    if (alert.classList.contains("is-dismissed")) return;
    alert.classList.add("is-dismissed");
    setTimeout(function () { alert.remove(); }, TOAST_FADE_MS);
  }

  function armToast(alert) {
    // Never re-arm a toast that's armed or already fading out.
    if (toastTimers.has(alert) || alert.classList.contains("is-dismissed")) return;
    toastTimers.set(
      alert,
      setTimeout(function () {
        toastTimers.delete(alert);
        dismissToast(alert);
      }, TOAST_AUTO_DISMISS_MS)
    );
  }

  function bindToast(alert) {
    var closeBtn = alert.querySelector(".alert-close");
    if (closeBtn && !closeBtn.dataset.toastBound) {
      closeBtn.dataset.toastBound = "1";
      closeBtn.addEventListener("click", function () {
        dismissToast(alert, true); // X click = instant removal, skip the fade
      });
    }
    // Only status toasts auto-dismiss; role="alert" errors stay until closed.
    if (alert.getAttribute("role") === "status") {
      armToast(alert);
    }
  }

  function setupToasts(root) {
    var alerts = root.matches && root.matches(".alert") ? [root] : root.querySelectorAll(".alert");
    alerts.forEach(bindToast);
  }
  setupToasts(document);

  // Surface a toast dynamically. If one is already showing, replace its
  // message and restart the countdown instead of stacking a second toast.
  window.showSoulCraftToast = function (message, variant) {
    var container = document.querySelector(".site-main .container");
    if (!container) return;
    var existing = container.querySelector(".alert");
    if (existing) dismissToast(existing, true); // one at a time — replace, don't stack

    var alert = document.createElement("div");
    alert.className = "alert alert--" + (variant || "info");
    alert.setAttribute("role", "status");

    var span = document.createElement("span");
    span.className = "alert-msg";
    span.textContent = message; // textContent only — never innerHTML for message text
    alert.appendChild(span);

    var close = document.createElement("button");
    close.type = "button";
    close.className = "alert-close";
    close.setAttribute("aria-label", "Dismiss");
    close.textContent = "\u00D7";
    alert.appendChild(close);

    container.insertBefore(alert, container.firstChild);
    bindToast(alert); // fresh timer — the countdown restarts on every call
  };

  /* ------------------------------------------------------------------ *
   * Support chatbot (Requirement 1 page + tiny rule-based backend)
   * ------------------------------------------------------------------ */
  var chatForm = document.getElementById("chat-form");
  var chatLog = document.getElementById("chat-log");
  if (chatForm && chatLog) {
    var chatText = document.getElementById("chat-text");
    chatForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var text = (chatText.value || "").trim();
      if (!text) return;
      appendMsg("user", text);
      chatText.value = "";
      chatText.focus();

      fetch(window.AURORA_CHAT_URL || "/support/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ message: text }),
      })
        .then(function (res) { return res.ok ? res.json() : Promise.reject(res); })
        .then(function (data) { appendMsg("bot", data.reply); })
        .catch(function () {
          appendMsg("bot", "Sorry — I couldn't reach the server. Please try again or submit a ticket below.");
        });
    });

    function appendMsg(kind, text) {
      var div = document.createElement("div");
      div.className = "msg msg--" + kind;
      var p = document.createElement("p");
      p.textContent = text; // textContent only — never innerHTML for user input
      div.appendChild(p);
      chatLog.appendChild(div);
      chatLog.scrollTop = chatLog.scrollHeight;
    }
  }
})();
