document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// Dữ liệu không còn nhúng sẵn trong file này nữa mà được tải từ backend qua
// /api/listening-question1-13-data (xem data_listening.js trong questiondata/),
// tránh việc ai cũng tải được toàn bộ transcript/đáp án qua file tĩnh.
// ===============================================================================================================

let listeningQuestions1 = [];

// Đề mới tính từ đâu
const demoi = 190;

// ===============================================================================================================
// ////////////// CÂU HỎI 1_13 ///////////////
// ===============================================================================================================
let question_index = 0;
function renderQuestion1_13(data) {
  const radioButtons = document.querySelectorAll('input[name="answer"]');
  radioButtons.forEach(button => {
    button.checked = false;  
  });

// Cập nhật tổng số câu
document.getElementById("totalListening").textContent = listeningQuestions1.length;

// Cập nhật input theo currentIndex
document.getElementById("jumpToListening").value = currentIndex + 1;
// Xử lý badge Đề mới
if (currentIndex > demoi) {
    document.getElementById("newBadge").innerHTML = "(Đề mới đi thi về)";
} else {
    document.getElementById("newBadge").innerHTML = "";
}


  const audio = document.getElementById("audioPlayer");
  const questionText = document.getElementById("questionText");
  audio.src = data.audioUrl;
  questionText.innerText = data.question;

  data.options.forEach((option, index) => {
    const label = document.getElementById("label" + index);
    const input = document.getElementById("option" + index);
    if (label && input) {
      label.innerText = option;
      input.value = option;
    }
  });

  // ✅ Đặt lại đáp án sau khi input đã có value
  const storedAnswer = userAnswers[currentIndex]; 
  if (storedAnswer) {
    const savedInput = document.querySelector(`input[name="answer"][value="${storedAnswer}"]`);
    if (savedInput) savedInput.checked = true;
  }

  const playBtn = document.getElementById("playButton");
  const playIcon = document.getElementById("playIcon");
  setupPlayButton(audio, playBtn, playIcon);

  const transcriptBox = document.getElementById("transcriptBox");
  const transcriptContent = document.getElementById("transcriptContent");
  transcriptContent.innerText = data.transcript;

  const showTranscriptButton = document.getElementById("showTranscriptButton");

  transcriptBox.style.display = "none";
  showTranscriptButton.innerText = "Show paragraph";

  showTranscriptButton.removeEventListener("click", toggleTranscript); 
  showTranscriptButton.addEventListener("click", toggleTranscript);
}



// 2. Hàm ẩn hiện paragrap
function toggleTranscript() {
  if (transcriptBox.style.display === "none") {
    transcriptBox.style.display = "block";
    showTranscriptButton.innerText = "Hide paragraph";
  } else {
    transcriptBox.style.display = "none";
    showTranscriptButton.innerText = "Show paragraph";
  }
}

// 3. Hàm load âm thanh
function setupPlayButton(audio, playBtn, playIcon) {
  if (playBtn.dataset.bound === "true") return;
  playBtn.dataset.bound = "true"; 

  playBtn.addEventListener("click", () => {
    if (audio.paused) {
      audio.playPromise = audio.play();
      if (audio.playPromise !== undefined) {
        audio.playPromise.then(() => {
          audio.playPromise = null;
          playIcon.classList.remove("bi-play-fill");
          playIcon.classList.add("bi-pause-fill");
        }).catch(err => {
          audio.playPromise = null;
          if (err.name !== 'AbortError') {
            console.error("Không phát được:", err);
          }
        });
      }
    } else {
      if (audio.playPromise) {
        audio.playPromise.then(() => {
          audio.pause();
          playIcon.classList.remove("bi-pause-fill");
          playIcon.classList.add("bi-play-fill");
        }).catch(() => {
          audio.pause();
          playIcon.classList.remove("bi-pause-fill");
          playIcon.classList.add("bi-play-fill");
        });
      } else {
        audio.pause();
        playIcon.classList.remove("bi-pause-fill");
        playIcon.classList.add("bi-play-fill");
      }
    }
  });

  audio.addEventListener("ended", () => {
    playIcon.classList.remove("bi-pause-fill");
    playIcon.classList.add("bi-play-fill");
  });
}



// ===============================================================================================================
// 4. Đáp án câu 1-13
document.querySelectorAll('input[name="answer"]').forEach((input, index) => {
  input.addEventListener('change', function() {
    storeUserAnswer(currentIndex, this.value);
  });
});

function storeUserAnswer(questionIndex, answer) {
  userAnswers[questionIndex] = answer;
}

