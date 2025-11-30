import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
import json
import os

class ExamSchedulerBackend:
    """Backend xếp lịch thi - DSatur Algorithm"""
    
    def __init__(self):
        # Dữ liệu cơ bản
        self.subjects = []  # Danh sách môn học/lớp học phần
        self.students_per_subject = defaultdict(set)  # {lớp_hp: {mssv1, mssv2, ...}}
        self.subject_info = {}  # {lớp_hp: {tên, số_sv, ...}}
        
        # Đồ thị xung đột
        self.graph = defaultdict(set)
        self.colors = {}  # {lớp_hp: ca_thi}
        self.num_colors = 0
        
        # Thông tin bổ sung
        self.exam_schedule = {}  # {ca_thi: {ngày, giờ, phòng, ...}}
        self.room_assignments = {}  # {lớp_hp: [phòng1, phòng2, ...]}
        
    def load_excel_file(self, filename: str) -> bool:
        """Đọc file Excel chứa danh sách lớp học phần"""
        try:
            print(f"\n📂 Đang đọc file: {filename}")
            xls = pd.ExcelFile(filename)
            
            if len(xls.sheet_names) == 0:
                print("❌ File Excel không có sheet nào!")
                return False
            
            print(f"📋 Tìm thấy {len(xls.sheet_names)} sheet")
            
            # Reset dữ liệu
            self.subjects.clear()
            self.students_per_subject.clear()
            self.subject_info.clear()
            
            processed_count = 0
            error_count = 0
            
            for idx, sheet_name in enumerate(xls.sheet_names, 1):
                try:
                    # Đọc sheet
                    df_raw = pd.read_excel(filename, sheet_name=sheet_name, header=None)
                    
                    if df_raw.empty:
                        continue
                    
                    # Lấy tên lớp học phần
                    subject_id = None
                    header_row = 0
                    
                    # Kiểm tra dòng 1 có phải tên lớp không
                    if len(df_raw) > 1:
                        first_row = str(df_raw.iloc[0, 0]) if pd.notna(df_raw.iloc[0, 0]) else ""
                        second_row = str(df_raw.iloc[1, 0]) if pd.notna(df_raw.iloc[1, 0]) else ""
                        
                        if (("_" in first_row or len(first_row) > 10) and 
                            ("stt" in second_row.lower() or "số" in second_row.lower())):
                            subject_id = first_row.strip()
                            header_row = 1
                    
                    if not subject_id:
                        subject_id = sheet_name.strip()
                        header_row = 0
                    
                    # Đọc với header đúng
                    df = pd.read_excel(filename, sheet_name=sheet_name, header=header_row)
                    
                    if df.empty:
                        continue
                    
                    df.columns = df.columns.astype(str).str.strip()
                    
                    # Tìm cột MSSV
                    mssv_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(x in col_lower for x in ['mssv', 'ma sv', 'masv', 'mã sv']):
                            mssv_col = col
                            break
                    
                    if not mssv_col:
                        # Tìm cột có nhiều số
                        for col in df.columns:
                            sample = df[col].dropna().astype(str).head(10)
                            if len(sample) > 0:
                                numeric_count = sum(1 for s in sample if s.replace('.', '').isdigit())
                                if numeric_count > len(sample) * 0.7:
                                    mssv_col = col
                                    break
                    
                    if not mssv_col:
                        error_count += 1
                        continue
                    
                    # Lấy danh sách sinh viên
                    students = df[mssv_col].dropna()
                    students = students[students.astype(str).str.strip() != '']
                    students = students.astype(str).str.strip().unique()
                    
                    if len(students) == 0:
                        error_count += 1
                        continue
                    
                    # Lưu thông tin
                    self.subjects.append(subject_id)
                    for student in students:
                        if student and student.lower() not in ['nan', 'none', '']:
                            self.students_per_subject[subject_id].add(student)
                    
                    self.subject_info[subject_id] = {
                        'ten': subject_id,
                        'so_sv': len(students),
                        'sheet_name': sheet_name
                    }
                    
                    processed_count += 1
                    print(f"  [{idx}/{len(xls.sheet_names)}] ✓ {subject_id[:50]}... ({len(students)} SV)")
                    
                except Exception as e:
                    error_count += 1
                    print(f"  [{idx}/{len(xls.sheet_names)}] ❌ {sheet_name}: {str(e)}")
                    continue
            
            print(f"\n✅ Hoàn thành: {processed_count} lớp học phần")
            if error_count > 0:
                print(f"⚠️  Bỏ qua: {error_count} sheet")
            
            return processed_count > 0
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc file: {str(e)}")
            return False
    
    def build_conflict_graph(self):
        """Xây dựng đồ thị xung đột"""
        print("\n🔨 Đang xây dựng đồ thị xung đột...")
        self.graph.clear()
        n = len(self.subjects)
        conflict_count = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                subj1, subj2 = self.subjects[i], self.subjects[j]
                # Kiểm tra có sinh viên chung
                common_students = self.students_per_subject[subj1] & self.students_per_subject[subj2]
                if common_students:
                    self.graph[subj1].add(subj2)
                    self.graph[subj2].add(subj1)
                    conflict_count += 1
        
        print(f"✅ Hoàn thành: {conflict_count} cạnh xung đột")
        return conflict_count
    
    def get_saturation_degree(self, subject: str) -> int:
        """Tính độ bão hòa"""
        used_colors = set()
        for neighbor in self.graph[subject]:
            if neighbor in self.colors:
                used_colors.add(self.colors[neighbor])
        return len(used_colors)
    
    def get_degree(self, subject: str) -> int:
        """Lấy bậc của đỉnh"""
        return len([n for n in self.graph[subject] if n not in self.colors])
    
    def dsatur_coloring(self) -> Dict[str, int]:
        """Thuật toán DSatur"""
        print("\n🎨 Đang chạy thuật toán DSatur...")
        self.colors.clear()
        uncolored = set(self.subjects)
        
        # Bước 1: Chọn môn có bậc cao nhất
        if uncolored:
            first_subject = max(uncolored, key=lambda s: len(self.graph[s]))
            self.colors[first_subject] = 1
            uncolored.remove(first_subject)
            print(f"  Khởi tạo: {first_subject[:40]}... -> Ca 1")
        
        # Bước 2: Lặp
        step = 2
        while uncolored:
            # Chọn môn có độ bão hòa cao nhất
            next_subject = max(uncolored, 
                             key=lambda s: (self.get_saturation_degree(s), 
                                          self.get_degree(s)))
            
            # Tìm màu nhỏ nhất khả dụng
            used_colors = {self.colors[n] for n in self.graph[next_subject] 
                          if n in self.colors}
            
            color = 1
            while color in used_colors:
                color += 1
            
            self.colors[next_subject] = color
            uncolored.remove(next_subject)
            
            if step <= 5 or len(uncolored) % 10 == 0:
                print(f"  Bước {step}: {next_subject[:40]}... -> Ca {color}")
            
            step += 1
        
        self.num_colors = max(self.colors.values()) if self.colors else 0
        print(f"✅ Hoàn thành: Cần {self.num_colors} ca thi")
        return self.colors
    
    def display_statistics(self):
        """Hiển thị thống kê"""
        print("\n" + "="*70)
        print("📊 THỐNG KÊ HỆ THỐNG XẾP LỊCH THI")
        print("="*70)
        
        total_students = len(set().union(*self.students_per_subject.values()))
        total_enrollments = sum(len(students) for students in self.students_per_subject.values())
        
        print(f"\n📚 Tổng số lớp học phần: {len(self.subjects)}")
        print(f"👨‍🎓 Tổng số sinh viên: {total_students}")
        print(f"📝 Tổng số đăng ký: {total_enrollments}")
        print(f"🎯 Số ca thi cần thiết: {self.num_colors}")
        print(f"🔗 Số xung đột: {sum(len(neighbors) for neighbors in self.graph.values()) // 2}")
        
        if self.colors:
            # Phân bố môn theo ca
            session_dist = defaultdict(int)
            for session in self.colors.values():
                session_dist[session] += 1
            
            print(f"\n📅 Phân bố lớp học phần theo ca:")
            for session in sorted(session_dist.keys()):
                bar = "█" * min(session_dist[session], 50)
                print(f"   Ca {session:2d}: {bar} ({session_dist[session]} lớp)")
            
            # Trung bình môn/sinh viên
            avg_subjects = total_enrollments / total_students if total_students > 0 else 0
            print(f"\n📈 Trung bình lớp/sinh viên: {avg_subjects:.2f}")
        
        print("="*70)
    
    def display_schedule_by_session(self, session: int = None):
        """Hiển thị lịch thi theo ca"""
        if not self.colors:
            print("⚠️  Chưa có lịch thi. Vui lòng chạy thuật toán trước!")
            return
        
        print("\n" + "="*70)
        if session:
            print(f"📅 LỊCH THI - CA {session}")
        else:
            print("📅 LỊCH THI TỔNG HỢP")
        print("="*70)
        
        # Sắp xếp theo ca
        sorted_schedule = sorted(self.colors.items(), key=lambda x: (x[1], x[0]))
        
        current_session = None
        for subject, sess in sorted_schedule:
            if session and sess != session:
                continue
            
            if sess != current_session:
                current_session = sess
                print(f"\n{'─'*70}")
                print(f"⏰ CA THI {sess}")
                print(f"{'─'*70}")
            
            num_students = len(self.students_per_subject[subject])
            print(f"  📖 {subject[:60]}")
            print(f"     👥 Số SV: {num_students}")
    
    def display_student_conflicts(self, student_id: str):
        """Hiển thị lịch thi của sinh viên"""
        print(f"\n{'='*70}")
        print(f"👨‍🎓 LỊCH THI SINH VIÊN: {student_id}")
        print(f"{'='*70}")
        
        student_subjects = []
        for subject, students in self.students_per_subject.items():
            if student_id in students:
                session = self.colors.get(subject, 'N/A')
                student_subjects.append((subject, session))
        
        if not student_subjects:
            print(f"⚠️  Không tìm thấy sinh viên {student_id}")
            return
        
        # Sắp xếp theo ca
        student_subjects.sort(key=lambda x: (x[1] if isinstance(x[1], int) else 999, x[0]))
        
        print(f"\n📚 Tổng số lớp: {len(student_subjects)}")
        print(f"\n{'STT':<5} {'Ca':<8} {'Lớp học phần':<50}")
        print("─"*70)
        
        for idx, (subject, session) in enumerate(student_subjects, 1):
            session_str = f"Ca {session}" if isinstance(session, int) else "N/A"
            print(f"{idx:<5} {session_str:<8} {subject[:50]}")
    
    def export_to_csv(self, filename: str = "lich_thi_output.csv"):
        """Xuất lịch thi ra file CSV"""
        if not self.colors:
            print("⚠️  Chưa có lịch thi để xuất!")
            return False
        
        try:
            data = []
            sorted_schedule = sorted(self.colors.items(), key=lambda x: (x[1], x[0]))
            
            for idx, (subject, session) in enumerate(sorted_schedule, 1):
                num_students = len(self.students_per_subject[subject])
                data.append({
                    'STT': idx,
                    'Ca_thi': session,
                    'Lop_hoc_phan': subject,
                    'So_sinh_vien': num_students
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ Đã xuất lịch thi: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi xuất file: {str(e)}")
            return False
    
    def export_student_schedule_csv(self, filename: str = "lich_thi_sinh_vien.csv"):
        """Xuất lịch thi sinh viên ra CSV"""
        if not self.colors:
            print("⚠️  Chưa có lịch thi để xuất!")
            return False
        
        try:
            data = []
            for subject, students in self.students_per_subject.items():
                session = self.colors.get(subject, 'N/A')
                for student in students:
                    data.append({
                        'MSSV': student,
                        'Lop_hoc_phan': subject,
                        'Ca_thi': session
                    })
            
            df = pd.DataFrame(data)
            df = df.sort_values(['MSSV', 'Ca_thi', 'Lop_hoc_phan'])
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ Đã xuất lịch sinh viên: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi xuất file: {str(e)}")
            return False


def main():
    """Chương trình chính"""
    scheduler = ExamSchedulerBackend()
    
    print("="*70)
    print("🎓 HỆ THỐNG XẾP LỊCH THI - THUẬT TOÁN DSATUR")
    print("="*70)
    
    while True:
        print("\n" + "─"*70)
        print("📋 MENU CHÍNH:")
        print("─"*70)
        print("1. 📂 Tải file Excel (danh sách lớp học phần)")
        print("2. 🎨 Chạy thuật toán DSatur")
        print("3. 📊 Xem thống kê")
        print("4. 📅 Xem lịch thi theo ca")
        print("5. 👨‍🎓 Tra cứu lịch thi sinh viên")
        print("6. 💾 Xuất lịch thi (CSV)")
        print("7. 💾 Xuất lịch sinh viên (CSV)")
        print("0. 🚪 Thoát")
        print("─"*70)
        
        choice = input("\n👉 Chọn chức năng (0-7): ").strip()
        
        if choice == '1':
            filename = input("\n📁 Nhập đường dẫn file Excel: ").strip()
            if os.path.exists(filename):
                scheduler.load_excel_file(filename)
            else:
                print(f"❌ File không tồn tại: {filename}")
        
        elif choice == '2':
            if not scheduler.subjects:
                print("⚠️  Vui lòng tải file dữ liệu trước!")
            else:
                scheduler.build_conflict_graph()
                scheduler.dsatur_coloring()
        
        elif choice == '3':
            if not scheduler.subjects:
                print("⚠️  Chưa có dữ liệu!")
            else:
                scheduler.display_statistics()
        
        elif choice == '4':
            if not scheduler.colors:
                print("⚠️  Chưa có lịch thi. Vui lòng chạy thuật toán trước!")
            else:
                session_input = input("\n🔍 Nhập số ca (Enter = xem tất cả): ").strip()
                if session_input:
                    try:
                        session = int(session_input)
                        scheduler.display_schedule_by_session(session)
                    except:
                        print("❌ Số ca không hợp lệ!")
                else:
                    scheduler.display_schedule_by_session()
        
        elif choice == '5':
            student_id = input("\n🔍 Nhập MSSV: ").strip()
            if student_id:
                scheduler.display_student_conflicts(student_id)
            else:
                print("❌ MSSV không được để trống!")
        
        elif choice == '6':
            filename = input("\n💾 Tên file xuất (Enter = lich_thi_output.csv): ").strip()
            if not filename:
                filename = "lich_thi_output.csv"
            scheduler.export_to_csv(filename)
        
        elif choice == '7':
            filename = input("\n💾 Tên file xuất (Enter = lich_thi_sinh_vien.csv): ").strip()
            if not filename:
                filename = "lich_thi_sinh_vien.csv"
            scheduler.export_student_schedule_csv(filename)
        
        elif choice == '0':
            print("\n👋 Cảm ơn đã sử dụng! Tạm biệt!")
            break
        
        else:
            print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
    