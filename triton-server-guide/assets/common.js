(function () {
  var pages = [
    ["index.html", "首页与结论"],
    ["concepts.html", "核心概念与架构"],
    ["single-gpu-lab.html", "单 GPU 实验条件"],
    ["model-repository.html", "Quickstart 与模型仓库"],
    ["pytorch-backend.html", "PyTorch 后端"],
    ["vllm-backend.html", "vLLM 与本地 LLM"],
    ["batching-observability.html", "Batching 与可观测性"],
    ["windows-wsl2.html", "Windows 与 WSL2"],
    ["learning-roadmap.html", "学习路线与检查表"]
  ];

  if (window.mermaid) {
    window.mermaid.initialize({
      startOnLoad: true,
      theme: "default",
      securityLevel: "loose",
      themeVariables: {
        background: "#ffffff",
        primaryColor: "#edf6eb",
        primaryBorderColor: "#356b2f",
        primaryTextColor: "#263238",
        lineColor: "#66727d",
        secondaryColor: "#edf4fb",
        tertiaryColor: "#fff8e6",
        fontFamily: "Segoe UI, PingFang SC, Microsoft YaHei, sans-serif"
      },
      flowchart: { htmlLabels: true, curve: "basis" },
      sequence: { useMaxWidth: true }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var siteNav = document.querySelector(".site-nav");
    var toc = document.querySelector(".toc");
    var content = document.querySelector(".content");
    var current = window.location.pathname.split("/").pop() || "index.html";

    if (siteNav) {
      pages.forEach(function (page) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = page[0];
        a.textContent = page[1];
        if (current === page[0]) a.className = "current";
        li.appendChild(a);
        siteNav.appendChild(li);
      });
    }

    if (toc && content) {
      var headings = Array.prototype.slice.call(content.querySelectorAll("h2, h3"));
      var links = [];
      headings.forEach(function (heading, index) {
        if (!heading.id) heading.id = "section-" + index;
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#" + heading.id;
        a.textContent = heading.textContent;
        a.className = heading.tagName === "H3" ? "h3" : "h2";
        li.appendChild(a);
        toc.appendChild(li);
        links.push(a);
      });

      if ("IntersectionObserver" in window) {
        var map = {};
        links.forEach(function (a) { map[a.hash.slice(1)] = a; });
        var observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            links.forEach(function (link) { link.classList.remove("active"); });
            if (map[entry.target.id]) map[entry.target.id].classList.add("active");
          });
        }, { rootMargin: "0px 0px -75% 0px" });
        headings.forEach(function (heading) { observer.observe(heading); });
      }
    }

    var toggle = document.querySelector(".menu-toggle");
    var sidebar = document.querySelector(".sidebar");
    if (toggle && sidebar) {
      toggle.addEventListener("click", function () { sidebar.classList.toggle("open"); });
      sidebar.addEventListener("click", function (event) {
        if (event.target.tagName === "A") sidebar.classList.remove("open");
      });
    }
  });
})();
