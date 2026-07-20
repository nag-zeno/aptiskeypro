// ============================================
//               WRITING TEST JS
// ============================================

document.addEventListener('DOMContentLoaded', function() {

    // Cập nhật câu hỏi 1, 2, 3, 4
    const questions = ["question1", "question2", "question3", "question4"];
    let currentQuestionIndex = 0; // Bắt đầu với câu hỏi 1

    // Hàm để hiển thị câu hỏi hiện tại
    function showCurrentQuestion() {
        // Ẩn tất cả các câu hỏi
        questions.forEach((questionId) => {
            const el = document.getElementById(questionId);
            if (el) el.style.display = 'none';
        });
        
        // Hiển thị câu hỏi hiện tại
        const curEl = document.getElementById(questions[currentQuestionIndex]);
        if (curEl) curEl.style.display = 'block';

        // Nếu người dùng đã đến câu hỏi cuối cùng, hiển thị nút "Chấm điểm"
        const btnCheck = document.getElementById('btn_checkallquestions');
        if (btnCheck) {
            if (currentQuestionIndex === questions.length - 1) {
                btnCheck.classList.remove('d-none');
            } else {
                btnCheck.classList.add('d-none');
            }
        }
    }

    // Đảm bảo rằng DOM đã được tải xong trước khi gắn sự kiện
    const nextButton = document.getElementById('nextButton');
    const backButton = document.getElementById('backButton');
    
    if (nextButton && backButton) {
        // Gắn sự kiện Next
        nextButton.addEventListener('click', function() {
            if (currentQuestionIndex < questions.length - 1) {
                currentQuestionIndex++; // Tăng chỉ số câu hỏi
                showCurrentQuestion();  // Hiển thị câu hỏi tiếp theo
            }
        });

        // Gắn sự kiện Back
        backButton.addEventListener('click', function() {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--; // Giảm chỉ số câu hỏi
                showCurrentQuestion();  // Hiển thị câu hỏi trước
            }
        });
    }

    // Hiển thị câu hỏi ban đầu (question1)
    showCurrentQuestion();

    // Hàm xử lý khi người dùng nhấn nút "Chấm điểm"
    const btnCheckAll = document.getElementById('btn_checkallquestions');
    if (btnCheckAll) {
        btnCheckAll.addEventListener('click', function() {
            const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
            confirmationModal.show();
        });
    }

    // Sự kiện khi nhấn "Yes" trong modal xác nhận
    const confirmBtn = document.getElementById('confirmButton');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            const confirmationModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
            if (confirmationModal) confirmationModal.hide();
            handleSubmitAllQuestions();
        });
    }
});

// Countdown Timer
let timeLeft = 50 * 60; // 50 minutes in seconds
document.addEventListener("DOMContentLoaded", function() {
    const countdownElement = document.getElementById('countdownTimer');
    if (!countdownElement) return;

    function updateCountdown() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        countdownElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        if (timeLeft > 0) {
            timeLeft--;
            setTimeout(updateCountdown, 1000);
        }
    }
    updateCountdown();
});

// Cập nhật prompt cho toàn bộ
let promptText_question1 = "";
let promptText_question2 = "";
let promptText_question3 = "";
let promptText_question4 = "";

