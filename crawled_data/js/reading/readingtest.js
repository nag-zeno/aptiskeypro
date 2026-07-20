document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// TẢI DỮ LIỆU BỘ ĐỀ TỪ BACKEND ///////////////
// ===============================================================================================================
// Trước đây mỗi trang /reading001 .. /reading012 dùng 1 file JS riêng (readingkey001.js .. readingkey012.js)
// nhúng sẵn toàn bộ nội dung + đáp án. Giờ dùng chung 1 file này, tải dữ liệu qua
// /api/reading-test-data/:id (xem data_readingtest.js trong questiondata/) để không lộ đáp án
// của tất cả bộ đề cùng lúc qua các file tĩnh.

const match = window.location.pathname.match(/reading(\d+)/);
const testId = match ? parseInt(match[1], 10) : 1;

let q2_topic = '';
let q3_topic = '';
let q4_topic = '';
let q5_topic = '';
let questions1_header = "Question 1 of 5 ";
let questions1 = [];
let question2Content = [];
let question3Content = [];
let question4Text = [];
let question4Content = [];
let correctAnswersQuestion4 = [];
let options = [];
let paragraph_question5 = [];
let meohoc = [];
let questions5 = [];

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

// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
let currentQuestion = 1; // Biến để theo dõi câu hỏi hiện tại

// Hàm để chuyển sang câu hỏi tiếp theo
document.getElementById('nextButton').addEventListener('click', function() {
    if (currentQuestion === 1) {
        document.getElementById('question1').style.display = 'none';
        document.getElementById('question2').style.display = 'block';
        currentQuestion = 2;
    } else if (currentQuestion === 2) {
        document.getElementById('question2').style.display = 'none';
        document.getElementById('question3').style.display = 'block';
        currentQuestion = 3;
    } else if (currentQuestion === 3) {
        document.getElementById('question3').style.display = 'none';
        document.getElementById('question4').style.display = 'block';
        currentQuestion = 4;
    } else if (currentQuestion === 4) {
        document.getElementById('question4').style.display = 'none';
        document.getElementById('question5').style.display = 'block';
        document.getElementById('nextButton').textContent = "Submit Test";
        currentQuestion = 5;
    } else if (currentQuestion === 5) {
        if (document.getElementById('nextButton').textContent === "Submit Test") {
            const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
            confirmationModal.show();
            const modalElement = document.getElementById('confirmationModal');
            modalElement.removeAttribute('aria-hidden');
            modalElement.querySelector('.btn-close').focus();
        }
        if (document.getElementById('nextButton').textContent === "Back to home") {
            window.location.href = "/home.html";
        }
    }
});

// Hàm xử lý sự kiện khi nhấn nút Back
document.getElementById('backButton').addEventListener('click', function() {
    if (currentQuestion === 2) {
        document.getElementById('question2').style.display = 'none';
        document.getElementById('question1').style.display = 'block';
        currentQuestion = 1;
    } else if (currentQuestion === 3) {
        document.getElementById('question3').style.display = 'none';
        document.getElementById('question2').style.display = 'block';
        currentQuestion = 2;
    } else if (currentQuestion === 4) {
        document.getElementById('question4').style.display = 'none';
        document.getElementById('question3').style.display = 'block';
        currentQuestion = 3;
    } else if (currentQuestion === 5) {
        document.getElementById('question5').style.display = 'none';
        document.getElementById('question4').style.display = 'block';
        currentQuestion = 4;
        document.getElementById('nextButton').textContent = "Next";
    }
});

// Handle the confirm submission button click
document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
    confirmationModal.hide();

    document.getElementById('nextButton').textContent = "Back to home";
    document.getElementById('backButton').style.display = 'none';

    const modalElement = document.getElementById('confirmationModal');
    modalElement.setAttribute('aria-hidden', 'true');
    document.getElementById('nextButton').focus();
});