// Hàm sửa lại để chỉ kiểm tra câu hỏi tại currentIndex
function showResults_question1_13() {
  const comparisonBody1 = document.getElementById('comparisonTableBody');
  const totalScoreDisplay = document.getElementById('totalScore');
  comparisonBody1.innerHTML = '';

  let score = 0;
  
  // Lấy câu hỏi hiện tại theo currentIndex
  const question = listeningQuestions1[currentIndex];
  const userAnswer = userAnswers[currentIndex];
  const isCorrect = userAnswer === question.correctAnswer;
  const textColor = isCorrect ? 'text-success' : 'text-danger'; // ✅ Màu chữ cho câu trả lời người dùng

  if (isCorrect) {
    score += 2; // Cộng điểm nếu trả lời đúng
  }

  // Thêm kết quả vào bảng so sánh
  comparisonBody1.innerHTML += `
    <tr>
      <td class="${textColor}">${userAnswer || 'Not answered'}</td>
      <td class="${isCorrect ? 'text-success' : 'text-danger'} fw-bold">${question.correctAnswer}</td>
    </tr>
  `;

  // Hiển thị điểm cho câu hỏi hiện tại
  totalScoreDisplay.innerText = `Score: ${score} / 2`;

  // Hiển thị modal
  const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
  resultModal.show();
}


// Sự kiện khi nhấn nút "Check result"
document.getElementById('checkResultButton').addEventListener('click', function () {
  showResults_question1_13();
});


// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
let currentIndex = 0;
let userAnswers = [];  // Mảng lưu trữ các đáp án người dùng

function renderQuestionByIndex(currentIndex) {
  question_index = currentIndex;
  if (currentIndex <= listeningQuestions1.length - 1) {
    renderQuestion1_13(listeningQuestions1[currentIndex]);
  } 
  if(currentIndex === listeningQuestions1.length - 1) {
    document.getElementById('nextButton').textContent = "The end"; 
  }
}




// ===== XỬ LÝ NÚT NEXT =====
document.getElementById('nextButton').addEventListener('click', function (e) {
  document.querySelectorAll('audio').forEach(audio => {
    if (!audio.paused) {
      audio.pause();
      audio.currentTime = 0;
    }
  });
    document.querySelectorAll('i[id^="playIcon"]').forEach(icon => {
      icon.classList.remove("bi-pause-fill");
      icon.classList.add("bi-play-fill");
    });
  if (currentIndex < listeningQuestions1.length - 1) {
    currentIndex++;
    renderQuestionByIndex(currentIndex);
  }
});

// ===== XỬ LÝ NÚT BACK =====
document.getElementById('backButton').addEventListener('click', function () {
  // 🔁 Reset tất cả audio và icon play
  document.querySelectorAll('audio').forEach(audio => {
    if (!audio.paused) {
      audio.pause();
      audio.currentTime = 0;
    }
  });
  document.querySelectorAll('i[id^="playIcon"]').forEach(icon => {
    icon.classList.remove("bi-pause-fill");
    icon.classList.add("bi-play-fill");
  });

  document.getElementById('nextButton').textContent = "Next";

  if (currentIndex > 0) {
    currentIndex--;
  }
  renderQuestionByIndex(currentIndex);
});




// 1. Tải dữ liệu từ backend rồi hiển thị câu hỏi đầu tiên
fetch('/api/listening-question1-13-data')
  .then(res => {
    if (!res.ok) throw new Error('Không tải được dữ liệu bài nghe');
    return res.json();
  })
  .then(data => {
    listeningQuestions1 = data;
    renderQuestion1_13(listeningQuestions1[0]);
  })
  .catch(err => {
    console.error('Lỗi tải dữ liệu listening:', err);
    const questionText = document.getElementById('questionText');
    if (questionText) {
      questionText.innerText = 'Không tải được dữ liệu bài nghe, vui lòng tải lại trang.';
    }
  });



// ===============================
// Jump to specific listening question
// ===============================
document.getElementById('jumpToListening').addEventListener('change', function () {

  let value = parseInt(this.value);

  if (!isNaN(value) && value >= 1 && value <= listeningQuestions1.length) {

    // reset audio
    document.querySelectorAll('audio').forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });

    document.querySelectorAll('i[id^="playIcon"]').forEach(icon => {
      icon.classList.remove("bi-pause-fill");
      icon.classList.add("bi-play-fill");
    });

    currentIndex = value - 1;
    renderQuestionByIndex(currentIndex);

  } else {
    this.value = currentIndex + 1;
  }
});


// ===============================================================================================================
// ////////////// ĐẾM NGƯỢC THỜI GIAN --- COUNT DOWN ///////////////
// ===============================================================================================================
// Countdown Timer
let timeLeft = 40 * 60; // 35 minutes in seconds
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
