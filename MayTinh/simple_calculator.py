import tkinter as tk
from tkinter import messagebox, ttk
import ctypes
# Thiết lập hỗ trợ DPI cao cho màn hình độ phân giải cao
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Tạo lớp MayTinhDonGian để quản lý giao diện 
class MayTinhDonGian:
    def __init__(self, cua_so_chinh):
        self.cua_so_chinh = cua_so_chinh
        self.cua_so_chinh.title("Máy Tính Đơn Giản")
        self.cua_so_chinh.geometry("450x500")  # Kích thước cửa sổ
        self.cua_so_chinh.resizable(False, False)  # Không cho phép thay đổi kích thước
        self.cua_so_chinh.configure(bg="#e0f7fa")  # Màu nền xanh nhạt
        
        # Thiết lập style cho các thành phần giao diện
        self.thiet_lap_style()
        
        # Tạo khung chính chứa tất cả các thành phần
        self.khung_chinh = ttk.Frame(cua_so_chinh, padding=20, style="Main.TFrame")
        self.khung_chinh.grid(row=0, column=0, sticky="nsew")
        
        # Cấu hình grid để khung chính mở rộng theo cửa sổ
        self.cua_so_chinh.grid_rowconfigure(0, weight=1)
        self.cua_so_chinh.grid_columnconfigure(0, weight=1)
        
        # Tạo các thành phần giao diện
        self.tao_o_nhap_so_thu_nhat()
        self.tao_o_nhap_so_thu_hai()
        self.tao_vung_chon_phep_toan()
        self.tao_cac_nut_chuc_nang()
        self.tao_vung_hien_thi_ket_qua()
    
    # Thiết lập style cho các thành phần giao diện
    def thiet_lap_style(self):
        style = ttk.Style()
        # Cấu hình style cho khung chính
        style.configure("TLabel", font=("Times New Roman", 14, "bold"), background="#e0f7fa")   # Style cho nhãn (Label)
        style.configure("TButton", font=("Times New Roman", 13, "bold"), padding=10)    # Style cho nút (Button)
        style.configure("TRadiobutton", font=("Times New Roman", 16, "bold"), background="#fdfefe")     # Style cho nút radio
    
    def tao_o_nhap_so_thu_nhat(self):
        # Nhãn "Số thứ nhất"
        self.nhan_so_1 = ttk.Label(self.khung_chinh, text="Số thứ nhất:", foreground="#e91e63")
        self.nhan_so_1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        # Ô nhập số thứ nhất
        self.o_nhap_so_1 = ttk.Entry(self.khung_chinh, font=("Times New Roman", 14), width=20)
        self.o_nhap_so_1.grid(row=0, column=1, padx=10, pady=10)
    
    # Tạo ô nhập số thứ hai và nhãn tương ứng
    def tao_o_nhap_so_thu_hai(self):
        # Nhãn "Số thứ hai"
        self.nhan_so_2 = ttk.Label(self.khung_chinh, text="Số thứ hai:", foreground="#e91e63")
        self.nhan_so_2.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        # Ô nhập số thứ hai
        self.o_nhap_so_2 = ttk.Entry(self.khung_chinh, font=("Times New Roman", 14), width=20)
        self.o_nhap_so_2.grid(row=1, column=1, padx=10, pady=10)
    
    # Tạo vùng chọn phép toán với các nút radio
    def tao_vung_chon_phep_toan(self):
        # Nhãn "Phép toán"
        self.nhan_phep_toan = ttk.Label(self.khung_chinh, text="Phép toán:", foreground="#000")
        self.nhan_phep_toan.grid(row=2, column=0, padx=10, pady=10, sticky="nw")
        
        # Khung chứa các nút radio phép toán
        self.khung_phep_toan = tk.Frame(self.khung_chinh, bg="#fdfefe")
        self.khung_phep_toan.grid(row=2, column=1, padx=10, pady=10)
        
        # Biến lưu phép toán được chọn (mặc định là cộng)
        self.phep_toan_duoc_chon = tk.StringVar(value="+")
        
        # Danh sách các phép toán và màu sắc tương ứng
        cac_phep_toan = [
            ("+", "#10e96a"), 
            ("-", "#e32611"),   
            ("×", "#ef1bba"),
            ("÷", "#cea80e")  
        ]
        
        # Tạo nút radio cho từng phép toán
        for chi_so, (ky_hieu_phep_toan, mau_sac) in enumerate(cac_phep_toan):
            nut_radio = tk.Radiobutton(
                self.khung_phep_toan, 
                text=ky_hieu_phep_toan, 
                variable=self.phep_toan_duoc_chon, 
                value=ky_hieu_phep_toan,
                font=("Times New Roman", 25, "bold"), 
                bg="#fdfefe", 
                fg=mau_sac,
                selectcolor="#fdfefe",  # Màu nền khi chọn
                indicatoron=True
            )
            # Sắp xếp nút radio theo dạng lưới 2x2
            nut_radio.grid(row=chi_so // 2, column=chi_so % 2, padx=15, pady=5)
    
    # Tạo các nút chức năng: Tính và Reset
    def tao_cac_nut_chuc_nang(self):
        # Khung chứa các nút chức năng
        self.khung_cac_nut = tk.Frame(self.khung_chinh, bg="#e0f7fa")
        self.khung_cac_nut.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Nút Tính - thực hiện phép tính
        self.nut_tinh = ttk.Button(self.khung_cac_nut, text="Tính", command=self.thuc_hien_phep_tinh)
        self.nut_tinh.grid(row=0, column=0, padx=20)
        
        # Nút Reset - xóa dữ liệu và reset về trạng thái ban đầu
        self.nut_reset = ttk.Button(self.khung_cac_nut, text="Reset", command=self.reset)
        self.nut_reset.grid(row=0, column=1, padx=20)
    
    # Tạo vùng hiển thị kết quả phép tính
    def tao_vung_hien_thi_ket_qua(self):
        self.nhan_ket_qua = ttk.Label(
            self.khung_chinh, 
            text="Kết quả: ", 
            foreground="#000000",
            font=("Times New Roman", 14, "bold"), 
            background="#ffe0b2" 
        )
        self.nhan_ket_qua.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")

    #Thực hiện phép tính dựa trên dữ liệu nhập vào và phép toán được chọnXử lý các lỗi có thể xảy ra (nhập sai định dạng, chia cho 0)
    def thuc_hien_phep_tinh(self): 
        try:
            # Lấy giá trị từ ô nhập và chuyển đổi sang số thực
            so_thu_nhat = float(self.o_nhap_so_1.get())
            so_thu_hai = float(self.o_nhap_so_2.get())
            phep_toan = self.phep_toan_duoc_chon.get()
            
            # Thực hiện phép tính dựa trên phép toán được chọn
            if phep_toan == "+":
                ket_qua = so_thu_nhat + so_thu_hai
            elif phep_toan == "-":
                ket_qua = so_thu_nhat - so_thu_hai
            elif phep_toan == "×":
                ket_qua = so_thu_nhat * so_thu_hai
            elif phep_toan == "÷":
                if so_thu_hai == 0: # Kiểm tra chia cho 0
                    raise ZeroDivisionError("Không thể chia cho 0!")
                ket_qua = so_thu_nhat / so_thu_hai 
            
            self.nhan_ket_qua.config(text=f"Kết quả: {ket_qua:.2f}")    # Hiển thị kết quả (làm tròn 2 chữ số thập phân)
            
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!", parent=self.cua_so_chinh)
            self.reset()
        except ZeroDivisionError as loi_chia_0:
            messagebox.showerror("Lỗi", str(loi_chia_0), parent=self.cua_so_chinh)
            self.reset()

    # Phương thức reset - xóa dữ liệu và đặt lại trạng thái ban đầu
    def reset(self):
        self.o_nhap_so_1.delete(0, tk.END)  
        self.o_nhap_so_2.delete(0, tk.END)  
        self.phep_toan_duoc_chon.set("+")   
        self.nhan_ket_qua.config(text="Kết quả: ")  

# Chương trình chính - tạo cửa sổ và khởi chạy ứng dụng máy tính
def main():
    cua_so_chinh = tk.Tk()  # Tạo cửa sổ chính
    style = ttk.Style() # Cấu hình style cho khung chính
    style.configure("Main.TFrame", background="#e0f7fa")
    ung_dung_may_tinh = MayTinhDonGian(cua_so_chinh)    # Khởi tạo ứng dụng máy tính 
    cua_so_chinh.mainloop() # Chạy vòng lặp chính của giao diện

# Điểm khởi đầu của chương trình
if __name__ == "__main__":
    main()