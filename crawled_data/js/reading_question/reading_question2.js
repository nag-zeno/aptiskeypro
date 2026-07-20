document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================
// Dữ liệu câu hỏi (thứ tự câu đúng) không còn nằm trong file này nữa mà được tải từ backend
// qua API /api/reading-question2-data (xem data_readingquestion.js trong questiondata/), tránh việc
// ai cũng tải được toàn bộ nội dung của tất cả bộ đề cùng lúc qua 1 file tĩnh.

let questionSets = [];
let questheader = [];
let currentSetIndex = 0; // Biến để theo dõi bộ câu hỏi hiện tại

// ===============================================================================================================
// ////////////// CÂU HỎI 2 ///////////////
// ===============================================================================================================

// Mảng lưu các câu trả lời đúng
var correctAnswersQuestion2 = [];

// Hàm trộn ngẫu nhiên (Fisher-Yates shuffle) để random các câu hỏi
function shuffleQuestions(questions) {
    for (let i = questions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [questions[i], questions[j]] = [questions[j], questions[i]];
    }
    return questions;  // Trả lại mảng đã xáo trộn
}

// Hàm render các câu hỏi vào trong các cards cho Question 2
function renderQuestion2(questionlist) {
    // Gán giá trị mới cho correctAnswersQuestion2 từ mảng questionlist
    correctAnswersQuestion2 = [];
    questionlist.forEach(item => {
    correctAnswersQuestion2.push(item);
});

    // Xáo trộn mảng câu hỏi
    let shuffledQuestionlist = shuffleQuestions([...questionlist]);

    // Xóa các card cũ
    const cardsContainer = document.getElementById('cardsContainer');
    cardsContainer.innerHTML = ''; // Clear previous cards

    // Tạo và thêm các thẻ card mới
    shuffledQuestionlist.forEach((text, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card', 'mb-2', 'draggable-item');
        cardDiv.setAttribute('draggable', 'true');
        cardDiv.id = `item${index + 1}`;

        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body');
        cardBody.innerText = text;

        cardDiv.appendChild(cardBody);
        cardsContainer.appendChild(cardDiv);
    });

    // Kích hoạt kéo thả bằng SortableJS
    initSortable();
    // Cập nhật tổng số bộ
    document.getElementById("totalReading").textContent = questheader.length;
    document.getElementById("jumpToQuestion").value = currentSetIndex + 1;

    document.getElementById('question2_topic').textContent = `Topic: ${questheader[currentSetIndex]}`;

}

// Hàm khởi tạo SortableJS cho các phần tử kéo thả
function initSortable() {
    const cardsContainer = document.getElementById('cardsContainer');

    // Khởi tạo Sortable cho cardsContainer
    new Sortable(cardsContainer, {
        group: 'shared',
        animation: 150,
    });
}


// ===============================
// Jump to specific question
// ===============================
document.getElementById('jumpToQuestion').addEventListener('change', function () {

    let value = parseInt(this.value);

    if (!isNaN(value) && value >= 1 && value <= questionSets.length) {

        currentSetIndex = value - 1;

        renderQuestion2(questionSets[currentSetIndex]);

    } else {

        this.value = currentSetIndex + 1;

    }
});

//-----------------------------------------------------------------------
// Mảng lưu đáp án của người học
const userAnswersQuestion2 = [];

// Lắng nghe sự kiện khi nhấn nút "Check result"
document.getElementById('checkResultButton').addEventListener('click', function() {
    // Lấy kết quả từ các card đã sắp xếp
    userAnswersQuestion2.length = 0; // Reset mảng userAnswers

    const cardsContainer = document.getElementById('cardsContainer');
    const cards = cardsContainer.querySelectorAll('.draggable-item');

    // Lặp qua các thẻ card và lấy câu trả lời của người học
    cards.forEach((card) => {
        const selectedAnswer = card.textContent.trim() || "(không chọn)";
        userAnswersQuestion2.push(selectedAnswer);
    });

    // So sánh kết quả người học với đáp án đúng
    const answers = [];
    const correctAnswers = [];

    correctAnswersQuestion2.forEach((correctAnswer, index) => {
        const selectedAnswer = userAnswersQuestion2[index] || "(không chọn)";  // Nếu không có lựa chọn, sử dụng "(không chọn)"
        answers.push(selectedAnswer);
        correctAnswers.push(correctAnswer);
    });

    // Hiển thị kết quả so sánh trong bảng
    question2Score = displayComparisonResultsQuestion2(answers, correctAnswers);

    // Mở modal kết quả sau khi tính điểm
    var resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
    resultModal.show();
});

// Hiển thị đáp án đúng và so sánh
function displayComparisonResultsQuestion2(userAnswers, correctAnswers) {
    const comparisonBody = document.getElementById('comparisonTableBody');
    const totalScoreElement = document.getElementById('totalScore');

    comparisonBody.innerHTML = ''; // Clear previous results
    let score = 0; // Variable to keep track of the score

    // Loop through the user's answers and compare with correct answers
    userAnswers.forEach((userAnswer, index) => {
        const tr = document.createElement('tr');

        // User's answer cell
        const userAnswerTd = document.createElement('td');
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        // Correct answer cell
        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        // If the user's answer is correct, increment score
        if (userAnswer === correctAnswers[index]) {
            score++;
        }

        comparisonBody.appendChild(tr);
    });

    // Display the score in the result section
    totalScoreElement.innerHTML = `<strong>Your score: ${score} / ${correctAnswers.length}</strong>`;

    // Return the score
    return score;
}

// Hàm để chuyển sang bộ câu hỏi tiếp theo
document.getElementById('nextButton').addEventListener('click', function() {
    if (currentSetIndex < questionSets.length - 1) {
        // Chuyển sang bộ câu hỏi tiếp theo
        currentSetIndex++;
        renderQuestion2(questionSets[currentSetIndex]);

        // Nếu đã đến bộ câu hỏi cuối, thay đổi nút Next thành "Đã hết câu hỏi"
        if (currentSetIndex === questionSets.length - 1) {
            document.getElementById('nextButton').textContent = "Đã hết câu hỏi";
        }
    }
});

// Hàm xử lý sự kiện khi nhấn nút Back
document.getElementById('backButton').addEventListener('click', function() {
    if (currentSetIndex > 0) {
        // Quay lại bộ câu hỏi trước
        currentSetIndex--;
        renderQuestion2(questionSets[currentSetIndex]);

        // Nếu không phải bộ câu hỏi cuối, đổi nút Next về "Next"
        if (currentSetIndex !== questionSets.length - 1) {
            document.getElementById('nextButton').textContent = "Next";
        }
    }
});

// Tải dữ liệu câu hỏi từ backend rồi mới render lần đầu
fetch('/api/reading-question2-data')
    .then(res => {
        if (!res.ok) throw new Error('Không tải được dữ liệu câu hỏi');
        return res.json();
    })
    .then(data => {
        questionSets = data.questionSets;
        questheader = Object.values(data.questheader1);
        renderQuestion2(questionSets[currentSetIndex]);
    })
    .catch(err => {
        console.error('Lỗi tải dữ liệu câu hỏi:', err);
        const container = document.getElementById('cardsContainer');
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
