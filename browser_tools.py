from __future__ import annotations

from typing import Any

from playwright.async_api import Page, TimeoutError
from smolagents import Tool


# Note: Your installed smolagents version (1.26.0) requires Tool subclasses to
# define class attributes: name, description, inputs, output_type.


class OpenURLTool(Tool):
    name = "open_url"
    description = "Navigate to a URL and wait for the page to load."
    inputs = {"url": {"type": "string", "description": "Target URL"}}
    output_type = "any"

    async def forward(self, url: str):

        try:
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)
            return True
        except TimeoutError:
            raise


class WaitForLoadTool(Tool):
    name = "wait"
    description = "Wait for the page to reach network idle state."
    inputs = {"page": {"type": "any", "description": "Playwright Page"}}
    output_type = "any"

    async def forward(self, page: Page):
        await page.wait_for_load_state("networkidle")
        return True



class RefreshPageTool(Tool):
    name = "refresh_page"
    description = "Refresh/reload the current page."
    inputs = {}
    output_type = "any"

    async def forward(self, page: Page):
        await page.reload()
        return True


class GoBackTool(Tool):
    name = "go_back"
    description = "Navigate back to the previous page."
    inputs = {}
    output_type = "any"

    async def forward(self, page: Page):
        await page.go_back()
        return True


class GoForwardTool(Tool):
    name = "go_forward"
    description = "Navigate forward to the next page."
    inputs = {}
    output_type = "any"

    async def forward(self, page: Page):
        await page.go_forward()
        return True


class NewTabTool(Tool):
    name = "new_tab"
    description = "Open a new tab and navigate to the specified URL. Returns the new Page."
    inputs = {"url": {"type": "string", "description": "Target URL"}}
    output_type = "any"

    async def forward(self, page: Page, url: str):
        context = page.context
        new_page = await context.new_page()
        await new_page.goto(url)
        await new_page.wait_for_load_state("domcontentloaded")
        await new_page.wait_for_timeout(2000)
        return new_page


class SwitchTabTool(Tool):
    name = "switch_tab"
    description = "Switch to a different tab/page by index."
    inputs = {"index": {"type": "number", "description": "Tab index"}}
    output_type = "any"

    async def forward(self, page: Page, index: int):
        pages = page.context.pages
        if index < len(pages):
            await pages[index].bring_to_front()
            return True
        return False


class CloseTabTool(Tool):
    name = "close_tab"
    description = "Close the current tab/page."
    inputs = {}
    output_type = "any"

    async def forward(self, page: Page):
        await page.close()
        return True


class ClickTool(Tool):
    name = "click"
    description = "Click an element by selector."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "any"

    async def forward(self, page: Page, selector: str):
        await page.click(selector)
        return True


class FillTool(Tool):
    name = "fill"
    description = "Fill an input field with text."
    inputs = {
        "selector": {"type": "string", "description": "Input selector"},
        "text": {"type": "string", "description": "Text to enter"},
    }
    output_type = "any"

    async def forward(self, page: Page, selector: str, text: str):
        locator = page.locator(selector)
        await locator.click(timeout=10000)
        await locator.fill(text)
        return True


class PressTool(Tool):
    name = "press"
    description = "Press a specific key on an element."
    inputs = {
        "selector": {"type": "string", "description": "Element selector"},
        "key": {"type": "string", "description": "Key to press"},
    }
    output_type = "any"

    async def forward(self, page: Page, selector: str, key: str):
        await page.press(selector, key)
        return True


class ScrollTool(Tool):
    name = "scroll"
    description = "Scroll the page down by a given pixel amount."
    inputs = {"amount": {"type": "number", "description": "Scroll amount (px)"}}
    output_type = "any"

    async def forward(self, page: Page, amount: int = 2000):
        await page.evaluate(f"window.scrollBy(0, {amount});")
        return True


class HoverTool(Tool):
    name = "hover"
    description = "Hover over an element."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "any"

    async def forward(self, page: Page, selector: str):
        await page.hover(selector)
        return True


class ExtractTextTool(Tool):
    name = "extract_text"
    description = "Extract text content from an element selector."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "string"

    async def forward(self, page: Page, selector: str) -> str:
        return await page.locator(selector).inner_text()


class ExtractLinksTool(Tool):
    name = "extract_links"
    description = "Extract href attributes from elements matching the selector."
    inputs = {"selector": {"type": "string", "description": "Element selector"}}
    output_type = "any"

    async def forward(self, page: Page, selector: str) -> list[str]:
        locator = page.locator(selector)
        elements = await locator.element_handles()
        links: list[str] = []
        for element in elements:
            href = await element.get_attribute("href")
            if href:
                links.append(href)
        return links


class ExtractTableTool(Tool):
    name = "extract_table"
    description = "Extract table content as text."
    inputs = {"selector": {"type": "string", "description": "Table selector"}}
    output_type = "string"

    async def forward(self, page: Page, selector: str) -> str:
        return await page.locator(selector).inner_text()


class ExtractFormFieldsTool(Tool):
    name = "extract_form_fields"
    description = "Extract basic form field values under a container selector."
    inputs = {"selector": {"type": "string", "description": "Container selector"}}
    output_type = "any"

    async def forward(self, page: Page, selector: str) -> dict[str, str]:
        container = page.locator(selector)
        inputs = await container.locator("input").all()
        fields: dict[str, str] = {}
        for i, inp in enumerate(inputs):
            name = await inp.get_attribute("name")
            value = await inp.input_value()
            fields[name or f"input_{i}"] = value
        return fields