function updatePrompts() {
    promptText_question1 = "Người trả lời là thành viên của câu lạc bộ " + club_name + ". Hãy chấm điểm 5 câu trả lời dưới đây theo thang năng lực Aptis từ A0 đến C1. Tiêu chí chấm điểm: Mỗi câu trả lời không quá 5 từ; nội dung đơn giản nhưng phải phù hợp với câu hỏi; chữ cái đầu câu phải viết hoa và cuối câu phải có dấu chấm; chấm điểm theo hướng dễ và ưu tiên khả năng truyền đạt ý; không bắt buộc câu trả lời phải là một câu hoàn chỉnh; chỉ cần câu trả lời có nội dung phù hợp và không quá 5 từ thì có thể đạt điểm cao. Hãy trả về mức điểm A0–C1 cho từng câu và giải thích ngắn gọn lý do chấm điểm.\n\n";
    promptText_question2 = "Người này đang là thành viên của câu lạc bộ " + club_name + " Hãy chấm điểm câu trả lời sau theo khung aptis mức độ A0 đến C1, độ dài trong phạm vi 20-30 words, kết quả trả về có giải thích:\n\n";
    promptText_question3 = "Người này đang là thành viên của câu lạc bộ " + club_name + " Hãy chấm điểm câu trả lời sau theo khung aptis mức độ A0 đến C1, độ dài trong phạm vi 30-40 từ, kết quả trả về có giải thích:\n\n";
    promptText_question4 = "Người này đang là thành viên của câu lạc bộ " + club_name + " Hãy chấm điểm câu trả lời sau theo khung aptis mức độ A0 đến C1, độ dài trong phạm vi 50 từ cho câu hỏi 1 và 120-150 từ cho câu hỏi 2, kết quả trả về có giải thích, sau khi chấm 4 câu hãy chấm cấp độ tổng thể cho các câu trên:\n\n";
}

// Hàm xử lý khi người dùng nhấn nút "Chấm điểm" cho tất cả 4 câu hỏi
async function handleSubmitAllQuestions() {
    const answers = {
        question1: {},
        question2: {},
        question3: {},
        question4: {}
    };

    // Lấy giá trị từ form câu hỏi 1
    const formElements_question1 = document.getElementById('question1Form').elements;
    for (let element of formElements_question1) {
        if (element.type === "text") {
            answers.question1[element.name] = element.value.trim() === "" ? "No answer" : element.value;
        }
    }

    // Lấy giá trị từ form câu hỏi 2
    const formElements_question2 = document.getElementById('question2Form').elements;
    for (let element of formElements_question2) {
        if (element.type === "textarea") {
            answers.question2[element.name] = element.value.trim() === "" ? "No answer" : element.value;
        }
    }

    // Lấy giá trị từ form câu hỏi 3
    const formElements_question3 = document.getElementById('question3Form').elements;
    for (let element of formElements_question3) {
        if (element.type === "textarea") {
            answers.question3[element.name] = element.value.trim() === "" ? "No answer" : element.value;
        }
    }

    // Lấy giá trị từ form câu hỏi 4
    const formElements_question4 = document.getElementById('question4Form').elements;
    for (let element of formElements_question4) {
        if (element.type === "textarea") {
            answers.question4[element.name] = element.value.trim() === "" ? "No answer" : element.value;
        }
    }

    // Chuyển đối tượng đáp án cho câu hỏi 1 thành một chuỗi
    const userAnswersText_question1 = Object.keys(answers.question1)
        .map(key => `${questions1[key]}: ${answers.question1[key]}`)
        .join("\n");

    // Chuyển đối tượng đáp án cho câu hỏi 2 thành một chuỗi
    const userAnswersText_question2 = Object.keys(answers.question2)
        .map(key => `${questions2[key]}: ${answers.question2[key]}`)
        .join("\n");

    // Chuyển đối tượng đáp án cho câu hỏi 3 thành một chuỗi
    const userAnswersText_question3 = Object.keys(answers.question3)
        .map(key => `${questions3[key]}: ${answers.question3[key]}`)
        .join("\n");

    // Chuyển đối tượng đáp án cho câu hỏi 4 thành một chuỗi
    const userAnswersText_question4 = Object.keys(answers.question4)
        .map(key => `${questions4[key]}: ${answers.question4[key]}`)
        .join("\n");

    // Gộp câu hỏi 1, câu hỏi 2, câu hỏi 3 và câu hỏi 4 thành một trường "question"
    const fullQuestion = `
        ${promptText_question1}${userAnswersText_question1}\n\n
        ${promptText_question2}${userAnswersText_question2}\n\n
        ${promptText_question3}${userAnswersText_question3}\n\n
        ${promptText_question4}${userAnswersText_question4}
    `;

    // Hiển thị modal loading
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show(); // Hiển thị modal loading

    // Gửi tất cả câu hỏi và đáp án cho server
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: fullQuestion // Gửi câu hỏi gộp dưới một trường "question"
            })
        });

        const data = await response.json();

        if (data.error) {
            console.log("Lỗi: ", data.error);
            return;
        }

        // Hiển thị kết quả trong modal kết quả
        const modalBody = document.getElementById('modal-body-ai');
        modalBody.innerHTML = renderAIGradingResult(data.answer); 
        console.log(data.answer);
        const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
        resultModal.show();

        // Tự động lưu kết quả bài làm vào lịch sử
        saveWritingResult(data.answer, fullQuestion);

    } catch (err) {
        console.error('Có lỗi xảy ra khi gửi yêu cầu:', err);
    } finally {
        // Ẩn modal loading khi xong
        loadingModal.hide(); // Ẩn modal loading
    }
}

