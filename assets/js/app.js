/* define:OMNI 참관 리포트 — 상호작용
   1) 탭 메뉴 현재 위치 표시  2) 읽기 진행 막대  3) 슬라이드 넘기기
   4) 사진 확대 보기  5) 등장 효과 */
(function () {
  "use strict";

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // 탭 이동 보정: 스크롤 중 사진이 늦게 로드되면 위치가 밀리므로, 멈춘 뒤 목표 위치로 다시 맞춘다.
  const SCROLL_SETTLE_MS = 140;
  const STABLE_CHECKS_TO_FINISH = 8;
  const SETTLE_TIMEOUT_MS = 5000;
  const POSITION_TOLERANCE_PX = 2;

  function initTabs() {
    const tabbar = document.querySelector(".tabbar");
    const header = document.querySelector(".site-header");
    const tabs = Array.from(document.querySelectorAll(".tabbar .tab"));
    const sections = tabs
      .map((tab) => document.querySelector(tab.getAttribute("href")))
      .filter(Boolean);
    if (!tabbar || !sections.length) return;

    let isJumping = false;
    let jumpToken = 0;

    // 탭바 자체만 가로로 스크롤한다. (scrollIntoView는 페이지 스크롤까지 건드려 이동을 끊어 버린다)
    const centerTab = (tab) => {
      const left = tab.offsetLeft - (tabbar.clientWidth - tab.offsetWidth) / 2;
      tabbar.scrollTo({ left: Math.max(0, left), behavior: prefersReducedMotion ? "auto" : "smooth" });
    };

    const setActive = (id) => {
      tabs.forEach((tab) => {
        const isActive = tab.getAttribute("href") === "#" + id;
        if (isActive && tab.getAttribute("aria-current") !== "true") centerTab(tab);
        tab.setAttribute("aria-current", isActive ? "true" : "false");
      });
    };

    const targetTop = (section) => {
      const offset = (header ? header.offsetHeight : 0) + 8;
      return Math.max(0, section.getBoundingClientRect().top + window.scrollY - offset);
    };

    const jumpTo = (section) => {
      const token = ++jumpToken;
      isJumping = true;
      setActive(section.id);
      window.scrollTo({ top: targetTop(section), behavior: prefersReducedMotion ? "instant" : "smooth" });

      // 도착한 뒤에도 잠시 지켜보다가, 위쪽 사진이 늦게 떠서 밀리면 다시 맞춘다.
      const startedAt = Date.now();
      let lastY = -1;
      let stableChecks = 0;
      const finish = () => { isJumping = false; setActive(section.id); };
      const settle = () => {
        if (token !== jumpToken) return;
        const y = window.scrollY;
        if (y !== lastY) { lastY = y; stableChecks = 0; setTimeout(settle, SCROLL_SETTLE_MS); return; }
        const goal = targetTop(section);
        const atBottom = y + window.innerHeight >= document.documentElement.scrollHeight - 1;
        const isTimedOut = Date.now() - startedAt > SETTLE_TIMEOUT_MS;
        if (Math.abs(goal - y) > POSITION_TOLERANCE_PX && !atBottom && !isTimedOut) {
          lastY = -1;
          window.scrollTo({ top: goal, behavior: "instant" });
          setTimeout(settle, SCROLL_SETTLE_MS);
          return;
        }
        stableChecks += 1;
        if (stableChecks >= STABLE_CHECKS_TO_FINISH || isTimedOut) { finish(); return; }
        setTimeout(settle, SCROLL_SETTLE_MS);
      };
      setTimeout(settle, SCROLL_SETTLE_MS);
    };

    // 탭뿐 아니라 목차·본문 속 '#세션' 링크도 모두 같은 방식으로 이동시킨다.
    document.addEventListener("click", (event) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest('a[href^="#"]');
      if (!link) return;
      const hash = link.getAttribute("href");
      if (hash.length < 2) return;
      const target = document.getElementById(decodeURIComponent(hash.slice(1)));
      if (!target) return;
      event.preventDefault();
      history.replaceState(null, "", hash);
      jumpTo(target);
    });

    // 사용자가 직접 휠·터치로 움직이면 보정을 멈춘다.
    const cancelJump = () => { if (isJumping) { jumpToken += 1; isJumping = false; } };
    ["wheel", "touchstart", "keydown", "pointerdown"].forEach((type) => window.addEventListener(type, cancelJump, { passive: true }));

    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (isJumping) return;
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
