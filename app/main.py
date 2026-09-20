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
        max-width: 760px;
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
        padding: 8px 14px;
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
        background: rgba(255, 255, 255, 0.5);
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

      /* Main Route Card */
      .doc-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        padding: 24px;
        overflow: hidden;
      }

      .endpoint-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 16px;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 20px;
        flex-wrap: wrap;
      }

      .banner-method {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #dbeafe;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 13px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
      }

      .banner-path {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
      }

      .banner-desc {
        margin-left: auto;
        font-size: 13px;
        color: #64748b;
      }

      /* Example presets */
      .presets-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 20px;
        background: #f8fafc;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #f1f5f9;
      }

      .presets-title {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
      }

      .preset-chip {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        color: #334155;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
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
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 14px;
      }

      .param-group {
        margin-bottom: 18px;
      }

      .param-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
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
        font-size: 12px;
        color: #64748b;
        margin-bottom: 6px;
      }

      .param-input, .param-textarea {
        width: 100%;
        padding: 9px 12px;
        font-size: 14px;
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

      /* Live Constructed Request URL Box - Overflow Fixed */
      .live-url-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin: 22px 0 16px 0;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        overflow: hidden;
      }

      .live-url-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        flex-wrap: wrap;
        gap: 8px;
      }

      .live-url-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #64748b;
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
      }

      .copy-btn:hover {
        background: #f1f5f9;
        color: #0f172a;
      }

      .live-url-row {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 12px;
        color: #0f172a;
        width: 100%;
        max-width: 100%;
        min-width: 0;
        box-sizing: border-box;
      }

      .live-method {
        font-weight: 700;
        color: #2563eb;
        white-space: nowrap;
        flex-shrink: 0;
        padding-top: 1px;
      }

      .live-url-text {
        min-width: 0;
        flex: 1 1 0%;
        word-break: break-all;
        overflow-wrap: anywhere;
        line-height: 1.45;
      }

      /* Execute Button */
      .btn-execute {
        display: block;
        width: 100%;
        padding: 11px 20px;
        font-size: 14px;
        font-weight: 600;
        color: #ffffff;
        background: #0f172a;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.15s ease;
      }

      .btn-execute:hover {
        background: #1e293b;
      }

      .btn-execute:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      /* Response Viewer */
      .response-card {
        display: none;
        margin-top: 22px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
      }

      .response-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
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

      .duration-tag {
        font-size: 11px;
        color: #64748b;
      }

      /* Key Result Pill */
      .result-summary-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
      }

      .result-summary-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
      }

      .result-summary-value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
      }

      .result-summary-meta {
        font-size: 12px;
        color: #64748b;
      }

      pre {
        margin: 0;
        background: #0f172a;
        color: #38bdf8;
        padding: 14px;
        border-radius: 8px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 12px;
        overflow-x: auto;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-all;
        width: 100%;
        box-sizing: border-box;
      }

      .footer {
        text-align: center;
        margin-top: 28px;
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

      <!-- Interactive Endpoint Card -->
      <div class="doc-card">
        <!-- Banner -->
        <div class="endpoint-banner">
          <span class="banner-method">GET</span>
          <span class="banner-path" id="banner-path">/choice</span>
          <span class="banner-desc" id="banner-desc">Evaluate input text against candidate options</span>
        </div>

        <!-- 1. /choice Panel -->
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

        <!-- 2. /noul Panel -->
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

        <!-- 3. /score Panel -->
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

        <!-- 4. /health Panel -->
        <div id="panel-health" class="endpoint-panel" style="display: none;">
          <div class="section-heading">Endpoint Details</div>
          <p style="font-size: 13px; color: #64748b; margin: 0 0 16px 0;">This endpoint takes no parameters. It checks if the service is running and ready to accept requests.</p>
        </div>

        <!-- Live Constructed URL Box (Fixed overflow) -->
        <div class="live-url-box">
          <div class="live-url-header">
            <span class="live-url-title">Constructed Request URL (updates live):</span>
            <button type="button" class="copy-btn" id="btn-copy" onclick="copyConstructedUrl()">Copy URL</button>
          </div>
          <div class="live-url-row">
            <span class="live-method">GET</span>
            <span class="live-url-text" id="live-url-text">http://...</span>
          </div>
        </div>

        <!-- Execute Button -->
        <button class="btn-execute" id="btn-execute" onclick="sendApiRequest()">Send Request</button>

        <!-- Response Viewer -->
        <div class="response-card" id="response-card">
          <div class="response-header">
            <span class="section-heading" style="margin: 0;">Response</span>
            <div class="response-meta">
              <span class="status-tag ok" id="status-tag">200 OK</span>
              <span class="duration-tag" id="duration-tag"></span>
            </div>
          </div>

          <!-- Highlight outcome -->
          <div class="result-summary-box" id="result-summary-box">
            <div>
              <div class="result-summary-label">Decision Result</div>
              <div class="result-summary-value" id="result-summary-value">—</div>
            </div>
            <div class="result-summary-meta" id="result-summary-meta"></div>
          </div>

          <div style="font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 6px;">Response Body (JSON)</div>
          <pre><code id="response-json">{}</code></pre>
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
          const input = document.getElementById('choice-input').value;
          const choices = document.getElementById('choice-options').value;
          return origin + '/choice?input=' + encodeQueryParam(input) + '&choices=' + encodeQueryParam(choices);
        } else if (currentEndpoint === 'noul') {
          const input = document.getElementById('noul-input').value;
          const question = document.getElementById('noul-question').value;
          return origin + '/noul?input=' + encodeQueryParam(input) + '&question=' + encodeQueryParam(question);
        } else if (currentEndpoint === 'score') {
          const input = document.getElementById('score-input').value;
          const question = document.getElementById('score-question').value;
          const min = document.getElementById('score-min').value;
          const max = document.getElementById('score-max').value;
          return origin + '/score?input=' + encodeQueryParam(input) + '&question=' + encodeQueryParam(question) + '&min=' + encodeQueryParam(min) + '&max=' + encodeQueryParam(max);
        } else if (currentEndpoint === 'health') {
          return origin + '/health';
        }
        return origin;
      }

      function updateLiveUrl() {
        const url = getConstructedUrl();
        const el = document.getElementById('live-url-text');
        if (el) el.innerText = url;
      }

      function copyConstructedUrl() {
        const url = getConstructedUrl();
        navigator.clipboard.writeText(url).then(() => {
          const btn = document.getElementById('btn-copy');
          const old = btn.innerText;
          btn.innerText = 'Copied!';
          setTimeout(() => { btn.innerText = old; }, 1500);
        });
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
        document.getElementById('response-card').style.display = 'none';
        updateLiveUrl();
      }

      function setChoice(input, choices) {
        document.getElementById('choice-input').value = input;
        document.getElementById('choice-options').value = choices;
        updateLiveUrl();
      }

      function setNoul(input, question) {
        document.getElementById('noul-input').value = input;
        document.getElementById('noul-question').value = question;
        updateLiveUrl();
      }

      function setScore(input, question, min, max) {
        document.getElementById('score-input').value = input;
        document.getElementById('score-question').value = question;
        document.getElementById('score-min').value = min;
        document.getElementById('score-max').value = max;
        updateLiveUrl();
      }

      document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('input, textarea').forEach(el => {
          el.addEventListener('input', updateLiveUrl);
        });
        updateLiveUrl();
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

        const responseCard = document.getElementById('response-card');
        const statusTag = document.getElementById('status-tag');
        const durationTag = document.getElementById('duration-tag');
        const summaryBox = document.getElementById('result-summary-box');
        const summaryVal = document.getElementById('result-summary-value');
        const summaryMeta = document.getElementById('result-summary-meta');
        const jsonBlock = document.getElementById('response-json');

        const startTime = performance.now();

        try {
          const res = await fetch(requestPath);
          const elapsed = Math.round(performance.now() - startTime);
          const data = await res.json();

          responseCard.style.display = 'block';
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
            summaryMeta.innerText = 'Verify parameters above';
          }
        } catch (err) {
          const elapsed = Math.round(performance.now() - startTime);
          responseCard.style.display = 'block';
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
