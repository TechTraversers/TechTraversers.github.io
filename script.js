function loadSidebar() {
  const placeholder = document.querySelector("[data-sidebar-placeholder]");

  if (!placeholder) {
    return;
  }

  if (window.location.protocol === "file:") {
    const warning = document.createElement("aside");
    warning.className = "sidebar";
    warning.textContent = "I'm sorry, please use a dynamic hosting service to view the site to use this function";
    placeholder.replaceWith(warning);
    return;
  }

  const scriptTag =
    document.currentScript ||
    document.querySelector('script[src$="/script.js"]') ||
    document.querySelector('script[src="script.js"]') ||
    document.querySelector('script[src="../script.js"]') ||
    document.querySelector('script[src="../../script.js"]');

  const scriptSrc = scriptTag ? scriptTag.src : new URL("script.js", document.baseURI).href;
  const sidebarUrl = new URL("sidebar.html", scriptSrc).href;

  fetch(sidebarUrl)
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Failed to load sidebar.");
      }

      return response.text();
    })
    .then(function (html) {
      const wrapper = document.createElement("div");
      wrapper.innerHTML = html.trim();

      const sidebar = wrapper.firstElementChild;

      if (!sidebar) {
        return;
      }

      const currentNav = placeholder.getAttribute("data-sidebar-current");
      if (currentNav) {
        const currentLink = sidebar.querySelector('[data-nav="' + currentNav + '"]');
        if (currentLink) {
          currentLink.id = "current";
        }
      }

      placeholder.replaceWith(sidebar);
      
      // Setup mobile menu toggle
      setupMobileMenu();
    })
    .catch(function (error) {
      console.error(error);
    });
}

function setupMobileMenu() {
  const menuToggle = document.getElementById("menu-toggle");
  const sidebar = document.querySelector(".sidebar");

  if (!menuToggle || !sidebar) {
    return;
  }

  menuToggle.addEventListener("click", function () {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", !isOpen);
    sidebar.classList.toggle("open");
  });

  // Close menu when clicking a link
  const sidebarLinks = sidebar.querySelectorAll("a");
  sidebarLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      menuToggle.setAttribute("aria-expanded", "false");
      sidebar.classList.remove("open");
    });
  });

  // Close menu when clicking outside
  document.addEventListener("click", function (event) {
    const isMenuClick = menuToggle.contains(event.target);
    const isSidebarClick = sidebar.contains(event.target);
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";

    if (isOpen && !isMenuClick && !isSidebarClick) {
      menuToggle.setAttribute("aria-expanded", "false");
      sidebar.classList.remove("open");
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", loadSidebar);
} else {
  loadSidebar();
}
