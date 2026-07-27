// Shared helpers for the Tiny-LLM analysis reports:
//  1. initialise Mermaid with a light theme
//  2. auto-build the left-hand table of contents from <h2>/<h3> in .content
//  3. highlight the active section while scrolling
//  4. mobile menu toggle

(function () {
  // ---- Mermaid (light theme) ----
  if (window.mermaid) {
    window.mermaid.initialize({
      startOnLoad: true,
      theme: "default",
      themeVariables: {
        background: "#ffffff",
        primaryColor: "#eaf1fb",
        primaryBorderColor: "#2563c9",
        primaryTextColor: "#23303a",
        lineColor: "#6b7785",
        fontfamily: "Segoe UI, PingFang SC, Microsoft YaHei, sans-serif"
      },
      flowchart: { htmlLabels: true, curve: "basis" },
      securityLevel: "loose"
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var content = document.querySelector(".content");
    var toc = document.querySelector(".toc");
    if (!content || !toc) return;

    var headings = content.querySelectorAll("h2, h3");
    var links = [];
    var counter = 0;

    headings.forEach(function (h) {
      if (!h.id) {
        h.id = "sec-" + (counter++);
      }
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent;
      a.className = h.tagName.toLowerCase() === "h3" ? "h3" : "h2";
      li.appendChild(a);
      toc.appendChild(li);
      links.push(a);
    });

    // Scroll spy
    var map = {};
    links.forEach(function (a) {
      map[a.getAttribute("href").slice(1)] = a;
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            links.forEach(function (l) { l.classList.remove("active"); });
            var active = map[entry.target.id];
            if (active) {
              active.classList.add("active");
              // keep active item visible in the sidebar
              active.scrollIntoView({ block: "nearest" });
            }
          }
        });
      },
      { rootMargin: "0px 0px -75% 0px", threshold: 0 }
    );
    headings.forEach(function (h) { observer.observe(h); });

    // Mobile toggle
    var toggle = document.querySelector(".menu-toggle");
    var sidebar = document.querySelector(".sidebar");
    if (toggle && sidebar) {
      toggle.addEventListener("click", function () { sidebar.classList.toggle("open"); });
      toc.addEventListener("click", function (e) {
        if (e.target.tagName === "A") sidebar.classList.remove("open");
      });
    }
  });
})();
