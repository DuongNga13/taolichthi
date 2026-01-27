# 📚 Xếp Lịch Thi Thông Minh - DSatur Pro

Hệ thống xếp lịch thi tự động sử dụng thuật toán **DSatur (Degree of Saturation)** để tối ưu hóa lịch thi, tránh xung đột thời gian cho sinh viên.

<img width="1920" height="1018" alt="image" src="https://github.com/user-attachments/assets/17f09bf0-bd71-4988-88de-4cec6d205c77" />
<img width="1920" height="1017" alt="image" src="https://github.com/user-attachments/assets/b535a611-d21e-4828-9c20-d2442be186cf" />
<img width="1920" height="1016" alt="image" src="https://github.com/user-attachments/assets/0b65d774-402a-4a93-b741-9014b14b4bce" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/29e9b1cf-8bda-4786-aeba-874f96eb523c" />


##  Tính năng chính

-  **Thuật toán DSatur**: Tự động xếp lịch thi tối ưu, giảm thiểu số ca thi
-  **Nhập dữ liệu linh hoạt**: Hỗ trợ file Excel với nhiều định dạng khác nhau
-  **Kiểm tra xung đột**: Phát hiện và cảnh báo khi sinh viên bị trùng ca thi
-  **Nhiều chế độ xem**: Lịch theo ngày, theo ca, theo sinh viên
-  **Trực quan hóa**: Vẽ đồ thị xung đột môn học
-  **Xuất Excel**: Xuất lịch thi ra file Excel với nhiều sheet chi tiết
-  **Giao diện thân thiện**: UI hiện đại, dễ sử dụng

## Giao diện

Giao diện được thiết kế với Tkinter, bao gồm:
- **Sidebar**: Nhập dữ liệu, cấu hình, thống kê
- **Tabs chính**: 
  -  Lịch thi theo ngày
  -  Lịch thi theo ca
  -  Lịch thi sinh viên (có tìm kiếm)
  -  Đồ thị xung đột
  -  Xuất file và kiểm tra

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.7 trở lên
- pip (Python package manager)

### Cài đặt các thư viện cần thiết

```bash
pip install pandas openpyxl networkx matplotlib
```

Hoặc sử dụng file `requirements.txt`:

```bash
pip install -r requirements.txt
```

### File requirements.txt

```
pandas>=1.3.0
openpyxl>=3.0.0
networkx>=2.6.0
matplotlib>=3.4.0
```

## 📖 Hướng dẫn sử dụng

### 1. Chuẩn bị dữ liệu

Tạo file Excel với cấu trúc:
- **Mỗi sheet** = 1 môn học
- **Mỗi dòng** = 1 sinh viên đăng ký môn đó
- **Các cột cần thiết**: Mã SV (hoặc MSSV), Họ Tên (tùy chọn)

Ví dụ cấu trúc file Excel:

```
Sheet "Toán Cao Cấp 1":
| Mã SV      | Họ Tên           |
|-----------|------------------|
| 20210001  | Nguyễn Văn A    |
| 20210002  | Trần Thị B      |
...

Sheet "Vật Lý Đại Cương":
| Mã SV      | Họ Tên           |
|-----------|------------------|
| 20210001  | Nguyễn Văn A    |
| 20210003  | Lê Văn C        |
...
```

### 2. Chạy ứng dụng

```bash
python frontend.py
```

### 3. Các bước thực hiện

1. **Chọn file Excel**: Click "CHỌN FILE EXCEL" và chọn file dữ liệu
2. **Cấu hình**:
   - Số ca tối đa mỗi ngày (1-10)
   - Ngày bắt đầu thi
3. **Chạy DSatur**: Click "CHẠY DSATUR" để xếp lịch tự động
4. **Xem kết quả**: Chuyển qua các tab để xem lịch thi
5. **Kiểm tra**: Tab "Export & Kiểm tra" để xem có xung đột không
6. **Xuất file**: Click "XUẤT FILE EXCEL" để lưu kết quả

## 🔧 Cấu trúc dự án