// ===============================================================================================================
// ////////////// NAVIGATOR REVIEW KẾT QUẢ ///////////////
// ===============================================================================================================
['navQ1', 'navQ2', 'navQ3', 'navQ4', 'navQ5'].forEach((navId, i) => {
    document.getElementById(navId).addEventListener('click', function() {
        document.querySelectorAll('[id^="comparisonResult_question"]').forEach(function(element) {
            element.style.display = 'none';
        });
        document.getElementById(`comparisonResult_question${i + 1}`).style.display = 'block';
        updateNavButtons(navId);
    });
});

function updateNavButtons(activeButtonId) {
    const buttons = document.querySelectorAll('[id^="navQ"]');
    buttons.forEach(function(button) {
        button.classList.remove('btn-active');
    });
    const activeButton = document.getElementById(activeButtonId);
    activeButton.classList.add('btn-active');
}

// ===============================================================================================================
// ////////////// CÂU HỎI 1 ///////////////
// ===============================================================================================================
const userAnswers = [];

function renderQuestions1() {
    const container = document.getElementById('questions-container');
    questions1.forEach((question, index) => {
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
    document.getElementById('question1_header').innerHTML = questions1_header;
}

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    const answers = [];
    const correctAnswers = [];

    questions1.forEach((question, index) => {
        const selectedAnswer = userAnswers[index] || "(không chọn)";
        answers.push(`${question.questionStart} ${selectedAnswer} ${question.questionEnd}`);
        correctAnswers.push(`${question.questionStart} ${question.correctAnswer} ${question.questionEnd}`);
    });

    question1Score = displayComparisonResultsQuestion1(userAnswers, correctAnswers);

    document.getElementById('question1').style.display = 'none';
    document.getElementById('question2').style.display = 'none';
    document.getElementById('question3').style.display = 'none';
    document.getElementById('question4').style.display = 'none';
    document.getElementById('question5').style.display = 'none';
    document.getElementById('result_navigation').style.display = 'block';
});

function displayComparisonResultsQuestion1(userAnswers, correctAnswers) {
    const comparisonResult = document.getElementById('comparisonResult_question1');
    const comparisonBody = document.getElementById('comparisonBody_question1');
    const totalScoreElement = document.getElementById('totalScore_question1');
    let totalScore = 0;

    comparisonResult.style.display = 'block';
    comparisonBody.innerHTML = '';

    questions1.forEach((question, index) => {
        const tr = document.createElement('tr');
        const userAnswer = userAnswers[index] || "(không chọn)";

        if (userAnswer === question.correctAnswer) {
            totalScore += 2;
        }

        const userAnswerTd = document.createElement('td');
        userAnswerTd.innerHTML = `${question.questionStart} <span class="${userAnswer === question.correctAnswer ? 'correct' : 'incorrect'}">${userAnswer}</span> ${question.questionEnd}`;
        tr.appendChild(userAnswerTd);

        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `${question.questionStart} <span class="correct">${question.correctAnswer}</span> ${question.questionEnd}`;
        tr.appendChild(correctAnswerTd);
        comparisonBody.appendChild(tr);

        totalScoreElement.innerHTML = `<strong>Your score: ${totalScore} / ${correctAnswers.length * 2}</strong>`;
    });

    return totalScore;
}

// ===============================================================================================================
// ////////////// CÂU HỎI 2 & 3 (sắp xếp câu) ///////////////
// ===============================================================================================================
function shuffleQuestions(questions) {
    for (let i = questions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [questions[i], questions[j]] = [questions[j], questions[i]];
    }
}

function renderQuestion2() {
    shuffleQuestions(question2Content);
    document.getElementById('question2_topic').innerHTML = 'Topic: ' + q2_topic;

    const questionContainer = document.getElementById('question2_questions_container');

    question2Content.forEach((item) => {
        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card', 'mb-2', 'draggable-item');
        cardDiv.setAttribute('draggable', 'true');
        cardDiv.id = item.id;

        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body');
        cardBody.innerText = item.text;

        cardDiv.appendChild(cardBody);
        questionContainer.appendChild(cardDiv);
    });

    initSortable();
}

