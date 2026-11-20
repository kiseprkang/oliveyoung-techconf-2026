/* define:OMNI 참관 리포트 — 상호작용
   1) 탭 메뉴 현재 위치 표시  2) 읽기 진행 막대  3) 슬라이드 넘기기
   4) 사진 확대 보기  5) 등장 효과 */
(function () {
  "use strict";

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function initTabs() {
    const tabs = Array.from(document.querySelectorAll(".tabbar .tab"));
    const sections = tabs
      .map((tab) => document.querySelector(tab.getAttribute("href")))
      .filter(Boolean);
    if (!sections.length || !("IntersectionObserver" in window)) return;

    const setActive = (id) => {
      tabs.forEach((tab) => {
        const isActive = tab.getAttribute("href") === "#" + id;
        tab.setAttribute("aria-current", isActive ? "true" : "false");
        if (isActive) {
          tab.scrollIntoView({ block: "nearest", inline: "center", behavior: prefersReducedMotion ? "auto" : "smooth" });
        }
      });
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      },
      { rootMargin: "-30% 0px -60% 0px" }
    );
    sections.forEach((section) => observer.observe(section));
  }

  function initProgress() {
    const bar = document.querySelector(".progress");
    if (!bar) return;
    let ticking = false;
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
      bar.style.transform = "scaleX(" + ratio + ")";
      ticking = false;
    };
    window.addEventListener("scroll", () => {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  function initDeck(deck) {
    const track = deck.querySelector(".deck-track");
    const slides = Array.from(track.querySelectorAll(".slide"));
    const prev = deck.querySelector("[data-deck-prev]");
    const next = deck.querySelector("[data-deck-next]");
    const count = deck.querySelector(".deck-count");
    const rail = deck.querySelector(".deck-rail");
    let current = 0;

    const railButtons = slides.map((slide, i) => {
      const button = document.createElement("button");
      button.type = "button";
      button.setAttribute("aria-label", (i + 1) + "번째 슬라이드로 이동");
      button.addEventListener("click", () => goTo(i));
      rail.appendChild(button);
      return button;
    });

    function render() {
      count.textContent = String(current + 1).padStart(2, "0") + " / " + String(slides.length).padStart(2, "0");
      prev.disabled = current === 0;
      next.disabled = current === slides.length - 1;
      railButtons.forEach((b, i) => b.setAttribute("aria-current", i === current ? "true" : "false"));
    }

    function goTo(index) {
      const target = Math.max(0, Math.min(index, slides.length - 1));
      track.scrollTo({ left: slides[target].offsetLeft - track.offsetLeft, behavior: prefersReducedMotion ? "auto" : "smooth" });
    }

    prev.addEventListener("click", () => goTo(current - 1));
    next.addEventListener("click", () => goTo(current + 1));

    track.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight") { event.preventDefault(); goTo(current + 1); }
      if (event.key === "ArrowLeft") { event.preventDefault(); goTo(current - 1); }
    });

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              current = slides.indexOf(entry.target);
              render();
            }
          });
        },
        { root: track, threshold: 0.6 }
      );
      slides.forEach((slide) => observer.observe(slide));
    }
    render();
  }

  function initLightbox() {
    const box = document.querySelector(".lightbox");
    if (!box) return;
    const img = box.querySelector("img");
    const cap = box.querySelector(".cap");
    const closeBtn = box.querySelector(".close");
    let lastFocus = null;

    const open = (src, alt) => {
      lastFocus = document.activeElement;
      img.src = src;
      img.alt = alt || "";
      cap.textContent = alt || "";
      box.classList.add("open");
      document.body.style.overflow = "hidden";
      closeBtn.focus();
    };
    const close = () => {
      box.classList.remove("open");
      document.body.style.overflow = "";
      img.removeAttribute("src");
      if (lastFocus) lastFocus.focus();
    };

    document.querySelectorAll("[data-zoom]").forEach((el) => {
      const image = el.querySelector("img");
      if (!image) return;
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "button");
      el.setAttribute("aria-label", "크게 보기: " + image.alt);
      const handler = () => open(image.currentSrc || image.src, image.alt);
      el.addEventListener("click", handler);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); handler(); }
      });
    });
    closeBtn.addEventListener("click", close);
    box.addEventListener("click", (e) => { if (e.target === box) close(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && box.classList.contains("open")) close(); });
  }

  function initReveal() {
    const items = document.querySelectorAll(".reveal");
    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("in"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px" }
    );
    items.forEach((el) => observer.observe(el));
  }

  document.documentElement.classList.remove("no-js");
  initTabs();
  initProgress();
  document.querySelectorAll(".deck").forEach(initDeck);
  initLightbox();
  initReveal();
})();
