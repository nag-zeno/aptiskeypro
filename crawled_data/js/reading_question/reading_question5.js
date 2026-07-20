document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================
// Dữ liệu câu hỏi (đoạn văn, lựa chọn, mẹo học) không còn nằm trong file này nữa mà được tải từ backend
// qua API /api/reading-question5-data (xem data_readingquestion.js trong questiondata/), tránh việc
// ai cũng tải được toàn bộ nội dung của tất cả bộ đề cùng lúc qua 1 file tĩnh.

let options = [];
let paragraph_question5 = [];
let meohoc = [];
let topic_name = {};
let dodai = 0;

// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
// Biến theo dõi câu hỏi hiện tại
let currentQuestion = 0; // Câu hỏi bắt đầu từ 0

// Hàm xử lý sự kiện khi nhấn nút Next
document.getElementById('nextButton').addEventListener('click', function() {

    // Kiểm tra nếu câu hỏi không phải câu cuối cùng
    if (currentQuestion < options.length - 1) {
        currentQuestion++; // Tăng chỉ số câu hỏi hiện tại

        // Xóa nội dung cũ trong container trước khi render câu hỏi mới
        const container = document.getElementById('question5-container');
        container.innerHTML = ''; // Xóa nội dung cũ

        // Gọi lại hàm render để hiển thị câu hỏi mới
        renderQuestion5(options[currentQuestion], paragraph_question5[currentQuestion], meohoc[currentQuestion]);

        // Nếu là câu hỏi cuối cùng, đổi văn bản nút Next thành "Submit Test"
        if (currentQuestion === options.length - 1) {
            document.getElementById('nextButton').textContent = 'The end';
        }
    }
});

// Hàm xử lý sự kiện khi nhấn nút Back
document.getElementById('backButton').addEventListener('click', function() {
    if (currentQuestion > 0) {
        currentQuestion--; // Giảm chỉ số câu hỏi hiện tại

        // Xóa nội dung cũ trong container trước khi render câu hỏi mới
        const container = document.getElementById('question5-container');
        container.innerHTML = ''; // Xóa nội dung cũ

        // Gọi lại hàm render để hiển thị câu hỏi cũ
        renderQuestion5(options[currentQuestion], paragraph_question5[currentQuestion], meohoc[currentQuestion]);

        document.getElementById('nextButton').textContent = 'Next';
    }
});

// ===============================================================================================================
// ////////////// CÂU HỎI 5 ///////////////
// ===============================================================================================================
// Hàm Fisher-Yates Shuffle để xáo trộn mảng (bỏ qua phần tử đầu tiên)
function shuffleArray(arr) {
    const firstElement = arr[0]; // Lưu phần tử đầu tiên (rỗng)

    // Tách phần tử đầu tiên và xáo trộn phần còn lại của mảng
    const remainingElements = arr.slice(1);

    // Xáo trộn phần còn lại của mảng
    for (let i = remainingElements.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [remainingElements[i], remainingElements[j]] = [remainingElements[j], remainingElements[i]]; // Swap elements
    }

    // Thêm lại phần tử đầu tiên vào đầu mảng đã xáo trộn
    remainingElements.unshift(firstElement);

    return remainingElements;
}

let questions5 = [];  // Khai báo ngoài để sử dụng toàn cục
// Hàm renderQuestion5 với đầu vào là options, paragraph_question5, meohoc (mảng chứa strong2Content và strong3Content)
function renderQuestion5(options, paragraph_question5, meohoc) {
    const container = document.getElementById('question5-container');  // Lấy container để chứa câu hỏi

    if (!container) {
        console.error("Container không tồn tại!");
        return;
    }
    // Thay đổi tên topic cho phần tử có id "question5_topic"
    document.getElementById("question5_topic").innerText = "TOPIC: " + topic_name["topic_" + (currentQuestion +1)];  // Use the dynamic key based on currentQuestion
    document.getElementById('question5_index').textContent = `Reading question 5 (${currentQuestion + 1}/${dodai})`;

    // Xáo trộn mảng options một lần, nhưng giữ phần tử đầu tiên là khoảng trống
    const shuffledOptions = shuffleArray([...options]);

    // Mảng câu hỏi (sử dụng paragraph_question5 và options đã xáo trộn)
    questions5 = [
        { id: 'question5_q1', label: '1.', paragraph: paragraph_question5[0], correctAnswer: options[1] },
        { id: 'question5_q2', label: '2.', paragraph: paragraph_question5[1], correctAnswer: options[2] },
        { id: 'question5_q3', label: '3.', paragraph: paragraph_question5[2], correctAnswer: options[3] },
        { id: 'question5_q4', label: '4.', paragraph: paragraph_question5[3], correctAnswer: options[4] },
        { id: 'question5_q5', label: '5.', paragraph: paragraph_question5[4], correctAnswer: options[5] },
        { id: 'question5_q6', label: '6.', paragraph: paragraph_question5[5], correctAnswer: options[6] },
        { id: 'question5_q7', label: '7.', paragraph: paragraph_question5[6], correctAnswer: options[7] },
    ];
// Lấy các phần tử cần thiết


// Thêm các phần tử vào modalBody khi nút "Xem mẹo" được nhấn
document.getElementById('showAnswerButton').addEventListener('click', function() {
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = '';

    const strong1 = document.createElement('p');
    strong1.innerHTML = '<strong>Học mẹo nếu bạn cần học gấp:</strong>';

    const strong2 = document.createElement('p');
    strong2.innerHTML = meohoc[0];

    const strong3 = document.createElement('p');
    strong3.innerHTML = meohoc[1];

    modalBody.appendChild(strong1);
    modalBody.appendChild(strong2);
    modalBody.appendChild(strong3);

    $('#answerModal').modal('show');
});

    // Tạo các câu hỏi động
    questions5.forEach(question => {
        // Tạo div cho mỗi câu hỏi
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('mb-3');

        // Tạo một div cha để hiển thị label và select trên cùng một hàng
        const questionRow = document.createElement('div');
        questionRow.style.display = 'flex';
        questionRow.style.alignItems = 'center'; // Căn chỉnh các phần tử giữa

        // Tạo label cho câu hỏi
        const label = document.createElement('label');
        label.setAttribute('for', question.id);
        label.classList.add('form-label');
        label.textContent = question.label;
        label.style.marginRight = '10px'; // Thêm khoảng cách giữa label và select

        // Tạo phần tử select cho câu hỏi
        const select = document.createElement('select');
        select.classList.add('form-select');
        select.id = question.id;

        // Thêm các option vào select
        shuffledOptions.forEach(optionValue => {
            const option = document.createElement('option');
            option.value = optionValue;
            option.textContent = optionValue.charAt(0).toUpperCase() + optionValue.slice(1); // Viết hoa chữ cái đầu tiên
            select.appendChild(option);
        });

        // Thêm label và select vào questionRow
        questionRow.appendChild(label);
        questionRow.appendChild(select);

        // Tạo đoạn văn cho câu hỏi (ẩn ban đầu)
        const paragraph = document.createElement('p');
        paragraph.classList.add('mt-2');
        paragraph.id = `paragraph${question.id.slice(10)}`;
        paragraph.style.display = 'none'; // Đảm bảo đoạn văn ẩn khi tải trang
        paragraph.textContent = question.paragraph;

        // Ghép các phần tử vào questionDiv
        questionDiv.appendChild(questionRow);
        questionDiv.appendChild(paragraph);

        // Thêm câu hỏi vào container
        container.appendChild(questionDiv);
    });
}

