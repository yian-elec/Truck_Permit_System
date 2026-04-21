"""
新北市大貨車臨時通行證 — PDF 產製（§8 樣張簡化版）。

責任：輸出單頁橫式 PDF bytes；中文須以 **可內嵌之字型** 繪製（優先 **Noto Sans TC TrueType**，
避免僅依 Adobe CID 時部分閱讀器出現方塊 ■）。備援：**MSung-Light**／**STSong-Light** CID。
產出後驗證 PDF 內嵌可顯示中文之字型。
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import urllib.request
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from shared.core.logger.logger import logger

from src.contexts.permit_document.app.errors import PermitCertificateFontError


@dataclass(frozen=True)
class PermitCertificateLayoutInput:
    permit_no: str
    vehicle_plate: str
    route_summary_text: str
    approved_start_at: datetime
    approved_end_at: datetime


_CJK_FONT_ORDER = ("MSung-Light", "STSong-Light")
_EMBEDDED_TTF_FONT_NAME = "PermitNotoTC"
# Google Fonts OFL：繁體中文可變字型（TrueType outlines，ReportLab 可內嵌子集）
_NOTO_SANS_TC_VF_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf"
)
_RAW_TYPE0 = re.compile(br"/Subtype\s*/Type0")
_RAW_TRUETYPE = re.compile(br"/Subtype\s*/TrueType")
_CJK_NAME_MARKERS = (
    b"MSung",
    b"STSong",
    b"Heisei",
    b"MHei",
    b"Bousung",
    b"UniGB-UCS2",
    b"UniCNS-UCS2",
    b"NotoSans",
    b"PermitNotoTC",
)


def _permit_font_resource_dir() -> Path:
    return Path(__file__).resolve().parent / "resources"


def _noto_tc_cache_path() -> Path:
    base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(base) / "truck_permit_system" / "NotoSansTC-VF.ttf"


def _candidate_ttf_paths() -> list[Path]:
    out: list[Path] = []
    env = os.environ.get("PERMIT_PDF_FONT_TTF")
    if env:
        out.append(Path(env))
    out.append(_permit_font_resource_dir() / "NotoSansTC-VF.ttf")
    out.append(_noto_tc_cache_path())
    return out


def _download_noto_sans_tc_vf(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(_NOTO_SANS_TC_VF_URL, target)


def register_embedded_noto_tc_font() -> str:
    """
    註冊 **Noto Sans TC** TrueType（內嵌子集），跨閱讀器中文顯示較穩定。

    Returns:
        已註冊之字型邏輯名稱 ``PermitNotoTC``。

    Raises:
        PermitCertificateFontError: 無可用 .ttf 且無法下載或註冊。
    """
    if _EMBEDDED_TTF_FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return _EMBEDDED_TTF_FONT_NAME

    last_err: Exception | None = None
    for p in _candidate_ttf_paths():
        try:
            if p.is_file() and p.stat().st_size > 1_000_000:
                pdfmetrics.registerFont(TTFont(_EMBEDDED_TTF_FONT_NAME, str(p)))
                return _EMBEDDED_TTF_FONT_NAME
        except Exception as e:
            last_err = e

    cache = _noto_tc_cache_path()
    try:
        _download_noto_sans_tc_vf(cache)
        pdfmetrics.registerFont(TTFont(_EMBEDDED_TTF_FONT_NAME, str(cache)))
        return _EMBEDDED_TTF_FONT_NAME
    except Exception as e:
        raise PermitCertificateFontError(
            "無法載入或下載 Noto Sans TC（TTF）作為許可證內嵌中文字型",
            {"paths_tried": [str(p) for p in _candidate_ttf_paths()], "cache": str(cache), "error": str(e), "prior": str(last_err) if last_err else None},
        ) from e


def register_permit_cjk_font() -> str:
    """
    備援：**Adobe Unicode CID**（MSung-Light → STSong-Light）。

    Returns:
        實際註冊並應用於繪製之字型名稱。

    Raises:
        PermitCertificateFontError: 兩種字型皆無法註冊。
    """
    attempts: list[dict[str, str]] = []
    for name in _CJK_FONT_ORDER:
        if name in pdfmetrics.getRegisteredFontNames():
            return name
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(name))
            return name
        except Exception as e:
            attempts.append({"font": name, "error": str(e)})
    raise PermitCertificateFontError(
        "無法註冊許可證 PDF 所需之中文 CID 字型（MSung-Light 與 STSong-Light 皆失敗）",
        {"attempts": attempts},
    )


def register_permit_pdf_font() -> str:
    """
    優先 **Noto Sans TC（TTF 內嵌）**；失敗則退回 Adobe CID（部分閱讀器可能仍顯示方塊）。
    """
    try:
        return register_embedded_noto_tc_font()
    except PermitCertificateFontError:
        logger.infra_warn(
            "Permit PDF: Noto Sans TC (TTF) unavailable; falling back to Adobe CID fonts — "
            "some PDF viewers may show Chinese as squares (■)",
        )
        return register_permit_cjk_font()


def _resolve_pdf_obj(obj, reader: PdfReader, *, _depth: int = 0) -> object:
    """
    解開 IndirectObject；勿使用無上限 `while get_object`（部分 pypdf 物件會形成循環或自指，導致無窮迴圈）。
    """
    if obj is None or _depth > 64:
        return obj
    if not hasattr(obj, "get_object"):
        return obj
    try:
        nxt = obj.get_object()
    except Exception:
        return obj
    if nxt is obj:
        return obj
    return _resolve_pdf_obj(nxt, reader, _depth=_depth + 1)


def _pypdf_document_has_type0_font(pdf_bytes: bytes) -> bool:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except PdfReadError:
        return False
    for page in reader.pages:
        res = page.get("/Resources")
        if res is None:
            continue
        res = _resolve_pdf_obj(res, reader)
        if not hasattr(res, "get"):
            continue
        fonts = res.get("/Font")
        if fonts is None:
            continue
        fonts = _resolve_pdf_obj(fonts, reader)
        if not hasattr(fonts, "keys"):
            continue
        for key in fonts.keys():
            fo = _resolve_pdf_obj(fonts[key], reader)
            if not hasattr(fo, "get"):
                continue
            st = fo.get("/Subtype")
            if st == "/Type0":
                return True
    return False


def _font_base_excludes_standard_latin_only(base: str) -> bool:
    u = (base or "").upper()
    if "HELVETICA" in u or "TIMES" in u or "COURIER" in u or "SYMBOL" in u or "ZAPF" in u:
        return False
    return "NOTO" in u or "PERMITNOTOTC" in u.replace("+", "").replace("-", "")


def _pypdf_document_has_embedded_truetype_cjk_font(pdf_bytes: bytes) -> bool:
    """TrueType 內嵌（如 Noto Sans TC）子集，閱讀器相容性通常優於純 CID。"""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except PdfReadError:
        return False
    for page in reader.pages:
        res = page.get("/Resources")
        if res is None:
            continue
        res = _resolve_pdf_obj(res, reader)
        if not hasattr(res, "get"):
            continue
        fonts = res.get("/Font")
        if fonts is None:
            continue
        fonts = _resolve_pdf_obj(fonts, reader)
        if not hasattr(fonts, "keys"):
            continue
        for key in fonts.keys():
            fo = _resolve_pdf_obj(fonts[key], reader)
            if not hasattr(fo, "get"):
                continue
            st = fo.get("/Subtype")
            base = str(fo.get("/BaseFont") or "")
            fd = fo.get("/FontDescriptor")
            if st == "/TrueType" and fd is not None and _font_base_excludes_standard_latin_only(base):
                return True
    return False


def _pypdf_document_has_acceptable_cjk_font(pdf_bytes: bytes) -> bool:
    return _pypdf_document_has_type0_font(pdf_bytes) or _pypdf_document_has_embedded_truetype_cjk_font(
        pdf_bytes
    )


def _pdffonts_stdout_suggests_cjk(pdf_bytes: bytes) -> str | None:
    exe = shutil.which("pdffonts")
    if not exe:
        return None
    path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            path = tmp.name
        proc = subprocess.run(
            [exe, path],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return proc.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        if path and os.path.isfile(path):
            try:
                os.unlink(path)
            except OSError:
                pass


def _pdffonts_text_indicates_type0_or_cjk(pdffonts_text: str) -> bool:
    for line in pdffonts_text.splitlines():
        low = line.lower()
        if "type 0" in low or "type0" in low.replace(" ", ""):
            return True
        if "cid" in low and "type" in low:
            return True
        if any(m in line for m in ("MSung", "STSong", "Heisei", "MHei", "Bousung")):
            return True
    return False


def _raw_pdf_bytes_suggest_type0_or_cjk_marker(pdf_bytes: bytes) -> bool:
    if _RAW_TYPE0.search(pdf_bytes):
        return True
    if _RAW_TRUETYPE.search(pdf_bytes) and (b"NotoSans" in pdf_bytes or b"PermitNotoTC" in pdf_bytes):
        return True
    return any(m in pdf_bytes for m in _CJK_NAME_MARKERS)


def assert_rendered_certificate_pdf_embeds_cjk_fonts(pdf_bytes: bytes) -> None:
    """
    驗證產出 PDF 內嵌可顯示中文之字型（**Type0 CID** 或 **TrueType 內嵌如 Noto**）。

    優先以 pypdf 走訪 /Resources/Font；必要時輔以 pdffonts 或原始位元組啟發式。
    """
    if _pypdf_document_has_acceptable_cjk_font(pdf_bytes):
        return

    pd_out = _pdffonts_stdout_suggests_cjk(pdf_bytes)
    if pd_out is not None and _pdffonts_text_indicates_type0_or_cjk(pd_out):
        return

    if _raw_pdf_bytes_suggest_type0_or_cjk_marker(pdf_bytes):
        return

    snippet = (pd_out[:800] + "…") if pd_out and len(pd_out) > 800 else pd_out
    raise PermitCertificateFontError(
        "產出之 PDF 未偵測到內嵌之中文字型（Type0 或 Noto TrueType）；禁止發布此檔",
        {
            "pdffonts_excerpt": snippet,
            "pypdf_embed_ok": False,
        },
    )


def _normalize_pdf_text(s: str) -> str:
    """
    供 PDF 繪製：Unicode NFC；可選修復「UTF-8 位元組被當成 Latin-1」之誤讀（與方塊字／CID 缺失問題分離）。
    """
    t = unicodedata.normalize("NFC", (s or "").strip())
    if not t:
        return t
    try:
        recovered = t.encode("latin1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return t

    def cjkish_count(txt: str) -> int:
        return sum(1 for ch in txt if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf")

    if cjkish_count(recovered) > cjkish_count(t):
        return unicodedata.normalize("NFC", recovered)
    return t


def _paragraph_style_cn(*, name: str, font: str, font_size: int, leading: int) -> ParagraphStyle:
    """不依賴 getSampleStyleSheet Normal（Helvetica），避免父樣式污染。"""
    return ParagraphStyle(
        name,
        parent=None,
        fontName=font,
        fontSize=font_size,
        leading=leading,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=0,
        wordWrap="CJK",
    )


STATIC_NOTES = (
    "一、本證應隨車攜帶，並依核定路線及時間行駛；違規者依法究辦。\n"
    "二、本證不得塗改、轉借；車號須與登記相符。\n"
    "三、請遵守道路交通法令及各該路段管制時間（例：上下學時段、尖峰時段）。\n"
    "四、本證影本無效；遺失應申請補發。\n"
    "五、其他依主管機關公告事項辦理。"
)

ISSUER_LINE = "新北市政府警察局製"


def render_permit_certificate_pdf(inp: PermitCertificateLayoutInput) -> bytes:
    """產製使用證 PDF（橫式 A4）；若無法嵌入／驗證中文字型則拋錯。"""
    font = register_permit_pdf_font()
    permit_no = _normalize_pdf_text(inp.permit_no)
    vehicle_plate = _normalize_pdf_text(inp.vehicle_plate)
    buf = BytesIO()
    page = landscape(A4)
    w, h = page
    c = canvas.Canvas(buf, pagesize=page)
    c.setTitle("新北市大貨車臨時通行證")

    c.setFillColor(colors.black)

    c.setFont(font, 18)
    c.drawCentredString(w / 2, h - 20 * mm, "新北市大貨車臨時通行證")

    c.setFont(font, 11)
    c.drawRightString(w - 15 * mm, h - 28 * mm, f"No. {permit_no}")

    c.setFont(font, 14)
    c.drawString(15 * mm, h - 45 * mm, "車號")
    c.setFont(font, 26)
    c.drawString(35 * mm, h - 48 * mm, vehicle_plate)

    c.setFont(font, 12)
    c.drawString(15 * mm, h - 62 * mm, "核定路線")

    route_display = _normalize_pdf_text(inp.route_summary_text or "")
    if not route_display:
        route_display = "（路線摘要尚未登錄，請於核准流程補齊路線後重產。）"

    body = _paragraph_style_cn(name="permit_route_body", font=font, font_size=10, leading=14)
    notes_style = _paragraph_style_cn(name="permit_notes", font=font, font_size=8, leading=10)
    assert body.fontName == font and notes_style.fontName == font

    route_html = escape(route_display).replace("\n", "<br/>")
    route_para = Paragraph(route_html, body)
    route_w = w - 30 * mm
    route_h = 32 * mm
    route_para.wrapOn(c, route_w, route_h)
    route_para.drawOn(c, 15 * mm, h - 62 * mm - route_h)

    c.setFont(font, 10)
    c.drawString(15 * mm, h - 100 * mm, "有效期間")
    period = (
        f"{inp.approved_start_at:%Y-%m-%d} 起 至 {inp.approved_end_at:%Y-%m-%d} 止（逾期作廢）"
    )
    c.drawString(40 * mm, h - 100 * mm, period)

    notes_html = escape(STATIC_NOTES).replace("\n", "<br/>")
    notes_para = Paragraph(notes_html, notes_style)
    notes_para.wrapOn(c, w - 30 * mm, 50 * mm)
    notes_para.drawOn(c, 15 * mm, 10 * mm)

    c.setFont(font, 10)
    c.drawCentredString(w / 2, 6 * mm, ISSUER_LINE)

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()

    try:
        assert_rendered_certificate_pdf_embeds_cjk_fonts(pdf_bytes)
    except PermitCertificateFontError as exc:
        logger.infra_error(
            f"Permit PDF CJK font validation failed: {exc.message}",
            details=exc.details,
        )
        raise

    sha8 = hashlib.sha256(pdf_bytes).hexdigest()[:8]
    reg_names = [
        n
        for n in pdfmetrics.getRegisteredFontNames()
        if n in (_EMBEDDED_TTF_FONT_NAME, *_CJK_FONT_ORDER)
    ]
    logger.info(
        "Permit certificate PDF rendered with embedded CJK-capable font",
        context="PermitPDF",
        resolved_font=font,
        paragraph_route_style_fontName=body.fontName,
        paragraph_notes_style_fontName=notes_style.fontName,
        registered_fonts=reg_names,
        sha256_prefix=sha8,
    )

    return pdf_bytes
