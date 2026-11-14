# Refined Mockups — khối "Dự đoán"

Nguồn: `../../ideation/rough-mockups/{wireframes,user-flow}.md`, `../user-stories/stories.md`, `../requirements-analysis/requirements.md`, `../practices-discovery/team-practices.md`, `assets/style.css`.

## Nguyên tắc: không phát minh hệ thống thứ hai

Tab thứ năm đã có hệ thống riêng và nó đang chạy: `--space-1…7`, `--radius-sm/…/pill`, `--shadow-xs/sm/md`, ba họ font, và bảy token màu chữ/nền. Khối dự đoán **dùng lại đúng** những thứ đó. Bất cứ chỗ nào tài liệu này đề xuất một giá trị mới, đó là dấu hiệu tài liệu sai.

## Bố cục cuối

```
<section aria-label="Dự đoán">                     ← --space-6 trên, --space-5 dưới
  <header>
    <h3>Dự đoán</h3>                               ← H3, --font-display, --text
    <p>Dự đoán cho một dòng hàng — một món hàng trong một đơn, có người bán riêng.</p>
  </header>                                          ← câu này BẮT BUỘC, --text-2

  <fieldset>                                         ← --surface, --radius, --shadow-sm
    <legend>Thông tin đầu vào</legend>               ← H4
    lưới 2 cột ở ≥ 1024px, 1 cột ở < 1024px
    ô 1 Bang người bán        ô 2 Bang người mua
    ô 3 Ngày đặt hàng         ô 4 Giá món hàng
    ô 5 Số ngày đặt → duyệt   ô 6 Số ngày duyệt → bàn giao
    ô 7 Số lượng món
    ── nhóm "Trường còn lại (mặc định, sửa được)" ──
    ô 8 payment_type        ô 9 payment_installments
    ô 10 has_items          ô 11 has_payment
  </fieldset>

**Mười một điều khiển**, không phải bảy: bảy trường lõi cộng bốn trường mặc định **có điều khiển sửa được** (FR3.1, AC2.2.2). Bản nháp đầu của tài liệu này vẽ bốn trường đó thành câu chú thích — mâu thuẫn với `stories.md` và `requirements.md`, đã sửa.

  <actions>                                          ← --space-4 trên
    [Dự đoán]  nút chính, --accent / --accent-hover, --radius-sm
    [Đặt lại mặc định]  nút phụ, viền --border-strong, nền --surface
  </actions>

  <section aria-label="Kết quả">                     ← --space-6 trên
    <h4>Kết quả</h4>
    <p class="verdict">0,37 · dưới ngưỡng 0,40 · KHÔNG cảnh báo</p>   ← 18px, --text
    <p class="verdict">0,61 · trên ngưỡng 0,40 · CẢNH BÁO: dòng hàng này có nguy cơ trễ</p>
    <p>Ba đóng góp lớn nhất (log-odds, không phải tổng):</p>          ← --text-2
    <ul> 3 dòng, mỗi dòng: dấu + tên trường + giá trị người dùng nhập + số log-odds
  </section>
</section>
```

## Kích thước và nhịp

| Thành phần | Giá trị | Token |
|---|---|---|
| Khoảng cách giữa các ô trong lưới | 16px | `--space-4` |
| Padding của `fieldset` | 24px | `--space-5` |
| Bán kính `fieldset` | 12px | `--radius` |
| Bóng `fieldset` | bóng nhẹ | `--shadow-sm` |
| Cao ô nhập | **38px** cho dropdown (`dash-dropdown` đang dùng giá trị này), 36px cho ô số/ngày | đo trên `.dash-dropdown` đang chạy, không đoán |
| Cỡ chữ nhãn | 13px | `--text-2` (không dùng `--text-3`: chỉ 3,85:1) |
| Cỡ chữ kết quả | 18px | `--text` |
| Dòng đóng góp | 14px | `--text-2` |

## Màu: chỉ dùng cái đã có

| Vai | Token | Ghi chú |
|---|---|---|
| Nền khối | `--surface` | trắng, đúng như ba mục kia |
| Nền phụ (dòng mặc định) | `--surface-sunken` | phân biệt bằng nền, không bằng chữ mờ |
| Chữ chính | `--text` | |
| Chữ phụ | `--text-2` | bắt buộc cho mọi chữ < 16px |
| Viền ô nhập | `--border` / `--border-strong` khi focus | |
| Nút chính | `--accent` → `--accent-hover` | cùng nút "chạy" của tab Tích hợp |
| **Kết quả cảnh báo** | **không đổi màu** | phân biệt bằng **chữ** và bằng vị trí so với ngưỡng |

**Đây là quyết định có chủ đích, không phải thiếu sót:** không dùng `--danger` cho kết quả cảnh báo. Lý do: (a) `--danger` là đỏ lỗi hệ thống, không phải đỏ "nguy cơ nghiệp vụ"; (b) người mù màu đỏ-lục không phân biệt được; (c) đợt này đã chốt không thêm token màu. Chữ `CẢNH BÁO` in hoa là tín hiệu.

## Bố cục theo bề rộng

| Bề rộng | Lưới biểu mẫu | Ghi chú |
|---|---|---|
| < 1024px | 1 cột | mỗi ô một dòng, nhãn trên ô |
| ≥ 1024px | 2 cột | ô 7 (số lượng món) chiếm nửa hàng cuối |
| ≥ 1440px | 2 cột, `fieldset` tối đa 720px | không kéo giãn để lấp chỗ trống |

Mốc 1280px là mốc đã kiểm ở NFR5.4 của đợt trước; bố cục phải đứng vững ở đó.

## Định dạng số

| Con số | Định dạng | Ví dụ |
|---|---|---|
| Xác suất | 2 chữ số thập phân, dấu phẩy thập phân | `0,37` |
| Ngưỡng | như trong báo cáo | `0,40` |
| Đóng góp log-odds | 2 chữ số thập phân, **luôn có dấu** | `+0,18`, `−0,04` |
| Giá trị người dùng nhập (trong dòng đóng góp) | theo định dạng Brazil của `formatting.py` | `129,90` |

`format_percent` **không** nhân 100 — nếu hiện phần trăm thì người gọi tự nhân. Khối này hiện xác suất dạng phân số, không dạng phần trăm, nên không gọi hàm đó.

## Điều mockup này **không** làm

Không biểu đồ. Không icon cho ba đóng góp. Không thanh tiến trình cho xác suất — một thanh sẽ gợi ý một thang đo tuyệt đối mà xác suất không có. Không màu cho kết quả. Không bo tròn lớn hơn `--radius-lg`.
