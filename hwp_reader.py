from __future__ import annotations

import re
import struct
import zlib
from io import BytesIO

import olefile

PARA_TEXT_TAG = 67

def _read_records(data: bytes):
    offset = 0
    while offset + 4 <= len(data):
        header = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        tag_id = header & 0x3FF
        level = (header >> 10) & 0x3FF
        size = (header >> 20) & 0xFFF
        if size == 0xFFF:
            if offset + 4 > len(data):
                break
            size = struct.unpack_from("<I", data, offset)[0]
            offset += 4
        if offset + size > len(data):
            break
        yield tag_id, level, data[offset : offset + size]
        offset += size

def _decode_para_text(payload: bytes) -> str:
    output: list[str] = []
    text_bytes = bytearray()

    def flush_text() -> None:
        if text_bytes:
            output.append(text_bytes.decode("utf-16le", errors="ignore"))
            text_bytes.clear()

    offset = 0
    while offset + 2 <= len(payload):
        code = struct.unpack_from("<H", payload, offset)[0]

        # HWP inline controls from 1 through 23 occupy eight UTF-16 code
        # units (16 bytes). Skipping only the first unit exposes the embedded
        # control id as garbage text such as "dces".
        if 1 <= code <= 23 and code not in (10, 13):
            flush_text()
            if code == 9:
                output.append("\t")
            offset += 16
            continue

        if code in (10, 13):
            flush_text()
            output.append("\n")
            offset += 2
            continue

        if code == 0:
            flush_text()
            offset += 2
            continue

        if 24 <= code <= 31:
            flush_text()
            if code in (30, 31):
                output.append(" ")
            offset += 2
            continue

        text_bytes.extend(payload[offset : offset + 2])
        offset += 2

    flush_text()
    text = "".join(output)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_hwp_text_bytes(hwp_bytes: bytes) -> str:
    with olefile.OleFileIO(BytesIO(hwp_bytes)) as ole:
        if not ole.exists("FileHeader") or not ole.exists("BodyText"):
            raise ValueError("지원하지 않는 HWP 파일입니다.")
        header = ole.openstream("FileHeader").read()
        if not header.startswith(b"HWP Document File"):
            raise ValueError("HWP 5.x 파일이 아닙니다.")
        flags = struct.unpack_from("<I", header, 36)[0]
        compressed = bool(flags & 0x01)
        if flags & 0x02:
            raise ValueError("암호화된 HWP 파일은 지원하지 않습니다.")

        section_names = []
        for path in ole.listdir(streams=True, storages=False):
            if len(path) == 2 and path[0] == "BodyText" and path[1].startswith("Section"):
                section_names.append(path)
        section_names.sort(key=lambda path: int(path[1][7:]))

        paragraphs = []
        for path in section_names:
            data = ole.openstream(path).read()
            if compressed:
                data = zlib.decompress(data, -15)
            for tag_id, _level, payload in _read_records(data):
                if tag_id == PARA_TEXT_TAG:
                    text = _decode_para_text(payload)
                    if text:
                        paragraphs.append(text)
        return "\n".join(paragraphs)
