/**
 * HỆ THỐNG QUẢN LÝ NGƯỜI DÙNG - APTISPRO 2026
 * Mọi thông tin đều được lấy từ Server thông qua API /api/me
 */

// 1. Hàm khởi tạo chính khi trang web tải xong
document.addEventListener("DOMContentLoaded", async () => {
    await initializeUser();
});

async function initializeUser() {
    const statusEl = document.getElementById("status_hocvien");
    const nameEl = document.getElementById("userName");
    const authBtn = document.getElementById("signOutBtn");
    const tabProfile = document.getElementById("tabprofile");
    const xProfile = document.getElementById("xProfile");

    try {
        // 1. Xây dựng headers: ưu tiên Bearer token từ localStorage
        const token = localStorage.getItem('ak_token');
        const headers = {};
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        // 2. Gọi API /api/me
        //    - credentials: 'include' → trình duyệt tự đính kèm Cookie HttpOnly (access_token)
        //      nếu Bearer header không hoạt động (ví dụ: token hết hạn trong localStorage)
        const response = await fetch('/api/me', {
            headers,
            credentials: 'include'
        });

        // 3. Nếu 401: xóa token cũ trong localStorage (đã hết hạn/không hợp lệ) rồi redirect
        if (!response.ok) {
            if (response.status === 401) {
                // Xóa token hết hạn để tránh vòng lặp redirect
                localStorage.removeItem('ak_token');
                localStorage.removeItem('ak_token_type');
                console.log("Hệ thống: Token không hợp lệ hoặc hết hạn, chuyển về trang đăng nhập.");
                redirectToLogin();
            }
            return;
        }

        // 4. KIỂM TRA KIỂU DỮ LIỆU
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            throw new TypeError("Server không trả về JSON hợp lệ!");
        }

        const data = await response.json();

        // 5. CẬP NHẬT GIAO DIỆN NẾU THÀNH CÔNG
        if (data.success) {
            // Lưu lại token mới từ cookie (phòng khi localStorage bị xóa)
            // Nếu không có token trong localStorage nhưng cookie hợp lệ thì không làm gì thêm
            updateUIForUser(data, nameEl, statusEl, authBtn, tabProfile, xProfile);
            
            // Nếu trang hiện tại có các nút admin, hãy kiểm tra quyền admin luôn
            if (typeof checkAdminUI === 'function') {
                checkAdminUI(); 
            }
        } else {
            localStorage.removeItem('ak_token');
            localStorage.removeItem('ak_token_type');
            redirectToLogin();
        }

    } catch (err) {
        // Khi có lỗi mạng hoặc parse JSON → KHÔNG redirect để tránh lặp
        // (Ví dụ: server đang khởi động, mạng chậm)
        console.warn("Lỗi xác thực:", err.message);
        // Chỉ redirect nếu không phải lỗi mạng
        if (err.name !== 'TypeError' || !err.message.includes('fetch')) {
            redirectToLogin();
        } else {
            console.log("Lỗi kết nối mạng, không redirect để tránh vòng lặp.");
        }
    }
}

// 2a. Chuyển hướng về trang đăng nhập, lưu lại URL hiện tại để redirect sau khi đăng nhập
function redirectToLogin() {
    // Không redirect nếu đang ở trang đăng nhập rồi (tránh vòng lặp vô hạn)
    if (window.location.pathname.includes('/frontend/auth')) return;
    // Không redirect nếu đang ở trang chủ tĩnh (index.html)
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        window.location.href = '/frontend/auth.html';
        return;
    }
    const currentUrl = encodeURIComponent(window.location.href);
    window.location.href = `/frontend/auth.html?redirect=${currentUrl}`;
}

// 2. Cập nhật giao diện cho khách
function updateUIForGuest(nameEl, statusEl, authBtn, tabProfile, xProfile) {
    if (nameEl) nameEl.textContent = "Khách";
    if (tabProfile) tabProfile.classList.add("d-none");
    if (xProfile) xProfile.style.display = "none";
    
    if (statusEl) {
        statusEl.innerHTML = `
            Khách trải nghiệm
            <small>Bạn chưa đăng ký học</small>
        `;
    }

    if (authBtn) {
        authBtn.textContent = "Đăng nhập";
        authBtn.onclick = () => window.location.href = "/frontend/auth.html";
    }

    // Tự động chèn link Từ vựng Aptis vào sidebar cho khách trải nghiệm
    const sidebarMenu = document.querySelector('.sidebar-menu');
    if (sidebarMenu && !document.getElementById('tabvocab')) {
        const vocabLi = document.createElement('li');
        vocabLi.className = 'nav-item';
        vocabLi.id = 'tabvocab';
        vocabLi.innerHTML = `
            <a href="/vocabulary.html" class="nav-link ${window.location.pathname.includes('vocabulary') ? 'active' : ''}">
                <i class="nav-icon bi bi-journal-bookmark-fill text-success"></i>
                <p>Từ vựng Aptis</p>
            </a>
        `;
        if (tabProfile) {
            tabProfile.parentNode.insertBefore(vocabLi, tabProfile);
        } else {
            sidebarMenu.appendChild(vocabLi);
        }
    }
}

