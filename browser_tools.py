"""
AMABA Browser Automation Tools

smolagents Tool subclasses for Playwright-based browser automation.

IMPORTANT — smolagents >= 1.14 validates that Tool.forward() parameters
(after self) match exactly the keys of the class-level `inputs` dict.
Therefore tools that need a Playwright Page must NOT accept it as a forward()
argument. Instead they access a module-level `_page` reference that is set
externally before the agent runs.
"""

from __future__ import annotations

from typing import Any

from smolagents import Tool

# ---------------------------------------------------------------------------
# Module-level page reference.  Set this BEFORE invoking any agent that uses
# these tools, e.g.:  browser_tools._page = await context.new_page()
# ---------------------------------------------------------------------------
_page = None


def set_page(page):
    """Set the shared Playwright Page reference used by all tools."""
    global _page
    _page = page


def _get_page():
    """Return the current page, raising if unset."""
    if _page is None:
        raise RuntimeError(
            "Playwright page not initialised. Call browser_tools.set_page(page) first."
        )
    return _page


# ===========================================================================
# Navigation tools
# ===========================================================================

from typing import Dict, List
from playwright.sync_api import sync_playwright, Page, Browser, Playwright, TimeoutError
import logging

logger = logging.getLogger(__name__)

# --- Singleton Browser Manager ---
class BrowserManager:
    _instance = None
    
    def __init__(self):
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.page: Page = None
        self._initialize()

    def _initialize(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            context = self.browser.new_context()
            self.page = context.new_page()
            logger.info("Browser initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")

    @classmethod
    def get_page(cls) -> Page:
        if cls._instance is None:
            cls._instance = BrowserManager()
        return cls._instance.page

# Initialize the global page getter
def get_page() -> Page:
    return BrowserManager.get_page()

# --- Tools ---
class OpenURLTool(Tool):
    name = "open_url"
    description = "Navigate to a URL and wait for the page to load."
    inputs = {"url": {"type": "string", "description": "Target URL"}}
    output_type = "any"

    async def forward(self, url: str):
        page = _get_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)
        return True

    def forward(self, url: str):
        page = get_page()
        try:
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            return True
        except TimeoutError:
            raise

class WaitForLoadTool(Tool):
    name = "wait"
    description = "Wait for the page to reach network idle state."
    inputs = {}
    output_type = "any"

    async def forward(self):
        page = _get_page()
        await page.wait_for_load_state("networkidle")
        return True


    def forward(self):
        page = get_page()
        page.wait_for_load_state("networkidle")
        return True

class RefreshPageTool(Tool):
    name = "refresh_page"
    description = "Refresh/reload the current page."
    inputs = {}
    output_type = "any"

    async def forward(self):
        page = _get_page()
        await page.reload()
        return True


    def forward(self):
        page = get_page()
        page.reload()
        return True

class GoBackTool(Tool):
    name = "go_back"
    description = "Navigate back to the previous page."
    inputs = {}
    output_type = "any"

    async def forward(self):
        page = _get_page()
        await page.go_back()
        return True


    def forward(self):
        page = get_page()
        page.go_back()
        return True

class GoForwardTool(Tool):
    name = "go_forward"
    description = "Navigate forward to the next page."
    inputs = {}
    output_type = "any"

    async def forward(self):
        page = _get_page()
        await page.go_forward()
        return True


class NewTabTool(Tool):
    name = "new_tab"
    description = "Open a new tab and navigate to the specified URL. Returns the new Page."
    inputs = {"url": {"type": "string", "description": "Target URL"}}
    output_type = "any"

    async def forward(self, url: str):
        page = _get_page()
        context = page.context
        new_page = await context.new_page()
        await new_page.goto(url)
        await new_page.wait_for_load_state("domcontentloaded")
        await new_page.wait_for_timeout(2000)
        return new_page

    def forward(self):
        page = get_page()
        page.go_forward()
        return True

