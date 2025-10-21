document.getElementById("toggle-btn").addEventListener("click", function () {
      const sidebar = document.getElementById("sidebar");
      sidebar.classList.toggle("collapsed");

      const title = document.getElementById("sidebar-title");
      title.style.display = sidebar.classList.contains("collapsed") ? "none" : "block";
  });