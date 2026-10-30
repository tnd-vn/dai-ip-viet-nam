#!/usr/bin/env python3
"""Tổng hợp dải IP Việt Nam và sinh sẵn cấu hình allow IP Việt Nam / deny all cho các tường lửa, web server phổ biến.

Chạy: python3 scripts/build.py   (từ thư mục gốc của repo)
Nếu tải lỗi hoặc dữ liệu bất thường (ít hơn 1000 dải IPv4) thì giữ nguyên file cũ và thoát mã 1.
"""
import csv
import datetime
import hashlib
import ipaddress
import json
import os
import sys
import urllib.request

REGISTRY = 'https://ftp.apnic.net/stats/apnic/delegated-apnic-latest'
EXTRA = 'https://www.ipdeny.com/ipblocks/data/aggregated/vn-aggregated.zone'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'tnd-dai-ip-viet-nam/1.0'}), timeout=120) as r:
        return r.read()


def write(path, text):
    path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + '.tmp', 'w', newline='') as f:
        f.write(text)
    os.replace(path + '.tmp', path)


def main():
    raw = fetch(REGISTRY)
    if hashlib.md5(raw).hexdigest() != fetch(REGISTRY + '.md5').decode().split()[-1]:
        sys.exit('md5 không khớp, giữ file cũ')
    v4, v6 = [], []
    for line in raw.decode().splitlines():
        p = line.split('|')
        if len(p) < 7 or p[1] != 'VN' or p[6] not in ('allocated', 'assigned'):
            continue
        if p[2] == 'ipv6':
            v6.append(ipaddress.ip_network(f'{p[3]}/{p[4]}'))
        elif p[2] == 'ipv4':
            start = ipaddress.IPv4Address(p[3])
            v4 += ipaddress.summarize_address_range(start, start + int(p[4]) - 1)
    if len(v4) < 1000:
        sys.exit(f'chỉ có {len(v4)} dải IPv4, bất thường, giữ file cũ')
    try:
        v4 += [ipaddress.ip_network(x.strip()) for x in fetch(EXTRA).decode().splitlines() if x.strip()]
    except Exception as e:  # nguồn phụ lỗi thì vẫn dùng nguồn chính
        print('bỏ qua nguồn phụ:', e)
    v4 = list(ipaddress.collapse_addresses(v4))
    v6 = list(ipaddress.collapse_addresses(v6))
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    head = f'# Dải IP Việt Nam - tổng hợp bởi TND (https://www.tnd.vn) - cập nhật {now}\n'
    s4, s6 = [str(n) for n in v4], [str(n) for n in v6]

    write('vn-ipv4.txt', '\n'.join(s4) + '\n')
    write('vn-ipv6.txt', '\n'.join(s6) + '\n')
    write('vn-all.txt', '\n'.join(s4 + s6) + '\n')
    rows = [[str(n), str(n[0]), str(n[-1]), n.num_addresses] for n in v4]
    with open(os.path.join(ROOT, 'vn-ipv4.csv.tmp'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cidr', 'ip_dau', 'ip_cuoi', 'so_ip'])
        w.writerows(rows)
    os.replace(os.path.join(ROOT, 'vn-ipv4.csv.tmp'), os.path.join(ROOT, 'vn-ipv4.csv'))

    # Nginx: include trong server{} / location{}, sau các dòng allow IP quản trị
    write('formats/nginx-allow-vn.conf', head + ''.join(f'allow {c};\n' for c in s4 + s6) + 'deny all;\n')
    # Apache 2.4: đặt trong <Directory>/<Location> hoặc .htaccess
    write('formats/apache-require-vn.conf', head + '<RequireAny>\n' +
          ''.join(f'    Require ip {c}\n' for c in s4 + s6) + '</RequireAny>\n')
    # ipset restore: ipset restore -exist < formats/ipset-vn.txt
    # Nạp vào set tạm rồi swap, để lúc cập nhật set đang dùng không bao giờ rỗng (luật DROP sẽ chặn cả IP Việt Nam)
    write('formats/ipset-vn.txt', head +
          'create vn4 hash:net family inet maxelem 65536 -exist\ncreate vn6 hash:net family inet6 maxelem 65536 -exist\n'
          'create vn4-tmp hash:net family inet maxelem 65536 -exist\ncreate vn6-tmp hash:net family inet6 maxelem 65536 -exist\n'
          'flush vn4-tmp\nflush vn6-tmp\n' +
          ''.join(f'add vn4-tmp {c}\n' for c in s4) + ''.join(f'add vn6-tmp {c}\n' for c in s6) +
          'swap vn4-tmp vn4\nswap vn6-tmp vn6\ndestroy vn4-tmp\ndestroy vn6-tmp\n')
    # nftables: include "/etc/nftables.d/vn.nft" trong table inet filter
    write('formats/nftables-vn.nft', head + 'set vn4 {\n    type ipv4_addr\n    flags interval\n    elements = {\n        ' +
          ',\n        '.join(s4) + '\n    }\n}\nset vn6 {\n    type ipv6_addr\n    flags interval\n    elements = {\n        ' +
          ',\n        '.join(s6) + '\n    }\n}\n')
    # MikroTik RouterOS: /import file-name=mikrotik-vn.rsc (RouterOS không đọc tốt Unicode nên dòng đầu file để không dấu)
    write('formats/mikrotik-vn.rsc', f'# Dai IP Viet Nam - tong hop boi TND (https://www.tnd.vn) - cap nhat {now}\n' + '/ip firewall address-list remove [find list=VN]\n/ip firewall address-list\n' +
          ''.join(f'add list=VN address={c}\n' for c in s4) +
          '/ipv6 firewall address-list remove [find list=VN]\n/ipv6 firewall address-list\n' +
          ''.join(f'add list=VN address={c}\n' for c in s6))
    # Windows Firewall: dán vào RemoteAddress, tách 500 dải mỗi rule; ghi UTF-8 có BOM để PowerShell 5.1 đọc đúng dấu
    chunks = [s4[i:i + 500] for i in range(0, len(s4), 500)]
    write('formats/windows-firewall-vn.ps1', '\ufeff' + head + '# Chạy bằng PowerShell (Admin). Đổi -LocalPort cho đúng cổng cần mở.\n' +
          ''.join(f'New-NetFirewallRule -DisplayName "Allow VN {i + 1}" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3389 '
                  f'-RemoteAddress {",".join(c)}\n' for i, c in enumerate(chunks)))

    meta = {'cap_nhat_utc': now, 'so_dai_ipv4': len(v4), 'tong_ip_v4': sum(n.num_addresses for n in v4), 'so_dai_ipv6': len(v6)}
    write('meta.json', json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == '__main__':
    main()