async function saveWritingResult(aiAnswer, fullQuestion) {
    try {
        const match = window.location.pathname.match(/writingkey(\d+)/);
        const keyNum = match ? parseInt(match[1], 10) : 1;

        // Bóc tách Band điểm từ phản hồi AI bằng Regex
        let band = 'B2';
        const bandMatch = aiAnswer.match(/(?:Band|Cấp độ|Grade|Dự kiến)\s*(?:ước tính|ước lượng)?\s*:\s*(?:<strong>)?\s*([A-C][1-2]?)\s*(?:<\/strong>)?/i);
        if (bandMatch && bandMatch[1]) {
            band = bandMatch[1].toUpperCase();
        }

        // Bóc tách điểm số từ phản hồi AI
        let score = 70.0;
        const scoreMatch = aiAnswer.match(/(\d+)\s*\/\s*50/) || aiAnswer.match(/(\d+)\s*\/\s*100/);
        if (scoreMatch) {
            const num = parseInt(scoreMatch[1], 10);
            score = scoreMatch[0].includes('50') ? (num / 50) * 100 : num;
        }

        const token = localStorage.getItem('ak_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        const resp = await fetch('/api/compat/save-result', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                skill: 'writing',
                test_id: keyNum,
                score: score,
                aptis_band: band,
                answers: { "Bài viết của học viên": fullQuestion },
                ai_feedback: aiAnswer,
                time_taken_seconds: 0
            }),
            credentials: 'include'
        });

        if (resp.ok) {
            console.log('Lưu kết quả Writing vào lịch sử thành công!');
        } else {
            console.warn('Lưu kết quả Writing thất bại, status:', resp.status);
        }
    } catch (e) {
        console.error('Lỗi khi tự động lưu kết quả Writing:', e);
    }
}

// Render các câu hỏi trên giao diện
function renderQuestions1() {
    const container = document.getElementById("questions-container1");
    if (!container) return;
    let formContent = '';
    for (let key in questions1) {
        formContent += `
            <div class="mb-3 d-flex align-items-center">
                <label for="${key}" class="form-label me-2 mb-0" style="white-space: nowrap;">${questions1[key]}</label>
                <input type="text" class="form-control form-control-sm" id="${key}" name="${key}" style="max-width: 250px;">
            </div>
        `;
    }
    container.innerHTML = formContent;
}

function renderQuestions2() {
    const container = document.getElementById("questions-container2");
    if (!container) return;
    container.innerHTML = `
        <div class="mb-4">
            <label for="question2_text" class="form-label">${questions2}</label>
            <textarea class="form-control" id="question2_text" name="question2_text" rows="4" style="width: 100%;"></textarea>
            <div id="question2-wordCount" class="text-muted text-end mt-1">Word Count: 0</div>
        </div>
    `;
    const textarea = document.getElementById("question2_text");
    textarea.addEventListener("input", function() {
        const content = (textarea.value || "").trim();
        const wordCount = content ? content.split(/\s+/).filter(Boolean).length : 0;
        document.getElementById("question2-wordCount").textContent = `Word Count: ${wordCount}`;
    });
}

