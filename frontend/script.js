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
  function displayResult(data) {
    resultView.style.display = "block";
    let html = "";

    if (data.status === "duplicate") {
      let reasonHtml = "";
      if (data.reason) {
        reasonHtml = `
            <div style="margin-top: 0.5rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 4px; font-size: 0.85rem; color: #fca5a5;">
                <strong>Reason:</strong> ${data.reason.method}<br>
                ${data.reason.detail}
                ${data.reason.sub_scores ? `<br><span style="opacity:0.8">${data.reason.sub_scores}</span>` : ""}
            </div>
        `;
      }

      html = `
            <div class="card" style="border: 1px solid #ef4444; background: rgba(239, 68, 68, 0.1);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">⚠️</div>
                    <div>
                        <h2 style="color: #ef4444; margin: 0;">Duplicate Detected</h2>
                        <p style="margin: 0.5rem 0;">This image is already in the database. <strong>Upload Rejected.</strong></p>
                        ${reasonHtml}
                    </div>
                </div>
                <div style="margin-top: 1rem; border-top: 1px solid rgba(239, 68, 68, 0.3); padding-top: 1rem;">
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.5rem;">Match found with:</p>
                    <img src="/${data.original_image}" style="max-height: 200px; border-radius: 8px; border: 2px solid #ef4444;">
                </div>
            </div>
          `;
    } else {
      html = `
            <div class="card" style="border: 1px solid #10b981; background: rgba(16, 185, 129, 0.1);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">✅</div>
                    <div>
                        <h2 style="color: #10b981; margin: 0;">Image Accepted</h2>
                        <p style="margin: 0.5rem 0;">This is a unique image. It has been saved to the database.</p>
                    </div>
                </div>
                 <div style="margin-top: 1rem; border-top: 1px solid rgba(16, 185, 129, 0.3); padding-top: 1rem;">
                    <img src="/${data.image_path}" style="max-height: 200px; border-radius: 8px; border: 2px solid #10b981;">
                </div>
            </div>
          `;
    }

    resultView.innerHTML = html;
  }

  });

  });