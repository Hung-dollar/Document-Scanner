# Xây dựng ứng dụng Scan văn bản

## I. Giới thiệu

- **Bài toán:** Document Scanner là bài toán xử lý ảnh nhằm tự động phát hiện một tài liệu trong ảnh chụp, xác định các góc của tài liệu và biến đổi phối cảnh để tạo ra hình ảnh phẳng, rõ ràng tương tự như tài liệu được quét bằng máy scan.
- Công nghệ này được ứng dụng rộng rãi trong số hóa giấy tờ, lưu trữ tài liệu, quét hóa đơn, bài tập và các loại văn bản bằng điện thoại hoặc máy tính.

## II. Quy trình xử lý ảnh

### 1. Tiền xử lý

- Ảnh ban đầu được biểu diễn bởi một tensor với chiều dài, chiều rộng và 3 kênh màu BGR.
- Do độ phân giải của camera thường rất lớn (vài MP), ta trước tiên cần giảm kích thước ảnh bằng các phương pháp interpolation (`nearest neighbor`, `bilinear`, `bicubic`, `area`) nhằm giảm chi phí tính toán.
- Ngoài ra, phương pháp Canny không cần thông tin về màu để tìm cạnh nên ta có thể đưa ảnh 3 kênh về ảnh grayscale theo công thức:

$$
Gray = 0.299R + 0.587G + 0.114B
$$

- Trong ảnh cũng có thể có nhiễu giống các tín hiệu khác, ta cần dùng các phương pháp làm mờ nhằm lọc bớt noise:
  - Averaging
  - Gaussian
  - Median
  - Bilateral

### 2. Phát hiện giấy

- Trong ảnh sẽ bao gồm cả background và giấy, ta cần xác định phần nào là giấy, phần nào là hình nền.
- Để xác định các cạnh của đa giác chứa giấy, có 2 cách tiếp cận:
  - **Classical CV:** Sử dụng thuật toán Canny edge detection.
  - **Deep Learning:** Sử dụng mạng CNN để dự đoán xác suất pixel thuộc giấy và cắt trên một ngưỡng nhất định để chọn ra các pixel thuộc giấy.

- Từ đầu ra của 2 phương pháp trước, ta chạy thuật toán **Suzuki-Abe border following algorithm** để tìm các contours (các biên của giấy) và chọn ra contour lớn nhất.
- Từ đó, ta có thể xấp xỉ đa giác bao quanh phần giấy bằng thuật toán **Douglas–Peucker**, ra được 4 đỉnh của đa giác.
- Cuối cùng, ta cần sắp xếp 4 đỉnh để biết đỉnh nào thuộc góc nào.

### 3. Thay đổi góc nhìn

- Khi đã có đa giác xấp xỉ, ta có thể tìm phép biến đổi **Homography** bằng cách giải hệ phương trình tuyến tính 8 ẩn.
- Sau khi thực hiện phép biến đổi, ta sẽ có ảnh giấy hướng chính diện.

### 4. Hậu xử lý

- Để tăng độ rõ của ảnh, ta có thể dùng:
  - **CLAHE:** giữ màu.
  - **Adaptive threshold:** tạo ảnh đen trắng kiểu scan.

## III. Triển khai

Dự án sẽ có các thành phần chính:

### Backend

- Sử dụng **FastAPI** để nhận ảnh và trả về ảnh đã xử lý.
- Các thư viện xử lý chính:
  - **OpenCV**
  - **PyTorch**

### Frontend

- Phụ trách giao diện người dùng.
- Công nghệ sử dụng:
  - HTML
  - CSS
  - JavaScript

### Train Model

- Huấn luyện model bằng **PyTorch** trên **Google Colab**.
- Kiến trúc dự kiến sử dụng: **ResNet18**, giúp huấn luyện mạng sâu ổn định.

### Dataset

- Sinh dữ liệu nhân tạo bằng Python.
- Sử dụng các biến đổi **Homography**, thay đổi ánh sáng, thêm nhiễu, ...
- Kết hợp với dataset thực **MIDV500**.
