// Topbar custom buttons injection
(function() {
  function addCustomButtons() {
    // Try multiple selectors for different screen sizes
    const searchBar = document.getElementById('search-bar-entry');
    const searchBarMobile = document.getElementById('search-bar-entry-mobile');
    
    // Desktop: search bar container
    const desktopContainer = searchBar?.parentElement;
    
    // Mobile: find the container with search and menu buttons
    const mobileContainer = searchBarMobile?.parentElement;
    
    if (!desktopContainer && !mobileContainer) {
      setTimeout(addCustomButtons, 100);
      return;
    }

    // Check if buttons already exist
    if (document.getElementById('custom-github-btn')) {
      return;
    }

    // Create buttons HTML
    function createButtons(isMobile = false) {
      const container = document.createElement('div');
      container.id = 'custom-buttons-container';
      container.className = 'flex items-center gap-2';
      container.style.cssText = isMobile ? 'flex-shrink: 0;' : 'flex-shrink: 0; margin-right: 12px;';

      // GitHub button
      const githubBtn = document.createElement('a');
      githubBtn.id = isMobile ? 'custom-github-btn-mobile' : 'custom-github-btn';
      githubBtn.href = 'https://github.com/retrogamecloud';
      githubBtn.target = '_blank';
      githubBtn.rel = 'noopener noreferrer';
      
      if (isMobile) {
        // Mobile: icon only
        githubBtn.className = 'text-gray-500 w-8 h-8 flex items-center justify-center hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300';
        githubBtn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
        `;
      } else {
        // Desktop: icon + text
        githubBtn.className = 'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 bg-transparent border border-gray-400/30 dark:border-gray-600/30 text-gray-700 dark:text-gray-300 hover:border-gray-600/30 dark:hover:border-gray-500/30 hover:bg-gray-50 dark:hover:bg-background-dark dark:hover:brightness-125';
        githubBtn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          <span>GitHub</span>
        `;
      }

      // Play button
      const playBtn = document.createElement('a');
      playBtn.id = isMobile ? 'custom-play-btn-mobile' : 'custom-play-btn';
      playBtn.href = 'https://retrogamehub.games';
      playBtn.target = '_blank';
      playBtn.rel = 'noopener noreferrer';
      
      if (isMobile) {
        // Mobile: icon only with gradient
        playBtn.className = 'w-8 h-8 flex items-center justify-center rounded-lg';
        playBtn.style.cssText = 'background: linear-gradient(135deg, #00ff88 0%, #00aa55 100%);';
        playBtn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        `;
      } else {
        // Desktop: icon + text
        playBtn.className = 'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 text-white shadow-md hover:shadow-lg transform hover:-translate-y-0.5';
        playBtn.style.cssText = 'background: linear-gradient(135deg, #00ff88 0%, #00aa55 100%); border: none;';
        playBtn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          <span>Jugar Ahora</span>
        `;
        
        // Hover effect for desktop
        playBtn.addEventListener('mouseenter', function() {
          this.style.background = 'linear-gradient(135deg, #00aa55 0%, #00ff88 100%)';
        });
        playBtn.addEventListener('mouseleave', function() {
          this.style.background = 'linear-gradient(135deg, #00ff88 0%, #00aa55 100%)';
        });
      }

      container.appendChild(githubBtn);
      container.appendChild(playBtn);
      return container;
    }

    // Add to desktop
    if (desktopContainer && searchBar) {
      const desktopButtons = createButtons(false);
      desktopContainer.insertBefore(desktopButtons, searchBar);
    }

    // Add to mobile - insert at the beginning of the container
    if (mobileContainer && searchBarMobile) {
      const mobileButtons = createButtons(true);
      mobileButtons.id = 'custom-buttons-container-mobile';
      // Insert as first child to avoid overlap
      mobileContainer.insertBefore(mobileButtons, mobileContainer.firstChild);
    }
  }

  // Run on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addCustomButtons);
  } else {
    addCustomButtons();
  }

  // Re-run on navigation (for SPA behavior)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      setTimeout(addCustomButtons, 300);
    }
  }).observe(document, {subtree: true, childList: true});
})();
