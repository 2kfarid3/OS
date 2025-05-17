#!/usr/bin/env python3

# Lazımi kitabxanaların daxil edilməsi
import argparse          # Komanda sətri arqumentlərini oxumaq üçün
import os                # Fayl və qovluq əməliyyatları üçün
import zlib              # Zlib sıxılmasını açmaq üçün
import lzma              # LZMA sıxılmasını açmaq üçün
import base64            # Base64 kodlaşdırma və deşifrə üçün
import struct            # Binary məlumatları formatlı şəkildə oxumaq üçün
import binascii          # Hex kodunu binar formata çevirmək üçün
import re                # Mətndə axtarış üçün regex
from cryptography.fernet import Fernet  # Fernet ilə şifrələnmiş məlumatı açmaq üçün


# Hexdump formatını aşkar etmək və çevirmək üçün funksiyalar
def parse_xxd_format(hex_lines):
    binary = b''  # Binar məlumat toplanacaq
    for line in hex_lines:
        line = line.strip()  # Sətirin əvvəl və sonundakı boşluqları sil
        if ':' in line:  # Sətirdə offset varsa (xxd format)
            hex_part = line.split(':', 1)[1].split('  ', 1)[0].replace(' ', '')  # Hex hissəni ayır
            binary += binascii.unhexlify(hex_part)  # Hex-i binara çevir və əlavə et
    return binary

def parse_plain_hex(hex_lines):
    hex_str = ''.join(line.strip() for line in hex_lines)  # Bütün sətrləri birləşdir
    return binascii.unhexlify(hex_str)  # Hex string-i binara çevir

def detect_hex_format(lines):
    for line in lines:
        if ':' in line:
            return 'xxd'  # Əgər sətirdə ':' varsa, bu xxd formatıdır
    return 'plain'  # Əks halda adi plain hex formatıdır

def convert_hex_to_binary(file_path):
    if file_path.endswith(".bin"):  # Əgər fayl artıq binary formatdadırsa
        with open(file_path, "rb") as f:
            return f.read()
    elif file_path.endswith(".hex") or file_path.endswith(".txt"):  # Hex və ya txt fayllar
        with open(file_path, 'r') as f:
            lines = f.readlines()  # Bütün sətrləri oxu
        format_type = detect_hex_format(lines)  # Formatı aşkar et
        if format_type == 'xxd':
            return parse_xxd_format(lines)  # xxd format üçün uyğun parse
        else:
            return parse_plain_hex(lines)  # Plain hex üçün uyğun parse
    else:
        raise ValueError("Unknown file type.")  # Dəstəklənməyən fayl tipi

# Binary fayldan integer dəyər oxumaq funksiyası
def read_uint(data, offset, size, endian='little'):
    fmt = {1: 'B', 4: 'I', 8: 'Q'}[size]  # Ölçüyə uyğun format tipi
    fmt = ('<' if endian == 'little' else '>') + fmt  # Endian tipinə görə formatlaşdır
    return struct.unpack_from(fmt, data, offset)[0], offset + size  # Dəyəri oxu və yeni offset qaytar