```
exam-scheduler/
│
├── frontend.py                 # Giao diện Tkinter
├── backend.py                  # Logic và thuật toán DSatur
├── requirements.txt            # Thư viện cần thiết
├── README.md                   # File này
│
├── data/                       # Thư mục chứa dữ liệu (tùy chọn)
│   └── DS_các_lớp_học_phần.xlsx
│
└── output/                     # Thư mục xuất file (tự động tạo)
    └── lich_thi_*.xlsx
```

## 🧮 Thuật toán DSatur

**DSatur (Degree of Saturation)** là thuật toán tô màu đồ thị heuristic:

1. **Khởi tạo**: Tính bậc (degree) của mỗi đỉnh
2. **Lặp**: Chọn đỉnh có độ bão hòa cao nhất (số màu khác nhau của các đỉnh kề)
3. **Tô màu**: Gán màu nhỏ nhất chưa được sử dụng bởi các đỉnh kề
4. **Cập nhật**: Cập nhật độ bão hòa của các đỉnh kề

### Ánh xạ vào bài toán xếp lịch:
- **Đỉnh** = Môn học
- **Cạnh** = Có sinh viên học cả 2 môn (xung đột)
- **Màu** = Ca thi
- **Mục tiêu**: Tối thiểu hóa số màu (số ca thi)

## 📊 Output

Khi xuất file Excel, bạn sẽ nhận được file với 4 sheet:

1. **Lich_Theo_Ngay**: Lịch thi theo từng ngày và ca
2. **Lich_Theo_Ca**: Danh sách môn thi theo từng ca
3. **Lich_SinhVien**: Lịch thi chi tiết của từng sinh viên
4. **ThongTin_TomTat**: Thống kê tổng quan

## 🎓 Các trường hợp sử dụng

- Trường đại học, cao đẳng xếp lịch thi cuối kỳ
- Trung tâm đào tạo xếp lịch kiểm tra
- Tổ chức kỳ thi tuyển sinh
- Bất kỳ tổ chức nào cần xếp lịch có ràng buộc xung đột

## ⚠️ Lưu ý

- File Excel cần có định dạng `.xlsx` hoặc `.xls`
- Mã sinh viên phải là số nguyên
- Tên sheet nên đặt là tên môn học rõ ràng
- Nên có cột "Họ Tên" để dễ kiểm tra, nhưng không bắt buộc
- Số ca/ngày nên chọn hợp lý (thường là 2-3)

## 🐛 Xử lý lỗi

### Lỗi "Không tìm thấy dữ liệu hợp lệ"
- Kiểm tra định dạng file Excel
- Đảm bảo có cột "Mã SV" hoặc "MSSV"
- Kiểm tra dữ liệu không bị trống

### Lỗi "CÓ LỖI TRÙNG CA"
- Đây là cảnh báo, không phải lỗi
- Xem lại cấu hình số ca/ngày
- Có thể cần tăng số ca hoặc số ngày thi

### Lỗi không hiển thị đồ thị
- Cài đặt: `pip install networkx matplotlib`
- Chức năng vẫn hoạt động bình thường, chỉ không có đồ thị trực quan


## 📝 Roadmap

- [ ] Thêm thuật toán tối ưu khác (Tabu Search, Genetic Algorithm)
- [ ] Hỗ trợ ràng buộc phòng thi
- [ ] Xuất PDF lịch thi
- [ ] API REST để tích hợp với hệ thống khác
- [ ] Web interface (Flask/Django)
- [ ] Tối ưu hiệu suất cho dữ liệu lớn (>10,000 sinh viên)

## 👨‍💻 Tác giả

- Dương Thị Nga

## 🙏 Cảm ơn

- Thuật toán DSatur được phát triển bởi Daniel Brélaz (1979)
- Cảm ơn cộng đồng Python vì các thư viện mã nguồn mở

## 📧 Liên hệ

Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ:

- Email: duongnga1326@gmail.com
- GitHub: [Dương Nga](https://github.com/DuongNga13)

---

⭐ **Nếu project này hữu ích, hãy cho một star nhé!** ⭐