function initSortable() {
    const questionContainer = document.getElementById('question2_questions_container');

    new Sortable(questionContainer, {
        group: 'shared',
        animation: 150,
        onAdd: function (evt) {
            const targetContainer = evt.to;
            const draggedItem = evt.item;

            if (targetContainer.children.length > 1) {
                const existingItem = [...targetContainer.children].find(child => child !== draggedItem);
                evt.from.appendChild(existingItem);
            }
        }
    });
}

let correctAnswersQuestion2 = [];
const userAnswersQuestion2 = [];

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    userAnswersQuestion2.length = 0;

    const questionContainer = document.getElementById('question2_questions_container');
    const cards = questionContainer.querySelectorAll('.draggable-item');

    cards.forEach((card) => {
        const selectedAnswer = card.textContent.trim() || "(không chọn)";
        userAnswersQuestion2.push(selectedAnswer);
    });

    const answers = [];
    const correctAnswers = [];

    correctAnswersQuestion2.forEach((correctAnswer, index) => {
        const selectedAnswer = userAnswersQuestion2[index] || "(không chọn)";
        answers.push(selectedAnswer);
        correctAnswers.push(correctAnswer);
    });

    question2Score = displayComparisonResultsQuestion2(answers, correctAnswers);
});

function displayComparisonResultsQuestion2(userAnswers, correctAnswers) {
    const comparisonBody = document.getElementById('comparisonBody_question2');
    const totalScoreElement = document.getElementById('totalScore_question2');

    comparisonBody.innerHTML = '';
    let score = 0;

    userAnswers.forEach((userAnswer, index) => {
        const tr = document.createElement('tr');

        const userAnswerTd = document.createElement('td');
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        if (userAnswer === correctAnswers[index]) {
            score++;
        }

        comparisonBody.appendChild(tr);
    });

    totalScoreElement.innerHTML = `<strong>Your score: ${score} / ${correctAnswers.length}</strong>`;

    return score;
}

// ===============================================================================================================
// ////////////// CÂU HỎI 3 ///////////////
// ===============================================================================================================
function renderQuestion3() {
    document.getElementById('question3_topic').innerHTML = 'Topic: ' + q3_topic;
    shuffleQuestions(question3Content);

    const questionContainer = document.getElementById('question3_questions_container');

    question3Content.forEach((item) => {
        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card', 'mb-2', 'draggable-item');
        cardDiv.setAttribute('draggable', 'true');
        cardDiv.id = item.id;

        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body');
        cardBody.innerText = item.text;

        cardDiv.appendChild(cardBody);
        questionContainer.appendChild(cardDiv);
    });

    initSortable3();
}

function initSortable3() {
    const questionContainer = document.getElementById('question3_questions_container');

    new Sortable(questionContainer, {
        group: 'q3_shared',
        animation: 150,
        onAdd: function (evt) {
            const targetContainer = evt.to;
            const draggedItem = evt.item;

            if (targetContainer.children.length > 1) {
                const existingItem = [...targetContainer.children].find(child => child !== draggedItem);
                evt.from.appendChild(existingItem);
            }
        }
    });
}

let correctAnswersquestion3 = [];
const userAnswersquestion3 = [];

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    userAnswersquestion3.length = 0;

    const questionContainer = document.getElementById('question3_questions_container');
    const cards = questionContainer.querySelectorAll('.draggable-item');

    cards.forEach((card) => {
        const selectedAnswer = card.textContent.trim() || "(không chọn)";
        userAnswersquestion3.push(selectedAnswer);
    });

    const answers = [];
    const correctAnswers = [];

    correctAnswersquestion3.forEach((correctAnswer, index) => {
        const selectedAnswer = userAnswersquestion3[index] || "(không chọn)";
        answers.push(selectedAnswer);
        correctAnswers.push(correctAnswer);
    });

    question3Score = displayComparisonResultsquestion3(answers, correctAnswers);
});

