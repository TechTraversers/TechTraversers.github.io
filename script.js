function loadSidebar() {
  const placeholder = document.querySelector("[data-sidebar-placeholder]");

  if (!placeholder) {
    return;
  }

  fetch("/sidebar.html")
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
    })
    .catch(function (error) {
      console.error(error);
    });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", loadSidebar);
} else {
  loadSidebar();
}
