Bài 1. Máy tính đơn giản (Simple Calculator GUI)
Đầu bài:
Viết chương trình máy tính có giao diện GUI cho phép người dùng nhập hai số và chọn phép toán +, –, ×, ÷ để tính toán.
Đầu vào – đầu ra:
•	Đầu vào: Hai số thực (qua ô Entry), và lựa chọn phép toán (qua nút hoặc menu Radio).
•	Đầu ra: Kết quả tính trên GUI (Label).
Tính năng yêu cầu:
•	Nhập số, kiểm tra lỗi (không phải số, chia 0).
•	Cập nhật kết quả ngay khi nhấn nút “Tính”.
•	Cho phép reset (xóa cả 2 ô nhập).
•	Bắt ngoại lệ với hộp thoại thông báo khi lỗi .
Kiểm tra & kết quả mẫu:
•	Nhập 3.5 và 2, chọn “×” → Kết quả: 7.0
•	Nhập “a” và 1 → Hộp thoại: “Vui lòng nhập số hợp lệ.”
Các bước triển khai:
1.	Thiết kế layout với Grid: hai Entry, nhóm Radio/OptionMenu, nút “Tính” và Label kết quả.
2.	Viết hàm calculate() đọc giá trị, chuyển qua float, xử lý phép toán, bắt ValueError và ZeroDivisionError.
3.	Gắn sự kiện nút “Tính” vào calculate().
4.	Test với bộ đầu vào chuẩn và sai.