function displayComparisonResultsquestion3(userAnswers, correctAnswers) {
    const comparisonBody = document.getElementById('comparisonBody_question3');
    const totalScoreElement = document.getElementById('totalScore_question3');

    comparisonBody.innerHTML = '';
    let score = 0;

    userAnswers.forEach((userAnswer, index) => {
        const tr = document.createElement('tr');

        const userAnswerTd = document.createElement('td');
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        if (userAnswer === correctAnswers[index]) {
            score++;
        }

        comparisonBody.appendChild(tr);
    });

    totalScoreElement.innerHTML = `<strong>Your score: ${score} / ${correctAnswers.length}</strong>`;

    return score;
}

// ===============================================================================================================
// ////////////// CÂU HỎI 4 (ai nói gì) ///////////////
// ===============================================================================================================
function renderQuestion4() {
    document.getElementById('question4_topic').innerHTML = 'Topic: ' + q4_topic;
    const container = document.getElementById('question4');
    const row = container.querySelector('.row');

    const leftColumn = row.querySelector('.col-md-7');
    question4Text.forEach(text => {
        const p = document.createElement('p');
        p.innerHTML = text;
        leftColumn.appendChild(p);
    });

    const rightColumn = row.querySelector('.col-md-5');
    const form = rightColumn.querySelector('form');

    question4Content.forEach(item => {
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
}

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    const answers = [];
    const correctAnswers = [];

    for (let i = 0; i < 7; i++) {
        const selectElement = document.getElementById(`question4_q${i + 1}`);
        if (selectElement) {
            const selectedAnswer = selectElement.value || "(không chọn)";
            answers.push(selectedAnswer);
            correctAnswers.push(correctAnswersQuestion4[i]);
        } else {
            console.error(`Element with id 'question4_q${i + 1}' not found`);
        }
    }

    question4Score = displayComparisonResultsQuestion4(answers, correctAnswers);
});

function displayComparisonResultsQuestion4(userAnswers, correctAnswers) {
    const comparisonBody = document.getElementById('comparisonBody_question4');
    const totalScoreElement = document.getElementById('totalScore_question4');
    const textContainer = document.getElementById('question4_textContainer');

    comparisonBody.innerHTML = '';
    textContainer.innerHTML = '';

    question4Text.forEach(text => {
        const p = document.createElement('p');
        p.innerHTML = text;
        textContainer.appendChild(p);
    });

    let score = 0;

    question4Content.forEach((item, index) => {
        const tr = document.createElement('tr');

        const questionTd = document.createElement('td');
        questionTd.innerHTML = item.question;
        tr.appendChild(questionTd);

        const userAnswerTd = document.createElement('td');
        const userAnswer = userAnswers[index] || "(không chọn)";
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        if (userAnswer === correctAnswers[index]) {
            score += 2;
        }

        comparisonBody.appendChild(tr);
    });

    totalScoreElement.innerHTML = `<strong>Your score: ${score} / ${correctAnswers.length * 2}</strong>`;

    return score;
}

// ===============================================================================================================
// ////////////// CÂU HỎI 5 (nối đoạn văn) ///////////////
// ===============================================================================================================
function shuffleArray(arr) {
    const firstElement = arr[0];
    const remainingElements = arr.slice(1);

    for (let i = remainingElements.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [remainingElements[i], remainingElements[j]] = [remainingElements[j], remainingElements[i]];
    }

    remainingElements.unshift(firstElement);

    return remainingElements;
}

