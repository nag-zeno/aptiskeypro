// Lịch sử cập nhật đề

document.addEventListener("DOMContentLoaded", function () {

  const updates = [

    { date: "16/7/2026", text:  "Thông báo: Nhằm nâng cao chất lượng đào tạo và hướng tới phương châm “Học thật – Thi đạt”, AptisPro sẽ chuyển đổi sang mô hình khóa học trực tuyến có giáo viên trực tiếp hướng dẫn và đồng hành cùng học viên. Vì vậy, chức năng gia hạn không còn nữa (bạn nào tk còn hạn thì vẫn học tiếp). Xem khóa học bên mình <a href='green-aptis.html' target='_blank'>tại đây</a>." },

    { date: "15/7/2026", text:  "Cập nhật thêm 5 bài luyện tập Ngữ pháp do AptisPro tự biên soạn, dựa trên định dạng và các dạng kỹ năng được công bố công khai của bài thi Aptis ESOL. <a href='grammar_bode.html' target='_blank'>Xem tại đây</a>" },

    { date: "14/7/2026", text:  "Thư xin lỗi về sự cố bảo mật. <a href='sucobaomat.html' target='_blank'>Xem tại đây</a>" },

    { date: "10/7/2026", text:  "Listening question 16-17: thêm đề mới câu 59. <a href='listening_question16_17.html' target='_blank'>Xem tại đây</a>" },

    { date: "9/7/2026", text:  "Reading part1 (học theo câu hỏi): thêm bộ đề 36-38. <a href='reading_question1.html' target='_blank'>Xem tại đây</a>" },

    { date: "8/7/2026", text:  "Reading part1 (học theo câu hỏi): thêm bộ đề 33-35. <a href='reading_question1.html' target='_blank'>Xem tại đây</a>" },

    { date: "7/7/2026", text:  "Reading part1 (học theo câu hỏi): thêm bộ đề 26-32. <a href='reading_question1.html' target='_blank'>Xem tại đây</a>" },

    { date: "6/7/2026", text:  "Reading part1 (học theo câu hỏi): thêm bộ đề 21-25. <a href='reading_question1.html' target='_blank'>Xem tại đây</a>" },

    { date: "5/7/2026", text:  "Reading part1 (học theo câu hỏi): thêm bộ đề 14-20. <a href='reading_question1.html' target='_blank'>Xem tại đây</a>" },

    { date: "1/7/2026", text:  "Thêm 3 bộ đề listening mới (013, 014, 015) với Q14: New museum, Q15: Children & Tech / Environmental / Local Culture!. <a href='listening_bode.html' target='_blank'>Xem tại đây</a>" },

    { date: "1/7/2026", text:  "Thêm chủ đề mẹo listening câu 15: Work Business / Business and Cultural!. <a href='listening_meo_cau15_method2.html' target='_blank'>Xem tại đây</a>" },

    { date: "25/6/2026", text:  "Thêm đề listening question 14: New museum in town!. <a href='listening_question14.html' target='_blank'>Xem tại đây</a>" },

    { date: "25/6/2026", text:  "Thêm đề listening question 15: Local Culture diffirent!. <a href='listening_meo_cau15_method2.html' target='_blank'>Xem tại đây</a>" },

    { date: "18/6/2026", text:  "Thêm đề listening question 15: Environmental volunteer program!. <a href='listening_question15.html' target='_blank'>Xem tại đây</a>" },

    { date: "12/6/2026", text:  "Thêm đề mới lis question 15 đề 13!. <a href='listening_question15.html' target='_blank'>Xem tại đây</a>" },

    { date: "28/5/2026", text:  "Thêm một số đề mới listening Q16-17!. <a href='listening_question16_17.html' target='_blank'>Xem tại đây</a>" },

    { date: "26/5/2026", text:  "Thêm một số đề mới listening Q1-13!. <a href='listening_question1_13.html' target='_blank'>Xem tại đây</a>" },

    { date: "25/5/2026", text:  "Thêm đề mới listening Q1-13 mới cập nhật từ câu 192!. <a href='listening_question1_13.html' target='_blank'>Xem tại đây</a>" },

    { date: "08/5/2026", text:  "Thêm câu listening question 15, câu Home schooling!. <a href='listening_meo_cau15_method2.html' target='_blank'>Xem tại đây</a>" },

    { date: "15/4/2026", text:  "Thêm chức năng review đề từ người đã thi. <a href='exam-review.html' target='_blank'>Xem tại đây</a>" },

    { date: "12/4/2026", text:  "Thêm tính năng học mẹo Reading question 5 để dễ nhớ hơn. <a href='reading_question5_meo.html' target='_blank'>Xem tại đây</a>" },

    { date: "12/4/2026", text:  "Listening: Thêm 1 số đề cho question 16 & 17. <a href='listening_question16_17.html' target='_blank'>Xem tại đây</a>" },

    { date: "11/4/2026", text:  "Reading: Phần học theo bộ đề bổ sung thêm bộ đề 12. <a href='reading012.html' target='_blank'>Xem tại đây</a>" },

    { date: "9/4/2026", text:  "Reading part4: Thêm 2 đề Volunteering và Career. <a href='reading_question4.html' target='_blank'>Xem tại đây</a>" },

    { date: "8/4/2026", text:  "Thêm câu 191 phần listening question 1-13. <a href='listening_question1_13.html' target='_blank'>Xem tại đây</a>" },

    { date: "25/3/2026", text: "Listening câu 1-13 thêm 1 câu mới ở cuối cùng (câu 190). <a href='listening_question1_13.html' target='_blank'>Xem tại đây</a>" },

    { date: "24/3/2026", text: "Cập nhật phiên bản mới của chủ đề 'Music Festival (Phiên bản 3)' trong reading part 4 (câu 12). <a href='reading_question4.html' target='_blank'>Xem tại đây</a>" },

    { date: "22/3/2026", text: "Cập nhật phiên bản mới của chủ đề 'The famous singer' trong reading part 2&3 (câu 39). <a href='reading_question2.html' target='_blank'>Xem tại đây</a>" },

    { date: "15/3/2026", text: "Reading part 5 của 3 chủ đề (Cultural Exchange), (Urban Development), (Digital innovation) đã thêm nội dung cho dễ học. <a href='history-capnhatde.html' target='_blank'>Xem chi tiết</a>" },    { date: "6/3/2026", text: "Đề đã ổn định, mọi người yên tâm ôn tập nhé!" },

    { date: "25/2/2026", text: "Chỉnh sửa câu 2&3 reading question câu 11/38 cho chuẩn hơn! (câu 2 bộ đề đọc 006)" },

    { date: "21/1/2026", text: "Hiệu chỉnh câu hỏi reading part1 cho dễ học hơn (key k đổi)" },

    { date: "21/1/2026", text: "Thêm 1 phiên bản của reading part2 & part3 (học theo câu hỏi) đề: The history of transportation (phiên bản 2)" },

    { date: "20/1/2026", text: "Bổ sung mẹo học listening câu 15 hay (mẹo cách 1)" },

    { date: "19/1/2026", text: "Bổ sung 2 đề 12 và 13 reading part 1 (học theo câu hỏi) và thêm đề 11 (học theo bộ đề)" },

    { date: "17/1/2026", text: "Có đề mới Listening part 1–13 (học theo câu hỏi) từ câu 157 trở đi" },

    { date: "16/1/2026", text: "Reading part 5 thêm đề Mountain (phiên bản 2)" }

  ];



  const listEl = document.getElementById("updateList");

  const popup = document.getElementById("updatePopup");

  const closeBtn = document.getElementById("closeUpdatePopup");



  if (!listEl || !popup) return;



  // Đổ dữ liệu + thêm class màu xanh nếu là 21/1/2026

  listEl.innerHTML = updates

    .map(item => {

      const isGreen = item.date === "16/7/2026";

      return `

        <li style="${isGreen ? 'color: green; font-weight: bold;' : ''}">

          <strong>${item.date}</strong> – ${item.text}

        </li>

      `;

    })

    .join("");



  // Đóng popup

  if (closeBtn) {

    closeBtn.addEventListener("click", function () {

      popup.style.display = "none";

    });

  }

});