class NewTabTool(Tool):
    name = "new_tab"
    description = "Open a new tab and navigate to the specified URL."
    inputs = {"url": {"type": "string", "description": "Target URL"}}
    output_type = "any"

    def forward(self, url: str):
        page = get_page()
        context = page.context
        new_page = context.new_page()
        new_page.goto(url)
        new_page.wait_for_load_state("domcontentloaded")
        new_page.wait_for_timeout(2000)
        BrowserManager._instance.page = new_page # Update active page
        return True

class SwitchTabTool(Tool):
    name = "switch_tab"
    description = "Switch to a different tab/page by index."
    inputs = {"index": {"type": "number", "description": "Tab index"}}
    output_type = "any"

    async def forward(self, index: int):
        page = _get_page()
        pages = page.context.pages
        if index < len(pages):
            await pages[index].bring_to_front()
            return True
        return False


    def forward(self, index: int):
        page = get_page()
        pages = page.context.pages
        if index < len(pages):
            pages[index].bring_to_front()
            BrowserManager._instance.page = pages[index]
            return True
        return False

class CloseTabTool(Tool):
    name = "close_tab"
    description = "Close the current tab/page."
    inputs = {}
    output_type = "any"

    async def forward(self):
        page = _get_page()
        await page.close()
        return True


# ===========================================================================
# Interaction tools
# ===========================================================================

    def forward(self):
        page = get_page()
        page.close()
        # Fallback to the last open page
        pages = page.context.pages
        if pages:
            BrowserManager._instance.page = pages[-1]
        return True

class ClickTool(Tool):
    name = "click"
    description = "Click an element by selector."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "any"

    async def forward(self, selector: str):
        page = _get_page()
        await page.click(selector)
        return True


    def forward(self, selector: str):
        page = get_page()
        page.click(selector)
        return True

class FillTool(Tool):
    name = "fill"
    description = "Fill an input field with text."
    inputs = {
        "selector": {"type": "string", "description": "Input selector"},
        "text": {"type": "string", "description": "Text to enter"},
    }
    output_type = "any"

    async def forward(self, selector: str, text: str):
        page = _get_page()
        locator = page.locator(selector)
        await locator.click(timeout=10000)
        await locator.fill(text)
        return True


    def forward(self, selector: str, text: str):
        page = get_page()
        locator = page.locator(selector)
        locator.click(timeout=10000)
        locator.fill(text)
        return True

class PressTool(Tool):
    name = "press"
    description = "Press a specific key on an element."
    inputs = {
        "selector": {"type": "string", "description": "Element selector"},
        "key": {"type": "string", "description": "Key to press"},
    }
    output_type = "any"

    async def forward(self, selector: str, key: str):
        page = _get_page()
        await page.press(selector, key)
        return True


    def forward(self, selector: str, key: str):
        page = get_page()
        page.press(selector, key)
        return True

class ScrollTool(Tool):
    name = "scroll"
    description = "Scroll the page down by a given pixel amount."
    inputs = {"amount": {"type": "number", "description": "Scroll amount (px)", "nullable": True}}
    output_type = "any"

    async def forward(self, amount: int = None):
        page = _get_page()
        if amount is None:
            amount = 2000
        await page.evaluate(f"window.scrollBy(0, {amount});")
        return True


    def forward(self, amount: int = 2000):
        page = get_page()
        page.evaluate(f"window.scrollBy(0, {amount});")
        return True

class HoverTool(Tool):
    name = "hover"
    description = "Hover over an element."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "any"

    async def forward(self, selector: str):
        page = _get_page()
        await page.hover(selector)
        return True


# ===========================================================================
# Extraction tools
# ===========================================================================

    def forward(self, selector: str):
        page = get_page()
        page.hover(selector)
        return True

class ExtractTextTool(Tool):
    name = "extract_text"
    description = "Extract text content from an element selector."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "string"

    async def forward(self, selector: str) -> str:
        page = _get_page()
        return await page.locator(selector).inner_text()

    def forward(self, selector: str) -> str:
        page = get_page()
        return page.locator(selector).inner_text()