function renderQuestion5() {
    const container = document.getElementById('question5-container');
    document.getElementById('question5_topic').innerHTML = 'Topic: ' + q5_topic;

    const showAnswerButton = document.getElementById('showAnswerButton');
    const answerModal = new bootstrap.Modal(document.getElementById('answerModal'));
    const modalBody = document.getElementById('modal-body');

    showAnswerButton.addEventListener('click', function() {
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

        answerModal.show();
    });

    const shuffledOptions = shuffleArray([...options]);

    questions5.length = 0;
    questions5.push(
        { id: 'question5_q1', label: '1.', paragraph: paragraph_question5[0], correctAnswer: options[1] },
        { id: 'question5_q2', label: '2.', paragraph: paragraph_question5[1], correctAnswer: options[2] },
        { id: 'question5_q3', label: '3.', paragraph: paragraph_question5[2], correctAnswer: options[3] },
        { id: 'question5_q4', label: '4.', paragraph: paragraph_question5[3], correctAnswer: options[4] },
        { id: 'question5_q5', label: '5.', paragraph: paragraph_question5[4], correctAnswer: options[5] },
        { id: 'question5_q6', label: '6.', paragraph: paragraph_question5[5], correctAnswer: options[6] },
        { id: 'question5_q7', label: '7.', paragraph: paragraph_question5[6], correctAnswer: options[7] }
    );

    questions5.forEach(question => {
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('mb-3');

        const questionRow = document.createElement('div');
        questionRow.style.display = 'flex';
        questionRow.style.alignItems = 'center';

        const label = document.createElement('label');
        label.setAttribute('for', question.id);
        label.classList.add('form-label');
        label.textContent = question.label;
        label.style.marginRight = '10px';

        const select = document.createElement('select');
        select.classList.add('form-select');
        select.id = question.id;

        shuffledOptions.forEach(optionValue => {
            const option = document.createElement('option');
            option.value = optionValue;
            option.textContent = optionValue.charAt(0).toUpperCase() + optionValue.slice(1);
            select.appendChild(option);
        });

        questionRow.appendChild(label);
        questionRow.appendChild(select);

        const paragraph = document.createElement('p');
        paragraph.classList.add('mt-2');
        paragraph.id = `paragraph${question.id.slice(10)}`;
        paragraph.style.display = 'none';
        paragraph.textContent = question.paragraph;

        questionDiv.appendChild(questionRow);
        questionDiv.appendChild(paragraph);

        container.appendChild(questionDiv);
    });
}

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    const answers = [];
    const correctAnswers = [];

    questions5.forEach((question, index) => {
        const selectedAnswer = document.getElementById(question.id).value || "(không chọn)";
        answers.push(selectedAnswer);
        correctAnswers.push(question.correctAnswer);
    });

    question5Score = displayComparisonResultsQuestion5(answers, correctAnswers);
});

function displayComparisonResultsQuestion5(userAnswers, correctAnswers) {
    const comparisonBody = document.getElementById('comparisonBody_question5');
    const totalScoreElement = document.getElementById('totalScore_question5');

    comparisonBody.innerHTML = '';
    let score = 0;

    userAnswers.forEach((userAnswer, index) => {
        const tr = document.createElement('tr');

        const userAnswerTd = document.createElement('td');
        userAnswerTd.innerHTML = `<span class="${userAnswer === correctAnswers[index] ? 'correct' : 'incorrect'}">${userAnswer}</span>`;
        tr.appendChild(userAnswerTd);

        const correctAnswerTd = document.createElement('td');
        correctAnswerTd.innerHTML = `<span class="correct">${correctAnswers[index]}</span>`;
        tr.appendChild(correctAnswerTd);

        if (userAnswer === correctAnswers[index]) {
            score += 2;
        }

        comparisonBody.appendChild(tr);
    });

    totalScoreElement.innerHTML = `<strong>Your score: ${score} / ${correctAnswers.length * 2}</strong>`;

    return score;
}

// ===============================================================================================================
// ////////////// HIỂN THỊ ĐOẠN VĂN VÀ XEM MẸO ///////////////
// ===============================================================================================================
document.getElementById('showParagraphButton').addEventListener('click', function() {
    const paragraphs = document.querySelectorAll('.mt-2');
    paragraphs.forEach(paragraph => {
        paragraph.style.display = (paragraph.style.display === 'none' || paragraph.style.display === '') ? 'block' : 'none';
    });
});

// ===============================================================================================================
// ////////////// TÍNH TỔNG ĐIỂM VÀ PHÂN LOẠI CẤP BẬC ///////////////
// ===============================================================================================================
var question1Score = 0;
var question2Score = 0;
var question3Score = 0;
var question4Score = 0;
var question5Score = 0;

