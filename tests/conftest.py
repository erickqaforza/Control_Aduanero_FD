import os
import re
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from pages.control_aduanero_page import ControlAduaneroPage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@pytest.fixture
def page(base_url):
    project_root = Path(__file__).resolve().parent.parent
    browser_channel = os.getenv("BROWSER_CHANNEL", "msedge")
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    slow_mo = int(os.getenv("SLOW_MO", "0"))
    record_video = os.getenv("RECORD_VIDEO", "true").lower() == "true"
    video_dir = project_root / os.getenv("VIDEO_DIR", "videos")
    trace_dir = project_root / "trace_tests"
    video_dir.mkdir(parents=True, exist_ok=True)
    trace_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel=browser_channel,
            headless=headless,
            slow_mo=slow_mo,
            args=["--start-maximized"],
        )
        context_options = {
            "base_url": base_url,
            "no_viewport": True,
            "timezone_id": "America/Guatemala",
            "locale": "es-GT",
        }
        if record_video:
            context_options["record_video_dir"] = str(video_dir)
            context_options["record_video_size"] = {"width": 1920, "height": 1080}

        context = browser.new_context(
            **context_options,
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        test_page = context.new_page()
        yield test_page

        test_name = os.environ.get("PYTEST_CURRENT_TEST", "test").split(" ")[0]
        safe_test_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_name)
        trace_path = trace_dir / f"trace_{safe_test_name}.zip"

        context.tracing.stop(path=str(trace_path))
        context.close()

        if record_video and test_page.video:
            video_path = Path(test_page.video.path())
            final_video_path = video_dir / f"{safe_test_name}.webm"
            if video_path.exists():
                if final_video_path.exists():
                    final_video_path.unlink()
                video_path.rename(final_video_path)
                allure.attach.file(
                    str(final_video_path),
                    name="Video de ejecucion",
                    attachment_type="video/webm",
                    extension="webm",
                )

        browser.close()


@pytest.fixture
def control_aduanero_page(page):
    return ControlAduaneroPage(page)
