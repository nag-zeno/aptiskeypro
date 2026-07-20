document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================
// Dữ liệu câu hỏi (đoạn văn, câu hỏi, đáp án đúng) không còn nằm trong file này nữa mà được tải từ backend
// qua API /api/reading-question4-data (xem data_readingquestion.js trong questiondata/), tránh việc
// ai cũng tải được toàn bộ nội dung/đáp án của tất cả bộ đề cùng lúc qua 1 file tĩnh.

let question4Text = [];
let question4Content = [];
let correctAnswersQuestion4 = [];
let question4Topic = [];

// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
let currentIndex = 0; // Biến lưu trữ chỉ số câu hỏi hiện tại

// Sự kiện cho nút Next
document.getElementById('nextButton').addEventListener('click', function() {
     document.getElementById('backButton').textContent = "Back";
    if (currentIndex < question4Text.length - 1) {
        currentIndex++; // Tăng chỉ số lên để chuyển sang câu hỏi tiếp theo
        renderQuestion4(currentIndex); // Render câu hỏi mới
    } else {
        // Nếu đã ở câu hỏi cuối cùng, thay đổi văn bản nút Next thành "Submit Test"
        document.getElementById('nextButton').textContent = "The end";
    }
});

// Sự kiện cho nút Back
document.getElementById('backButton').addEventListener('click', function() {
    if (currentIndex > 0) {
        currentIndex--; // Giảm chỉ số xuống để quay lại câu hỏi trước
        renderQuestion4(currentIndex); // Render câu hỏi trước
        document.getElementById('nextButton').textContent = "Next";
    } else {
        // Khi đã đến câu hỏi đầu tiên, có thể thay đổi văn bản nút Back hoặc thực hiện hành động khác
        document.getElementById('backButton').textContent = "No Previous Question";
    }
});

// ===============================================================================================================
// ////////////// MẢNG CÂU HỎI VÀ ĐÁP ÁN CÂU HỎI 4 ///////////////
// ===============================================================================================================
// Hàm render câu hỏi với dữ liệu đầu vào là question4Text và question4Content
function renderQuestion4(index) {
    document.getElementById('question4_index').textContent = "Reading Question 4" + " (" + (index + 1) + "/" + question4Text.length + ")";
    // Kiểm tra xem mảng question4Text và question4Content có hợp lệ không
    if (!question4Text[index] || !question4Content[index]) {
        console.error('Không tìm thấy dữ liệu cho câu hỏi tại index: ' + index);
        return;  // Dừng hàm nếu dữ liệu không hợp lệ
    }

    const container = document.getElementById('question4');
    const row = container.querySelector('.row');

    // Render các đoạn văn vào cột bên trái
    const leftColumn = row.querySelector('.col-md-7');
    leftColumn.innerHTML = ''; // Xóa nội dung cũ
    question4Text[index].forEach(text => {
        const p = document.createElement('p');
        p.innerHTML = text;  // Cho phép HTML trong đoạn văn (ví dụ <strong>)
        leftColumn.appendChild(p);
    });

    // Render các câu hỏi và dropdown vào cột bên phải
    const rightColumn = row.querySelector('.col-md-5');
    const form = rightColumn.querySelector('form');
    form.innerHTML = ''; // Xóa nội dung cũ

    question4Content[index].forEach(item => {
        const div = document.createElement('div');
        div.classList.add('mb-3', 'row', 'align-items-center');

        const label = document.createElement('label');
        label.setAttribute('for', item.id);
        label.classList.add('col-9', 'col-form-label');
        label.textContent = item.question;

        const selectDiv = document.createElement('div');
        selectDiv.classList.add('col-3');

        const select = document.createElement('select');
        select.id = item.id;
        select.classList.add('form-select', 'select-fixed');

        item.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });

        selectDiv.appendChild(select);
        div.appendChild(label);
        div.appendChild(selectDiv);
        form.appendChild(div);
    });

    // Cập nhật chủ đề cho câu hỏi
    const topicElement = document.getElementById('question4_topic');
    topicElement.textContent = `Topic: ${question4Topic[index]}`;
}

// 2. Xử lý kết quả khi nhấn submit
document.getElementById('checkResultButton').addEventListener('click', function() {
    const answers = [];
    const correctAnswers = [];

    // Lặp qua các câu hỏi và lấy đáp án người học, sau đó so sánh với đáp án đúng
    for (let i = 0; i < 7; i++) {
        const selectElement = document.getElementById(`question4_q${i + 1}`);
        if (selectElement) {
            const selectedAnswer = selectElement.value || "(không chọn)";
            answers.push(selectedAnswer);
            correctAnswers.push(correctAnswersQuestion4[currentIndex][i]); // Sử dụng currentIndex để lấy mảng đúng
        } else {
            console.error(`Element with id 'question4_q${i + 1}' not found`);
        }
    }

    // Hiển thị kết quả so sánh
    question4Score = displayComparisonResultsQuestion4(answers, correctAnswers);

    // Show the modal after displaying the results
    $('#resultModal').modal('show');
});

// Hàm hiển thị kết quả so sánh và điểm số
function displayComparisonResultsQuestion4(userAnswers, correctAnswers) {
    const comparisonResult = document.getElementById('comparisonResult_question4');
    const comparisonBody = document.getElementById('comparisonTableBody');
    const totalScoreElement = document.getElementById('totalScore');

    // Clear previous results
    comparisonBody.innerHTML = '';

    // Tính điểm
    let score = 0;

    // Lặp qua các câu hỏi từ mảng question4Content và hiển thị đáp án người học và đáp án đúng
    question4Content[currentIndex].forEach((item, index) => {
        const tr = document.createElement('tr');

        // Cột câu hỏi
        const questionTd = document.createElement('td');
        questionTd.innerHTML = item.question;  // Lấy câu hỏi từ question4Content
        tr.appendChild(questionTd);

        // Cột đáp án người học
        const userAnswerTd = document.createElement('td');
        const userAnswer = userAnswers[index] || "(không chọn)";
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        // Cột đáp án đúng
        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        // Nếu người học chọn đúng, cộng điểm
        if (userAnswer === correctAnswers[index]) {
            score += 2;
        }

        comparisonBody.appendChild(tr);
    });


    // Trả về điểm số
    return score;
}

// Tải dữ liệu câu hỏi từ backend rồi mới render lần đầu
fetch('/api/reading-question4-data')
    .then(res => {
        if (!res.ok) throw new Error('Không tải được dữ liệu câu hỏi');
        return res.json();
    })
    .then(data => {
        question4Text = data.question4Text;
        question4Content = data.question4Content;
        correctAnswersQuestion4 = data.correctAnswersQuestion4;
        question4Topic = Object.values(data.question4Topic1);
        renderQuestion4(currentIndex);
    })
    .catch(err => {
        console.error('Lỗi tải dữ liệu câu hỏi:', err);
        const container = document.getElementById('question4');
        if (container) {
            container.innerHTML = '<p class="text-danger">Không tải được dữ liệu câu hỏi, vui lòng tải lại trang.</p>';
        }
    });


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


// Kết thúc
});
