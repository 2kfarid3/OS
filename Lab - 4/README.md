# OS Laboratory 4 — Archive Extractor Tool

This project is part of the Operating Systems Lab 4 and consists of two main tasks:

- **Part 1:** Network configuration and file transfer setup between virtual machines
- **Part 2:** A command-line utility to extract encrypted and/or compressed files from custom archive formats

---

## Part 1 — Network Setup

Two Ubuntu VMs were configured in VirtualBox using a **NAT Network**:
- File transfer verified via `scp` and `netcat`
- Connectivity tested with `ping`
- SSH setup done via OpenSSH server

---

## Part 2 — Archive Extraction Tool

### Features
- Supports `.hex`, `.txt`, and `.bin` input files
- Automatically detects file format (plain hex, xxd, binary)
- Detects endianness (little or big endian) using magic number
- Handles the following processing methods:
  - `0x00` - No processing
  - `0x01` - zlib compression
  - `0x02` - LZMA compression
  - `0x03` - Fernet encryption with embedded keys

### Output
- Extracted files are saved in a specified output directory
- `metadata.txt`: Shows file name, original size, processed size, and method
- `log.txt`: Detailed logs for Fernet keys and error tracking

---

## Usage

```bash
python3 archextract.py -i <input_file> -o <output_directory> -v <verbosity>
```

- `-i`: Input file path (.hex, .txt, or .bin)
- `-o`: Output folder (default: `./extracted`)
- `-v`: Verbosity (0: silent, 1: info, 2: debug)

---

## Example

```bash
python3 archextract.py -i archive_le.hex -o output_le -v 1
```

---

## Requirements

- Python 3.6+
- cryptography module:
```bash
pip3 install cryptography
```

---

## Screenshots

See `screenshots/` folder for:
- VM configuration
- `ping` and `scp` tests
- Terminal output of Python script
- Extracted file previews

---

## Notes

- Fernet key decoding is handled with proper base64 padding
- All UTF-8 decode errors are caught and handled gracefully
- Directory paths are created automatically for nested files
