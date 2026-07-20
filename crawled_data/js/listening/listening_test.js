document.addEventListener('DOMContentLoaded', function() {



// ===============================================================================================================

// ////////////// DANH SÁCH CÂU HỎI ///////////////

// Dữ liệu không còn nhúng sẵn trong file này nữa mà được tải từ backend qua

// /api/listeningkey-data/:id (xem data_listening.js trong questiondata/), dùng chung cho

// /listeningkey001 .. /listeningkey015 (views/bode/listening.html).

// ===============================================================================================================



let listeningQuestions1 = [];

let question14Data = {};

let question15Data = {};

let question16Data = [];



function renderQuestion1_13(data) {

  const radioButtons = document.querySelectorAll('input[name="answer"]');

  radioButtons.forEach(button => {

    button.checked = false;  

  });



  document.getElementById("question1_13_id").innerText = data.heading;



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





function showResults_question1_13() {

  const comparisonBody1 = document.getElementById('comparisonBody_question1');

  const totalScoreDisplay = document.getElementById('totalScore_question1_13');

  comparisonBody1.innerHTML = '';



  let score = 0;



  listeningQuestions1.forEach((question, index) => {

    const userAnswer = userAnswers[index];

    const isCorrect = userAnswer === question.correctAnswer;

    const textColor = isCorrect ? 'text-success' : 'text-danger'; // ✅ Màu chữ cho câu trả lời người dùng



    if (isCorrect) {

      score += 2;

    }



    comparisonBody1.innerHTML += `

      <tr>

        <td>${index + 1}</td>

        <td class="${textColor} fw-bold">${userAnswer || 'Not answered'}</td>

        <td class="text-success fw-bold">${question.correctAnswer}</td>

      </tr>

    `;

  });



  question1_13Score = score;

  totalScoreDisplay.innerText = `Score: ${score} / 26`;

  document.getElementById('comparisonResult_question1').style.display = "block";

}

















// ===============================================================================================================

// ////////////// CÂU HỎI 2 (14 of 17) ///////////////

// ===============================================================================================================

// 1. Hàm render

//let correctAnswer14 = []; // ✅ Đáp án đúng 4 phần tử đầu tiên (dùng cho chấm điểm)



// ✅ Hàm render

let shuffledOptions14 = [];

function renderQuestion14(data) {

  document.getElementById("audioPlayer2").src = data.audioUrl;

  document.getElementById("question14_topic").innerText = data.topic;



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

  transcriptContent.innerText = data.transcript;



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









// Hàm ẩn hiện transcript

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





//let correctAnswer14 = []; // Đáp án đúng cho câu 14

function showResults_question14() {

  const comparisonBody14 = document.getElementById('comparisonBody_question14');

  const totalScoreEl = document.getElementById('totalScore_question14');

  comparisonBody14.innerHTML = '';



  //const correctAnswer14 = question14Data.options.slice(0, 4); // 4 đáp án đúng

  let score = 0;

  let html14 = '';



  correctAnswer14.forEach((correctOption, index) => {

    const userAnswer = userAnswers_question14[index] || 'Not answered';

    const isCorrect = userAnswer === correctOption;

    const textColor = isCorrect ? 'text-success' : 'text-danger';



    if (isCorrect) {

      score += 2; // Mỗi câu đúng 2 điểm

    }



    html14 += `

      <tr>

        <td>${index + 1}</td>

        <td class="${textColor} fw-bold">${userAnswer}</td>

        <td class="text-success fw-bold">${correctOption}</td>

      </tr>

    `;

  });



  comparisonBody14.innerHTML = html14;

  totalScoreEl.innerText = `Score: ${score} / 8`;

  question14Score = score;



  // Hiện bảng kết quả nếu muốn

  // document.getElementById('comparisonResult_question14').style.display = "block";

}











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

  document.getElementById("question15_id").innerText = data.topic;



  data.questions.forEach((question, index) => {

    const label = document.getElementById("opinion" + (index + 1) + "_label");  // Dùng index để tạo id cho label

    const select = document.getElementById("opinion" + (index + 1));  // Dùng index để tạo id cho select



    if (label) {

      label.innerText = question;  // Gán nội dung question từ mảng vào label

    }



    if (select) {

      select.innerHTML = `<option value="">-- Select an answer --</option>`; // reset

      const options = ["Man", "Woman", "Both"];

      options.forEach((opt, i) => {

        const val = String.fromCharCode(65 + i); // 'A', 'B', 'C'

        const optionEl = document.createElement("option");

        optionEl.value = val;

        optionEl.innerText = opt;

        select.appendChild(optionEl);

      });



      // Nếu người dùng đã chọn đáp án trước đó, hiển thị lại đáp án đã chọn

      if (userAnswers_question15[index]) {

        const selectedIndex = options.indexOf(userAnswers_question15[index]);

        select.value = String.fromCharCode(65 + selectedIndex); // Chọn lại giá trị đã lưu

      }

    }

  });



  const audio = document.getElementById("audioPlayer3");

  const playBtn = document.getElementById("playButton3");

  const playIcon = document.getElementById("playIcon3");

  setupPlayButton(audio, playBtn, playIcon);



  const transcriptBox = document.getElementById("transcriptBox15");

  const transcriptContent = document.getElementById("transcriptContent15");

  transcriptContent.innerText = data.transcript;



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

  const comparisonBody15 = document.getElementById('comparisonBody_question15');

  const totalScoreEl = document.getElementById('totalScore_question15');

  comparisonBody15.innerHTML = '';



  const correctAnswer15 = question15Data.correctAnswer;

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

        <td>${index + 1}</td>

        <td class="${textColor} fw-bold">${userAns}</td>

        <td class="text-success fw-bold">${correctAns}</td>

      </tr>

    `;

  });



  comparisonBody15.innerHTML = html15;

  totalScoreEl.innerText = `Score: ${score} / 8`;

  question15Score = score;



  // document.getElementById('comparisonResult_question15').style.display = 'block';

}











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



  data.questions.forEach((q, index) => {

  const qIndex = index + 1;



  // Gán tiêu đề câu hỏi

  const labelEl = document.getElementById(`q16_opinion${qIndex}_label`);

  labelEl.innerText = `${q.id} ${q.question}`;



  // Lưu đáp án đúng (phần tử đầu tiên)

  correctAnswers_question16[q.id] = q.options[0];



  // Chỉ xáo trộn nếu chưa có câu trả lời

  if (Object.keys(userAnswers_question16).length === 0) {

    const shuffled = [...q.options].sort(() => Math.random() - 0.5);

    shuffledOptionsMap_question16[q.id] = shuffled;

  } else {

    shuffledOptionsMap_question16[q.id] = shuffledOptionsMap_question16[q.id] || [...q.options];

  }



  const shuffled = shuffledOptionsMap_question16[q.id];



  shuffled.forEach((text, optIndex) => {

    const letter = String.fromCharCode(65 + optIndex); // A, B, C

    const radio = document.getElementById(`opinion${qIndex}_${letter}`);

    const label = document.querySelector(`label[for=opinion${qIndex}_${letter}]`);



    if (radio && label) {

      label.innerText = text;

      radio.checked = false;



      // Nếu đã chọn trước đó, hiển thị lại

      if (userAnswers_question16[q.id] === letter) {

        radio.checked = true;

      }



      radio.onchange = () => {

        userAnswers_question16[q.id] = letter;

        console.log(userAnswers_question16, correctAnswers_question16);

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

  const container = document.getElementById("comparisonResult_question16");

  const tbody = document.getElementById("comparisonBody_question16");

  const totalScoreEl = document.getElementById("totalScore_question16");

  tbody.innerHTML = "";



  let score = 0;



  question16Data.forEach(section => {

    section.questions.forEach(q => {

      const qid = q.id;

      const correctText = correctAnswers_question16[qid];                // đáp án đúng gốc

      const shuffled = shuffledOptionsMap_question16[qid];              // mảng đã xáo trộn

      const userLetter = userAnswers_question16[qid];                   // A/B/C

      const userText = userLetter ? shuffled[userLetter.charCodeAt(0) - 65] : "Not answered";



      const isCorrect = userText === correctText;

      if (isCorrect) score += 2;



      const row = document.createElement("tr");

      const userClass = isCorrect ? "text-success fw-bold" : "text-danger fw-bold";



      row.innerHTML = `

        <td>${qid}</td>

        <td class="${userClass}">${userText}</td>

        <td class="text-success fw-bold">${correctText}</td>

      `;

      tbody.appendChild(row);

    });

  });



  totalScoreEl.innerText = `Score: ${score} / 8`;

  question16_17Score = score;

}









// ===============================================================================================================

// ////////////// NÚT NHẤN NEXT VÀ BACK ///////////////

// ===============================================================================================================

let currentIndex = 0;

let userAnswers = [];  // Mảng lưu trữ các đáp án người dùng



function renderQuestionByIndex(currentIndex) {

  if (currentIndex <= listeningQuestions1.length - 1) {

    renderQuestion1_13(listeningQuestions1[currentIndex]);

    document.getElementById("question1_13").style.display = "block";

    document.getElementById("question14").style.display = "none";

    document.getElementById("question15").style.display = "none";

    document.getElementById("question16").style.display = "none";

  } else if (currentIndex === listeningQuestions1.length) {

    renderQuestion14(question14Data);

    document.getElementById("question1_13").style.display = "none";

    document.getElementById("question14").style.display = "block";

    document.getElementById("question15").style.display = "none";

    document.getElementById("question16").style.display = "none";

  } else if (currentIndex === listeningQuestions1.length + 1) {

    renderQuestion15(question15Data);

    document.getElementById("question1_13").style.display = "none";

    document.getElementById("question14").style.display = "none";

    document.getElementById("question15").style.display = "block";

    document.getElementById("question16").style.display = "none";

  } else if (currentIndex === listeningQuestions1.length + 2) {

    renderQuestion16(question16Data[0]);

    document.getElementById("question1_13").style.display = "none";

    document.getElementById("question14").style.display = "none";

    document.getElementById("question15").style.display = "none";

    document.getElementById("question16").style.display = "block";

    document.getElementById('question16_id').textContent = "Question 16 of 17"; // Change Next to Submit

  } else if (currentIndex === listeningQuestions1.length + 3) {

    renderQuestion16(question16Data[1]);

    document.getElementById("question1_13").style.display = "none";

    document.getElementById("question14").style.display = "none";

    document.getElementById("question15").style.display = "none";

    document.getElementById("question16").style.display = "block";

    document.getElementById('question16_id').textContent = "Question 17 of 17"; 

    document.getElementById('nextButton').textContent = "Submit Test"; 

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



  const btn = e.target;

  const btnText = btn.innerText.trim().toLowerCase();



  if (btnText === "submit test") {

    const modal = new bootstrap.Modal(document.getElementById("confirmationModal"));

    modal.show();

    return;

  }



  if (btnText === "back to home") {

    window.location.href = "/home.html";

    return;

  }



  if (currentIndex < listeningQuestions1.length + 3) {

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





// Lắng nghe sự kiện nhấn nút "confirmSubmitBtn" (trên popup)

document.getElementById('confirmSubmitBtn').addEventListener('click', function () {

  // Gọi tất cả hàm hiển thị kết quả các phần

  showResults_question1_13();   // Câu 1–13

  showResults_question14();    // Câu 14

  showResults_question15();    // Câu 15

  showResults_question16();    // Câu 16–17



  // Tính tổng điểm và phân loại

  calculateTotalScore();



      document.getElementById("question1_13").style.display = "none";

    document.getElementById("question14").style.display = "none";

    document.getElementById("question15").style.display = "none";

    document.getElementById("question16").style.display = "none";

    document.getElementById('backButton').style.display = "none";



  // Hiển thị khu vực kết quả phân loại và navigation

  document.getElementById('result_navigation').style.display = 'block';

  document.getElementById('nextButton').textContent = "Back to home";

});











// 1. Tải dữ liệu bộ đề từ backend rồi hiển thị câu hỏi đầu tiên

const __match = window.location.pathname.match(/listeningkey(\d+)/);

const __keyNum = __match ? parseInt(__match[1], 10) : 1;



fetch(`/api/listeningkey-data/${__keyNum}`)

  .then(res => {

    if (!res.ok) throw new Error('Không tải được dữ liệu bộ đề');

    return res.json();

  })

  .then(data => {

    listeningQuestions1 = data.q1_13;

    question14Data = data.q14;

    question15Data = data.q15;

    question16Data = data.q16_17;

    renderQuestion1_13(listeningQuestions1[0]);

  })

  .catch(err => {

    console.error('Lỗi tải dữ liệu bộ đề listening:', err);

    const questionText = document.getElementById('questionText');

    if (questionText) {

      questionText.innerText = 'Không tải được dữ liệu bộ đề, vui lòng tải lại trang.';

    }

  });





















// ===============================================================================================================

// ////////////// TÍNH TỔNG ĐIỂM VÀ PHÂN LOẠI CẤP BẬC ///////////////

// ===============================================================================================================

var question1_13Score = 0;

var question14Score = 0;

var question15Score = 0;

var question16_17Score = 0;

function calculateTotalScore() {

    var totalScore = 0;

    totalScore = question1_13Score + question14Score + question15Score + question16_17Score;

    

    if (totalScore === 48) {

        totalScore = 50;

    }

    document.getElementById('totalScore').innerText = `Total Score: ${totalScore} / 50`;

    classifyScore(totalScore);



}



// 2. Phân loại điểm

function classifyScore(score) {

    let grade = '';

    

    if (score >= 42) {

        grade = 'C1';

    } else if (score >= 34) {

        grade = 'B2';

    } else if (score >= 24) {

        grade = 'B1';

    } else if (score >= 16) {

        grade = 'A2';

    }else {

        grade = 'A1';

    }

    document.getElementById('scoreClassification').innerText = `Your grade: ${grade}`;

}

document.getElementById('confirmSubmitBtn').addEventListener('click', function() {

    calculateTotalScore();

    document.getElementById('result_navigation').style.display = 'block';

    // Tự động lưu kết quả bài thi vào lịch sử
    saveListeningResult();

});

async function saveListeningResult() {
    try {
        const match = window.location.pathname.match(/listeningkey(\d+)/);
        const keyNum = match ? parseInt(match[1], 10) : 1;

        const totalScore = question1_13Score + question14Score + question15Score + question16_17Score;
        
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
            "Part 1 (Information matching)": `${question1_13Score} / 26`,
            "Part 2 (Conversation matching)": `${question14Score} / 8`,
            "Part 3 (Opinion matching)": `${question15Score} / 8`,
            "Part 4 (Monologue comprehension)": `${question16_17Score} / 8`
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
                skill: 'listening',
                test_id: keyNum,
                score: pctScore,
                aptis_band: band,
                answers: answersSummary,
                time_taken_seconds: 0
            }),
            credentials: 'include'
        });

        if (resp.ok) {
            console.log('Lưu kết quả listening vào lịch sử thành công!');
        } else {
            console.warn('Lưu kết quả thất bại, status:', resp.status);
        }
    } catch (e) {
        console.error('Lỗi khi tự động lưu kết quả bài thi listening:', e);
    }
}




// ===============================================================================================================

// ////////////// HIỂN THỊ SỐ ĐIỂM ///////////////

// ===============================================================================================================

// Bản đồ giữa nút và phần kết quả tương ứng

const navMap = {

  navQ1: 'comparisonResult_question1',

  navQ2: 'comparisonResult_question14',

  navQ3: 'comparisonResult_question15',

  navQ4: 'comparisonResult_question16'

};



// Lặp qua tất cả các nút điều hướng

Object.keys(navMap).forEach(navId => {

  const button = document.getElementById(navId);

  button.addEventListener('click', () => {

    // 1. Ẩn toàn bộ các khu vực kết quả

    Object.values(navMap).forEach(resultId => {

      const section = document.getElementById(resultId);

      if (section) section.style.display = 'none';

    });



    // 2. Hiện phần được chọn

    const targetResult = document.getElementById(navMap[navId]);

    if (targetResult) targetResult.style.display = 'block';



    // 3. Cập nhật nút đang được chọn (btn-active)

    Object.keys(navMap).forEach(id => {

      const btn = document.getElementById(id);

      btn.classList.remove('btn-active');

    });

    button.classList.add('btn-active');

  });

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

