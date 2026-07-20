document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================

// Dữ liệu câu hỏi 15
// Dữ liệu không còn nhúng sẵn trong file này nữa mà được tải từ backend qua
// /api/listening-question15-data (xem data_listening.js trong questiondata/).
let question15Data = [];


// ===============================================================================================================
// ////////////// CÂU HỎI 15 ///////////////
// ===============================================================================================================
// Mảng lưu đáp án người dùng cho câu hỏi 15
let userAnswers_question15 = [];



// Hàm lưu đáp án người dùng cho câu hỏi 15
function storeUserAnswerQuestion15(index, answer) {
  const options = ["Man", "Woman", "Both"]; // Các lựa chọn thực tế
  const selectedAnswer = options[answer.charCodeAt(0) - 65];  // Chuyển từ 'A' -> "man", 'B' -> "woman", 'C' -> "both"
  userAnswers_question15[index] = selectedAnswer; // Lưu đáp án vào mảng
}

// Hàm render câu hỏi 15
function renderQuestion15(data) {
  document.getElementById("audioPlayer3").src = data.audioUrl;
  const topicEl = document.getElementById("question15_id");
  topicEl.innerHTML = data.topic + (data.topicNote ? `<br><small class="text-danger fw-normal">${data.topicNote}</small>` : '');
  const descEl = document.getElementById("question15_desc");
  if (descEl && data.description) descEl.innerText = data.description;

  document.getElementById('q15_total').textContent = question15Data.length;
  document.getElementById('jumpToQ15').value = currentIndex + 1;

  data.questions.forEach((question, index) => {
    const label = document.getElementById("opinion" + (index + 1) + "_label");  // Dùng index để tạo id cho label
    const select = document.getElementById("opinion" + (index + 1));  // Dùng index để tạo id cho select

    if (label) {
      label.innerText = question;  // Gán nội dung question từ mảng vào label
    }

    if (select) {
      select.innerHTML = `<option value="">-- Select an answer --</option>`; // reset lại các lựa chọn
      const options = ["Man", "Woman", "Both"];
      options.forEach((opt, i) => {
        const val = String.fromCharCode(65 + i); // 'A', 'B', 'C'
        const optionEl = document.createElement("option");
        optionEl.value = val;
        optionEl.innerText = opt;
        select.appendChild(optionEl);
      });

      // Xóa phần này để không hiển thị đáp án đã chọn trước đó
      // Nếu bạn không muốn lưu đáp án đã chọn trước đó, không cần đoạn này:
      // if (userAnswers_question15[index]) {
      //   const selectedIndex = options.indexOf(userAnswers_question15[index]);
      //   select.value = String.fromCharCode(65 + selectedIndex); // Chọn lại giá trị đã lưu
      // }
    }
  });

  const audio = document.getElementById("audioPlayer3");
  const playBtn = document.getElementById("playButton3");
  const playIcon = document.getElementById("playIcon3");
  setupPlayButton(audio, playBtn, playIcon);

  const transcriptBox = document.getElementById("transcriptBox15");
  const transcriptContent = document.getElementById("transcriptContent15");
  transcriptContent.innerHTML = data.transcript
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/(^|\n)M:/g, '$1Man:')
    .replace(/(^|\n)W:/g, '$1Woman:')
    .replace(/\n/g, '<br>')
    .replace(/(Man:|Woman:)/g, '<strong>$1</strong>');

  const showTranscriptButton = document.getElementById("showTranscriptButton15");

  transcriptBox.style.display = "none";
  showTranscriptButton.innerText = "Show paragraph";

  showTranscriptButton.removeEventListener("click", toggleTranscript15);
  showTranscriptButton.addEventListener("click", toggleTranscript15);
}


// Hàm ẩn hiện transcript
function toggleTranscript15() {
  const transcriptBox = document.getElementById("transcriptBox15");
  const showTranscriptButton = document.getElementById("showTranscriptButton15");

  if (transcriptBox.style.display === "none") {
    transcriptBox.style.display = "block";
    showTranscriptButton.innerText = "Hide paragraph";
  } else {
    transcriptBox.style.display = "none";
    showTranscriptButton.innerText = "Show paragraph";
  }
}

// Lắng nghe sự kiện khi người dùng chọn đáp án cho câu hỏi 15 (selectbox)
document.querySelectorAll('select[id^="opinion"]').forEach((select, index) => {
  select.addEventListener('change', function() {
    storeUserAnswerQuestion15(index, this.value); // Lưu đáp án người dùng cho câu hỏi 15
  });
});


// Hàm hiển thị kết quả cho câu hỏi 15
function showResults_question15() {
  const comparisonBody15 = document.getElementById('comparisonTableBody'); // Đã sửa lại ID cho modal
  const totalScoreEl = document.getElementById('totalScore'); // Đã sửa lại ID cho modal
  comparisonBody15.innerHTML = ''; // Xóa nội dung cũ

  const correctAnswer15 = question15Data[currentIndex].correctAnswer;
  let score = 0;
  let html15 = '';

  correctAnswer15.forEach((correctAns, index) => {
    const userAns = userAnswers_question15[index] || 'Not answered';
    const isCorrect = userAns === correctAns;
    const textColor = isCorrect ? 'text-success' : 'text-danger';

    if (isCorrect) {
      score += 2;
    }

    html15 += `
      <tr>
        <td class="${textColor} fw-bold">${userAns}</td>
        <td class="text-success fw-bold">${correctAns}</td>
      </tr>
    `;
  });

  comparisonBody15.innerHTML = html15; // Đưa dữ liệu vào bảng so sánh
  totalScoreEl.innerText = `Score: ${score} / 8`; // Hiển thị tổng điểm

  // Mở modal khi nhấn nút "Check result"
  const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
  resultModal.show();
}

// Gắn sự kiện cho nút "Check result"
document.getElementById('checkResultButton').addEventListener('click', showResults_question15);




// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
let currentIndex = 0;
function renderQuestionByIndex(currentIndex) {
  if (currentIndex <= question15Data.length - 1) {
    renderQuestion15(question15Data[currentIndex]);
  }
  if (currentIndex === question15Data.length - 1) {
    document.getElementById('nextButton').textContent = "The end"; 
  }
}




// ===== XỬ LÝ NÚT NEXT =====
document.getElementById('nextButton').addEventListener('click', function (e) {
  userAnswers_question15 = [];
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
  if (currentIndex < question15Data.length - 1) {
    currentIndex++;
    renderQuestionByIndex(currentIndex);
  }
});

// ===== XỬ LÝ NÚT BACK =====
document.getElementById('backButton').addEventListener('click', function () {
  userAnswers_question15 = [];
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




// ===== JUMP TO QUESTION =====
document.getElementById('jumpToQ15').addEventListener('change', function () {
  const value = parseInt(this.value);
  if (!isNaN(value) && value >= 1 && value <= question15Data.length) {
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

// 1. Tải dữ liệu từ backend rồi hiển thị câu hỏi đầu tiên
fetch('/api/listening-question15-data')
  .then(res => {
    if (!res.ok) throw new Error('Không tải được dữ liệu bài nghe');
    return res.json();
  })
  .then(data => {
    question15Data = data;
    renderQuestionByIndex(0);
  })
  .catch(err => {
    console.error('Lỗi tải dữ liệu listening15:', err);
    const topicEl = document.getElementById('question15_id');
    if (topicEl) {
      topicEl.innerText = 'Không tải được dữ liệu bài nghe, vui lòng tải lại trang.';
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

// Kết thúc
});