class ExtractLinksTool(Tool):
    name = "extract_links"
    description = "Extract href attributes from elements matching the selector."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "any"

    async def forward(self, selector: str) -> list[str]:
        page = _get_page()
        locator = page.locator(selector)
        elements = await locator.element_handles()
        links: list[str] = []
        for element in elements:
            href = await element.get_attribute("href")
    def forward(self, selector: str) -> List[str]:
        page = get_page()
        locator = page.locator(selector)
        elements = locator.element_handles()
        links = []
        for element in elements:
            href = element.get_attribute("href")
            if href:
                links.append(href)
        return links


class ExtractTableTool(Tool):
    name = "extract_table"
    description = "Extract table content as text."
    inputs = {"selector": {"type": "string", "description": "Table selector"}}
    output_type = "string"

    async def forward(self, selector: str) -> str:
        page = _get_page()
        return await page.locator(selector).inner_text()

    def forward(self, selector: str) -> str:
        page = get_page()
        return page.locator(selector).inner_text()

class ExtractFormFieldsTool(Tool):
    name = "extract_form_fields"
    description = "Extract basic form field values under a container selector."
    inputs = {"selector": {"type": "string", "description": "Container selector"}}
    output_type = "any"

    async def forward(self, selector: str) -> dict[str, str]:
        page = _get_page()
        container = page.locator(selector)
        input_elements = await container.locator("input").all()
        fields: dict[str, str] = {}
        for i, inp in enumerate(input_elements):
            name = await inp.get_attribute("name")
            value = await inp.input_value()
            fields[name or f"input_{i}"] = value
        return fields


    def forward(self, selector: str) -> Dict[str, str]:
        page = get_page()
        container = page.locator(selector)
        inputs = container.locator("input").all()
        fields = {}
        for i, inp in enumerate(inputs):
            name = inp.get_attribute("name")
            value = inp.input_value()
            fields[name or f"input_{i}"] = value
        return fields

class ExtractPageTitleTool(Tool):
    name = "extract_page_title"
    description = "Get the current page title."
    inputs = {}
    output_type = "string"

    async def forward(self) -> str:
        page = _get_page()
        return await page.title()

    def forward(self) -> str:
        page = get_page()
        return page.title()

class GetCurrentURLTool(Tool):
    name = "get_current_url"
    description = "Get the current page URL."
    inputs = {}
    output_type = "string"

    async def forward(self) -> str:
        page = _get_page()
        return page.url


    def forward(self) -> str:
        page = get_page()
        return page.url

class TakeScreenshotTool(Tool):
    name = "take_screenshot"
    description = "Take a screenshot and save it to a file path."
    inputs = {"path": {"type": "string", "description": "Output file path"}}
    output_type = "any"

    async def forward(self, path: str):
        page = _get_page()
        await page.screenshot(path=path)
        return True


# ===========================================================================
# Recovery tools (placeholders)
# ===========================================================================
    def forward(self, path: str):
        page = get_page()
        page.screenshot(path=path)
        return True


# --- Placeholders for recovery/debug/critique tools referenced by main.py ---

class RetryActionTool(Tool):
    name = "retry_action"
    description = "Placeholder for retrying an action after failure."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "retry_action_placeholder"

    def forward(self): return "retry_action_placeholder"

class CaptureFailureScreenshotTool(Tool):
    name = "capture_failure_screenshot"
    description = "Placeholder for capturing failure screenshot."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "capture_failure_screenshot_placeholder"

    def forward(self): return "capture_failure_screenshot_placeholder"

class AlternativeSelectorTool(Tool):
    name = "alternative_selector"
    description = "Placeholder for selecting alternative selector."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "alternative_selector_placeholder"

    def forward(self): return "alternative_selector_placeholder"

class RestartBrowserTool(Tool):
    name = "restart_browser"
    description = "Placeholder for restarting the browser."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "restart_browser_placeholder"

    def forward(self): return "restart_browser_placeholder"

