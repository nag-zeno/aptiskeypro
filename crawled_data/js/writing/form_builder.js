/**
 * form_builder.js – AptisPro Writing Form Builder
 * Cho phép học viên chọn chủ đề CLB và xem form mẫu điền sẵn
 * hoặc tự luyện với ô trống.
 */
(function () {
  'use strict';

  // ── Mapping 40 đề → club name ──────────────────────────────────────────
  const TESTS = [
    { file: 'test_001.json', club: 'Art Club' },
    { file: 'test_002.json', club: 'Beautiful Homes Club' },
    { file: 'test_003.json', club: 'Book Club' },
    { file: 'test_004.json', club: 'Business Club' },
    { file: 'test_005.json', club: 'Car Club' },
    { file: 'test_006.json', club: 'Cinema Club' },
    { file: 'test_007.json', club: 'College Club' },
    { file: 'test_008.json', club: 'Community Club' },
    { file: 'test_009.json', club: 'Computer Club' },
    { file: 'test_010.json', club: 'Cooking Club' },
    { file: 'test_011.json', club: 'Debate Club' },
    { file: 'test_012.json', club: 'English Club' },
    { file: 'test_013.json', club: 'Film Club' },
    { file: 'test_014.json', club: 'Fitness Club' },
    { file: 'test_015.json', club: 'Food Club' },
    { file: 'test_016.json', club: 'Garden Club' },
    { file: 'test_017.json', club: 'Healthy Club' },
    { file: 'test_018.json', club: 'Home Living Club' },
    { file: 'test_019.json', club: 'Language Club' },
    { file: 'test_020.json', club: 'Language Club 2' },
    { file: 'test_021.json', club: 'Movie Club' },
    { file: 'test_022.json', club: 'Museum Club' },
    { file: 'test_023.json', club: 'Music Club' },
    { file: 'test_024.json', club: 'Nature Club' },
    { file: 'test_025.json', club: 'Outdoor Club' },
    { file: 'test_026.json', club: 'Photography Club' },
    { file: 'test_027.json', club: 'Reading Club' },
    { file: 'test_028.json', club: 'Science Club' },
    { file: 'test_029.json', club: 'Social Club' },
    { file: 'test_030.json', club: 'Sports Club' },
    { file: 'test_031.json', club: 'Technology Club' },
    { file: 'test_032.json', club: 'Television Club' },
    { file: 'test_033.json', club: 'Travel Club' },
    { file: 'test_034.json', club: 'Travel Club 2' },
    { file: 'test_035.json', club: 'Walking Club' },
    { file: 'test_036.json', club: 'Writing Club' },
    { file: 'test_037.json', club: 'Fashion Club' },
    { file: 'test_038.json', club: 'English Club 2' },
    { file: 'test_039.json', club: 'English Club 3' },
    { file: 'test_040.json', club: 'Nature Club 2' },
  ];

  // ── State ───────────────────────────────────────────────────────────────
  let isPracticeMode = false;
  let currentData = null;

  // ── DOM refs ────────────────────────────────────────────────────────────
  const selectEl      = document.getElementById('fb-club-select');
  const btnGenerate   = document.getElementById('fb-btn-generate');
  const btnRandom     = document.getElementById('fb-btn-random');
  const btnToggleMode = document.getElementById('fb-btn-toggle-mode');
  const outputEl      = document.getElementById('fb-output');
  const loadingEl     = document.getElementById('fb-loading');
  const emptyEl       = document.getElementById('fb-empty');
  const btnPrintForm  = document.getElementById('fb-btn-print');

  // ── Init dropdown ───────────────────────────────────────────────────────
  function initDropdown() {
    if (!selectEl) return;
    TESTS.forEach((t, i) => {
      const opt = document.createElement('option');
      opt.value = i;
      opt.textContent = `${t.club} (Bộ đề #${String(i + 1).padStart(3, '0')})`;
      selectEl.appendChild(opt);
    });
  }

  // ── Fetch & render ───────────────────────────────────────────────────────
  function generateForm(index) {
    const test = TESTS[index];
    if (!test) return;

    showLoading(true);
    if (outputEl) outputEl.style.display = 'none';
    if (emptyEl)  emptyEl.style.display   = 'none';
    if (btnToggleMode) btnToggleMode.style.display = 'none';
    if (btnPrintForm)  btnPrintForm.style.display  = 'none';

    // Detect base path (supports file:// and http://)
    const loc = window.location.pathname.replace(/\\/g, '/');
    const basePath = loc.includes('/crawled_data/') ? './writing/' : './crawled_data/writing/';
    const url = basePath + test.file;

    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'text';
    xhr.onload = function () {
      showLoading(false);
      if (xhr.status === 200 || (xhr.status === 0 && xhr.responseText)) {
        try {
          currentData = JSON.parse(xhr.responseText);
          renderAll(currentData);
          if (outputEl) outputEl.style.display = 'block';
          if (btnToggleMode) btnToggleMode.style.display = 'inline-flex';
          if (btnPrintForm)  btnPrintForm.style.display  = 'inline-flex';
        } catch (parseErr) {
          console.error('[FormBuilder] JSON parse error:', parseErr);
          showError('Dữ liệu đề thi bị lỗi. Vui lòng thử lại.');
        }
      } else {
        console.error('[FormBuilder] XHR error status:', xhr.status, url);
        showError('Không thể tải dữ liệu đề thi. Vui lòng thử lại.');
      }
    };
    xhr.onerror = function () {
      showLoading(false);
      console.error('[FormBuilder] XHR network error for:', url);
      showError('Không thể tải dữ liệu. Hãy kiểm tra kết nối hoặc mở qua web server.');
    };
    xhr.send();
  }


  // ── Master render ───────────────────────────────────────────────────────
  function renderAll(data) {
    if (!outputEl) return;
    outputEl.innerHTML = '';
    outputEl.appendChild(renderBanner(data));
    outputEl.appendChild(renderPart1(data));
    outputEl.appendChild(renderPart2(data));
    outputEl.appendChild(renderPart3(data));
    outputEl.appendChild(renderPart4(data));
    applyMode();
  }

  // ── Banner ──────────────────────────────────────────────────────────────
  function renderBanner(data) {
    const el = document.createElement('div');
    el.className = 'fb-banner';
    el.innerHTML = `
      <div class="fb-banner-icon"><i class="bi bi-journal-check"></i></div>
      <div>
        <div class="fb-banner-title">${escHtml(data.club_name)}</div>
        <div class="fb-banner-sub">${escHtml(data.key_id)} — Form mẫu áp dụng chuẩn Band B2+</div>
      </div>`;
    return el;
  }

  // ── Part 1 ──────────────────────────────────────────────────────────────
  function renderPart1(data) {
    const qs = data.questions1 || {};
    const as = data.questions1_answer || {};
    const keys = ['question1_1','question1_2','question1_3','question1_4','question1_5'];
    const textLines = [];

    const rows = keys.map((k, i) => {
      const q = qs[k] || '';
      const a = as[`${k}_answer`] || '';
      textLines.push(`${i+1}. ${q}\n   ➜ ${a}`);
      return `
        <div class="fb-qa-row">
          <div class="fb-q-label"><span class="fb-num">${i+1}</span>${escHtml(q)}</div>
          <div class="fb-a-wrap">
            <span class="fb-arrow">➜</span>
            <span class="fb-answer-text">${escHtml(a)}</span>
            <input  class="fb-practice-input form-control form-control-sm" type="text" placeholder="Viết câu trả lời của bạn…" style="display:none">
            <button class="fb-reveal-btn btn btn-outline-secondary btn-sm" data-ans="${escHtml(a)}" style="display:none">Xem đáp án</button>
          </div>
        </div>`;
    }).join('');

    return buildPartCard({
      id: 'fb-part1', badgeClass: 'badge-part1', badgeLabel: 'P1',
      title: 'Part 1: Short Answers', hint: '5 câu trả lời ngắn gọn (1–5 từ)',
      body: rows, copyText: textLines.join('\n\n'),
    });
  }

  // ── Part 2 ──────────────────────────────────────────────────────────────
  function renderPart2(data) {
    const q = data.questions2?.question2 || '';
    const a = data.questions2_answer?.question2 || '';
    const body = `
      <div class="fb-qa-row fb-qa-block">
        <div class="fb-q-label mb-2"><i class="bi bi-chat-left-text me-2 text-warning"></i>${escHtml(q)}</div>
        <div class="fb-a-wrap-block">
          <span class="fb-answer-text">${escHtml(a)}</span>
          <textarea class="fb-practice-input form-control" rows="3" placeholder="Viết đoạn mô tả (20–30 từ)…" style="display:none"></textarea>
          <button class="fb-reveal-btn btn btn-outline-secondary btn-sm mt-2" data-ans="${escHtml(a)}" style="display:none">Xem đáp án mẫu</button>
        </div>
      </div>`;
    return buildPartCard({
      id: 'fb-part2', badgeClass: 'badge-part2', badgeLabel: 'P2',
      title: 'Part 2: Form Filling', hint: '20–30 từ mô tả sở thích / lý do tham gia CLB',
      body, copyText: `${q}\n\n${a}`,
    });
  }

  // ── Part 3 ──────────────────────────────────────────────────────────────
  function renderPart3(data) {
    const qs = data.questions3 || {};
    const as = data.questions3_answer || {};
    const members = [
      { qKey: 'question3_1', aKey: 'question3_1_answer', label: 'Member 1' },
      { qKey: 'question3_2', aKey: 'question3_2_answer', label: 'Member 2' },
      { qKey: 'question3_3', aKey: 'question3_3_answer', label: 'Member 3' },
    ];
    const textLines = [];
    const rows = members.map(m => {
      const q = qs[m.qKey] || '';
      const a = as[m.aKey]  || '';
      textLines.push(`👤 ${m.label}: ${q}\n✏ Bạn: ${a}`);
      return `
        <div class="fb-chat-row">
          <div class="fb-chat-bubble-q">
            <span class="fb-chat-name">👤 ${m.label}:</span>
            <span class="fb-chat-q-text">${escHtml(q)}</span>
          </div>
          <div class="fb-chat-bubble-a">
            <span class="fb-chat-you">✏ Bạn:</span>
            <span class="fb-answer-text">${escHtml(a)}</span>
            <textarea class="fb-practice-input form-control" rows="2" placeholder="Viết câu trả lời (30–40 từ)…" style="display:none"></textarea>
            <button class="fb-reveal-btn btn btn-outline-secondary btn-sm mt-1" data-ans="${escHtml(a)}" style="display:none">Xem đáp án</button>
          </div>
        </div>`;
    }).join('');

    return buildPartCard({
      id: 'fb-part3', badgeClass: 'badge-part3', badgeLabel: 'P3',
      title: 'Part 3: Social Network Chat', hint: '3 câu trả lời thành viên chat (30–40 từ/câu)',
      body: rows, copyText: textLines.join('\n\n'),
    });
  }

  // ── Part 4 ──────────────────────────────────────────────────────────────
  function renderPart4(data) {
    const notice = data.questions4_main || '';
    const q41 = data.question4_1_text || '';
    const q42 = data.question4_2_text || '';
    const a41 = (data.question4_1_text_answer || '').replace(/<br\s*\/?>/gi, '\n');
    const a42 = (data.question4_2_text_answer || '').replace(/<br\s*\/?>/gi, '\n');

    const body = `
      <div class="fb-notice-box mb-3">
        <i class="bi bi-megaphone-fill text-primary me-2"></i>
        <strong>Thông báo CLB:</strong> ${escHtml(notice)}
      </div>
      <!-- 4.1 -->
      <div class="fb-email-block mb-4" id="fb-email-41">
        <div class="fb-email-header">
          <span class="template-badge badge-friend me-2"><i class="bi bi-person-fill"></i></span>
          <strong>Part 4.1 – Email cho bạn (~50 từ)</strong>
          <button class="btn btn-outline-primary copy-btn fb-email-copy ms-auto" data-email-ans="${escHtml(a41)}">
            <i class="bi bi-clipboard me-1"></i>Sao chép
          </button>
        </div>
        <div class="fb-q-label my-2 text-muted"><i class="bi bi-question-circle me-1"></i>${escHtml(q41)}</div>
        <div class="fb-answer-text fb-email-body">${escHtml(a41).replace(/\n/g,'<br>')}</div>
        <textarea class="fb-practice-input form-control" rows="5" placeholder="Viết email cho bạn (~50 từ)…" style="display:none"></textarea>
        <button class="fb-reveal-btn btn btn-outline-secondary btn-sm mt-2" data-ans="${escHtml(a41)}" style="display:none">Xem đáp án mẫu</button>
      </div>
      <!-- 4.2 -->
      <div class="fb-email-block" id="fb-email-42">
        <div class="fb-email-header">
          <span class="template-badge badge-manager me-2"><i class="bi bi-briefcase-fill"></i></span>
          <strong>Part 4.2 – Email cho Chủ tịch CLB (~120–150 từ)</strong>
          <button class="btn btn-outline-primary copy-btn fb-email-copy ms-auto" data-email-ans="${escHtml(a42)}">
            <i class="bi bi-clipboard me-1"></i>Sao chép
          </button>
        </div>
        <div class="fb-q-label my-2 text-muted"><i class="bi bi-question-circle me-1"></i>${escHtml(q42)}</div>
        <div class="fb-answer-text fb-email-body">${escHtml(a42).replace(/\n/g,'<br>')}</div>
        <textarea class="fb-practice-input form-control" rows="8" placeholder="Viết email cho CLB (~120–150 từ)…" style="display:none"></textarea>
        <button class="fb-reveal-btn btn btn-outline-secondary btn-sm mt-2" data-ans="${escHtml(a42)}" style="display:none">Xem đáp án mẫu</button>
      </div>`;

    return buildPartCard({
      id: 'fb-part4', badgeClass: 'badge-manager', badgeLabel: 'P4',
      title: 'Part 4: Email Writing',
      hint: 'Email cho bạn (50 từ) + Email cho Chủ tịch CLB (120–150 từ)',
      body, noCopyBtn: true,
    });
  }

  // ── Build part card ─────────────────────────────────────────────────────
  function buildPartCard({ id, badgeClass, badgeLabel, title, hint, body, copyText, noCopyBtn }) {
    const wrap = document.createElement('div');
    wrap.className = 'fb-part-card';
    wrap.id = id;
    if (copyText) wrap.dataset.copyText = copyText;

    const copyBtn = noCopyBtn ? '' : `
      <button class="btn btn-outline-primary copy-btn fb-part-copy ms-auto" data-part-id="${id}">
        <i class="bi bi-clipboard me-1"></i>Sao chép
      </button>`;

    wrap.innerHTML = `
      <div class="fb-part-header">
        <div class="d-flex align-items-center gap-2">
          <span class="template-badge ${badgeClass}">${badgeLabel}</span>
          <div>
            <div class="fb-part-title">${title}</div>
            <div class="fb-part-hint">${hint}</div>
          </div>
        </div>
        ${copyBtn}
      </div>
      <div class="fb-part-body">${body}</div>`;
    return wrap;
  }

  // ── Mode toggle ──────────────────────────────────────────────────────────
  function applyMode() {
    if (!outputEl) return;
    outputEl.querySelectorAll('.fb-answer-text').forEach(el => { el.style.display = isPracticeMode ? 'none' : ''; });
    outputEl.querySelectorAll('.fb-practice-input').forEach(el => { el.style.display = isPracticeMode ? '' : 'none'; if (!isPracticeMode) el.value = ''; });
    outputEl.querySelectorAll('.fb-reveal-btn').forEach(el => { el.style.display = isPracticeMode ? '' : 'none'; });
    outputEl.querySelectorAll('.fb-email-copy, .fb-part-copy').forEach(el => { el.style.display = isPracticeMode ? 'none' : ''; });

    if (btnToggleMode) {
      btnToggleMode.innerHTML = isPracticeMode
        ? '<i class="bi bi-eye me-1"></i>Xem đáp án mẫu'
        : '<i class="bi bi-pencil-square me-1"></i>Chế độ Tự luyện';
      btnToggleMode.className = isPracticeMode
        ? 'btn btn-outline-success btn-sm'
        : 'btn btn-outline-warning btn-sm';
    }
  }

  // ── Event delegation on output ───────────────────────────────────────────
  outputEl && outputEl.addEventListener('click', e => {
    // Reveal answer
    const revBtn = e.target.closest('.fb-reveal-btn');
    if (revBtn) {
      const wrap = revBtn.closest('.fb-a-wrap,.fb-a-wrap-block,.fb-chat-bubble-a,.fb-email-block');
      if (wrap) {
        const ansEl = wrap.querySelector('.fb-answer-text');
        if (ansEl) ansEl.style.display = '';
        revBtn.style.display = 'none';
      }
      return;
    }

    // Copy email
    const emailCopy = e.target.closest('.fb-email-copy');
    if (emailCopy) {
      const raw = emailCopy.getAttribute('data-email-ans') || '';
      copyToClipboard(emailCopy, raw.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"'));
      return;
    }

    // Copy part
    const partCopy = e.target.closest('.fb-part-copy');
    if (partCopy) {
      const card = document.getElementById(partCopy.getAttribute('data-part-id'));
      const text = card ? (card.dataset.copyText || card.innerText) : '';
      copyToClipboard(partCopy, text);
      return;
    }
  });

  function copyToClipboard(btn, text) {
    navigator.clipboard.writeText(text.trim()).then(() => {
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Đã sao chép!';
      setTimeout(() => { btn.innerHTML = orig; }, 1600);
    });
  }

  // ── Button events ────────────────────────────────────────────────────────
  btnGenerate && btnGenerate.addEventListener('click', () => {
    const idx = parseInt(selectEl.value, 10);
    if (isNaN(idx)) return;
    isPracticeMode = false;
    generateForm(idx);
  });

  btnRandom && btnRandom.addEventListener('click', () => {
    const idx = Math.floor(Math.random() * TESTS.length);
    selectEl.value = idx;
    isPracticeMode = false;
    generateForm(idx);
  });

  btnToggleMode && btnToggleMode.addEventListener('click', () => {
    if (!currentData) return;
    isPracticeMode = !isPracticeMode;
    applyMode();
  });

  btnPrintForm && btnPrintForm.addEventListener('click', () => window.print());

  selectEl && selectEl.addEventListener('keydown', e => {
    if (e.key === 'Enter') btnGenerate && btnGenerate.click();
  });

  // ── Helpers ──────────────────────────────────────────────────────────────
  function showLoading(show) {
    if (loadingEl) loadingEl.style.display = show ? 'flex' : 'none';
  }

  function showError(msg) {
    if (!outputEl) return;
    outputEl.innerHTML = `<div class="alert alert-danger mt-2"><i class="bi bi-exclamation-triangle me-2"></i>${msg}</div>`;
    outputEl.style.display = 'block';
  }

  function escHtml(str) {
    return String(str || '')
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ── Boot ─────────────────────────────────────────────────────────────────
  initDropdown();
})();
