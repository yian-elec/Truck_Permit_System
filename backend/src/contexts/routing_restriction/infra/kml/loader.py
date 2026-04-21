"""
KML/KMZ 載入：URL、inline XML，或 KMZ zip 解壓取得主 .kml 字串。
"""

from __future__ import annotations

import io
import zipfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def is_likely_inline_kml(text: str) -> bool:
    s = text.lstrip()
    if s.startswith("<?xml") or s.startswith("<kml"):
        return True
    return len(s) > 100 and "<kml" in s[:2000]


def _is_zip_magic(b: bytes) -> bool:
    return len(b) >= 4 and b[0:2] == b"PK"


def extract_kml_from_kmz(data: bytes) -> str:
    """自 KMZ bytes 解出第一個 .kml 內容（優先 doc.kml）。"""
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        preferred = [n for n in names if n.lower().endswith(".kml")]
        if not preferred:
            raise ValueError("KMZ archive contains no .kml file")
        chosen = "doc.kml" if "doc.kml" in names else preferred[0]
        for n in preferred:
            if n.lower().endswith("doc.kml"):
                chosen = n
                break
        raw = zf.read(chosen)
    return raw.decode("utf-8", errors="replace")


def load_kml_xml(source: str, *, timeout_s: int = 90) -> str:
    """
    回傳 KML XML 字串。

    - HTTP(S) URL：GET；若回傳為 zip/KMZ 則解壓。
    - 其餘：視為 inline KML/XML。
    """
    s = source.strip()
    if not s:
        raise ValueError("source is empty")

    if is_likely_inline_kml(s):
        return s

    if s.startswith("http://") or s.startswith("https://"):
        req = Request(s, headers={"User-Agent": "TruckPermitSystem-KmlImport/1.0"})
        try:
            with urlopen(req, timeout=timeout_s) as resp:
                data = resp.read()
        except HTTPError as e:
            raise ValueError(f"HTTP error fetching KML URL: {e.code} {e.reason}") from e
        except URLError as e:
            raise ValueError(f"Network error fetching KML URL: {e.reason}") from e

        if _is_zip_magic(data):
            return extract_kml_from_kmz(data)
        return data.decode("utf-8", errors="replace")

    raise ValueError(
        "Unsupported source: provide an http(s) URL to .kml/.kmz or paste inline KML XML"
    )
