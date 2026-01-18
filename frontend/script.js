document.addEventListener("DOMContentLoaded", () => {
  // File Input Helper
  document.querySelectorAll('input[type="file"]').forEach((input) => {
    input.addEventListener("change", (e) => {
      const fileName = e.target.files[0]?.name;
      const dropArea = e.target.closest(".file-drop-area");
      const msg = dropArea.querySelector(".file-msg");
      if (fileName) {
        msg.textContent = fileName;
        dropArea.style.borderColor = "var(--primary-color)";
      } else {
        msg.textContent = "Drag & Drop or Click to Upload";
        dropArea.style.borderColor = "";
      }
    });

     const uploadForm = document.getElementById("upload-form");
    const resultView = document.getElementById("result-view");

  });





















  });