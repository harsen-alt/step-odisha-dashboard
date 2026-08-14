/* Shared left sidebar nav, injected into every app page (everything except
 * the landing page index.html). Add `<div id="app-nav"></div>` right before
 * the page's main content and include this script — no per-page markup
 * duplication, so adding/renaming a nav item is a one-file change.
 *
 * Placeholder pages: Classroom Transaction, Classroom Observation, Learning
 * Circle, Review Meetings, School-Level Showcase, Stakeholder School Visits,
 * Qualitative Insights, and Settings have no content built yet — flagged
 * with `placeholder: true` here, which shows a "Soon" badge in the nav and
 * matches the "Coming soon" pages at their hrefs.
 */
(function () {
  "use strict";

  var NAV_ITEMS = [
    { label: "Dashboard", href: "dashboard.html" },
    { label: "School Coverage", href: "dashboard.html#district-level-school-coverage" },
    { label: "Classroom Transaction", href: "classroom-transaction.html", placeholder: true },
    { label: "Classroom Observation", href: "classroom-observation.html", placeholder: true },
    { label: "Learning Circle", href: "learning-circle.html", placeholder: true },
    { label: "Review Meetings", href: "review-meetings.html", placeholder: true },
    { label: "School-Level Showcase", href: "school-showcase.html", placeholder: true },
    { label: "Stakeholder School Visits", href: "stakeholder-visits.html", placeholder: true },
    { label: "Qualitative Insights", href: "qualitative-insights.html", placeholder: true },
    { label: "Settings", href: "settings.html", placeholder: true }
  ];

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function isActive(item) {
    var currentFile = location.pathname.split("/").pop() || "index.html";
    var currentHash = location.hash || "";
    var parts = item.href.split("#");
    var itemFile = parts[0];
    var itemHash = parts[1] ? "#" + parts[1] : "";
    if (itemFile !== currentFile) return false;
    return itemHash === "" ? currentHash === "" : currentHash === itemHash;
  }

  // Re-run on hashchange too: clicking an in-page anchor (e.g. Dashboard ->
  // School Coverage, same document) never fires DOMContentLoaded again, so
  // without this the sidebar would keep highlighting the page's first
  // matching item forever instead of following the hash.
  function updateActiveStates() {
    document.querySelectorAll(".app-sidebar a.nav-item").forEach(function (a) {
      var item = NAV_ITEMS[Number(a.getAttribute("data-idx"))];
      a.classList.toggle("active", !!item && isActive(item));
    });
  }

  function render(container) {
    var itemsHtml = NAV_ITEMS.map(function (item, idx) {
      return '<a class="nav-item" data-idx="' + idx + '" href="' + escapeHtml(item.href) + '">' +
        '<span class="dot"></span><span>' + escapeHtml(item.label) + "</span>" +
        (item.placeholder ? '<span class="soon-badge">Soon</span>' : "") +
        "</a>";
    }).join("");

    var html =
      '<div class="nav-topbar">' +
        '<button class="hamburger" type="button" aria-label="Open menu" aria-expanded="false">' +
          '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="0" y1="1" x2="18" y2="1"></line><line x1="0" y1="7" x2="18" y2="7"></line><line x1="0" y1="13" x2="18" y2="13"></line></svg>' +
        "</button>" +
        '<span class="title">STEP Odisha</span>' +
      "</div>" +
      '<div class="nav-backdrop"></div>' +
      '<aside class="app-sidebar">' +
        '<a class="brand" href="index.html"><span class="name">STEP Odisha</span><span class="tag">Program Dashboard</span></a>' +
        "<nav>" + itemsHtml + "</nav>" +
        '<div class="sidebar-foot">AY2026-27 &middot; Mantra4Change</div>' +
      "</aside>";

    container.outerHTML = html;

    var sidebar = document.querySelector(".app-sidebar");
    var backdrop = document.querySelector(".nav-backdrop");
    var toggle = document.querySelector(".hamburger");

    function closeNav() {
      sidebar.classList.remove("open");
      backdrop.classList.remove("show");
      toggle.setAttribute("aria-expanded", "false");
    }
    function openNav() {
      sidebar.classList.add("open");
      backdrop.classList.add("show");
      toggle.setAttribute("aria-expanded", "true");
    }
    toggle.addEventListener("click", function () {
      if (sidebar.classList.contains("open")) closeNav(); else openNav();
    });
    backdrop.addEventListener("click", closeNav);
    sidebar.querySelectorAll("a.nav-item").forEach(function (a) {
      a.addEventListener("click", closeNav);
    });

    updateActiveStates();
    window.addEventListener("hashchange", updateActiveStates);
  }

  function init() {
    var container = document.getElementById("app-nav");
    if (container) render(container);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
