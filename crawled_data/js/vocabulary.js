/**
 * AptisKey - Vocabulary System Logic
 * Quản lý tra cứu, phân loại, phát âm và lật thẻ Flashcards 3D
 */

const API_BASE = (window.location.origin && window.location.origin !== 'null' && window.location.origin.startsWith('http')) 
    ? window.location.origin 
    : 'http://localhost:8001';

document.addEventListener("DOMContentLoaded", function () {
  // State
  let currentPage = 1;
  const pageLimit = 18;
  let currentSkill = "ALL";
  let currentStatus = "ALL";
  let currentVocabList = [];
  let flashcardIndex = 0;
  let viewMode = "grid"; // "grid" or "flashcard"

  // DOM Elements
  const searchInput = document.getElementById("searchInput");
  const cefrFilter = document.getElementById("cefrFilter");
  const categoryFilter = document.getElementById("categoryFilter");
  const posFilter = document.getElementById("posFilter");
  const btnViewGrid = document.getElementById("btnViewGrid");
  const btnViewFlashcard = document.getElementById("btnViewFlashcard");
  const gridContainer = document.getElementById("gridContainer");
  const flashcardContainer = document.getElementById("flashcardContainer");
  const vocabGrid = document.getElementById("vocabGrid");
  const paginationWrap = document.getElementById("paginationWrap");

  // Stats Elements
  const statTotalWords = document.getElementById("statTotalWords");
  const statMasteredWords = document.getElementById("statMasteredWords");
  const statBookmarkedWords = document.getElementById("statBookmarkedWords");
  const statB1Count = document.getElementById("statB1Count");

  // Flashcard Elements
  const flashcardWrapper = document.getElementById("flashcardWrapper");
  const fcWord = document.getElementById("fcWord");
  const fcPhonetic = document.getElementById("fcPhonetic");
  const fcCefr = document.getElementById("fcCefr");
  const fcPos = document.getElementById("fcPos");
  const fcMeaning = document.getElementById("fcMeaning");
  const fcCategory = document.getElementById("fcCategory");
  const fcSkill = document.getElementById("fcSkill");
  const fcExampleEn = document.getElementById("fcExampleEn");
  const fcExampleVi = document.getElementById("fcExampleVi");
  const fcCounter = document.getElementById("fcCounter");
  const fcPrevBtn = document.getElementById("fcPrevBtn");
  const fcNextBtn = document.getElementById("fcNextBtn");
  const fcSpeakBtn = document.getElementById("fcSpeakBtn");
  const fcMasteredBtn = document.getElementById("fcMasteredBtn");
  const fcBookmarkBtn = document.getElementById("fcBookmarkBtn");

  // --- INITIALIZATION ---
  init();

  function init() {
    // Kiểm tra URL param mode=flashcard
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("mode") === "flashcard") {
      setViewMode("flashcard");
    }

    loadStats();
    loadCategories();
    fetchVocabularies();

    setupEventListeners();
  }

  // --- EVENT LISTENERS ---
  function setupEventListeners() {
    // Search with debounce
    let searchTimeout = null;
    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentPage = 1;
        fetchVocabularies();
      }, 350);
    });

    // Select filters
    cefrFilter.addEventListener("change", () => { currentPage = 1; fetchVocabularies(); });
    categoryFilter.addEventListener("change", () => { currentPage = 1; fetchVocabularies(); });
    posFilter.addEventListener("change", () => { currentPage = 1; fetchVocabularies(); });

    // Skill Pills
    document.querySelectorAll("#skillPills .pill-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        document.querySelectorAll("#skillPills .pill-btn").forEach((b) => b.classList.remove("active"));
        this.classList.add("active");
        currentSkill = this.getAttribute("data-skill");
        currentPage = 1;
        fetchVocabularies();
      });
    });

    // Status Pills
    document.querySelectorAll("#statusPills .pill-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        document.querySelectorAll("#statusPills .pill-btn").forEach((b) => b.classList.remove("active"));
        this.classList.add("active");
        currentStatus = this.getAttribute("data-status");
        currentPage = 1;
        fetchVocabularies();
      });
    });

    // View Mode Toggle
    btnViewGrid.addEventListener("click", () => setViewMode("grid"));
    btnViewFlashcard.addEventListener("click", () => setViewMode("flashcard"));

    // Flashcard Flip
    flashcardWrapper.addEventListener("click", function (e) {
      if (e.target.closest("button")) return; // Don't flip if clicking inside action buttons
      flashcardWrapper.classList.toggle("flipped");
    });

    // Flashcard Controls
    fcPrevBtn.addEventListener("click", (e) => { e.stopPropagation(); prevFlashcard(); });
    fcNextBtn.addEventListener("click", (e) => { e.stopPropagation(); nextFlashcard(); });
    fcSpeakBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const currentItem = currentVocabList[flashcardIndex];
      if (currentItem) speakWord(currentItem.word);
    });

    fcMasteredBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const item = currentVocabList[flashcardIndex];
      if (item) toggleVocabStatus(item.id, item.user_status === "mastered" ? "none" : "mastered");
    });

    fcBookmarkBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const item = currentVocabList[flashcardIndex];
      if (item) toggleVocabStatus(item.id, item.user_status === "bookmarked" ? "none" : "bookmarked");
    });

    // Keyboard Shortcuts for Flashcard
    document.addEventListener("keydown", function (e) {
      if (viewMode !== "flashcard") return;
      if (document.activeElement.tagName === "INPUT") return;

      if (e.code === "Space") {
        e.preventDefault();
        flashcardWrapper.classList.toggle("flipped");
      } else if (e.code === "ArrowLeft") {
        prevFlashcard();
      } else if (e.code === "ArrowRight") {
        nextFlashcard();
      }
    });
  }

  // --- API CALLS ---
  function loadStats() {
    fetch(`${API_BASE}/api/vocabulary/stats`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        statTotalWords.textContent = data.total_words || 0;
        statMasteredWords.textContent = data.user_mastered_count || 0;
        statBookmarkedWords.textContent = data.user_bookmarked_count || 0;
        statB1Count.textContent = data.by_level?.B1 || 0;
      })
      .catch((err) => console.error("Lỗi tải thống kê từ vựng:", err));
  }

  function loadCategories() {
    fetch(`${API_BASE}/api/vocabulary/categories`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        categoryFilter.innerHTML = `<option value="ALL">Tất cả chủ đề</option>`;
        if (data.categories) {
          data.categories.forEach((cat) => {
            const opt = document.createElement("option");
            opt.value = cat;
            opt.textContent = cat;
            categoryFilter.appendChild(opt);
          });
        }
      })
      .catch((err) => console.error("Lỗi tải chủ đề từ vựng:", err));
  }

  function fetchVocabularies() {
    const params = new URLSearchParams({
      page: currentPage,
      limit: pageLimit,
    });

    const queryVal = searchInput.value.trim();
    if (queryVal) params.append("query", queryVal);
    if (currentSkill !== "ALL") params.append("skill", currentSkill);

    const cefrVal = cefrFilter.value;
    if (cefrVal !== "ALL") params.append("cefr_level", cefrVal);

    const catVal = categoryFilter.value;
    if (catVal !== "ALL") params.append("category", catVal);

    const posVal = posFilter.value;
    if (posVal !== "ALL") params.append("pos", posVal);

    if (currentStatus !== "ALL") params.append("status_filter", currentStatus);

    fetch(`${API_BASE}/api/vocabulary?${params.toString()}`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        currentVocabList = data.items || [];
        renderGrid(data);
        renderPagination(data);

        if (viewMode === "flashcard") {
          flashcardIndex = 0;
          renderFlashcard();
        }
      })
      .catch((err) => {
        console.error("Lỗi tải từ vựng:", err);
        vocabGrid.innerHTML = `
          <div class="col-12 text-center py-5 text-muted">
            <i class="bi bi-exclamation-circle text-danger fs-1"></i>
            <p class="mt-2">Không thể tải dữ liệu từ vựng. Vui lòng kiểm tra kết nối Backend Server (Cổng 8001).</p>
          </div>
        `;
      });
  }

  function toggleVocabStatus(vocabId, newStatus) {
    fetch(`${API_BASE}/api/vocabulary/${vocabId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ status: newStatus }),
    })
      .then((res) => {
        if (!res.ok) {
          if (res.status === 401) {
            alert("Vui lòng đăng nhập để lưu tiến trình học từ vựng cá nhân!");
            return;
          }
          throw new Error("Không thể cập nhật trạng thái");
        }
        return res.json();
      })
      .then(() => {
        // Update local item state
        const item = currentVocabList.find((v) => v.id === vocabId);
        if (item) {
          item.user_status = newStatus === "none" ? null : newStatus;
        }

        // Refresh view
        if (viewMode === "grid") {
          renderGrid({ items: currentVocabList });
        } else {
          renderFlashcard();
        }
        loadStats();
      })
      .catch((err) => console.error("Lỗi cập nhật từ vựng:", err));
  }

  // --- RENDER GRID MODE ---
  function renderGrid(data) {
    const items = data.items || [];
    if (items.length === 0) {
      vocabGrid.innerHTML = `
        <div class="col-12 text-center py-5 text-muted">
          <i class="bi bi-journal-x fs-1 text-secondary"></i>
          <h5 class="fw-bold mt-2">Không tìm thấy từ vựng nào</h5>
          <p class="small">Hãy thử thay đổi bộ lọc hoặc từ khóa tìm kiếm.</p>
        </div>
      `;
      return;
    }

    let html = "";
    items.forEach((item) => {
      const cefrClass = `cefr-${item.cefr_level || 'B1'}`;
      const isBookmarked = item.user_status === "bookmarked";
      const isMastered = item.user_status === "mastered";

      html += `
        <div class="vocab-card" data-id="${item.id}">
          <div>
            <div class="vocab-card-header">
              <div>
                <h4 class="v-word">${escapeHtml(item.word)}</h4>
                <div class="d-flex align-items-center">
                  <span class="v-phonetic">${escapeHtml(item.phonetic || "")}</span>
                  <button class="speak-btn" onclick="speakWord('${escapeHtml(item.word)}')"><i class="bi bi-volume-up-fill"></i></button>
                </div>
              </div>
              <span class="badge-cefr ${cefrClass}">${escapeHtml(item.cefr_level || "B1")}</span>
            </div>
            <div class="mt-1"><span class="badge-pos">${escapeHtml(item.pos || "word")}</span></div>
            <div class="v-meaning">${escapeHtml(item.meaning_vi)}</div>
          </div>

          ${item.example_en ? `
            <div class="v-example mt-2">
              <strong>Ví dụ đề thi:</strong> ${escapeHtml(item.example_en)}
              ${item.example_vi ? `<div class="text-muted small mt-1">${escapeHtml(item.example_vi)}</div>` : ''}
            </div>
          ` : ''}

          <div class="vocab-card-footer">
            <span class="text-muted small fw-bold">${escapeHtml(item.category || "General")}</span>
            <div class="d-flex gap-2">
              <button class="action-icon-btn ${isBookmarked ? 'active-bookmark' : ''}" 
                      onclick="handleStatusClick(event, ${item.id}, '${isBookmarked ? 'none' : 'bookmarked'}')"
                      title="${isBookmarked ? 'Bỏ lưu' : 'Lưu từ'}">
                <i class="bi ${isBookmarked ? 'bi-bookmark-star-fill' : 'bi-bookmark'}"></i>
              </button>
              <button class="action-icon-btn ${isMastered ? 'active-mastered' : ''}" 
                      onclick="handleStatusClick(event, ${item.id}, '${isMastered ? 'none' : 'mastered'}')"
                      title="${isMastered ? 'Đã thuộc' : 'Đánh dấu đã thuộc'}">
                <i class="bi ${isMastered ? 'bi-check-circle-fill' : 'bi-check-circle'}"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    });

    vocabGrid.innerHTML = html;
  }

  // Global handler for inline button onclick
  window.handleStatusClick = function (e, id, status) {
    e.stopPropagation();
    toggleVocabStatus(id, status);
  };

  // --- RENDER FLASHCARD MODE ---
  function renderFlashcard() {
    if (currentVocabList.length === 0) {
      fcWord.textContent = "Hết từ vựng";
      fcPhonetic.textContent = "";
      fcMeaning.textContent = "Không tìm thấy từ vựng nào trong bộ lọc này.";
      fcExampleEn.textContent = "";
      fcExampleVi.textContent = "";
      fcCounter.textContent = "0 / 0";
      return;
    }

    const item = currentVocabList[flashcardIndex];
    flashcardWrapper.classList.remove("flipped");

    fcWord.textContent = item.word;
    fcPhonetic.textContent = item.phonetic || "";
    fcCefr.textContent = item.cefr_level || "B1";
    fcCefr.className = `badge-cefr cefr-${item.cefr_level || "B1"}`;
    fcPos.textContent = item.pos || "word";

    fcMeaning.textContent = item.meaning_vi;
    fcCategory.textContent = item.category || "General";
    fcSkill.textContent = (item.skill || "General").toUpperCase();
    fcExampleEn.textContent = item.example_en || "Chưa có ví dụ.";
    fcExampleVi.textContent = item.example_vi || "";

    fcCounter.textContent = `${flashcardIndex + 1} / ${currentVocabList.length}`;

    // Update Action Buttons State
    const isBookmarked = item.user_status === "bookmarked";
    const isMastered = item.user_status === "mastered";

    fcBookmarkBtn.className = `btn btn-sm ${isBookmarked ? 'btn-warning text-dark' : 'btn-outline-warning'} rounded-pill px-3`;
    fcBookmarkBtn.innerHTML = `<i class="bi ${isBookmarked ? 'bi-bookmark-star-fill' : 'bi-bookmark'} me-1"></i>${isBookmarked ? 'Đã lưu' : 'Lưu từ'}`;

    fcMasteredBtn.className = `btn btn-sm ${isMastered ? 'btn-success text-white' : 'btn-outline-success'} rounded-pill px-3`;
    fcMasteredBtn.innerHTML = `<i class="bi ${isMastered ? 'bi-check-circle-fill' : 'bi-check-circle'} me-1"></i>${isMastered ? 'Đã thuộc' : 'Thuộc từ'}`;
  }

  function prevFlashcard() {
    if (currentVocabList.length === 0) return;
    flashcardIndex = (flashcardIndex - 1 + currentVocabList.length) % currentVocabList.length;
    renderFlashcard();
  }

  function nextFlashcard() {
    if (currentVocabList.length === 0) return;
    flashcardIndex = (flashcardIndex + 1) % currentVocabList.length;
    renderFlashcard();
  }

  function setViewMode(mode) {
    viewMode = mode;
    if (mode === "grid") {
      btnViewGrid.classList.add("active");
      btnViewFlashcard.classList.remove("active");
      gridContainer.classList.remove("d-none");
      flashcardContainer.classList.add("d-none");
    } else {
      btnViewFlashcard.classList.add("active");
      btnViewGrid.classList.remove("active");
      flashcardContainer.classList.remove("d-none");
      gridContainer.classList.add("d-none");
      flashcardIndex = 0;
      renderFlashcard();
    }
  }

  // --- RENDER PAGINATION ---
  function renderPagination(data) {
    if (!data.total_pages || data.total_pages <= 1) {
      paginationWrap.innerHTML = "";
      return;
    }

    let html = "";
    const totalPages = data.total_pages;

    html += `
      <button class="pg-btn" ${currentPage === 1 ? "disabled" : ""} onclick="changePage(${currentPage - 1})">
        <i class="bi bi-chevron-left"></i>
      </button>
    `;

    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
        html += `
          <button class="pg-btn ${i === currentPage ? "active" : ""}" onclick="changePage(${i})">${i}</button>
        `;
      } else if (i === currentPage - 3 || i === currentPage + 3) {
        html += `<span class="px-1 text-muted">...</span>`;
      }
    }

    html += `
      <button class="pg-btn" ${currentPage === totalPages ? "disabled" : ""} onclick="changePage(${currentPage + 1})">
        <i class="bi bi-chevron-right"></i>
      </button>
    `;

    paginationWrap.innerHTML = html;
  }

  window.changePage = function (page) {
    currentPage = page;
    fetchVocabularies();
    window.scrollTo({ top: 200, behavior: "smooth" });
  };

  // --- WEB SPEECH API (AUDIO TTS) ---
  window.speakWord = function (word) {
    if (!("speechSynthesis" in window)) {
      alert("Trình duyệt của bạn không hỗ trợ tính năng phát âm thanh tự động.");
      return;
    }

    window.speechSynthesis.cancel(); // Stop current speaking
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = "en-GB"; // British English accent for Aptis
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  };

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