// 3. Cập nhật giao diện cho học viên
function updateUIForUser(data, nameEl, statusEl, authBtn, tabProfile, xProfile) {
    if (nameEl) nameEl.textContent = data.fullName;
    
    // Đồng bộ ảnh đại diện đã chọn từ localStorage
    const savedAvatar = localStorage.getItem('profile_avatar') || './images/assets/img/avatar.png';
    const smallAv = document.getElementById('userAvatarSmall');
    const headerAv = document.getElementById('userAvatarHeader');
    if (smallAv) smallAv.src = savedAvatar;
    if (headerAv) headerAv.src = savedAvatar;

    if (tabProfile) tabProfile.classList.remove("d-none");
    if (xProfile) xProfile.style.display = "inline-block";

    // Tự động chèn link Từ vựng Aptis vào sidebar nếu chưa có
    const sidebarMenu = document.querySelector('.sidebar-menu');
    if (sidebarMenu && !document.getElementById('tabvocab')) {
        const profileItem = document.getElementById('tabprofile');
        const vocabLi = document.createElement('li');
        vocabLi.className = 'nav-item';
        vocabLi.id = 'tabvocab';
        vocabLi.innerHTML = `
            <a href="/vocabulary.html" class="nav-link ${window.location.pathname.includes('vocabulary') ? 'active' : ''}">
                <i class="nav-icon bi bi-journal-bookmark-fill text-success"></i>
                <p>Từ vựng Aptis</p>
            </a>
        `;
        if (profileItem) {
            profileItem.parentNode.insertBefore(vocabLi, profileItem);
        } else {
            sidebarMenu.appendChild(vocabLi);
        }
    }

    // Tự động chèn link Quản trị hệ thống vào sidebar nếu người dùng là Admin
    if (data.isAdmin && sidebarMenu && !document.getElementById('tabadmin')) {
        const profileItem = document.getElementById('tabprofile') || tabProfile;
        
        const adminLi = document.createElement('li');
        adminLi.className = 'nav-item';
        adminLi.id = 'tabadmin';
        adminLi.innerHTML = `
            <a href="/admin_dashboard.html" class="nav-link">
                <i class="nav-icon bi bi-shield-lock-fill text-danger"></i>
                <p>Quản trị hệ thống</p>
            </a>
        `;
        
        if (profileItem) {
            profileItem.parentNode.insertBefore(adminLi, profileItem.nextSibling);
        } else {
            sidebarMenu.appendChild(adminLi);
        }
    }

    // Xử lý nút Đăng xuất
    if (authBtn) {
        authBtn.textContent = "Đăng xuất";
        authBtn.onclick = handleLogout;
    }

    // Xử lý trạng thái tài khoản & ngày hết hạn
    if (statusEl) {
        const expireDateObj = new Date(data.expiredAt);
        const now = new Date();
        
        // Format ngày theo kiểu Việt Nam: dd/mm/yyyy hh:mm
        const formattedDate = expireDateObj.toLocaleString('vi-VN', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit'
        });

        if (expireDateObj < now) {
            // Đã hết hạn
            statusEl.innerHTML = `
                Học viên đăng ký
                <small style="color:yellow; font-weight:normal;">
                    Tài khoản của bạn đã hết hạn! 
                    <a href="/gia-han" style="color:lime; text-decoration:underline; margin-left:5px;">
                        Gia hạn thêm
                    </a>
                </small>
            `;
        } else {
            // Còn hạn
            statusEl.innerHTML = `
                Học viên chính thức
                <small>Ngày hết hạn: ${formattedDate}</small>
            `;
        }
    }
}

// 4. Hàm xử lý đăng xuất
async function handleLogout(e) {
    e.preventDefault();
    try {
        // Xóa Cookie phía server
        await fetch('/logout', { method: 'GET', credentials: 'include' });
        // Xóa JWT token khỏi localStorage
        localStorage.removeItem('ak_token');
        localStorage.removeItem('ak_token_type');
        // Hiệu ứng chờ một chút cho chuyên nghiệp
        document.body.style.opacity = "0.5";
        setTimeout(() => {
            window.location.href = '/frontend/auth.html';
        }, 1000);
    } catch (err) {
        console.error("Lỗi đăng xuất:", err);
        localStorage.removeItem('ak_token');
        localStorage.removeItem('ak_token_type');
        window.location.href = '/frontend/auth.html';
    }
}