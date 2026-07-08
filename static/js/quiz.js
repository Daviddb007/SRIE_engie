/* ========================================
   STONELYTICS — Quiz JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {
  const totalSteps = document.querySelectorAll('.quiz-step').length;
  let currentStep = 1;
  const answers = [];

  const prevBtn = document.getElementById('quizPrev');
  const nextBtn = document.getElementById('quizNext');
  const progressDots = document.querySelectorAll('.quiz-progress__dot');
  const quizContact = document.getElementById('quizContact');
  const quizResult = document.getElementById('quizResult');

  function updateUI() {
    // Hide all steps
    document.querySelectorAll('.quiz-step').forEach(s => s.classList.remove('active'));
    quizContact.classList.remove('active');
    quizResult.classList.remove('active');

    // Show current
    if (currentStep <= totalSteps) {
      document.querySelector(`.quiz-step[data-step="${currentStep}"]`).classList.add('active');
    } else if (currentStep === totalSteps + 1) {
      quizContact.classList.add('active');
    } else {
      quizResult.classList.add('active');
      nextBtn.style.display = 'none';
      prevBtn.style.display = 'none';
      return;
    }

    // Progress dots
    progressDots.forEach(dot => {
      const stepNum = parseInt(dot.dataset.step);
      dot.classList.remove('active', 'completed');
      if (stepNum === currentStep) {
        dot.classList.add('active');
      } else if (stepNum < currentStep || (currentStep > totalSteps && stepNum <= totalSteps)) {
        dot.classList.add('completed');
      }
    });

    // Buttons
    prevBtn.style.display = currentStep > 1 ? 'inline-flex' : 'none';

    if (currentStep === totalSteps + 1) {
      nextBtn.innerHTML = '<span class="btn__text">Enviar solicitud</span><span class="btn__loader"><i class="ti ti-loader-2 ti-spin"></i></span>';
    } else {
      nextBtn.innerHTML = 'Siguiente <i class="ti ti-arrow-right"></i>';
    }

    // Check if current step has selection
    const selected = document.querySelector(`.quiz-option.selected[data-step="${currentStep}"]`);
    nextBtn.disabled = !selected && currentStep <= totalSteps;
  }

  // Option selection
  document.querySelectorAll('.quiz-option').forEach(option => {
    option.addEventListener('click', () => {
      const step = option.dataset.step;
      // Deselect siblings
      document.querySelectorAll(`.quiz-option[data-step="${step}"]`).forEach(o => o.classList.remove('selected'));
      option.classList.add('selected');

      // Store answer
      const existing = answers.findIndex(a => a.step === parseInt(step));
      const answerData = { step: parseInt(step), value: option.dataset.value, points: parseInt(option.dataset.points) };
      if (existing >= 0) {
        answers[existing] = answerData;
      } else {
        answers.push(answerData);
      }

      nextBtn.disabled = false;
    });
  });

  // Next button
  nextBtn.addEventListener('click', async () => {
    if (currentStep <= totalSteps) {
      const selected = document.querySelector(`.quiz-option.selected[data-step="${currentStep}"]`);
      if (!selected) return;
      currentStep++;
      updateUI();
    } else if (currentStep === totalSteps + 1) {
      // Validate contact
      const name = document.getElementById('qName').value.trim();
      const email = document.getElementById('qEmail').value.trim();
      const business = document.getElementById('qBusiness').value.trim();
      const whatsapp = document.getElementById('qWhatsapp').value.trim();

      if (!name || !email || !business) {
        alert('Por favor completa los campos obligatorios.');
        return;
      }

      // Submit
      nextBtn.disabled = true;
      nextBtn.classList.add('loading');

      try {
        const res = await fetch('/quiz/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            answers,
            contact: { name, email, business, whatsapp },
          }),
        });

        const data = await res.json();

        if (data.ok) {
          const plan = data.plan;
          document.getElementById('resultPlan').textContent = plan.name;
          document.getElementById('resultDescription').textContent = plan.description;

          const featuresList = document.getElementById('resultFeatures');
          featuresList.innerHTML = '';
          plan.features.forEach(f => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="ti ti-check"></i> ${f}`;
            featuresList.appendChild(li);
          });

          currentStep++;
          updateUI();
        } else {
          alert(data.error || 'Ocurrió un error. Intenta de nuevo.');
          nextBtn.disabled = false;
        }
      } catch {
        alert('Error de conexión. Verifica tu internet e intenta de nuevo.');
        nextBtn.disabled = false;
      } finally {
        nextBtn.classList.remove('loading');
      }
    }
  });

  // Previous button
  prevBtn.addEventListener('click', () => {
    if (currentStep > 1) {
      currentStep--;
      updateUI();
    }
  });

  // Init
  updateUI();
});
