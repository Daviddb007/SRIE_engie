/* ========================================
   STONELYTICS — Main JavaScript
   Consolidated: counters, scroll, nav, burger, contact form
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- ANIMATED COUNTERS ---------- */
  function animateCounter(el, target, duration) {
    const start = performance.now();
    const suffix = el.dataset.suffix || '';
    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString('es-CO') + suffix;
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  function setupCounterObserver(selector, options = {}) {
    const { threshold = 0.3, duration = 2000, delay = 300 } = options;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('.counter').forEach((el, i) => {
            const target = parseInt(el.dataset.target, 10);
            setTimeout(() => animateCounter(el, target, duration), i * delay);
          });
          observer.unobserve(entry.target);
        }
      });
    }, { threshold });
    const el = document.querySelector(selector);
    if (el) observer.observe(el);
  }

  setupCounterObserver('.hero__stats', { duration: 1800, delay: 200 });
  setupCounterObserver('.dashboard-mock__metrics');

  /* ---------- SMOOTH SCROLL ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (href === '#') return;
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
        const navLinks = document.getElementById('navLinks');
        if (navLinks) navLinks.classList.remove('open');
      }
    });
  });

  /* ---------- ACTIVE NAV LINK ---------- */
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.navbar__link');

  if (sections.length && navLinks.length) {
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
          });
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0 });
    sections.forEach(section => sectionObserver.observe(section));
  }

  /* ---------- MOBILE BURGER ---------- */
  const burger = document.getElementById('burger');
  const navLinksEl = document.getElementById('navLinks');

  if (burger && navLinksEl) {
    burger.addEventListener('click', () => {
      navLinksEl.classList.toggle('open');
      burger.innerHTML = navLinksEl.classList.contains('open')
        ? '<i class="ti ti-x"></i>'
        : '<i class="ti ti-menu-2"></i>';
    });
  }

  /* ---------- MOBILE NAV (full-screen) ---------- */
  const mobileNav = document.getElementById('mobileNav');
  const mobileNavClose = document.getElementById('mobileNavClose');
  if (mobileNav && mobileNavClose) {
    mobileNavClose.addEventListener('click', () => mobileNav.classList.remove('active'));
    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => mobileNav.classList.remove('active'));
    });
    if (burger) {
      burger.addEventListener('click', () => mobileNav.classList.add('active'));
    }
  }

  /* ---------- NAVBAR SCROLL EFFECT ---------- */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('navbar--scrolled', window.scrollY > 50);
    });
  }

  /* ---------- CONTACT FORM (fetch) ---------- */
  const form = document.getElementById('contactForm');
  const submitBtn = document.getElementById('submitBtn');
  const formMessage = document.getElementById('formMessage');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }

      const btnText = submitBtn.querySelector('.btn__text');
      const btnLoader = submitBtn.querySelector('.btn__loader');

      submitBtn.disabled = true;
      if (btnText) btnText.hidden = true;
      if (btnLoader) btnLoader.hidden = false;
      formMessage.className = 'form-message';
      formMessage.textContent = '';

      try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const res = await fetch('/contacto', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const result = await res.json();

        if (result.ok) {
          formMessage.className = 'form-message success';
          formMessage.textContent = '¡Mensaje enviado con éxito! Te contactaremos pronto.';
          form.reset();
        } else {
          formMessage.className = 'form-message error';
          formMessage.textContent = result.error || 'Ocurrió un error. Intenta de nuevo.';
        }
      } catch {
        formMessage.className = 'form-message error';
        formMessage.textContent = 'Error de conexión. Verifica tu internet e intenta de nuevo.';
      } finally {
        submitBtn.disabled = false;
        if (btnText) btnText.hidden = false;
        if (btnLoader) btnLoader.hidden = true;
      }
    });
  }

  /* ---------- VIDEO PLAYER ---------- */
  const video = document.getElementById('demoVideo');
  const videoOverlay = document.getElementById('videoOverlay');

  if (video && videoOverlay) {
    videoOverlay.addEventListener('click', () => {
      if (video.paused) {
        video.play();
        videoOverlay.style.opacity = '0';
        videoOverlay.style.pointerEvents = 'none';
      } else {
        video.pause();
        videoOverlay.style.opacity = '1';
        videoOverlay.style.pointerEvents = 'auto';
      }
    });

    video.addEventListener('ended', () => {
      videoOverlay.style.opacity = '1';
      videoOverlay.style.pointerEvents = 'auto';
    });

    video.addEventListener('click', () => {
      if (!video.paused) {
        video.pause();
        videoOverlay.style.opacity = '1';
        videoOverlay.style.pointerEvents = 'auto';
      }
    });
  }

});
