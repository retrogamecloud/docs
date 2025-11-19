// Cambiar texto de "Copy page" a "Copiar"
function translateCopyButton() {
  const copyButtons = document.querySelectorAll('#page-context-menu-button span, #page-context-menu button span');
  copyButtons.forEach(button => {
    if (button.textContent === 'Copy page') {
      button.textContent = 'Copiar';
    }
  });
}

// Cambiar texto de "Powered by Mintlify"
function translateFooter() {
  const footerLinks = document.querySelectorAll('footer a');
  footerLinks.forEach(link => {
    if (link.textContent.includes('Powered by Mintlify')) {
      link.textContent = 'Documentación RetroGame Cloud';
    }
  });
}

// Cambiar tooltips de "Copy" en bloques de código
function translateCodeTooltips() {
  const tooltips = document.querySelectorAll('.code-block [aria-hidden="true"]');
  tooltips.forEach(tooltip => {
    if (tooltip.textContent === 'Copy') {
      tooltip.textContent = 'Copiar';
    }
    if (tooltip.textContent === 'Copied!') {
      tooltip.textContent = '¡Copiado!';
    }
  });
}

// Función principal de traducción
function translateUI() {
  translateCopyButton();
  translateFooter();
  translateCodeTooltips();
}

// Ejecutar cuando la página carga
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', translateUI);
} else {
  translateUI();
}

// Observar cambios en el DOM para páginas navegadas con SPA
const observer = new MutationObserver(() => {
  translateUI();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});
