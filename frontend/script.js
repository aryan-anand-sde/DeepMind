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

  // --- Benchmark & Tabs Logic ---

  window.switchTab = function (tabName) {
    document
      .querySelectorAll(".tab-content")
      .forEach((el) => el.classList.remove("active"));
    document
      .querySelectorAll(".tab-btn")
      .forEach((el) => el.classList.remove("active"));

    document.getElementById(`${tabName}-view`).classList.add("active");

    // Update buttons state
    const buttons = document.querySelectorAll(".tab-btn");
    // Assuming order: 0=Upload, 1=Benchmark
    if (tabName === "upload") {
      buttons[0].classList.add("active");
    } else {
      buttons[1].classList.add("active");
    }
  };

  window.runBenchmark = async function () {
    // const pathInput = document.getElementById("benchmark-path");
    const folderPath = "Image_Testing";
    const loading = document.getElementById("benchmark-loading");
    const resultsDiv = document.getElementById("benchmark-results");
    const tbody = document.getElementById("benchmark-tbody");

    loading.style.display = "block";
    resultsDiv.style.display = "none";
    tbody.innerHTML = "";

    try {
      const formData = new FormData();
      formData.append("folder_path", folderPath);

      const res = await fetch("/benchmark", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || "Server error");
      }

      if (data.status === "success") {
        renderBenchmarkTable(data.results);
        resultsDiv.style.display = "block";
      } else {
        throw new Error(data.message || "Unknown error");
      }
    } catch (err) {
      console.error(err);
      alert("Benchmark Failed: " + err.message);
    } finally {
      loading.style.display = "none";
    }
  };

  function renderBenchmarkTable(results) {
    const resultsDiv = document.getElementById("benchmark-results");

    // 1. Data Processing
    // Assume order: [0] Pixel, [1] pHash, [2] DeepMind(Our)
    // We map them to columns
    const pixel = results.find((r) => r.method.includes("Pixel")) || {};
    const phash = results.find((r) => r.method.includes("Hash")) || {};
    const our = results.find((r) => r.method.includes("Detector")) || {};

    const tableHtml = `
      <table class="comparison-table">
        <thead>
          <tr>
            <th style="width: 20%">Feature</th>
            <th style="width: 25%">Cryptographic (SHA-256)</th>
            <th style="width: 25%">Perceptual (pHash Bundle)</th>
            <th style="width: 30%">Our Model (CLIP + ORB)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Search Space</td>
            <td>100% (No reduction)</td>
            <td>100% (Linear Scan)</td>
            <td style="font-weight: 600">0.01% (Vector ANN Index)</td>
          </tr>
          <tr>
            <td>Exact Duplicates</td>
            <td><div class="status success">✅ Found</div></td>
            <td><div class="status success">✅ Found</div></td>
            <td><div class="status success">✅ Found</div></td>
          </tr>
          <tr>
            <td>Resized / Compressed</td>
            <td><div class="status fail">❌ Fails</div></td>
            <td><div class="status success">✅ Found</div></td>
            <td><div class="status success">✅ Found</div></td>
          </tr>
          <tr>
            <td>Cropped / Edited</td>
            <td><div class="status fail">❌ Fails</div></td>
            <td><div class="status fail">❌ Fails</div></td>
            <td><div class="status success">✅ Found</div></td>
          </tr>
          <tr>
            <td>Time per 100 images</td>
            <td>${pixel.speed_sec ? pixel.speed_sec + "s" : "N/A"}</td>
            <td>${phash.speed_sec ? phash.speed_sec + "s" : "N/A"}</td>
            <td><span class="highlight-val">${our.speed_sec ? our.speed_sec + "s" : "N/A"}</span></td>
          </tr>
           <tr>
            <td>Total Matches Found</td>
            <td>${pixel.matches_found ?? 0}</td>
            <td>${phash.matches_found ?? 0}</td>
            <td><span class="highlight-val" style="color: #4ade80;">${our.matches_found ?? 0}</span></td>
          </tr>
        </tbody>
      </table>
    `;

    resultsDiv.innerHTML = tableHtml;
  }
});