class ReopenTabTool(Tool):
    name = "reopen_tab"
    description = "Placeholder for reopening a tab."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "reopen_tab_placeholder"

    def forward(self): return "reopen_tab_placeholder"

class GetLastErrorTool(Tool):
    name = "get_last_error"
    description = "Placeholder for returning last error."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "get_last_error_placeholder"

    def forward(self): return "get_last_error_placeholder"

class GetLastActionTool(Tool):
    name = "get_last_action"
    description = "Placeholder for returning last action."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "get_last_action_placeholder"

    def forward(self): return "get_last_action_placeholder"

class GetCurrentPageSnapshotTool(Tool):
    name = "get_current_page_snapshot"
    description = "Placeholder for returning a page snapshot."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "get_current_page_snapshot_placeholder"


# ===========================================================================
# Debug tools (placeholders)
# ===========================================================================
    def forward(self): return "get_current_page_snapshot_placeholder"

class ReadConsoleLogsTool(Tool):
    name = "read_console_logs"
    description = "Placeholder: read console logs."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "read_console_logs_placeholder"

    def forward(self): return "read_console_logs_placeholder"

class ReadNetworkLogsTool(Tool):
    name = "read_network_logs"
    description = "Placeholder: read network logs."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "read_network_logs_placeholder"

    def forward(self): return "read_network_logs_placeholder"

class InspectDOMTool(Tool):
    name = "inspect_dom"
    description = "Placeholder: inspect DOM."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "inspect_dom_placeholder"

    def forward(self): return "inspect_dom_placeholder"

class AnalyzeStacktraceTool(Tool):
    name = "analyze_stacktrace"
    description = "Placeholder: analyze stack trace."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "analyze_stacktrace_placeholder"

    def forward(self): return "analyze_stacktrace_placeholder"

class FindBrokenSelectorTool(Tool):
    name = "find_broken_selector"
    description = "Placeholder: find broken selector."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "find_broken_selector_placeholder"

    def forward(self): return "find_broken_selector_placeholder"

class AnalyzePlaywrightErrorTool(Tool):
    name = "analyze_playwright_error"
    description = "Placeholder: analyze playwright error."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "analyze_playwright_error_placeholder"

    def forward(self): return "analyze_playwright_error_placeholder"

class GenerateFixTool(Tool):
    name = "generate_fix"
    description = "Placeholder: generate a fix."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "generate_fix_placeholder"

    def forward(self): return "generate_fix_placeholder"

class GenerateSelectorTool(Tool):
    name = "generate_selector"
    description = "Placeholder: generate a selector."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "generate_selector_placeholder"

    def forward(self): return "generate_selector_placeholder"

class ExplainErrorTool(Tool):
    name = "explain_error"
    description = "Placeholder: explain error."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "explain_error_placeholder"


# ===========================================================================
# Critique / Verification tools (placeholders)
# ===========================================================================
    def forward(self): return "explain_error_placeholder"

class VerifyURLTool(Tool):
    name = "verify_url"
    description = "Placeholder: verify url."
    inputs = {"expected_url": {"type": "string", "description": "Expected URL"}}
    output_type = "string"

    async def forward(self, expected_url: str):
        return "verify_url_placeholder"

    def forward(self, expected_url: str): return "verify_url_placeholder"

class VerifyTitleTool(Tool):
    name = "verify_title"
    description = "Placeholder: verify title."
    inputs = {"expected_title": {"type": "string", "description": "Expected title"}}
    output_type = "string"

    async def forward(self, expected_title: str):
        return "verify_title_placeholder"

    def forward(self, expected_title: str): return "verify_title_placeholder"

class VerifyTextExistsTool(Tool):
    name = "verify_text_exists"
    description = "Placeholder: verify text exists."
    inputs = {
        "selector": {"type": "string", "description": "Selector"},
        "expected_text": {"type": "string", "description": "Expected text"},
    }
    output_type = "string"

    async def forward(self, selector: str, expected_text: str):
        return "verify_text_exists_placeholder"

    def forward(self, selector: str, expected_text: str): return "verify_text_exists_placeholder"