// Render các câu hỏi part 3
function renderQuestions3() {
    const container = document.getElementById("questions-container3");
    if (!container) return;
    let formContent = '';
    for (let key in questions3) {
        formContent += `
            <div class="mb-4">
                <label for="${key}" class="form-label">${questions3[key]}</label>
                <textarea class="form-control" id="${key}" name="${key}" rows="3" style="width: 100%;"></textarea>
                <div id="${key}-wordCount" class="text-muted text-end mt-1">Word Count: 0</div>
            </div>
        `;
    }
    container.innerHTML = formContent;
    for (let key in questions3) {
        let textarea = document.getElementById(key);
        textarea.addEventListener("input", function() {
            const content = (textarea.value || "").trim();
            const wordCount = content ? content.split(/\s+/).filter(Boolean).length : 0;
            document.getElementById(`${key}-wordCount`).textContent = `Word Count: ${wordCount}`;
        });
    }
}

// Render các câu hỏi part 4
function renderQuestions4() {
    const container = document.getElementById("questions-container4");
    if (!container) return;
    
    const description_q4 = document.getElementById('description_q4');
    if (description_q4) description_q4.textContent = questions4_main;

    let formContent = '';
    for (let key in questions4) {
        formContent += `
            <div class="mb-4">
                <label for="${key}" class="form-label">${questions4[key]}</label>
                <textarea class="form-control" id="${key}" name="${key}" rows="4" style="width: 100%;"></textarea>
                <div id="${key}-wordCount" class="text-muted text-end mt-1">Word Count: 0</div>
            </div>
        `;
    }
    container.innerHTML = formContent;
    for (let key in questions4) {
        let textarea = document.getElementById(key);
        textarea.addEventListener("input", function() {
            const content = (textarea.value || "").trim();
            const wordCount = content ? content.split(/\s+/).filter(Boolean).length : 0;
            document.getElementById(`${key}-wordCount`).textContent = `Word Count: ${wordCount}`;
        });
    }
}

