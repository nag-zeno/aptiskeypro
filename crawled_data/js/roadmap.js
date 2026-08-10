/**
 * APTISKEY - ROADMAP LOGIC (Neumorphism Design System)
 */

const API_BASE_URL = window.location.origin && window.location.origin !== 'null' && window.location.origin.startsWith('http') 
  ? `${window.location.origin}/api` 
  : 'http://127.0.0.1:8001/api';
let currentTreeData = null;
let currentSelectedNode = null;

document.addEventListener('DOMContentLoaded', () => {
  fetchRoadmapTree();
});

function getAuthHeader() {
  const token = localStorage.getItem('ak_token');
  if (!token) return {};
  return { 'Authorization': `Bearer ${token}` };
}

async function fetchRoadmapTree() {
  const container = document.getElementById('roadmapTreeContainer');
  try {
    const response = await fetch(`${API_BASE_URL}/roadmap/tree`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });

    if (response.status === 401) {
      // User not logged in, offer guest alert
      container.innerHTML = `
        <div class="alert alert-warning text-center p-4">
          <h4 class="fw-bold mb-2"><i class="bi bi-exclamation-triangle-fill me-2"></i>Vui lòng đăng nhập</h4>
          <p class="mb-3">Bạn cần đăng nhập để lưu trữ tiến trình học tập và nhận đánh giá từ AI.</p>
          <a href="/frontend/auth.html" class="btn btn-primary">Đăng Nhập Ngay</a>
        </div>
      `;
      return;
    }

    if (!response.ok) {
      throw new Error('Không thể tải sơ đồ lộ trình học tập');
    }

    const data = await response.json();
    currentTreeData = data;
    renderDashboard(data);
    renderRoadmapTree(data);
    fetchAIRecommendations();
  } catch (error) {
    console.error('Roadmap error:', error);
    container.innerHTML = `
      <div class="alert alert-danger text-center p-4">
        <i class="bi bi-x-circle-fill fs-2 me-2"></i>
        <span>Có lỗi xảy ra khi kết nối hệ thống: ${error.message}</span>
      </div>
    `;
  }
}

async function fetchAIRecommendations() {
  try {
    const response = await fetch(`${API_BASE_URL}/roadmap/recommendations`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    });
    if (!response.ok) return;
    const data = await response.json();

    const banner = document.getElementById('aiRecommendationBanner');
    const adviceText = document.getElementById('aiAdviceText');
    const nodesContainer = document.getElementById('aiRecommendedNodesContainer');

    if (banner && adviceText && nodesContainer) {
      banner.classList.remove('d-none');
      adviceText.innerText = data.ai_advice || 'AI đã sẵn sàng tư vấn lộ trình học tập cá nhân hóa cho bạn!';

      if (data.recommended_nodes && data.recommended_nodes.length > 0) {
        let btnHtml = '';
        data.recommended_nodes.forEach(n => {
          btnHtml += `
            <button class="btn btn-sm btn-outline-primary fw-bold" onclick="openTheoryModal(${n.id})">
              <i class="bi ${n.icon || 'bi-journal-check'} me-1"></i>${n.title}
            </button>
          `;
        });
        nodesContainer.innerHTML = btnHtml;
      }
    }
  } catch (err) {
    console.warn('AI Recommendation fetch error:', err);
  }
}

function renderDashboard(data) {
  document.getElementById('displayTargetBand').innerText = data.target_band || 'B1';
  document.getElementById('statProgress').innerText = `${data.progress_percentage}%`;
  document.getElementById('statCompleted').innerText = `${data.completed_nodes}/${data.total_nodes}`;
  document.getElementById('statStars').innerText = `${data.total_stars} ⭐`;
  document.getElementById('statStreak').innerText = `${data.streak_days} Ngày 🔥`;
}