// 2. Xử lý kết quả

// Hàm lấy kết quả khi nhấn nút "Submit Test"
document.getElementById('checkResultButton').addEventListener('click', function() {
    const answers = [];
    let correctAnswers = [];
    // Lặp qua các câu hỏi và lưu đáp án người học, sau đó so sánh với đáp án đúng
    questions5.forEach((question, index) => {
        const selectedAnswer = document.getElementById(question.id).value || "(không chọn)";  // Lấy đáp án từ các select box
        answers.push(selectedAnswer);
        correctAnswers.push(question.correctAnswer);
    });

    // Hiển thị kết quả so sánh và mở modal
    displayComparisonResultsQuestion5(answers, correctAnswers);
    $('#resultModal').modal('show');  // Mở modal khi đã có kết quả
});

// Hàm hiển thị kết quả so sánh và điểm số
function displayComparisonResultsQuestion5(userAnswers, correctAnswers) {
    const comparisonBody = document.getElementById('comparisonTableBody');
    const totalScoreElement = document.getElementById('totalScore_question4');

    // Clear previous results
    comparisonBody.innerHTML = '';

    // Tính điểm
    let score = 0;

    // Lặp qua các câu hỏi và so sánh đáp án của người dùng và đáp án đúng
    userAnswers.forEach((userAnswer, index) => {
        const tr = document.createElement('tr');

        // Hiển thị câu hỏi (có thể thay đổi tùy vào câu hỏi)
        const questionTd = document.createElement('td');
        questionTd.innerHTML = `${index + 1}`;
        tr.appendChild(questionTd);

        // Hiển thị đáp án của người học
        const userAnswerTd = document.createElement('td');
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        // Hiển thị đáp án đúng
        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        // Nếu người học chọn đúng, cộng điểm
        if (userAnswer === correctAnswers[index]) {
            score += 2;
        }

        comparisonBody.appendChild(tr);
    });

    // Hiển thị điểm số vào phần tử có id "totalScore_question4"
    totalScoreElement.innerHTML = `<strong>Your score: ${score} / ${correctAnswers.length * 2}</strong>`;

    // Trả về điểm số
    return score;
}

// ===============================================================================================================
// ////////////// HIỂN THỊ ĐOẠN VĂN VÀ XEM MẸO ///////////////
// ===============================================================================================================

// Hiển thị/Ẩn đoạn văn khi nhấn nút "Hiển thị đoạn văn"
document.getElementById('showParagraphButton').addEventListener('click', function() {
    const paragraphs = document.querySelectorAll('.mt-2');
    paragraphs.forEach(paragraph => {
        paragraph.style.display = (paragraph.style.display === 'none' || paragraph.style.display === '') ? 'block' : 'none';
    });
});

// Tải dữ liệu câu hỏi từ backend rồi mới render lần đầu
fetch('/api/reading-question5-data')
    .then(res => {
        if (!res.ok) throw new Error('Không tải được dữ liệu câu hỏi');
        return res.json();
    })
    .then(data => {
        options = data.options;
        paragraph_question5 = data.paragraph_question5;
        meohoc = data.meohoc;
        topic_name = data.topic_name;
        dodai = options.length;
        renderQuestion5(options[0], paragraph_question5[0], meohoc[0]);
    })
    .catch(err => {
        console.error('Lỗi tải dữ liệu câu hỏi:', err);
        const container = document.getElementById('question5-container');
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