function calculateTotalScore() {
    var totalScore = question1Score + question2Score + question3Score + question4Score + question5Score;

    if (totalScore === 48) {
        totalScore = 50;
    }
    document.getElementById('totalScore').innerText = `Total Score: ${totalScore} / 50`;
    classifyScore(totalScore);
}

function classifyScore(score) {
    let grade = '';

    if (score >= 46) {
        grade = 'C1';
    } else if (score >= 38) {
        grade = 'B2';
    } else if (score >= 26) {
        grade = 'B1';
    } else if (score >= 16) {
        grade = 'A2';
    } else {
        grade = 'A1';
    }
    document.getElementById('scoreClassification').innerText = `Your grade: ${grade}`;
}

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {
    calculateTotalScore();
    document.getElementById('result_navigation').style.display = 'block';
    
    // Tự động lưu kết quả bài thi vào lịch sử
    saveReadingResult();
});

async function saveReadingResult() {
    try {
        const match = window.location.pathname.match(/reading(\d+)/);
        const keyNum = match ? parseInt(match[1], 10) : 1;

        const totalScore = question1Score + question2Score + question3Score + question4Score + question5Score;
        
        // Điểm quy về hệ 100
        const pctScore = (totalScore / 50) * 100;

        // Xác định band Aptis dựa theo logic classifyScore
        let band = 'A1';
        if (totalScore >= 46) {
            band = 'C';
        } else if (totalScore >= 38) {
            band = 'B2';
        } else if (totalScore >= 26) {
            band = 'B1';
        } else if (totalScore >= 16) {
            band = 'A2';
        }

        const answersSummary = {
            "Part 1 (Sentence completion)": `${question1Score} / 10`,
            "Part 2 (Text organization)": `${question2Score} / 10`,
            "Part 3 (Opinions matching)": `${question3Score} / 10`,
            "Part 4 (Long text comprehension)": `${question4Score} / 10`,
            "Part 5 (Three-choice cloze)": `${question5Score} / 10`
        };

        const token = localStorage.getItem('ak_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        const resp = await fetch('/api/compat/save-result', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                skill: 'reading',
                test_id: keyNum,
                score: pctScore,
                aptis_band: band,
                answers: answersSummary,
                time_taken_seconds: 0
            }),
            credentials: 'include'
        });

        if (resp.ok) {
            console.log('Lưu kết quả thi vào lịch sử thành công!');
        } else {
            console.warn('Lưu kết quả thất bại, status:', resp.status);
        }
    } catch (e) {
        console.error('Lỗi khi tự động lưu kết quả bài thi:', e);
    }
}


// ===============================================================================================================
// ////////////// TẢI DỮ LIỆU RỒI RENDER LẦN ĐẦU ///////////////
// ===============================================================================================================
fetch(`/api/reading-test-data/${testId}`)
    .then(res => {
        if (!res.ok) throw new Error('Không tải được dữ liệu bộ đề');
        return res.json();
    })
    .then(data => {
        document.getElementById('question_step').innerHTML = data.label;

        questions1 = data.questions1;
        q2_topic = data.question2Topic;
        question2Content = data.question2Content;
        correctAnswersQuestion2 = question2Content.map(item => item.text);
        q3_topic = data.question3Topic;
        question3Content = data.question3Content;
        correctAnswersquestion3 = question3Content.map(item => item.text);
        q4_topic = data.question4Topic;
        question4Text = data.question4Text;
        question4Content = data.question4Content;
        correctAnswersQuestion4 = data.correctAnswersQuestion4;
        q5_topic = data.question5Topic;
        options = data.options;
        paragraph_question5 = data.paragraph_question5;
        meohoc = data.meohoc;

        renderQuestions1();
        renderQuestion4();
        renderQuestion2();
        renderQuestion3();
        renderQuestion5();
    })
    .catch(err => {
        console.error('Lỗi tải dữ liệu bộ đề:', err);
        const container = document.getElementById('questions-container');
        if (container) {
            container.innerHTML = '<p class="text-danger">Không tải được dữ liệu bộ đề, vui lòng tải lại trang.</p>';
        }
    });

// Kết thúc
});
