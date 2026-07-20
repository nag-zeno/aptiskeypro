document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================


// Dữ liệu câu hỏi 14
// Dữ liệu không còn nhúng sẵn trong file này nữa mà được tải từ backend qua
// /api/listening-question14-data (xem data_listening.js trong questiondata/).
let question14Data = [];


// ===============================================================================================================
// ////////////// CÂU HỎI 2 (14 of 17) ///////////////
// ===============================================================================================================
// 1. Hàm render
let correctAnswer14 = []; // ✅ Đáp án đúng 4 phần tử đầu tiên (dùng cho chấm điểm)

// ✅ Hàm render
let shuffledOptions14 = [];

function processTranscript(text) {
  return text
    .replace(/\n/g, '<br>')
    .replace(/(^|<br>)(Person )?([A-D]):\s*"?/g, '$1<strong>Person $3:</strong> ')
    .replace(/"(<br>|$)/g, '$1');
}

function renderQuestion14(data) {
  document.getElementById("audioPlayer2").src = data.audioUrl;
  document.getElementById("question14_topic").innerText = data.topic;
  document.getElementById("question14_topic_inline").innerText = data.topic.replace(/^Topic:\s*/i, '');


  // Cập nhật input số câu và tổng số câu
  document.getElementById('questionJumpInput').value = currentIndex + 1;
  document.getElementById('question14_total').textContent = question14Data.length;
  // Lưu lại 4 đáp án đúng đầu tiên
  correctAnswer14 = data.options.slice(0, 4);

  // Tạo mảng xáo trộn để render
  shuffledOptions14 = [...data.options].sort(() => Math.random() - 0.5);

  const selectIds = ["person1", "person2", "person3", "person4"];
  selectIds.forEach((id, index) => {
    const select = document.getElementById(id);
    select.innerHTML = `<option value="">-- Select an answer --</option>`;

    shuffledOptions14.forEach((opt, idx) => {
      const val = String.fromCharCode(65 + idx);
      const optionEl = document.createElement("option");
      optionEl.value = val;
      optionEl.innerText = opt;
      select.appendChild(optionEl);
    });

    // Nếu người dùng đã chọn đáp án → chọn lại
    const prevAnswer = userAnswers_question14[index];
    if (prevAnswer) {
      const selectedIndex = shuffledOptions14.indexOf(prevAnswer);
      select.selectedIndex = selectedIndex + 1; // vì index 0 là "-- Select an answer --"
    }
  });

  const audio = document.getElementById("audioPlayer2");
  const playBtn = document.getElementById("playButton2");
  const playIcon = document.getElementById("playIcon2");
  setupPlayButton(audio, playBtn, playIcon);

  const transcriptBox = document.getElementById("transcriptBox14");
  const transcriptContent = document.getElementById("transcriptContent14");
  transcriptContent.innerHTML = processTranscript(data.transcript);

  const showTranscriptButton = document.getElementById("showTranscriptButton14");
  transcriptBox.style.display = "none";
  showTranscriptButton.innerText = "Show paragraph";

  showTranscriptButton.removeEventListener("click", toggleTranscript14);
  showTranscriptButton.addEventListener("click", toggleTranscript14);
}


// 2. Hàm ẩn hiện
function toggleTranscript14() {
  const transcriptBox = document.getElementById("transcriptBox14");
  const showTranscriptButton = document.getElementById("showTranscriptButton14");

  if (transcriptBox.style.display === "none") {
    transcriptBox.style.display = "block";
    showTranscriptButton.innerText = "Hide paragraph";
  } else {
    transcriptBox.style.display = "none";
    showTranscriptButton.innerText = "Show paragraph";
  }
}
// ===============================================================================================================
// Đáp án câu 14 (với 4 phần tử đầu tiên của options trong question14Data)
// ===============================================================================================================

// Lắng nghe sự kiện khi người dùng chọn đáp án cho câu hỏi 14 (selectbox)
document.querySelectorAll('select[id^="person"]').forEach((select, index) => {
  select.addEventListener('change', function() {
    storeUserAnswerQuestion14(index, this.value); // Lưu đáp án người dùng cho câu hỏi 14
  });
});

// Hàm lưu đáp án câu 14 vào mảng userAnswers_question14
let userAnswers_question14 = [];

// Hàm lưu đáp án người dùng cho câu hỏi 14 vào mảng
function storeUserAnswerQuestion14(index, answerLetter) {
  const optionIndex = answerLetter.charCodeAt(0) - 65;
  const selectedAnswer = shuffledOptions14[optionIndex]; // ✅ Dùng mảng đã xáo trộn
  userAnswers_question14[index] = selectedAnswer;
}






// Giả sử đã có `correctAnswer14` và `userAnswers_question14` được định nghĩa ở nơi khác trong mã của bạn
function showResults_question14() {
  const comparisonBody14 = document.getElementById('comparisonTableBody');
  const totalScoreEl = document.getElementById('totalScore');
  const scoreClassificationEl = document.getElementById('scoreClassification');
  comparisonBody14.innerHTML = '';  // Xóa nội dung bảng cũ

  let score = 0;
  let html14 = '';

  // Giả sử correctAnswer14 là một mảng với các đáp án đúng
  correctAnswer14.forEach((correctOption, index) => {
    const userAnswer = userAnswers_question14[index] || 'Not answered';
    const isCorrect = userAnswer === correctOption;

    // Đặt màu sắc cho đáp án người dùng và đáp án đúng
    const userAnswerColor = isCorrect ? 'text-success' : 'text-danger';  // Màu xanh nếu đúng, đỏ nếu sai
    const correctAnswerColor = 'text-success';  // Đáp án đúng luôn màu xanh

    if (isCorrect) {
      score += 2; // Mỗi câu đúng 2 điểm
    }

    html14 += `
      <tr>
        <td class="${userAnswerColor}">${userAnswer}</td>
        <td class="${correctAnswerColor}">${correctOption}</td>
      </tr>
    `;
  });

  comparisonBody14.innerHTML = html14;  // Hiển thị kết quả vào bảng
  totalScoreEl.innerText = `Score: ${score} / 8`;  // Hiển thị tổng điểm
  question14Score = score;

  // Phân loại điểm
  let classification = '';
  if (score >= 8) {
    classification = 'Excellent';
  } else if (score >= 6) {
    classification = 'Good';
  } else if (score >= 4) {
    classification = 'Satisfactory';
  }
  else {
    classification = 'Needs Improvement';
  }

  scoreClassificationEl.innerText = `Classification: ${classification}`;  // Hiển thị phân loại điểm

  // Hiển thị modal
  const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
  resultModal.show();
}


// Gắn sự kiện click cho nút "Check result"
document.getElementById('checkResultButton').addEventListener('click', showResults_question14);







// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
let currentIndex = 0;
let userAnswers = [];  // Mảng lưu trữ các đáp án người dùng

function renderQuestionByIndex(currentIndex) {
  // Kiểm tra nếu currentIndex còn trong phạm vi của question14Data
  if (currentIndex <= question14Data.length - 1) {
    renderQuestion14(question14Data[currentIndex]);
  }
  
  // Thay đổi text của nextButton khi đến câu hỏi cuối cùng
  if (currentIndex === question14Data.length - 1) {
    document.getElementById('nextButton').textContent = "The end"; 
  }
}





// ===== XỬ LÝ NÚT NEXT =====
document.getElementById('nextButton').addEventListener('click', function (e) {
  userAnswers_question14 = [];
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

  if (currentIndex < question14Data.length - 1) {
    currentIndex++;
    renderQuestionByIndex(currentIndex);
  }
});

// ===== XỬ LÝ NÚT BACK =====
document.getElementById('backButton').addEventListener('click', function () {
  userAnswers_question14 = [];
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





// Nhảy câu khi nhập số vào input và nhấn Enter
document.getElementById('questionJumpInput').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') {
    const val = parseInt(this.value, 10);
    if (val >= 1 && val <= question14Data.length) {
      currentIndex = val - 1;
      renderQuestionByIndex(currentIndex);
    } else {
      this.value = currentIndex + 1;
    }
    this.blur();
  }
});

// 1. Tải dữ liệu từ backend rồi hiển thị câu hỏi đầu tiên
fetch('/api/listening-question14-data')
  .then(res => {
    if (!res.ok) throw new Error('Không tải được dữ liệu bài nghe');
    return res.json();
  })
  .then(data => {
    question14Data = data;
    renderQuestion14(question14Data[0]);
  })
  .catch(err => {
    console.error('Lỗi tải dữ liệu listening14:', err);
    const topicEl = document.getElementById('question14_topic');
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
  if (audio || playBtn) {
    const topBar = (audio && audio.closest ? audio.closest('.top-bar') : null) || (playBtn && playBtn.closest ? playBtn.closest('.top-bar') : null);
    if (topBar && !topBar.dataset.volumeBound) {
      topBar.dataset.volumeBound = "true";
      const volumeSlider = topBar.querySelector('input[type="range"]');
      const buttons = topBar.querySelectorAll('button');
      const volumeBtn = Array.from(buttons).find(b => b !== playBtn);
      const volumeIcon = volumeBtn ? volumeBtn.querySelector('i') : null;

      if (volumeSlider && audio) {
        volumeSlider.min = "0";
        volumeSlider.max = "1";
        volumeSlider.step = "0.01";
        volumeSlider.value = audio.volume !== undefined ? audio.volume : 1;

        const updateVolumeIcon = (vol) => {
          if (!volumeIcon) return;
          volumeIcon.className = "bi fs-5";
          if (vol === 0) {
            volumeIcon.classList.add("bi-volume-mute-fill");
          } else if (vol < 0.5) {
            volumeIcon.classList.add("bi-volume-down-fill");
          } else {
            volumeIcon.classList.add("bi-volume-up-fill");
          }
        };

        const setVolume = (val) => {
          const num = Math.max(0, Math.min(1, parseFloat(val)));
          audio.volume = num;
          volumeSlider.value = num;
          updateVolumeIcon(num);
        };

        volumeSlider.addEventListener("input", (e) => setVolume(e.target.value));
        volumeSlider.addEventListener("change", (e) => setVolume(e.target.value));

        if (volumeBtn) {
          let lastVol = 1;
          volumeBtn.addEventListener("click", () => {
            if (audio.volume > 0) {
              lastVol = audio.volume;
              setVolume(0);
            } else {
              setVolume(lastVol > 0 ? lastVol : 1);
            }
          });
        }
      }
    }
  }

  if (!playBtn || playBtn.dataset.bound === "true") return;
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