function renderRoadmapTree(data) {
  const container = document.getElementById('roadmapTreeContainer');
  if (!data.stages || data.stages.length === 0) {
    container.innerHTML = `<div class="alert alert-info text-center">Chưa có bài học nào trong lộ trình.</div>`;
    return;
  }

  let html = '';

  data.stages.forEach((stage, sIdx) => {
    html += `
      <div class="stage-card">
        <div class="stage-header">
          <div class="d-flex align-items-center">
            <i class="bi ${stage.icon || 'bi-compass'} fs-3 text-primary me-3"></i>
            <div>
              <h4 class="fw-bold mb-1">${stage.title}</h4>
              <p class="text-muted small mb-0">${stage.description || ''}</p>
            </div>
          </div>
          <span class="stage-badge bg-primary text-white">${stage.target_band}</span>
        </div>

        <div class="nodes-grid">
    `;

    stage.nodes.forEach((node) => {
      const statusClass = `status-${node.user_status}`;
      const skillClass = `skill-${node.skill}`;
      
      let statusBadge = '';
      if (node.user_status === 'completed') {
        statusBadge = `<span class="badge bg-success"><i class="bi bi-check-circle-fill me-1"></i>Đã xong</span>`;
      } else if (node.user_status === 'unlocked') {
        statusBadge = `<span class="badge bg-primary"><i class="bi bi-unlock-fill me-1"></i>Đang học</span>`;
      } else {
        statusBadge = `<span class="badge bg-secondary"><i class="bi bi-lock-fill me-1"></i>Đã khóa</span>`;
      }

      let aiBadge = '';
      if (node.recommendation && node.recommendation.is_recommended) {
        aiBadge = `<span class="badge bg-warning text-dark me-1" title="${node.recommendation.reason || ''}"><i class="bi bi-robot me-1"></i>AI Đề xuất</span>`;
      }

      let starsHtml = '';
      for (let i = 1; i <= 3; i++) {
        if (i <= node.stars) {
          starsHtml += `<i class="bi bi-star-fill text-warning"></i>`;
        } else {
          starsHtml += `<i class="bi bi-star text-muted"></i>`;
        }
      }

      const isLocked = node.user_status === 'locked';

      html += `
        <div class="node-card ${statusClass}">
          <div>
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="node-icon-wrapper ${skillClass}">
                <i class="bi ${node.icon || 'bi-journal-bookmark'}"></i>
              </div>
              <div class="d-flex align-items-center gap-1">${aiBadge}${statusBadge}</div>
            </div>

            <span class="badge bg-light text-dark mb-2 fw-semibold">${node.part_name}</span>
            <h5 class="node-title">${node.title}</h5>
            <p class="node-desc">${node.description || ''}</p>
          </div>

          <div>
            <div class="d-flex align-items-center justify-content-between mb-3">
              <div class="stars-container">${starsHtml}</div>
              <small class="text-muted fw-bold">Qua bài: ${node.target_pass_score}%</small>
            </div>

            <div class="d-grid gap-2">
              <button class="btn btn-secondary btn-sm" onclick="openTheoryModal(${node.id})">
                <i class="bi bi-lightbulb-fill me-1 text-warning"></i>Lý Thuyết & Mẹo Thi
              </button>
              <button class="btn ${isLocked ? 'btn-light disabled' : 'btn-primary'} btn-sm" 
                      ${isLocked ? 'disabled' : ''} 
                      onclick="startPractice(${node.id}, '${node.practice_url || '#'}')">
                <i class="bi bi-play-fill me-1"></i>Luyện Tập Ngay
              </button>
            </div>
          </div>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function openTheoryModal(nodeId) {
  if (!currentTreeData) return;

  let foundNode = null;
  for (const stage of currentTreeData.stages) {
    for (const n of stage.nodes) {
      if (n.id === nodeId) {
        foundNode = n;
        break;
      }
    }
  }

  if (!foundNode) return;
  currentSelectedNode = foundNode;

  document.getElementById('modalNodeTitle').innerText = foundNode.title;
  document.getElementById('modalSkillBadge').innerText = foundNode.part_name;
  document.getElementById('modalTheoryBody').innerHTML = foundNode.theory_content || '<p>Chưa có nội dung lý thuyết.</p>';

  const btnPractice = document.getElementById('btnStartPractice');
  btnPractice.onclick = () => {
    const modalEl = document.getElementById('theoryModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
    startPractice(foundNode.id, foundNode.practice_url);
  };

  const theoryModal = new bootstrap.Modal(document.getElementById('theoryModal'));
  theoryModal.show();
}

function startPractice(nodeId, url) {
  if (!url || url === '#') {
    alert('Bài luyện tập đang được cập nhật!');
    return;
  }

  // Chuyển hướng sang trang bài làm kèm roadmap_node_id
  const targetUrl = url.includes('?') ? `${url}&roadmap_node_id=${nodeId}` : `${url}?roadmap_node_id=${nodeId}`;
  window.location.href = targetUrl;
}

function openTargetBandModal() {
  const modal = new bootstrap.Modal(document.getElementById('targetBandModal'));
  modal.show();
}

async function setTargetBand(band) {
  try {
    const response = await fetch(`${API_BASE_URL}/roadmap/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ target_band: band })
    });

    if (response.ok) {
      const modalEl = document.getElementById('targetBandModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();

      fetchRoadmapTree();
    }
  } catch (err) {
    console.error('Update band error:', err);
  }
}

function startPlacementTest() {
  alert('Hệ thống Đánh giá Đầu vào (Placement Test 15 phút): Bạn sẽ thực hiện bài test ngẫu nhiên 10 câu hỏi để xác định chặng học!');
  // Chuyển sang bài test trắc nghiệm tổng hợp
  window.location.href = '/grammar_test001.html?placement=true';
}
