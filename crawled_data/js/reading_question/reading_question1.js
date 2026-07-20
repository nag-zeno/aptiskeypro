// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================
// Dữ liệu câu hỏi (và đáp án đúng) không còn nằm trong file này nữa mà được tải từ backend
// qua API /api/reading-question1-data (xem data_readingquestion.js ở project root), tránh việc
// ai cũng tải được toàn bộ đáp án của tất cả bộ đề cùng lúc qua 1 file tĩnh.

document.addEventListener('DOMContentLoaded', function() {


// ===============================================================================================================
// ////////////// ĐẾM NGƯỢC THỜI GIAN --- COUNT DOWN ///////////////
// ===============================================================================================================
// Countdown Timer
let timeLeft = 35 * 60; // 35 minutes in seconds
const countdownElement = document.getElementById('countdownTimer');

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


    let currentArrayIndex = 0; // 0: questions1_1, 1: questions1_2, 2: questions1_3
    let questionsArrays = []; // Được nạp từ API /api/reading-question1-data

    const userAnswers = [];

    // Hàm để render câu hỏi từ mảng
    function renderQuestions() {
        const container = document.getElementById('questions-container');
        container.innerHTML = ''; // Xóa câu hỏi cũ

        const questions = questionsArrays[currentArrayIndex];
        questions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.classList.add('mb-3', 'd-flex', 'align-items-center', 'border', 'p-3', 'rounded', 'shadow-sm', 'bg-light');

            const label = document.createElement('label');
            label.classList.add('form-label', 'me-3');
            label.setAttribute('for', `gap${index}`);
            label.innerText = `${question.questionStart}`;

            const select = document.createElement('select');
            select.classList.add('form-select', 'w-auto');
            select.id = `gap${index}`;
            select.name = `gap${index}`;
            select.addEventListener('change', function() {
                userAnswers[index] = select.value;
            });

            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.innerText = '';
            select.appendChild(emptyOption);

            question.answerOptions.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.innerText = option;
                select.appendChild(optionElement);
            });

            const span = document.createElement('span');
            span.classList.add('ms-3');
            span.innerText = question.questionEnd;

            questionDiv.appendChild(label);
            questionDiv.appendChild(select);
            questionDiv.appendChild(span);

            container.appendChild(questionDiv);
        });
        const jumpEl = document.getElementById('questionJumpInput');
        jumpEl.value = currentArrayIndex + 1;
        jumpEl.max = questionsArrays.length;
        document.getElementById('question1_total').textContent = questionsArrays.length;

        // Vô hiệu hóa nút Back ở câu đầu, nút Next ở câu cuối
        const isFirst = currentArrayIndex === 0;
        const isLast = currentArrayIndex === questionsArrays.length - 1;
        document.getElementById('backButton').disabled = isFirst;
        document.getElementById('nextButton').disabled = isLast;
        document.getElementById('nextButton').textContent = isLast ? 'The end' : 'Next';
    }

    // Tải dữ liệu câu hỏi từ backend rồi mới render lần đầu
    fetch('/api/reading-question1-data')
        .then(res => {
            if (!res.ok) throw new Error('Không tải được dữ liệu câu hỏi');
            return res.json();
        })
        .then(data => {
            questionsArrays = data;
            renderQuestions();
        })
        .catch(err => {
            console.error('Lỗi tải dữ liệu câu hỏi:', err);
            const container = document.getElementById('questions-container');
            if (container) {
                container.innerHTML = '<p class="text-danger">Không tải được dữ liệu câu hỏi, vui lòng tải lại trang.</p>';
            }
        });

    function jumpToQuestion(val) {
        if (val >= 1 && val <= questionsArrays.length) {
            currentArrayIndex = val - 1;
            userAnswers.length = 0;
            renderQuestions();
        }
    }

    const jumpInput = document.getElementById('questionJumpInput');

    jumpInput.addEventListener('input', function() {
        const val = parseInt(this.value, 10);
        jumpToQuestion(val);
    });

    jumpInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const val = parseInt(this.value, 10);
            if (val < 1 || val > questionsArrays.length || isNaN(val)) {
                this.value = currentArrayIndex + 1;
            }
            this.blur();
        }
    });

    // Hàm chuyển đến câu hỏi tiếp theo
    document.getElementById('nextButton').addEventListener('click', function() {
        if (currentArrayIndex < questionsArrays.length - 1) {
            currentArrayIndex++;
            userAnswers.length = 0;
            renderQuestions();
        }
    });

    // Hàm quay lại câu hỏi trước đó
    document.getElementById('backButton').addEventListener('click', function() {
        if (currentArrayIndex > 0) {
            currentArrayIndex--;
            userAnswers.length = 0;
            renderQuestions();
        }
    });

    // Hiển thị kết quả khi nhấn nút Check Result
    document.getElementById('checkResultButton').addEventListener('click', function() {
        const correctAnswers = [];

        // Tạo bảng so sánh kết quả trong modal
        const comparisonTableBody = document.getElementById('comparisonTableBody');
        comparisonTableBody.innerHTML = ''; // Xóa kết quả cũ

        const questions = questionsArrays[currentArrayIndex]; // Lấy câu hỏi hiện tại

        questions.forEach((question, index) => {
            const userAnswer = userAnswers[index] || "(không chọn)";
            const correctAnswer = question.correctAnswer;

            // Tạo dòng trong bảng so sánh
            const tr = document.createElement('tr');

            // Cột trái: đáp án của người học
            const userAnswerTd = document.createElement('td');
            userAnswerTd.innerHTML = `${userAnswer}`;
            if (userAnswer === correctAnswer) {
                userAnswerTd.classList.add('text-success'); // Màu xanh nếu đúng
            } else {
                userAnswerTd.classList.add('text-danger'); // Màu đỏ nếu sai
            }
            tr.appendChild(userAnswerTd);

            // Cột phải: đáp án đúng
            const correctAnswerTd = document.createElement('td');
            correctAnswerTd.innerHTML = `${correctAnswer}`;
            correctAnswerTd.classList.add('text-success'); // Màu xanh cho đáp án đúng
            tr.appendChild(correctAnswerTd);

            comparisonTableBody.appendChild(tr);
        });

        // Cập nhật điểm tổng và phân loại điểm
        document.getElementById('totalScore').innerText = 'Your Score: ' + calculateScore(userAnswers, questionsArrays);
        document.getElementById('scoreClassification').innerText = 'Classification: ' + getScoreClassification(calculateScore(userAnswers, questionsArrays));

        // Hiển thị modal kết quả
        const myModal = new bootstrap.Modal(document.getElementById('resultModal'));
        myModal.show();
    });

    // Tính điểm
    function calculateScore(userAnswers, questionsArrays) {
        let score = 0;
        const questions = questionsArrays[currentArrayIndex]; // Lấy câu hỏi hiện tại
        questions.forEach((question, index) => {
            if (userAnswers[index] === question.correctAnswer) {
                score += 2; // Mỗi câu đúng được 2 điểm
            }
        });
        return score;
    }

    // Phân loại điểm
    function getScoreClassification(score) {
        if (score >= 10) {
            return 'Excellent';
        } else if (score >= 5) {
            return 'Good';
        } else {
            return 'Cố gắng thêm nhé!';
        }
    }
});

