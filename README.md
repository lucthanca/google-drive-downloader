# google-driver-downloader
Google Drive Downloader

![alt text](https://github.com/udav-haui/google-drive-downloader/blob/master/2021-07-25_02-09.png?raw=true)

---
## Yêu cầu hệ thống

- Môi trường chạy python 3.x
- ID của folder/file muốn tải
- Có mạng
---
## Bắt Đầu

* ##### Bước 1
    - Clone repo hoặc tải zip về máy 
    - Cài đặt python lên máy. [(tìm ở đây)]( https://python.org)
* ##### Bước 2
  - Cài `pip`, trỏ đường dẫn CMD vào thư mục của tool rồi chạy lệnh
    
    `py get-pip.py`
  - Sau khi cài `pip` xong thì tiến hành cài các thư viện cần thiết
    ```apacheconf
    pip install --upgrade google-api-python-client colorama termcolor oauth2client alive-progress yaspin
    ```
* ##### Bước 3
  - Lấy `credentials.json` để có access vào các files/folders được chia sẻ
  - Cách lấy (tham khảo thêm google):
    1. [Tạo 1 app google](https://console.cloud.google.com/)
    2. Tạo xong app thì vào [APIs and Services](https://console.cloud.google.com/apis/library) sau đó thêm Google Drive API vào
    3. Sau đó vào [tạo DESKTOP App credentials](https://console.cloud.google.com/apis/credentials)
    4. Tạo xong thì ở phần OAuth 2.0 Client IDs sẽ có hiển thị 1 bản ghi chứa credentials, chọn vào phần tải về để tải về, rồi đổi tên thành credentials.json và copy vào thư mục của tool.
* ##### Bước 4
  - Sau đó mở cmd tại thư mục tool, rồi chạy lệnh
    ```apacheconf
    py .\download.py
    ``` 
  - Tiếp theo thì làm theo hướng dẫn hiển trị trên cmd
### Cách sử dụng

Chạy lệnh `py .\download.py` và làm theo hướng dẫn

```apacheconf
$> py .\download.py
```