class VerifyElementExistsTool(Tool):
    name = "verify_element_exists"
    description = "Placeholder: verify element exists."
    inputs = {"selector": {"type": "string", "description": "Selector"}}
    output_type = "string"

    async def forward(self, selector: str):
        return "verify_element_exists_placeholder"

    def forward(self, selector: str): return "verify_element_exists_placeholder"

class VerifyPageLoadedTool(Tool):
    name = "verify_page_loaded"
    description = "Placeholder: verify page loaded."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "verify_page_loaded_placeholder"

    def forward(self): return "verify_page_loaded_placeholder"

class VerifyTaskCompletionTool(Tool):
    name = "verify_task_completion"
    description = "Placeholder: verify task completion."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "verify_task_completion_placeholder"

    def forward(self): return "verify_task_completion_placeholder"

class CompareExpectedVsActualTool(Tool):
    name = "compare_expected_vs_actual"
    description = "Placeholder: compare expected vs actual."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "compare_expected_vs_actual_placeholder"

    def forward(self): return "compare_expected_vs_actual_placeholder"

class ValidateExtractedDataTool(Tool):
    name = "validate_extracted_data"
    description = "Placeholder: validate extracted data."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "validate_extracted_data_placeholder"

    def forward(self): return "validate_extracted_data_placeholder"

class ValidateOutputQualityTool(Tool):
    name = "validate_output_quality"
    description = "Placeholder: validate output quality."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "validate_output_quality_placeholder"


# ===========================================================================
# Instantiate tools with the variable names orchestration.py expects
# ===========================================================================

# Navigation
    def forward(self): return "validate_output_quality_placeholder"


# Instantiate tools with the variable names main.py expects
open_url = OpenURLTool()
wait_for_load = WaitForLoadTool()
wait = WaitForLoadTool()
refresh_page = RefreshPageTool()
go_back = GoBackTool()
go_forward = GoForwardTool()
new_tab = NewTabTool()
switch_tab = SwitchTabTool()
close_tab = CloseTabTool()

# Interaction
click = ClickTool()
fill = FillTool()
press = PressTool()
scroll = ScrollTool()
hover = HoverTool()

# Extraction
extract_text = ExtractTextTool()
extract_links = ExtractLinksTool()
extract_table = ExtractTableTool()
extract_form_fields = ExtractFormFieldsTool()
extract_page_title = ExtractPageTitleTool()
get_current_url = GetCurrentURLTool()
take_screenshot = TakeScreenshotTool()

# Recovery
retry_action = RetryActionTool()
capture_failure_screenshot = CaptureFailureScreenshotTool()
alternative_selector = AlternativeSelectorTool()
restart_browser = RestartBrowserTool()
reopen_tab = ReopenTabTool()
get_last_error = GetLastErrorTool()
get_last_action = GetLastActionTool()
get_current_page_snapshot = GetCurrentPageSnapshotTool()

# Debug
read_console_logs = ReadConsoleLogsTool()
read_network_logs = ReadNetworkLogsTool()
inspect_dom = InspectDOMTool()
analyze_stacktrace = AnalyzeStacktraceTool()
find_broken_selector = FindBrokenSelectorTool()
analyze_playwright_error = AnalyzePlaywrightErrorTool()
generate_fix = GenerateFixTool()
generate_selector = GenerateSelectorTool()
explain_error = ExplainErrorTool()

# Critique
verify_url = VerifyURLTool()
verify_title = VerifyTitleTool()
verify_text_exists = VerifyTextExistsTool()
verify_element_exists = VerifyElementExistsTool()
verify_page_loaded = VerifyPageLoadedTool()
verify_task_completion = VerifyTaskCompletionTool()
compare_expected_vs_actual = CompareExpectedVsActualTool()
validate_extracted_data = ValidateExtractedDataTool()
validate_output_quality = ValidateOutputQualityTool()
