"""Main FastAPI application for JEV for Dummies."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import router
from app.typesafe import (
    TypeSafeConfigError,
    TypeSafeUpstreamError,
    close_http_client,
)

# Load environment variables from .env if present
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager for setup and teardown."""
    yield
    # Clean up persistent HTTP client
    await close_http_client()


app = FastAPI(
    title="JEV for Dummies",
    description=(
        "A tiny, open-source, self-hosted HTTP API wrapper around TypeSafe's Jev. "
        "Turns Jev's decision primitives into simple HTTP GET requests."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,  # We serve modern Scalar UI at /docs and Swagger UI at /swagger
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/", include_in_schema=False)
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def simple_docs() -> HTMLResponse:
    """Serve a super simple, human, beginner-friendly interactive tester."""
    html_content = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>JEV for Dummies - API Documentation & Playground</title>
    <style>
      *, *::before, *::after {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        padding: 32px 16px 64px 16px;
        background-color: #f8fafc;
        color: #0f172a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.5;
        -webkit-font-smoothing: antialiased;
      }

      .container {
        max-width: 1060px;
        margin: 0 auto;
      }

      /* Header */
      .header {
        margin-bottom: 24px;
      }

      .header-top {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .brand h1 {
        font-size: 24px;
        font-weight: 700;
        margin: 0;
        color: #0f172a;
        letter-spacing: -0.5px;
      }

      .version-badge {
        background: #f1f5f9;
        color: #475569;
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
      }

      .header p {
        font-size: 14px;
        color: #64748b;
        margin: 0;
      }

      /* Route Tabs */
      .route-tabs {
        display: flex;
        gap: 6px;
        background: #f1f5f9;
        padding: 5px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        overflow-x: auto;
      }

      .route-tab {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border: none;
        background: transparent;
        color: #64748b;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 13px;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s ease;
        white-space: nowrap;
      }

      .route-tab:hover {
        color: #0f172a;
        background: rgba(255, 255, 255, 0.6);
      }

      .route-tab.active {
        background: #ffffff;
        color: #0f172a;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
      }

      .method-pill {
        background: #e0e7ff;
        color: #3730a3;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        letter-spacing: 0.5px;
      }

      /* ========================================================== */
      /* Top Grid: Left (Request Section) & Right (Main Panel Form) */
      /* ========================================================== */
      .playground-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        align-items: start;
        margin-bottom: 24px;
      }

      @media (max-width: 880px) {
        .playground-grid {
          grid-template-columns: 1fr;
          gap: 20px;
        }
      }

      .card-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        padding: 22px;
      }

      .pane-col-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 18px;
        flex-wrap: wrap;
        gap: 8px;
      }

      .pane-col-title {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: #334155;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .pane-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        background: #f1f5f9;
        color: #64748b;
        letter-spacing: 0;
        text-transform: none;
      }

      .pane-badge.upstream {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
      }

      /* Left Side Inspector Sub-cards */
      .req-sub-stack {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }

      .inspect-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
      }

      .inspect-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        gap: 8px;
        flex-wrap: wrap;
      }

      .inspect-card-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #475569;
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .copy-btn {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        color: #334155;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s ease;
        white-space: nowrap;
      }

      .copy-btn:hover {
        background: #f1f5f9;
        color: #0f172a;
      }

      .copy-btn.copied {
        background: #ecfdf5;
        border-color: #a7f3d0;
        color: #059669;
        font-weight: 700;
      }

      /* Request URL Box */
      .req-url-box {
        padding: 12px 14px;
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 12px;
        background: #ffffff;
        min-width: 0;
      }

      .req-method {
        font-weight: 700;
        color: #2563eb;
        white-space: nowrap;
        flex-shrink: 0;
        padding-top: 1px;
      }

      .req-url-text {
        min-width: 0;
        flex: 1 1 0%;
        word-break: break-all;
        overflow-wrap: anywhere;
        line-height: 1.5;
        color: #0f172a;
      }

      /* Explanatory Footnote */
      .explain-note {
        padding: 8px 12px;
        font-size: 11px;
        color: #64748b;
        background: #f8fafc;
        border-top: 1px solid #f1f5f9;
        line-height: 1.4;
      }

      /* Code pre styling */
      pre {
        margin: 0;
        background: #090d16;
        padding: 12px 14px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 11.5px;
        overflow-x: auto;
        line-height: 1.45;
        white-space: pre-wrap;
        word-break: break-all;
        width: 100%;
        box-sizing: border-box;
      }

      pre.code-req {
        color: #a5f3fc;
      }

      pre.code-res {
        color: #38bdf8;
      }

      /* Right Side Main Panel Banner */
      .endpoint-banner {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 12px;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }

      .banner-method {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #dbeafe;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 12px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
      }

      .banner-path {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
      }

      .banner-desc {
        margin-left: auto;
        font-size: 12px;
        color: #64748b;
      }

      /* Example presets */
      .presets-bar {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
        margin-bottom: 16px;
        background: #f8fafc;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #f1f5f9;
      }

      .presets-title {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
      }

      .preset-chip {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        color: #334155;
        font-size: 11.5px;
        font-weight: 500;
        padding: 2px 9px;
        border-radius: 9999px;
        cursor: pointer;
        transition: all 0.15s ease;
      }

      .preset-chip:hover {
        background: #f1f5f9;
        border-color: #94a3b8;
        color: #0f172a;
      }

      /* Parameters Section */
      .section-heading {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 12px;
      }

      .param-group {
        margin-bottom: 16px;
      }

      .param-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
      }

      .req-star {
        color: #dc2626;
        font-weight: 700;
        font-size: 14px;
        line-height: 1;
        user-select: none;
      }

      .param-name {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 13px;
        font-weight: 700;
        color: #0f172a;
      }

      .param-desc {
        font-size: 11.5px;
        color: #64748b;
        margin-bottom: 6px;
      }

      .param-input, .param-textarea {
        width: 100%;
        padding: 9px 12px;
        font-size: 13.5px;
        font-family: inherit;
        color: #0f172a;
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        outline: none;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
      }

      .param-input:focus, .param-textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
      }

      .param-textarea {
        resize: vertical;
        min-height: 64px;
      }

      .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }

      /* Execute Button */
      .btn-execute {
        display: block;
        width: 100%;
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 600;
        color: #ffffff;
        background: #0f172a;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.15s ease, transform 0.05s ease;
        margin-top: 14px;
      }

      .btn-execute:hover {
        background: #1e293b;
      }

      .btn-execute:active {
        transform: translateY(1px);
      }

      .btn-execute:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      /* ========================================================== */
      /* Underneath: Response Section (Only Appears After Request)  */
      /* ========================================================== */
      .response-card {
        display: none;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        padding: 22px;
        margin-top: 20px;
      }

      .response-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 16px;
        flex-wrap: wrap;
        gap: 8px;
      }

      .response-meta {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .status-tag {
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
      }

      .status-tag.ok {
        background: #ecfdf5;
        color: #059669;
      }

      .status-tag.err {
        background: #fef2f2;
        color: #dc2626;
      }

      .status-tag.ready {
        background: #f1f5f9;
        color: #64748b;
        border: 1px solid #e2e8f0;
      }

      .duration-tag {
        font-size: 11px;
        color: #64748b;
      }

      /* Key Result Pill */
      .result-summary-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 16px;
      }

      .result-summary-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 2px;
      }

      .result-summary-value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 18px;
        font-weight: 700;
        color: #0f172a;
      }

      .result-summary-meta {
        font-size: 12px;
        color: #64748b;
        font-weight: 500;
      }

      .footer {
        text-align: center;
        margin-top: 32px;
        font-size: 12px;
        color: #94a3b8;
      }

      .footer a {
        color: #64748b;
        text-decoration: underline;
      }

      .footer a:hover {
        color: #0f172a;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <div class="header-top">
          <div class="brand">
            <h1>JEV for Dummies</h1>
            <span class="version-badge">v0.1.0</span>
          </div>
        </div>
        <p>A tiny, self-hosted HTTP API wrapper turning TypeSafe Jev decision primitives into simple HTTP GET requests.</p>
      </div>

      <!-- Route Navigation Tabs -->
      <div class="route-tabs" role="tablist">
        <button class="route-tab active" id="tab-choice" onclick="selectEndpoint('choice')">
          <span class="method-pill">GET</span>
          <span>/choice</span>
        </button>
        <button class="route-tab" id="tab-noul" onclick="selectEndpoint('noul')">
          <span class="method-pill">GET</span>
          <span>/noul</span>
        </button>
        <button class="route-tab" id="tab-score" onclick="selectEndpoint('score')">
          <span class="method-pill">GET</span>
          <span>/score</span>
        </button>
        <button class="route-tab" id="tab-health" onclick="selectEndpoint('health')">
          <span class="method-pill">GET</span>
          <span>/health</span>
        </button>
      </div>

      <!-- ========================================================= -->
      <!-- Top Grid: Request Section (Left) & Main Panel Form (Right) -->
      <!-- ========================================================= -->
      <div class="playground-grid">
        <!-- 1. LEFT SIDE: Request Section (Constructed Live Before Sending) -->
        <div class="card-panel">
          <div class="pane-col-header">
            <div class="pane-col-title">
              <span>Request Details</span>
              <span class="pane-badge">HTTP GET + JEV</span>
            </div>
          </div>

          <div class="req-sub-stack">
            <!-- 1a. Constructed HTTP Request URL -->
            <div class="inspect-card">
              <div class="inspect-card-header">
                <div class="inspect-card-title">HTTP Request URL</div>
                <button type="button" class="copy-btn" id="btn-copy-url" onclick="copyConstructedUrl()">Copy URL</button>
              </div>
              <div class="req-url-box">
                <span class="req-method">GET</span>
                <span class="req-url-text" id="live-url-text">http://...</span>
              </div>
            </div>

            <!-- 1b. Raw TypeSafe JEV Request (Structured JSON) -->
            <div class="inspect-card">
              <div class="inspect-card-header">
                <div class="inspect-card-title">
                  <span>Raw JEV Request</span>
                  <span class="pane-badge upstream">POST /v1/systemone</span>
                </div>
                <button type="button" class="copy-btn" id="btn-copy-payload" onclick="copyRawJevJson()">Copy Payload</button>
              </div>
              <pre class="code-req"><code id="raw-jev-json">{}</code></pre>
              <div class="explain-note">
                ⚡ <strong>Under the hood:</strong> JEV for Dummies translates your simple GET into this TypeSafe System One payload.
              </div>
            </div>
          </div>
        </div>

        <!-- 2. RIGHT SIDE: Main Panel Form (Query Parameters & Send Button) -->
        <div class="card-panel">
          <!-- Endpoint Banner -->
          <div class="endpoint-banner">
            <span class="banner-method">GET</span>
            <span class="banner-path" id="banner-path">/choice</span>
            <span class="banner-desc" id="banner-desc">Evaluate input text against candidate options</span>
          </div>

          <!-- /choice Panel -->
          <div id="panel-choice" class="endpoint-panel">
            <div class="presets-bar">
              <span class="presets-title">Quick Presets:</span>
              <button class="preset-chip" onclick="setChoice('Win a free brand new car! Click here now.', 'scam, not scam')">Scam Filter</button>
              <button class="preset-chip" onclick="setChoice('This was the most delicious pizza I have ever had.', 'positive, neutral, negative')">Sentiment</button>
              <button class="preset-chip" onclick="setChoice('Production database is down and customers cannot checkout.', 'urgent, high, normal, low')">Ticket Priority</button>
            </div>

            <div class="section-heading">Query Parameters</div>

            <div class="param-group">
              <div class="param-meta">
                <span class="req-star">*</span>
                <code class="param-name">input</code>
              </div>
              <div class="param-desc">The content string to evaluate.</div>
              <textarea class="param-textarea" id="choice-input" placeholder="e.g. Win a free car">Win a free brand new car! Click here now.</textarea>
            </div>

            <div class="param-group">
              <div class="param-meta">
                <span class="req-star">*</span>
                <code class="param-name">choices</code>
              </div>
              <div class="param-desc">Comma-separated candidate options (minimum 2).</div>
              <input type="text" class="param-input" id="choice-options" value="scam, not scam" placeholder="e.g. scam, not scam" />
            </div>
          </div>

          <!-- /noul Panel -->
          <div id="panel-noul" class="endpoint-panel" style="display: none;">
            <div class="presets-bar">
              <span class="presets-title">Quick Presets:</span>
              <button class="preset-chip" onclick="setNoul('Win a free brand new car! Click here now.', 'Is this a scam?')">Is this a scam?</button>
              <button class="preset-chip" onclick="setNoul('Our team successfully shipped version 2.0 ahead of schedule!', 'Is this positive news?')">Is this positive?</button>
              <button class="preset-chip" onclick="setNoul('Where can I download my annual billing receipt?', 'Is this asking a question?')">Is it a question?</button>
            </div>

            <div class="section-heading">Query Parameters</div>

            <div class="param-group">
              <div class="param-meta">
                <span class="req-star">*</span>
                <code class="param-name">input</code>
              </div>
              <div class="param-desc">The content string to evaluate.</div>
              <textarea class="param-textarea" id="noul-input" placeholder="e.g. Win a free car">Win a free brand new car! Click here now.</textarea>
            </div>

            <div class="param-group">
              <div class="param-meta">
                <span class="req-star">*</span>
                <code class="param-name">question</code>
              </div>
              <div class="param-desc">The yes/no question or proposition to test against the input.</div>
              <input type="text" class="param-input" id="noul-question" value="Is this a scam?" placeholder="e.g. Is this a scam?" />
            </div>
          </div>

          <!-- /score Panel -->
          <div id="panel-score" class="endpoint-panel" style="display: none;">
            <div class="presets-bar">
              <span class="presets-title">Quick Presets:</span>
              <button class="preset-chip" onclick="setScore('This was an extraordinary performance by the whole cast!', 'How positive is this review?', 0, 10)">Review (0-10)</button>
              <button class="preset-chip" onclick="setScore('User is threatening violence against staff in chat.', 'How severe is this violation?', 1, 5)">Severity (1-5)</button>
            </div>

            <div class="section-heading">Query Parameters</div>

            <div class="param-group">
              <div class="param-meta">
                <span class="req-star">*</span>
                <code class="param-name">input</code>
              </div>
              <div class="param-desc">The content string to evaluate.</div>
              <textarea class="param-textarea" id="score-input" placeholder="e.g. Content to rate...">This was an extraordinary performance by the whole cast!</textarea>
            </div>

            <div class="param-group">
              <div class="param-meta">
                <span class="req-star">*</span>
                <code class="param-name">question</code>
              </div>
              <div class="param-desc">The rating question or dimension to score.</div>
              <input type="text" class="param-input" id="score-question" value="How positive is this review?" placeholder="e.g. How positive is this review?" />
            </div>

            <div class="grid-2">
              <div class="param-group">
                <div class="param-meta">
                  <span class="req-star">*</span>
                  <code class="param-name">min</code>
                </div>
                <div class="param-desc">Minimum score value.</div>
                <input type="number" class="param-input" id="score-min" value="0" />
              </div>
              <div class="param-group">
                <div class="param-meta">
                  <span class="req-star">*</span>
                  <code class="param-name">max</code>
                </div>
                <div class="param-desc">Maximum score value (must be > min).</div>
                <input type="number" class="param-input" id="score-max" value="10" />
              </div>
            </div>
          </div>

          <!-- /health Panel -->
          <div id="panel-health" class="endpoint-panel" style="display: none;">
            <div class="section-heading">Endpoint Details</div>
            <p style="font-size: 13px; color: #64748b; margin: 0 0 16px 0;">This endpoint takes no parameters. It checks if the service is running and ready to accept requests.</p>
          </div>

          <!-- Execute Button -->
          <button class="btn-execute" id="btn-execute" onclick="sendApiRequest()">Send Request</button>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- Underneath: Response Section (Only Appears After Request)  -->
      <!-- ========================================================= -->
      <div class="response-card" id="response-section">
        <div class="response-card-header">
          <div class="pane-col-title">Response / Output</div>
          <div class="response-meta">
            <span class="status-tag ok" id="status-tag">200 OK</span>
            <span class="duration-tag" id="duration-tag"></span>
          </div>
        </div>

        <!-- Decision Result Highlight Card -->
        <div class="result-summary-box" id="result-summary-box">
          <div>
            <div class="result-summary-label">Decision Result</div>
            <div class="result-summary-value" id="result-summary-value">—</div>
          </div>
          <div class="result-summary-meta" id="result-summary-meta"></div>
        </div>

        <!-- Full Response Body (JSON) -->
        <div class="inspect-card">
          <div class="inspect-card-header">
            <div class="inspect-card-title">Response Body (JSON)</div>
            <button type="button" class="copy-btn" id="btn-copy-response" onclick="copyResponseJson()">Copy JSON</button>
          </div>
          <pre class="code-res"><code id="response-json">{}</code></pre>
        </div>
      </div>

      <div class="footer">
        JEV for Dummies • Raw HTTP Wrapper for TypeSafe Jev • <a href="/swagger">Advanced Swagger Docs</a>
      </div>
    </div>

    <script>
      let currentEndpoint = 'choice';

      const descriptions = {
        choice: 'Evaluate input text against candidate options',
        noul: 'Evaluate a yes/no question against an input text (boolean decision)',
        score: 'Score input text along a custom numerical scale (min to max)',
        health: 'Check server availability and health status'
      };

      function encodeQueryParam(str) {
        return encodeURIComponent(str || '')
          .replace(/%20/g, '+')
          .replace(/%2C/gi, ',');
      }

      function getConstructedUrl() {
        const origin = window.location.origin;
        if (currentEndpoint === 'choice') {
          const input = document.getElementById('choice-input') ? document.getElementById('choice-input').value : '';
          const choices = document.getElementById('choice-options') ? document.getElementById('choice-options').value : '';
          return origin + '/choice?input=' + encodeQueryParam(input) + '&choices=' + encodeQueryParam(choices);
        } else if (currentEndpoint === 'noul') {
          const input = document.getElementById('noul-input') ? document.getElementById('noul-input').value : '';
          const question = document.getElementById('noul-question') ? document.getElementById('noul-question').value : '';
          return origin + '/noul?input=' + encodeQueryParam(input) + '&question=' + encodeQueryParam(question);
        } else if (currentEndpoint === 'score') {
          const input = document.getElementById('score-input') ? document.getElementById('score-input').value : '';
          const question = document.getElementById('score-question') ? document.getElementById('score-question').value : '';
          const min = document.getElementById('score-min') ? document.getElementById('score-min').value : '0';
          const max = document.getElementById('score-max') ? document.getElementById('score-max').value : '10';
          return origin + '/score?input=' + encodeQueryParam(input) + '&question=' + encodeQueryParam(question) + '&min=' + encodeQueryParam(min) + '&max=' + encodeQueryParam(max);
        } else if (currentEndpoint === 'health') {
          return origin + '/health';
        }
        return origin;
      }

      function getRawJevPayload(endpoint) {
        const model = 'jev-latest';
        if (endpoint === 'choice') {
          const input = (document.getElementById('choice-input') ? document.getElementById('choice-input').value : '').trim();
          const choicesRaw = (document.getElementById('choice-options') ? document.getElementById('choice-options').value : '').split(',');
          const criteria = {};
          choicesRaw.map(c => c.trim()).filter(Boolean).forEach(c => {
            criteria[c] = null;
          });
          return {
            state: input,
            model: model,
            questions: {
              choice_q: {
                type: 'choice',
                instructions: 'Select the option that best matches the input.',
                criteria: criteria
              }
            }
          };
        } else if (endpoint === 'noul') {
          const input = (document.getElementById('noul-input') ? document.getElementById('noul-input').value : '').trim();
          const question = (document.getElementById('noul-question') ? document.getElementById('noul-question').value : '').trim();
          return {
            state: input,
            model: model,
            questions: {
              noul_q: {
                type: 'noul',
                instructions: question
              }
            }
          };
        } else if (endpoint === 'score') {
          const input = (document.getElementById('score-input') ? document.getElementById('score-input').value : '').trim();
          const question = (document.getElementById('score-question') ? document.getElementById('score-question').value : '').trim();
          const minVal = parseInt(document.getElementById('score-min') ? document.getElementById('score-min').value : '0', 10) || 0;
          const maxVal = parseInt(document.getElementById('score-max') ? document.getElementById('score-max').value : '10', 10) || 10;
          let criteria = [];
          const steps = maxVal - minVal + 1;
          if (steps > 0 && steps <= 10) {
            for (let i = 0; i < steps; i++) {
              criteria.push(String(minVal + i));
            }
          } else if (steps > 10) {
            for (let i = 0; i < 10; i++) {
              criteria.push(String(Math.round(minVal + (i * (maxVal - minVal) / 9))));
            }
          }
          return {
            state: input,
            model: model,
            questions: {
              score_q: {
                type: 'score',
                instructions: question,
                criteria: criteria
              }
            }
          };
        } else if (endpoint === 'health') {
          return {
            info: 'Local wrapper health check — no upstream TypeSafe Jev call required',
            upstream_call: false,
            endpoint: '/health'
          };
        }
        return {};
      }

      function updateLiveRequestPane() {
        const url = getConstructedUrl();
        const urlEl = document.getElementById('live-url-text');
        if (urlEl) urlEl.innerText = url;

        const rawPayload = getRawJevPayload(currentEndpoint);
        const rawEl = document.getElementById('raw-jev-json');
        if (rawEl) {
          rawEl.innerText = JSON.stringify(rawPayload, null, 2);
        }
      }

      async function copyTextToClipboard(text, btn, defaultLabel) {
        if (!text) return;
        let copied = false;

        if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function' && window.isSecureContext) {
          try {
            await navigator.clipboard.writeText(text);
            copied = true;
          } catch (e) {
            copied = false;
          }
        }

        if (!copied) {
          try {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-9999px';
            textArea.style.top = '-9999px';
            textArea.style.opacity = '0';
            textArea.setAttribute('readonly', '');
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            textArea.setSelectionRange(0, 99999);
            copied = document.execCommand('copy');
            document.body.removeChild(textArea);
          } catch (e) {
            copied = false;
          }
        }

        if (copied) {
          if (btn) {
            btn.innerText = 'Copied!';
            btn.classList.add('copied');
            if (btn._copyTimeout) clearTimeout(btn._copyTimeout);
            btn._copyTimeout = setTimeout(() => {
              btn.innerText = defaultLabel;
              btn.classList.remove('copied');
            }, 1800);
          }
        } else {
          if (btn) {
            btn.innerText = 'Failed';
            setTimeout(() => { btn.innerText = defaultLabel; }, 1500);
          }
          window.prompt('Copy to clipboard: Ctrl+C / Cmd+C, Enter', text);
        }
      }

      function copyConstructedUrl() {
        const liveEl = document.getElementById('live-url-text');
        const url = (liveEl && liveEl.innerText && liveEl.innerText !== 'http://...')
          ? liveEl.innerText
          : getConstructedUrl();
        const btn = document.getElementById('btn-copy-url');
        copyTextToClipboard(url, btn, 'Copy URL');
      }

      function copyRawJevJson() {
        const rawEl = document.getElementById('raw-jev-json');
        const text = rawEl ? rawEl.innerText : JSON.stringify(getRawJevPayload(currentEndpoint), null, 2);
        const btn = document.getElementById('btn-copy-payload');
        copyTextToClipboard(text, btn, 'Copy Payload');
      }

      function copyResponseJson() {
        const resEl = document.getElementById('response-json');
        const text = resEl ? resEl.innerText : '{}';
        const btn = document.getElementById('btn-copy-response');
        copyTextToClipboard(text, btn, 'Copy JSON');
      }

      function selectEndpoint(endpoint) {
        currentEndpoint = endpoint;
        ['choice', 'noul', 'score', 'health'].forEach(ep => {
          const panel = document.getElementById('panel-' + ep);
          if (panel) panel.style.display = (ep === endpoint) ? 'block' : 'none';
          const tab = document.getElementById('tab-' + ep);
          if (tab) {
            if (ep === endpoint) {
              tab.classList.add('active');
            } else {
              tab.classList.remove('active');
            }
          }
        });

        document.getElementById('banner-path').innerText = '/' + endpoint;
        document.getElementById('banner-desc').innerText = descriptions[endpoint] || '';
        
        // Hide response section until a request is sent on this tab
        const responseSection = document.getElementById('response-section');
        if (responseSection) responseSection.style.display = 'none';

        updateLiveRequestPane();
      }

      function setChoice(input, choices) {
        document.getElementById('choice-input').value = input;
        document.getElementById('choice-options').value = choices;
        updateLiveRequestPane();
      }

      function setNoul(input, question) {
        document.getElementById('noul-input').value = input;
        document.getElementById('noul-question').value = question;
        updateLiveRequestPane();
      }

      function setScore(input, question, min, max) {
        document.getElementById('score-input').value = input;
        document.getElementById('score-question').value = question;
        document.getElementById('score-min').value = min;
        document.getElementById('score-max').value = max;
        updateLiveRequestPane();
      }

      document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('input, textarea').forEach(el => {
          el.addEventListener('input', updateLiveRequestPane);
        });
        const responseSection = document.getElementById('response-section');
        if (responseSection) responseSection.style.display = 'none';
        updateLiveRequestPane();
      });

      async function sendApiRequest() {
        const executeBtn = document.getElementById('btn-execute');
        executeBtn.disabled = true;
        executeBtn.innerText = 'Sending Request...';

        let requestPath = '';
        if (currentEndpoint === 'choice') {
          const input = document.getElementById('choice-input').value.trim();
          const choices = document.getElementById('choice-options').value.trim();
          if (!input || !choices) {
            alert('Both "input" and "choices" query parameters are required.');
            executeBtn.disabled = false;
            executeBtn.innerText = 'Send Request';
            return;
          }
          requestPath = '/choice?input=' + encodeQueryParam(input) + '&choices=' + encodeQueryParam(choices);
        } else if (currentEndpoint === 'noul') {
          const input = document.getElementById('noul-input').value.trim();
          const question = document.getElementById('noul-question').value.trim();
          if (!input || !question) {
            alert('Both "input" and "question" query parameters are required.');
            executeBtn.disabled = false;
            executeBtn.innerText = 'Send Request';
            return;
          }
          requestPath = '/noul?input=' + encodeQueryParam(input) + '&question=' + encodeQueryParam(question);
        } else if (currentEndpoint === 'score') {
          const input = document.getElementById('score-input').value.trim();
          const question = document.getElementById('score-question').value.trim();
          const min = document.getElementById('score-min').value;
          const max = document.getElementById('score-max').value;
          if (!input || !question) {
            alert('Both "input" and "question" query parameters are required.');
            executeBtn.disabled = false;
            executeBtn.innerText = 'Send Request';
            return;
          }
          requestPath = '/score?input=' + encodeQueryParam(input) + '&question=' + encodeQueryParam(question) + '&min=' + encodeQueryParam(min) + '&max=' + encodeQueryParam(max);
        } else if (currentEndpoint === 'health') {
          requestPath = '/health';
        }

        const responseSection = document.getElementById('response-section');
        const statusTag = document.getElementById('status-tag');
        const durationTag = document.getElementById('duration-tag');
        const summaryBox = document.getElementById('result-summary-box');
        const summaryVal = document.getElementById('result-summary-value');
        const summaryMeta = document.getElementById('result-summary-meta');
        const jsonBlock = document.getElementById('response-json');

        // Display response section underneath
        responseSection.style.display = 'block';

        // Set evaluating loading state
        statusTag.className = 'status-tag ok';
        statusTag.innerText = 'Evaluating...';
        durationTag.innerText = '...';
        summaryBox.style.display = 'flex';
        summaryVal.innerText = 'Evaluating...';
        summaryMeta.innerText = 'Calling TypeSafe Jev API...';
        jsonBlock.innerText = '// Sending request to ' + requestPath + '...';

        const startTime = performance.now();

        try {
          const res = await fetch(requestPath);
          const elapsed = Math.round(performance.now() - startTime);
          const data = await res.json();

          durationTag.innerText = elapsed + 'ms';
          jsonBlock.innerText = JSON.stringify(data, null, 2);

          if (res.ok) {
            statusTag.className = 'status-tag ok';
            statusTag.innerText = res.status + ' OK';
            summaryBox.style.display = 'flex';

            if (currentEndpoint === 'choice') {
              summaryVal.innerText = (data.result !== undefined) ? data.result : (data.choice || '—');
              summaryMeta.innerText = (data.confidence !== undefined) ? Math.round(data.confidence * 100) + '% confidence' : '';
            } else if (currentEndpoint === 'noul') {
              const val = (data.result !== undefined) ? data.result : data.value;
              summaryVal.innerText = val ? 'true (Yes)' : 'false (No)';
              summaryMeta.innerText = (data.confidence !== undefined) ? Math.round(data.confidence * 100) + '% confidence' : '';
            } else if (currentEndpoint === 'score') {
              const max = document.getElementById('score-max').value;
              const val = (data.result !== undefined) ? data.result : data.score;
              summaryVal.innerText = val + ' / ' + max;
              summaryMeta.innerText = (data.confidence !== undefined) ? Math.round(data.confidence * 100) + '% confidence' : '';
            } else if (currentEndpoint === 'health') {
              summaryVal.innerText = data.status || 'ok';
              summaryMeta.innerText = 'Service healthy';
            }
          } else {
            statusTag.className = 'status-tag err';
            statusTag.innerText = res.status + ' ' + (res.statusText || 'Error');
            summaryBox.style.display = 'flex';
            summaryVal.innerHTML = '<span style="color:#b91c1c; font-size:14px;">' + (data.error || 'Request Error') + '</span>';
            summaryMeta.innerText = 'Verify parameters';
          }
        } catch (err) {
          const elapsed = Math.round(performance.now() - startTime);
          statusTag.className = 'status-tag err';
          statusTag.innerText = 'Network Error';
          durationTag.innerText = elapsed + 'ms';
          summaryBox.style.display = 'flex';
          summaryVal.innerHTML = '<span style="color:#b91c1c; font-size:14px;">Failed to connect</span>';
          summaryMeta.innerText = err.message;
          jsonBlock.innerText = JSON.stringify({ error: err.message }, null, 2);
        } finally {
          executeBtn.disabled = false;
          executeBtn.innerText = 'Send Request';
          responseSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    </script>
  </body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/swagger", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    """Serve standard Swagger UI for advanced developers."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="JEV for Dummies - Swagger UI",
    )


@app.exception_handler(TypeSafeConfigError)
async def config_error_handler(request: Request, exc: TypeSafeConfigError) -> JSONResponse:
    """Handle missing configuration errors."""
    return JSONResponse(
        status_code=500,
        content={"error": exc.message},
    )


@app.exception_handler(TypeSafeUpstreamError)
async def upstream_error_handler(request: Request, exc: TypeSafeUpstreamError) -> JSONResponse:
    """Handle TypeSafe API upstream failures."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle general value validation errors."""
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors and format into standard error JSON."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = first.get("loc", [])
        field = loc[-1] if loc else "parameter"
        msg = f"{field} is required" if first.get("type") == "missing" else first.get("msg", "Invalid parameter")
        return JSONResponse(status_code=400, content={"error": msg})
    return JSONResponse(status_code=400, content={"error": "Invalid request parameters"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions such as 404 Not Found."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server errors without leaking stack traces."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# Register endpoints
app.include_router(router)
