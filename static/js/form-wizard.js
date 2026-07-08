/* ========================================
   STONELYTICS — Form Wizard JavaScript
   Multi-step contact form with live module preview
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {

  const WIZARD_MODULES = [
    { id: 'landing', name: 'Landing Page', icon: 'ti-layout', active: true },
    { id: 'whatsapp', name: 'WhatsApp', icon: 'ti-brand-whatsapp', active: true },
    { id: 'contact', name: 'Formulario', icon: 'ti-mail', active: true },
    { id: 'quiz', name: 'Quiz Interactivo', icon: 'ti-chart-dots', active: false },
    { id: 'crm', name: 'CRM', icon: 'ti-users', active: false },
    { id: 'agenda', name: 'Agenda', icon: 'ti-calendar', active: false },
    { id: 'dashboard', name: 'Dashboard', icon: 'ti-dashboard', active: false },
    { id: 'ai', name: 'IA Asistente', icon: 'ti-robot', active: false },
    { id: 'analytics', name: 'Analytics', icon: 'ti-chart-bar', active: false },
    { id: 'automation', name: 'Automatización', icon: 'ti-arrows-diagonal', active: false },
  ];

  const modules = WIZARD_MODULES.map(m => ({ ...m }));

  function renderModules(container, mods) {
    container.innerHTML = mods.map(m =>
      `<div class="build-module ${m.active ? 'build-module--active' : ''}">
        <i class="ti ${m.icon}"></i>
        <span>${m.name}</span>
        ${m.active ? '<i class="ti ti-check build-module__check"></i>' : ''}
      </div>`
    ).join('');
  }

  function updateModules() {
    const challenge = document.getElementById('challenge')?.value;
    const acquisition = document.getElementById('acquisition')?.value;
    const businessType = document.getElementById('business_type')?.value;

    modules.forEach(m => m.active = false);
    modules.find(m => m.id === 'landing').active = true;
    modules.find(m => m.id === 'whatsapp').active = true;
    modules.find(m => m.id === 'contact').active = true;

    if (challenge === 'captacion' || challenge === 'presencia') {
      modules.find(m => m.id === 'quiz').active = true;
      modules.find(m => m.id === 'crm').active = true;
    }
    if (challenge === 'procesos' || challenge === 'herramientas') {
      modules.find(m => m.id === 'agenda').active = true;
      modules.find(m => m.id === 'automation').active = true;
    }
    if (challenge === 'tiempo') {
      modules.find(m => m.id === 'dashboard').active = true;
      modules.find(m => m.id === 'analytics').active = true;
    }
    if (businessType === 'salud' || businessType === 'legal') {
      modules.find(m => m.id === 'agenda').active = true;
    }
    if (acquisition === 'redes' || acquisition === 'google') {
      modules.find(m => m.id === 'analytics').active = true;
    }

    const buildEl = document.getElementById('buildModules');
    const resultEl = document.getElementById('resultModules');
    if (buildEl) renderModules(buildEl, modules);
    if (resultEl) renderModules(resultEl, modules.filter(m => m.active));
  }

  function goToStep(step) {
    document.querySelectorAll('.form-wizard__panel').forEach(p => p.classList.remove('form-wizard__panel--active'));
    document.querySelector(`[data-panel="${step}"]`)?.classList.add('form-wizard__panel--active');
    document.querySelectorAll('.form-wizard__step').forEach(s => {
      const sNum = parseInt(s.dataset.step);
      s.classList.toggle('form-wizard__step--done', sNum < step);
      s.classList.toggle('form-wizard__step--active', sNum === step);
    });
  }

  document.querySelectorAll('.wizard-next').forEach(btn => {
    btn.addEventListener('click', () => {
      updateModules();
      goToStep(parseInt(btn.dataset.next));
    });
  });

  document.querySelectorAll('.wizard-prev').forEach(btn => {
    btn.addEventListener('click', () => {
      goToStep(parseInt(btn.dataset.prev));
    });
  });

  document.querySelectorAll('select').forEach(sel => {
    sel.addEventListener('change', updateModules);
  });

});