# Əsas arxiv çıxarma funksiyası
def extract_archive(data, output_dir, verbose=0, log_file="log.txt"):
    offset = 0  # Faylda mövcud oxuma mövqeyi
    log_lines = []  # Xətalar üçün log sətirləri
    metadata_lines = []  # Metadata məlumatı toplanacaq

    try:
        magic, offset = read_uint(data, offset, 4, 'little')  # Magic dəyəri oxu
        magic_str = magic.to_bytes(4, 'big').decode()  # Magic string formatına çevir
        version = data[offset]  # Versiya dəyərini oxu
        offset += 1
        endian = 'little' if magic_str == 'ARCH' else 'big'  # Endian istiqamətini təyin et
    except Exception as e:
        print(f"[!] Error reading header: {e}")  # Əgər başlıqda problem varsa, çıx
        return

    index = 0  # Fayl indeksləri üçün sayğac
    while offset < len(data):  # Faylın sonuna qədər oxumağa davam et
        method_str = "unknown"  # Emal metodunun string qarşılığı
        try:
            if offset + 4 > len(data):  # Fayl adının uzunluğunu oxumağa yer yoxdursa
                raise ValueError("Not enough data to read name length")

            name_length, offset = read_uint(data, offset, 4, endian)  # Adın uzunluğunu oxu

            if offset + name_length > len(data):  # Fayl adını oxumağa yer yoxdursa
                raise ValueError("Not enough data to read filename")

            filename = data[offset:offset+name_length].decode('utf-8', errors='replace')  # Fayl adını deşifrə et
            offset += name_length

            if offset + 16 > len(data):  # Ölçüləri oxumaq üçün yetərli data yoxdursa
                raise ValueError("Not enough data to read sizes")

            original_size, offset = read_uint(data, offset, 8, endian)  # Orijinal ölçü
            processed_size, offset = read_uint(data, offset, 8, endian)  # Emal olunmuş ölçü

            if offset + 1 + processed_size > len(data):  # Məzmun və metod üçün yer yoxdursa
                raise ValueError("Not enough data to read method and content")

            method = data[offset]  # Metod dəyəri oxunur
            offset += 1
            processed_data = data[offset:offset+processed_size]  # Emal olunmuş data alınır
            offset += processed_size

            method_str = {0x00: 'none', 0x01: 'zlib', 0x02: 'lzma', 0x03: 'fernet'}.get(method, 'unknown')

            if verbose >= 1:
                print(f"[*] Extracting: {filename} ({method_str})")  # Fayl çıxarılır mesajı

            # Emal metoduna görə uyğun açma əməliyyatı
            if method == 0x00:
                content = processed_data  # Heç bir emal yoxdur
            elif method == 0x01:
                content = zlib.decompress(processed_data)  # Zlib ilə dekompress
            elif method == 0x02:
                content = lzma.decompress(processed_data)  # LZMA ilə dekompress
            elif method == 0x03:
                if len(processed_data) < 44:
                    raise ValueError("Fernet key too short")  # Açar yetərli uzunluqda deyil
                key_b64 = processed_data[:44]  # İlk 44 bayt açar
                enc_data = processed_data[44:]  # Qalan hissə şifrələnmiş məlumatdır
                key_padded = key_b64 + b'=' * ((4 - len(key_b64) % 4) % 4)  # Base64 üçün padding əlavə et
                key = base64.urlsafe_b64decode(key_padded)
                fernet = Fernet(base64.urlsafe_b64encode(key.ljust(32, b'\x00')[:32]))  # Açar düzəldilir
                content = fernet.decrypt(enc_data)  # Şifrə açılır
            else:
                raise ValueError(f"Unknown method: 0x{method:02x}")  # Naməlum metod

            full_path = os.path.join(output_dir, filename)  # Faylın çıxış yolu
            os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Qovluq yoxdursa yaradılır
            with open(full_path, "wb") as out_file:
                out_file.write(content)  # Fayl yazılır

            metadata_lines.append(f"{filename}\t{original_size}\t{processed_size}\t{method_str}")  # Metadataya əlavə olunur

        except Exception as e:
            err_msg = f"Error extracting file at index {index}: {e}"  # Xəta mesajı
            log_lines.append(err_msg)
            metadata_lines.append(f"ERROR_{index}\tERROR\tERROR\t{method_str}: {e}")
            if verbose >= 1:
                print("[!] " + err_msg)

            offset += 1  # Sonsuz loopdan çıxmaq üçün offset irəlilədilir

        index += 1  # Növbəti fayla keç

    # metadata və log faylları yazılır
    with open(os.path.join(output_dir, "metadata.txt"), 'w') as meta:
        meta.write("\n".join(metadata_lines))
    with open(os.path.join(output_dir, log_file), 'w') as log:
        log.write("\n".join(log_lines))


# Komanda sətrindən daxilolma nöqtəsi
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract ARCH binary from hex or xxd dumps")  # CLI üçün təsvir
    parser.add_argument("-i", required=True, help="Input hex or txt file")  # Giriş faylı
    parser.add_argument("-o", default="./extracted", help="Output directory")  # Çıxış qovluğu
    parser.add_argument("-v", type=int, choices=[0, 1, 2], default=0, help="Verbose level")  # Ətraflı səviyyə
    args = parser.parse_args()

    bin_data = convert_hex_to_binary(args.i)  # Giriş faylı binar data çevrilir
    os.makedirs(args.o, exist_ok=True)  # Çıxış qovluğu yaradılır
    extract_archive(bin_data, args.o, verbose=args.v)  # Arxiv çıxarılır

    if args.v >= 1:
        print("Extraction complete.")  # Bitdi mesajı