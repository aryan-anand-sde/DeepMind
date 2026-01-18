document.addEventListener("DOMContentLoaded", () => {
  // file input helper
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
    uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const btn = uploadForm.querySelector("button");
    const originalBtnText = btn.textContent;
    btn.textContent = "Processing...";
    btn.disabled = true;

    try {
      const res = await fetch("/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      displayResult(data);
    } catch (err) {
      console.error(err);
      resultView.innerHTML = `<div class="card" style="border: 1px solid red; color: red;">Error: ${err.message}</div>`;
      resultView.style.display = "block";
    } finally {
      btn.textContent = originalBtnText;
      btn.disabled = false;
    }
  });

  });





















  });