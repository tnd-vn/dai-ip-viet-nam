# Dải IP Việt Nam - Danh sách địa chỉ IP Việt Nam (IPv4 + IPv6) cập nhật hàng tuần

**Tổng hợp dải IP Việt Nam** đầy đủ, đã gộp gọn, sẵn sàng dùng để **whitelist IP Việt Nam và chặn toàn bộ IP nước ngoài** (deny all) trên máy chủ, VPS, tường lửa, router. Danh sách được **tổng hợp bởi [TND](https://www.tnd.vn)** và tự động cập nhật mỗi thứ Hai.

| | Số lượng |
|---|---|
| Dải IPv4 Việt Nam (đã gộp) | **1.270** dải CIDR |
| Tổng địa chỉ IPv4 Việt Nam | **~16,5 triệu** địa chỉ |
| Dải IPv6 Việt Nam (đã gộp) | **949** dải CIDR |

> Số liệu tại thời điểm 30/10/2026. Xem số mới nhất trong [`meta.json`](meta.json).

## Mục lục

- [Tải danh sách IP Việt Nam](#tải-danh-sách-ip-việt-nam)
- [Khi nào nên whitelist IP Việt Nam?](#khi-nào-nên-whitelist-ip-việt-nam)
- [Cách chặn IP nước ngoài, chỉ cho phép IP Việt Nam](#cách-chặn-ip-nước-ngoài-chỉ-cho-phép-ip-việt-nam)
  - [iptables + ipset (Linux)](#1-iptables--ipset-linux)
  - [nftables (Linux)](#2-nftables-linux)
  - [UFW (Ubuntu)](#3-ufw-ubuntu)
  - [Nginx](#4-nginx)
  - [Apache / .htaccess](#5-apache--htaccess)
  - [CSF Firewall (cPanel, DirectAdmin)](#6-csf-firewall-cpanel-directadmin)
  - [MikroTik RouterOS](#7-mikrotik-routeros)
  - [Windows Server / Remote Desktop](#8-windows-server--remote-desktop-rdp)
  - [Cloudflare](#9-cloudflare)
- [Lưu ý quan trọng trước khi chặn IP nước ngoài](#lưu-ý-quan-trọng-trước-khi-chặn-ip-nước-ngoài)
- [Câu hỏi thường gặp](#câu-hỏi-thường-gặp)
- [Góp ý, bổ sung](#góp-ý-bổ-sung)

## Tải danh sách IP Việt Nam

Mỗi file là danh sách **dải IP Việt Nam** dạng CIDR, mỗi dòng một dải:

| File | Nội dung | Link tải trực tiếp (raw) |
|---|---|---|
| [`vn-ipv4.txt`](vn-ipv4.txt) | Dải IPv4 Việt Nam | `https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/vn-ipv4.txt` |
| [`vn-ipv6.txt`](vn-ipv6.txt) | Dải IPv6 Việt Nam | `https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/vn-ipv6.txt` |
| [`vn-all.txt`](vn-all.txt) | IPv4 + IPv6 | `https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/vn-all.txt` |
| [`vn-ipv4.csv`](vn-ipv4.csv) | CIDR, IP đầu, IP cuối, số IP (mở bằng Excel / Google Sheets) | `https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/vn-ipv4.csv` |

File cấu hình dựng sẵn trong thư mục [`formats/`](formats):

| File | Dùng cho |
|---|---|
| [`ipset-vn.txt`](formats/ipset-vn.txt) | iptables + ipset (`ipset restore`) |
| [`nftables-vn.nft`](formats/nftables-vn.nft) | nftables (set `vn4`, `vn6`) |
| [`nginx-allow-vn.conf`](formats/nginx-allow-vn.conf) | Nginx `allow` / `deny all` |
| [`apache-require-vn.conf`](formats/apache-require-vn.conf) | Apache 2.4 `Require ip` |
| [`mikrotik-vn.rsc`](formats/mikrotik-vn.rsc) | MikroTik address-list `VN` |
| [`windows-firewall-vn.ps1`](formats/windows-firewall-vn.ps1) | Windows Firewall (RDP 3389) |

Tải nhanh bằng lệnh:

```bash
curl -fsSL https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/vn-ipv4.txt -o vn-ipv4.txt
```

## Khi nào nên whitelist IP Việt Nam?

Phần lớn các đợt dò mật khẩu SSH, RDP, quét lỗ hổng WordPress, tấn công vào cổng cơ sở dữ liệu đến từ IP nước ngoài. Nếu người dùng và quản trị viên của bạn đều ở Việt Nam, việc **chỉ cho phép IP Việt Nam và chặn cả thế giới** sẽ cắt bỏ phần lớn lưu lượng độc hại đó, giảm tải log và giảm bề mặt tấn công.

Phù hợp để bảo vệ:

- Cổng quản trị: **SSH (22)**, **Remote Desktop (3389)**, Proxmox (8006), Webmin, cPanel/DirectAdmin.
- Trang quản trị web: `/wp-admin`, `wp-login.php`, `/admin`, phpMyAdmin.
- Cơ sở dữ liệu mở ra ngoài: MySQL (3306), PostgreSQL (5432), SQL Server (1433), Redis.
- Tổng đài VoIP / SIP (5060), VPN (WireGuard, OpenVPN, L2TP), phần mềm kế toán, máy chủ nội bộ.
- Website hoặc ứng dụng chỉ phục vụ khách hàng trong nước.

> Đây là **một lớp bảo vệ bổ sung**, không thay thế mật khẩu mạnh, xác thực 2 lớp, SSH key và cập nhật bản vá. Kẻ tấn công vẫn có thể dùng IP Việt Nam (VPS, proxy trong nước).

## Cách chặn IP nước ngoài, chỉ cho phép IP Việt Nam

**Luôn thêm IP quản trị của bạn vào whitelist trước**, và giữ một phiên SSH/console đang mở khi áp dụng, để không tự khoá mình khỏi máy chủ.

### 1. iptables + ipset (Linux)

Cách nhanh và nhẹ nhất cho Linux, xử lý hàng nghìn dải IP mà không làm chậm máy:

```bash
# Cài ipset (Debian/Ubuntu: apt install ipset | CentOS/AlmaLinux: dnf install ipset)
curl -fsSL https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/formats/ipset-vn.txt -o /etc/ipset-vn.txt
ipset restore -exist < /etc/ipset-vn.txt

# Chỉ cho phép IP Việt Nam vào SSH, chặn mọi IP nước ngoài
iptables -I INPUT -p tcp --dport 22 -j DROP
iptables -I INPUT -p tcp --dport 22 -m set --match-set vn4 src -j ACCEPT
iptables -I INPUT -p tcp --dport 22 -s 203.0.113.10 -j ACCEPT   # IP quản trị của bạn (sửa lại)

ip6tables -I INPUT -p tcp --dport 22 -j DROP
ip6tables -I INPUT -p tcp --dport 22 -m set --match-set vn6 src -j ACCEPT
```

Muốn chặn toàn bộ IP nước ngoài (mọi cổng), thay `--dport 22` bằng quy tắc chung và nhớ cho phép `lo` và kết nối `ESTABLISHED,RELATED`.

### 2. nftables (Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/formats/nftables-vn.nft -o /etc/nftables.d/vn.nft
```

```nft
table inet filter {
    include "/etc/nftables.d/vn.nft"

    chain input {
        type filter hook input priority 0; policy accept;
        tcp dport 22 ip saddr 203.0.113.10 accept      # IP quản trị của bạn
        tcp dport 22 ip saddr @vn4 accept
        tcp dport 22 ip6 saddr @vn6 accept
        tcp dport 22 drop
    }
}
```

### 3. UFW (Ubuntu)

UFW không hỗ trợ ipset trực tiếp; thêm 1.270 rule sẽ chậm. Cách gọn: nạp ipset như mục 1 rồi thêm vào `/etc/ufw/before.rules` trước dòng `COMMIT`:

```
-A ufw-before-input -p tcp --dport 22 -m set --match-set vn4 src -j ACCEPT
-A ufw-before-input -p tcp --dport 22 -j DROP
```

Sau đó `ufw reload`. Cần nạp ipset trước khi UFW khởi động (ví dụ bằng gói `ipset-persistent` hoặc một systemd unit).

### 4. Nginx

```bash
curl -fsSL https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/formats/nginx-allow-vn.conf -o /etc/nginx/vn-allow.conf
```

```nginx
location ~ ^/(wp-admin|wp-login\.php) {
    allow 203.0.113.10;              # IP quản trị của bạn
    include /etc/nginx/vn-allow.conf; # allow dải IP Việt Nam + deny all
    # ... cấu hình PHP như bình thường
}
```

Kiểm tra rồi nạp lại: `nginx -t && systemctl reload nginx`.

### 5. Apache / .htaccess

Apache 2.4, đặt trong `<Directory>`, `<Location>` hoặc file `.htaccess`:

```apache
<Files "wp-login.php">
    Include /etc/apache2/vn-require.conf
</Files>
```

Với `.htaccess` (không dùng được `Include`), dán thẳng nội dung file [`apache-require-vn.conf`](formats/apache-require-vn.conf). LiteSpeed / OpenLiteSpeed đọc được cú pháp này.

### 6. CSF Firewall (cPanel, DirectAdmin)

CSF có sẵn tính năng chặn theo quốc gia (cần cấu hình nguồn GeoIP `CC_SRC` trong CSF). Trong `/etc/csf/csf.conf`:

```
CC_ALLOW_PORTS = "VN"
CC_ALLOW_PORTS_TCP = "22,2087,2222"
```

Hoặc dùng danh sách của repo này: thêm dòng `Include /etc/csf/vn-ipv4.txt` vào `csf.allow`, rồi `csf -r`.

### 7. MikroTik RouterOS

```
/tool fetch url="https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/formats/mikrotik-vn.rsc" dst-path=vn.rsc
/import file-name=vn.rsc
/ip firewall filter add chain=input protocol=tcp dst-port=8291,22 src-address-list=!VN action=drop comment="Chi cho IP Viet Nam vao Winbox/SSH"
```

### 8. Windows Server / Remote Desktop (RDP)

Mở PowerShell bằng quyền Administrator, chạy [`windows-firewall-vn.ps1`](formats/windows-firewall-vn.ps1) để tạo rule cho phép IP Việt Nam vào cổng 3389. Sau đó **tắt rule Remote Desktop mặc định** (đang cho phép mọi IP) để chặn IP nước ngoài:

```powershell
Disable-NetFirewallRule -DisplayGroup "Remote Desktop"
```

### 9. Cloudflare

Nếu website đi qua Cloudflare (đám mây cam), máy chủ chỉ thấy IP của Cloudflare, nên chặn theo IP ở máy chủ sẽ không đúng. Hãy chặn ở Cloudflare: **Security > WAF > Custom rules**, biểu thức:

```
(ip.src.country ne "VN" and starts_with(http.request.uri.path, "/wp-admin"))
```

Action: **Block** hoặc **Managed Challenge**.

## Lưu ý quan trọng trước khi chặn IP nước ngoài

- **Đừng chặn toàn bộ website công khai** nếu cần SEO: Googlebot, Bingbot thu thập dữ liệu chủ yếu từ IP Mỹ. Chỉ nên chặn trang quản trị và các cổng dịch vụ.
- Khi bạn đi nước ngoài, dùng mạng di động roaming hoặc VPN, IP của bạn **không còn là IP Việt Nam**. Hãy có sẵn một đường vào dự phòng (VPN về văn phòng, console của nhà cung cấp VPS).
- Cổng thanh toán, webhook, API của dịch vụ quốc tế (PayPal, Stripe, Google, Facebook, GitHub...) gọi từ IP nước ngoài: hãy whitelist IP của họ nếu chặn cổng web.
- Dữ liệu địa chỉ IP thay đổi theo thời gian (cấp mới, thu hồi). Cập nhật danh sách định kỳ, ví dụ cron hàng tuần:

```bash
17 3 * * 1 curl -fsSL https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/formats/ipset-vn.txt -o /etc/ipset-vn.txt && ipset restore -exist < /etc/ipset-vn.txt
```

## Câu hỏi thường gặp

### IP Việt Nam là gì?

IP Việt Nam là các địa chỉ IP được cấp cho tổ chức, doanh nghiệp, nhà mạng tại Việt Nam (VNPT, Viettel, FPT, CMC, các nhà cung cấp hosting, VPS và doanh nghiệp có vùng IP riêng). Khi truy cập Internet từ mạng trong nước, thiết bị của bạn thường mang một địa chỉ thuộc các dải này.

### Việt Nam có bao nhiêu địa chỉ IP?

Khoảng **16,5 triệu địa chỉ IPv4** (1.270 dải sau khi gộp) và 949 dải IPv6. Con số cập nhật nằm trong [`meta.json`](meta.json).

### Làm sao kiểm tra một IP có phải IP Việt Nam không?

Trên Linux, sau khi nạp ipset ở mục 1:

```bash
ipset test vn4 113.161.1.1
```

Hoặc bằng Python:

```python
import ipaddress, urllib.request
vn = [ipaddress.ip_network(x) for x in urllib.request.urlopen(
    "https://raw.githubusercontent.com/tnd-vn/dai-ip-viet-nam/main/vn-ipv4.txt").read().decode().split()]
print(any(ipaddress.ip_address("113.161.1.1") in n for n in vn))
```

### Danh sách có chính xác 100% không?

Danh sách phản ánh các vùng địa chỉ được cấp phát cho Việt Nam. Một số ít IP có thể được dùng thực tế ở nước khác (doanh nghiệp đặt máy chủ ở nước ngoài) và ngược lại. Với mục đích whitelist bảo mật, độ chính xác này là đủ dùng; nếu phát hiện sai lệch, hãy góp ý theo mục bên dưới.

### Danh sách được cập nhật bao lâu một lần?

Tự động **mỗi thứ Hai** qua GitHub Actions ([`update.yml`](.github/workflows/update.yml)). Bạn cũng có thể tự chạy `python3 scripts/build.py` để tạo lại toàn bộ file.

## Góp ý, bổ sung

Danh sách **tổng hợp bởi TND**. Nếu bạn thấy dải IP Việt Nam nào còn thiếu, bị sai, hoặc cần thêm định dạng cấu hình khác (pfSense, FortiGate, Sophos, Juniper...), hãy:

- Mở [Issue](https://github.com/tnd-vn/dai-ip-viet-nam/issues) hoặc gửi Pull Request, hoặc
- Liên hệ góp ý trực tiếp với TND tại [www.tnd.vn/lien-he](https://www.tnd.vn/lien-he/).

Nếu repo hữu ích, hãy bấm **Star** để nhiều người cần whitelist IP Việt Nam tìm thấy hơn.

## Về TND

[TND](https://www.tnd.vn) là nhà cung cấp hạ tầng tại Việt Nam, vận hành máy chủ và dải IP riêng trong nước. Nếu bạn cần máy chủ đặt tại Việt Nam để áp dụng whitelist này, hoặc cần IP Việt Nam cố định để truy cập các hệ thống chỉ mở cho IP trong nước:

- **[VPS Việt Nam giá rẻ](https://www.tnd.vn/vps/)** - VPS NVMe đặt tại Việt Nam, tạo máy trong 60 giây, từ 129K/tháng.
- **[Proxy Việt Nam IPv4 riêng](https://www.tnd.vn/proxy-viet-nam/)** - IP tĩnh Việt Nam dùng riêng, 95K/tháng.
- **[Proxy IPv4 tĩnh Việt Nam và Mỹ](https://www.tnd.vn/proxy/)** - IP Việt Nam hoặc IP Mỹ dùng riêng.

---

Giấy phép [MIT](LICENSE). Tự do sử dụng, sửa đổi, chia sẻ; vui lòng giữ ghi chú "tổng hợp bởi TND".