class ExtractPageTitleTool(Tool):
    name = "extract_page_title"
    description = "Get the current page title."
    inputs = {}
    output_type = "string"

    async def forward(self, page: Page) -> str:
        return await page.title()


class GetCurrentURLTool(Tool):
    name = "get_current_url"
    description = "Get the current page URL."
    inputs = {}
    output_type = "string"

    async def forward(self, page: Page) -> str:
        return page.url


class TakeScreenshotTool(Tool):
    name = "take_screenshot"
    description = "Take a screenshot and save it to a file path."
    inputs = {"path": {"type": "string", "description": "Output file path"}}
    output_type = "any"

    async def forward(self, page: Page, path: str):
        await page.screenshot(path=path)
        return True


# --- Placeholders for recovery/debug/critique tools referenced by main.py ---


class RetryActionTool(Tool):
    name = "retry_action"
    description = "Placeholder for retrying an action after failure."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "retry_action_placeholder"


class CaptureFailureScreenshotTool(Tool):
    name = "capture_failure_screenshot"
    description = "Placeholder for capturing failure screenshot."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "capture_failure_screenshot_placeholder"


class AlternativeSelectorTool(Tool):
    name = "alternative_selector"
    description = "Placeholder for selecting alternative selector."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "alternative_selector_placeholder"


class RestartBrowserTool(Tool):
    name = "restart_browser"
    description = "Placeholder for restarting the browser."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "restart_browser_placeholder"


class ReopenTabTool(Tool):
    name = "reopen_tab"
    description = "Placeholder for reopening a tab."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "reopen_tab_placeholder"


class GetLastErrorTool(Tool):
    name = "get_last_error"
    description = "Placeholder for returning last error."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "get_last_error_placeholder"


class GetLastActionTool(Tool):
    name = "get_last_action"
    description = "Placeholder for returning last action."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "get_last_action_placeholder"


class GetCurrentPageSnapshotTool(Tool):
    name = "get_current_page_snapshot"
    description = "Placeholder for returning a page snapshot."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "get_current_page_snapshot_placeholder"


class ReadConsoleLogsTool(Tool):
    name = "read_console_logs"
    description = "Placeholder: read console logs."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "read_console_logs_placeholder"


class ReadNetworkLogsTool(Tool):
    name = "read_network_logs"
    description = "Placeholder: read network logs."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "read_network_logs_placeholder"


class InspectDOMTool(Tool):
    name = "inspect_dom"
    description = "Placeholder: inspect DOM."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "inspect_dom_placeholder"


class AnalyzeStacktraceTool(Tool):
    name = "analyze_stacktrace"
    description = "Placeholder: analyze stack trace."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "analyze_stacktrace_placeholder"


class FindBrokenSelectorTool(Tool):
    name = "find_broken_selector"
    description = "Placeholder: find broken selector."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "find_broken_selector_placeholder"


class AnalyzePlaywrightErrorTool(Tool):
    name = "analyze_playwright_error"
    description = "Placeholder: analyze playwright error."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "analyze_playwright_error_placeholder"


class GenerateFixTool(Tool):
    name = "generate_fix"
    description = "Placeholder: generate a fix."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "generate_fix_placeholder"


class GenerateSelectorTool(Tool):
    name = "generate_selector"
    description = "Placeholder: generate a selector."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "generate_selector_placeholder"


class ExplainErrorTool(Tool):
    name = "explain_error"
    description = "Placeholder: explain error."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "explain_error_placeholder"


class VerifyURLTool(Tool):
    name = "verify_url"
    description = "Placeholder: verify url."
    inputs = {"expected_url": {"type": "string", "description": "Expected URL"}}
    output_type = "string"

    async def forward(self, expected_url: str):
        return "verify_url_placeholder"


class VerifyTitleTool(Tool):
    name = "verify_title"
    description = "Placeholder: verify title."
    inputs = {"expected_title": {"type": "string", "description": "Expected title"}}
    output_type = "string"

    async def forward(self, expected_title: str):
        return "verify_title_placeholder"


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


class VerifyElementExistsTool(Tool):
    name = "verify_element_exists"
    description = "Placeholder: verify element exists."
    inputs = {"selector": {"type": "string", "description": "Selector"}}
    output_type = "string"

    async def forward(self, selector: str):
        return "verify_element_exists_placeholder"


class VerifyPageLoadedTool(Tool):
    name = "verify_page_loaded"
    description = "Placeholder: verify page loaded."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "verify_page_loaded_placeholder"


class VerifyTaskCompletionTool(Tool):
    name = "verify_task_completion"
    description = "Placeholder: verify task completion."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "verify_task_completion_placeholder"


class CompareExpectedVsActualTool(Tool):
    name = "compare_expected_vs_actual"
    description = "Placeholder: compare expected vs actual."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "compare_expected_vs_actual_placeholder"


class ValidateExtractedDataTool(Tool):
    name = "validate_extracted_data"
    description = "Placeholder: validate extracted data."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "validate_extracted_data_placeholder"


class ValidateOutputQualityTool(Tool):
    name = "validate_output_quality"
    description = "Placeholder: validate output quality."
    inputs = {}
    output_type = "string"

    async def forward(self):
        return "validate_output_quality_placeholder"


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
click = ClickTool()
fill = FillTool()
press = PressTool()
scroll = ScrollTool()
hover = HoverTool()
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

