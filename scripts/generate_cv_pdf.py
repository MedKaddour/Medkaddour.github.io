#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT_RELATIVE_ATTR_RE = re.compile(r'(?P<prefix>\b(?:href|src|content)=["\'])/(?P<path>[^"\']+)')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the CV PDF from the rendered print page.")
    parser.add_argument(
        "--input-html",
        default="_site/cv/print/index.html",
        help="Rendered HTML file used as the PDF source.",
    )
    parser.add_argument(
        "--output-pdf",
        default="_site/assets/pdf/new_academic_cv.pdf",
        help="Output PDF path inside the generated site.",
    )
    parser.add_argument(
        "--sync-source-pdf",
        default="assets/pdf/new_academic_cv.pdf",
        help="Optional source PDF path to keep in sync. Pass an empty string to disable.",
    )
    return parser.parse_args()


def find_browser() -> str:
    browser_candidates = [
        os.environ.get("CV_PDF_CHROME_PATH"),
        os.environ.get("CHROME_BIN"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]

    for candidate in browser_candidates:
        if candidate and Path(candidate).exists():
            return candidate

    raise FileNotFoundError(
        "Could not find a Chromium-based browser. Set CV_PDF_CHROME_PATH or install google-chrome/chromium."
    )


def rewrite_root_relative_urls(html: str, site_root: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        target_path = site_root / match.group("path")
        return f"{match.group('prefix')}{target_path.resolve().as_uri()}"

    return ROOT_RELATIVE_ATTR_RE.sub(replace, html)


def prepare_render_input(input_html: Path) -> tuple[Path, str]:
    site_root = input_html.parents[2]
    html = input_html.read_text(encoding="utf-8")
    return site_root, rewrite_root_relative_urls(html, site_root)


def render_pdf_with_playwright(browser: str, input_html: Path, output_pdf: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    _site_root, rewritten_html = prepare_render_input(input_html)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cv-pdf-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        temp_html = temp_dir / "cv-print.html"
        temp_html.write_text(rewritten_html, encoding="utf-8")

        with sync_playwright() as playwright:
            browser_instance = playwright.chromium.launch(executable_path=browser, headless=True)
            page = browser_instance.new_page(viewport={"width": 1280, "height": 1800})
            page.goto(temp_html.resolve().as_uri(), wait_until="networkidle")
            page.evaluate("() => document.fonts.ready")
            page.emulate_media(media="screen")
            page.pdf(
                path=str(output_pdf.resolve()),
                format="A4",
                print_background=True,
                margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"},
                prefer_css_page_size=True,
            )
            browser_instance.close()

    return True


def render_pdf_with_cli(browser: str, input_html: Path, output_pdf: Path) -> None:
    _site_root, rewritten_html = prepare_render_input(input_html)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cv-pdf-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        temp_html = temp_dir / "cv-print.html"
        temp_html.write_text(rewritten_html, encoding="utf-8")

        user_data_dir = temp_dir / "chrome-profile"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        base_command = [
            browser,
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=15000",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={user_data_dir}",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={output_pdf.resolve()}",
            temp_html.resolve().as_uri(),
        ]

        commands = [
            [browser, "--headless=new", *base_command[1:]],
            [browser, "--headless", *base_command[1:]],
        ]

        last_error: subprocess.CalledProcessError | None = None
        for command in commands:
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                return
            except subprocess.CalledProcessError as exc:
                last_error = exc

        if last_error is not None:
            sys.stderr.write(last_error.stderr)
            raise last_error


def render_pdf(browser: str, input_html: Path, output_pdf: Path) -> None:
    if render_pdf_with_playwright(browser, input_html, output_pdf):
        return

    render_pdf_with_cli(browser, input_html, output_pdf)


def sync_source_pdf(generated_pdf: Path, source_pdf_arg: str) -> None:
    if not source_pdf_arg:
        return

    source_pdf = Path(source_pdf_arg)
    source_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated_pdf, source_pdf)


def main() -> int:
    args = parse_args()
    input_html = Path(args.input_html)
    output_pdf = Path(args.output_pdf)

    if not input_html.exists():
        raise FileNotFoundError(f"Rendered CV print page not found: {input_html}")

    browser = find_browser()
    render_pdf(browser, input_html, output_pdf)
    sync_source_pdf(output_pdf, args.sync_source_pdf)

    print(f"Generated CV PDF at {output_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