// Quản lý Modal "Xem đáp án" của các câu hỏi
document.addEventListener("DOMContentLoaded", function() {
    const modalBody = document.getElementById("modal-body");
    const question1AnswerModal = new bootstrap.Modal(document.getElementById('question1_answerModal'));
    const showAnswerBtn1 = document.getElementById("question1_showanswer");
    
    if (showAnswerBtn1) {
        showAnswerBtn1.addEventListener("click", function() {
            modalBody.innerHTML = '';
            for (let i = 1; i <= 5; i++) {
                const questionKey = `question1_${i}`;
                const answerKey = `question1_${i}_answer`;
                const qP = document.createElement('p');
                qP.innerHTML = `<strong>${i}. ${questions1[questionKey]}</strong>`;
                const aP = document.createElement('p');
                aP.innerHTML = `${questions1_answer[answerKey]}`;
                modalBody.appendChild(qP);
                modalBody.appendChild(aP);
            }
            question1AnswerModal.show();
        });
    }

    const modalBody2 = document.getElementById("modal-body2");
    const question2AnswerModal = new bootstrap.Modal(document.getElementById('question2_answerModal'));
    const showAnswerBtn2 = document.getElementById("question2_showanswer");
    if (showAnswerBtn2) {
        showAnswerBtn2.addEventListener("click", function() {
            modalBody2.innerHTML = '';
            const qP = document.createElement('p');
            qP.innerHTML = `<strong>${questions2}</strong>`;
            const aP = document.createElement('p');
            aP.innerHTML = `${questions2_answer}`;
            modalBody2.appendChild(qP);
            modalBody2.appendChild(aP);
            question2AnswerModal.show();
        });
    }

    const modalBody3 = document.getElementById("modal-body3");
    const question3AnswerModal = new bootstrap.Modal(document.getElementById('question3_answerModal'));
    const showAnswerBtn3 = document.getElementById("question3_showanswer");
    if (showAnswerBtn3) {
        showAnswerBtn3.addEventListener("click", function() {
            modalBody3.innerHTML = '';
            for (let i = 1; i <= 3; i++) {
                const questionKey = `question3_${i}`;
                const answerKey = `question3_${i}_answer`;
                const qP = document.createElement('p');
                qP.innerHTML = `<strong>${i}. ${questions3[questionKey]}</strong>`;
                const aP = document.createElement('p');
                aP.innerHTML = `${questions3_answer[answerKey]}`;
                modalBody3.appendChild(qP);
                modalBody3.appendChild(aP);
            }
            question3AnswerModal.show();
        });
    }

    const modalBody4 = document.getElementById("modal-body4");
    const question4AnswerModal = new bootstrap.Modal(document.getElementById('question4_answerModal'));
    const showAnswerBtn4 = document.getElementById("question4_showanswer");
    if (showAnswerBtn4) {
        showAnswerBtn4.addEventListener("click", function() {
            modalBody4.innerHTML = '';
            const qP1 = document.createElement('p');
            qP1.innerHTML = `<strong>4.1. ${question4_1_text}</strong>`;
            const aP1 = document.createElement('p');
            aP1.innerHTML = `${question4_1_text_answer}`;
            const qP2 = document.createElement('p');
            qP2.innerHTML = `<strong>4.2. ${question4_2_text}</strong>`;
            const aP2 = document.createElement('p');
            aP2.innerHTML = `${question4_2_text_answer}`;
            modalBody4.appendChild(qP1);
            modalBody4.appendChild(aP1);
            modalBody4.appendChild(qP2);
            modalBody4.appendChild(aP2);
            question4AnswerModal.show();
        });
    }
});

// Tải dữ liệu bộ đề từ backend rồi khởi tạo giao diện
const __match = window.location.pathname.match(/writingkey(\d+)/);
const __keyNum = __match ? parseInt(__match[1], 10) : 1;

fetch(`/api/writingkey-data/${__keyNum}`)
  .then(res => {
    if (!res.ok) throw new Error('Không tải được dữ liệu bộ đề');
    return res.json();
  })
  .then(data => {
    key_id = data.key_id;
    club_name = data.club_name;
    questions1 = data.questions1;
    questions1_answer = data.questions1_answer;
    questions2 = data.questions2;
    questions2_answer = data.questions2_answer;
    questions3 = data.questions3;
    questions3_answer = data.questions3_answer;
    questions4_main = data.questions4_main;
    question4_1_text = data.question4_1_text;
    question4_2_text = data.question4_2_text;
    question4_1_text_answer = data.question4_1_text_answer;
    question4_2_text_answer = data.question4_2_text_answer;

    questions4 = {
        "question4_1": `${questions4_main} <br><strong>${question4_1_text}</strong>`,
        "question4_2": `${questions4_main} <br><strong>${question4_2_text}</strong>`,
    };

    updatePrompts();

    const keysIdEl = document.getElementById('keys_id');
    if (keysIdEl) keysIdEl.innerHTML = key_id;

    renderQuestions1();
    renderQuestions2();
    renderQuestions3();
    renderQuestions4();
  })
  .catch(err => {
    console.error('Lỗi tải dữ liệu bộ đề writing:', err);
    const keysIdEl = document.getElementById('keys_id');
    if (keysIdEl) keysIdEl.innerHTML = 'Không tải được dữ liệu bộ đề, vui lòng tải lại trang.';
  });

function renderAIGradingResult(rawHtml) {
    // Trả về HTML đã định dạng từ AI
    return rawHtml;
}
