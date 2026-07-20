document.addEventListener('DOMContentLoaded', function() {

// ===============================================================================================================
// ////////////// DANH SÁCH CÂU HỎI ///////////////
// ===============================================================================================================
// Dữ liệu câu hỏi 16 & 17
// Dữ liệu không còn nhúng sẵn trong file này nữa mà được tải từ backend qua
// /api/listening-question16-17-data (xem data_listening.js trong questiondata/).
let question16Data = [];



// Đề mới bắt đầu từ câu số mấy (tính từ 1)
const demoi_batdau = 55;

// ===============================================================================================================
// ////////////// CÂU HỎI 16 ///////////////
// ===============================================================================================================



let userAnswers_question16 = {}; // Lưu đáp án người dùng
let correctAnswers_question16 = {};        // q.id → correct answer text
let shuffledOptionsMap_question16 = {};    // q.id → shuffled options array


function renderQuestion16(data) {
  // Gán audio và tiêu đề
  document.getElementById("audioPlayer16").src = data.audioUrl;
  document.getElementById("question16_topic").innerText = `Topic: ${data.topic}`;
  document.getElementById("transcriptContent16").innerText = data.transcript;


  document.getElementById('q16_total').textContent = question16Data.length;
  document.getElementById('jumpToQ16').value = currentIndex + 1;
  document.getElementById('newBadge16').textContent = currentIndex >= demoi_batdau - 1 ? "(Đề mới đi thi về)" : "";


  data.questions.forEach((q, index) => {
    const qIndex = index + 1;

    // Gán tiêu đề câu hỏi
    const labelEl = document.getElementById(`q16_opinion${qIndex}_label`);
    labelEl.innerText = `${q.id} ${q.question}`;

    // Lưu đáp án đúng (phần tử đầu tiên)
    correctAnswers_question16[q.id] = q.options[0];

    // Xáo trộn phương án
    const shuffled = [...q.options].sort(() => Math.random() - 0.5);
    shuffledOptionsMap_question16[q.id] = shuffled;

    shuffled.forEach((text, optIndex) => {
      const letter = String.fromCharCode(65 + optIndex); // A, B, C
      const radio = document.getElementById(`opinion${qIndex}_${letter}`);
      const label = document.querySelector(`label[for=opinion${qIndex}_${letter}]`);

      if (radio && label) {
        label.innerText = text;
        radio.checked = false;

        // // Nếu đã chọn trước đó, hiển thị lại
        // if (userAnswers_question16[q.id] === letter) {
        //   radio.checked = true;
        // }

        // Lưu đáp án được chọn (A/B/C)
        radio.onchange = () => {
          userAnswers_question16[q.id] = letter;
        };
      }
    });
  });

  // 👉 Thêm đoạn này
  const audio = document.getElementById("audioPlayer16");
  const playBtn = document.getElementById("playButton16");
  const playIcon = document.getElementById("playIcon16");
  setupPlayButton(audio, playBtn, playIcon);

  // Ẩn/hiện transcript
  const btn = document.getElementById("showTranscriptButton16");
  const box = document.getElementById("transcriptBox16");
  btn.innerText = "Show Paragraph";
  box.style.display = "none";

  btn.onclick = () => {
    if (box.style.display === "none") {
      box.style.display = "block";
      btn.innerText = "Hide Paragraph";
    } else {
      box.style.display = "none";
      btn.innerText = "Show Paragraph";
    }
  };
}


function showResults_question16() {
  const tbody = document.getElementById("comparisonTableBody");
  const totalScoreEl = document.getElementById("totalScore");
  const scoreClassificationEl = document.getElementById("scoreClassification");
  tbody.innerHTML = ""; // Xóa các hàng cũ trong bảng kết quả

  let score = 0;

  // Kiểm tra xem currentIndex có hợp lệ không
  if (currentIndex < 0 || currentIndex >= question16Data.length) {
    console.error("Invalid currentIndex");
    return; // Nếu currentIndex không hợp lệ, dừng hàm
  }

  // Lấy phần tử tại currentIndex và duyệt qua các câu hỏi
  const currentData = question16Data[currentIndex];
  currentData.questions.forEach(q => {
    const qid = q.id;
    const correctText = correctAnswers_question16[qid];  // Đáp án đúng
    const shuffled = shuffledOptionsMap_question16[qid]; // Mảng đã xáo trộn các phương án
    const userLetter = userAnswers_question16[qid];       // Câu trả lời của người dùng (A/B/C)
    const userText = userLetter ? shuffled[userLetter.charCodeAt(0) - 65] : "Not answered"; // Đáp án người dùng chọn

    const isCorrect = userText === correctText; // Kiểm tra đáp án đúng
    if (isCorrect) score += 2; // Tính điểm

    // Tạo một dòng mới trong bảng kết quả
    const row = document.createElement("tr");
    const userClass = isCorrect ? "text-success fw-bold" : "text-danger fw-bold";

    row.innerHTML = `
      <td class="${userClass}">${userText}</td>
      <td class="text-success fw-bold">${correctText}</td>
    `;
    tbody.appendChild(row);
  });

  // Hiển thị điểm tổng
  totalScoreEl.innerText = `Score: ${score} / 4`;

  // Phân loại điểm
  if (score === 4) {
    scoreClassificationEl.innerText = "Excellent";
  } else if (score >= 2) {
    scoreClassificationEl.innerText = "Good";
  } else {
    scoreClassificationEl.innerText = "Needs Improvement";
  }

  // Hiển thị modal với kết quả
  const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
  resultModal.show();
}



// Xử lý sự kiện khi nhấn nút "Check result"
const checkResultButton = document.getElementById('checkResultButton');
checkResultButton.addEventListener('click', showResults_question16);


// ===============================================================================================================
// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////
// ===============================================================================================================
let currentIndex = 0;
function renderQuestionByIndex(currentIndex) {
  if (currentIndex <= question16Data.length - 1) {
    renderQuestion16(question16Data[currentIndex]);
  }
  if (currentIndex === question16Data.length - 1) {
    document.getElementById('nextButton').textContent = "The end"; 
  }
}


// ===== XỬ LÝ NÚT NEXT =====
document.getElementById('nextButton').addEventListener('click', function (e) {
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


  if (currentIndex < question16Data.length-1) {
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


// ===== JUMP TO QUESTION =====
document.getElementById('jumpToQ16').addEventListener('change', function () {
  const value = parseInt(this.value);
  if (!isNaN(value) && value >= 1 && value <= question16Data.length) {
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
fetch('/api/listening-question16-17-data')
  .then(res => {
    if (!res.ok) throw new Error('Không tải được dữ liệu bài nghe');
    return res.json();
  })
  .then(data => {
    question16Data = data;
    renderQuestionByIndex(0);
  })
  .catch(err => {
    console.error('Lỗi tải dữ liệu listening16_17:', err);
    const topicEl = document.getElementById('question16_topic');
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
