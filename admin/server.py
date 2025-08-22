import json
import logging
import os
import threading
from typing import Any, Dict

from flask import Flask, Response, jsonify, render_template_string, request

from .logging_stream import LogEvent, globalBroker


def create_app() -> Flask:
    app = Flask(__name__)

    INDEX_HTML = """
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <title>Yapper Admin</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; background: #0b0f13; color: #e6edf3; }
          header { padding: 16px 24px; background: #11161c; border-bottom: 1px solid #2a313a; position: sticky; top: 0; z-index: 1; }
          h1 { font-size: 18px; margin: 0; }
          .container { padding: 16px 24px; }
          .category { background: #0f141a; border: 1px solid #2a313a; border-radius: 8px; margin-bottom: 12px; }
          .cat-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; cursor: pointer; }
          .cat-title { display: flex; gap: 10px; align-items: center; }
          .badge { font-size: 11px; padding: 2px 8px; border-radius: 999px; border: 1px solid #3a424e; background: #141a21; color: #cfd8e3; }
          .badge.ok { color: #15c27c; border-color: #124e3a; background: #0a1f16; }
          .badge.error { color: #f87171; border-color: #4c1d1d; background: #1a0f0f; }
          .chevron { color: #8ea0b5; transition: transform 0.2s; }
          .cat-body { display: none; border-top: 1px solid #2a313a; max-height: 320px; overflow: auto; background: #0b1016; }
          .log-line { padding: 8px 14px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; border-bottom: 1px solid #0f141a; color: #cbd5e1; }
          .log-line.error { color: #fecaca; }
          .log-line .ts { opacity: 0.6; margin-right: 8px; }
        </style>
      </head>
      <body>
        <header>
          <h1>Yapper Admin Panel</h1>
        </header>
        <div class=\"container\">
          <div id=\"categories\"></div>
        </div>
        <script>
          const categories = [
            "lastfm", "osuSlack", "musicRoast", "joined", "leave", "leetcode", "mention"
          ];

          function createCategoryElement(name) {
            const wrap = document.createElement('div');
            wrap.className = 'category';

            const header = document.createElement('div');
            header.className = 'cat-header';
            const title = document.createElement('div');
            title.className = 'cat-title';
            const h = document.createElement('div');
            h.textContent = name;
            const badge = document.createElement('span');
            badge.className = 'badge';
            badge.textContent = 'idle';
            title.appendChild(h);
            title.appendChild(badge);

            const chev = document.createElement('span');
            chev.className = 'chevron';
            chev.textContent = '▾';

            header.appendChild(title);
            header.appendChild(chev);

            const body = document.createElement('div');
            body.className = 'cat-body';

            header.addEventListener('click', () => {
              const open = body.style.display === 'block';
              body.style.display = open ? 'none' : 'block';
              chev.style.transform = open ? 'rotate(0deg)' : 'rotate(180deg)';
            });

            wrap.appendChild(header);
            wrap.appendChild(body);
            return {wrap, badge, body};
          }

          const catsEl = document.getElementById('categories');
          const catMap = new Map();
          for (const c of categories) {
            const el = createCategoryElement(c);
            catsEl.appendChild(el.wrap);
            catMap.set(c, el);
          }

          function fmtTs(ts) {
            try { return new Date(ts * 1000).toLocaleTimeString(); } catch { return ''; }
          }

          function appendLog(evt) {
            const { category, level, message, ts } = evt;
            if (!catMap.has(category)) return;
            const el = catMap.get(category);

            el.badge.classList.remove('ok', 'error');
            el.badge.classList.add(level === 'error' ? 'error' : 'ok');
            el.badge.textContent = level === 'error' ? 'error' : 'ok';

            const line = document.createElement('div');
            line.className = 'log-line ' + (level === 'error' ? 'error' : '');
            const tsSpan = document.createElement('span');
            tsSpan.className = 'ts';
            tsSpan.textContent = '[' + fmtTs(ts) + ']';
            line.appendChild(tsSpan);
            line.appendChild(document.createTextNode(message));
            el.body.appendChild(line);
            el.body.scrollTop = el.body.scrollHeight;
          }

          const es = new EventSource('/events');
          es.addEventListener('message', (e) => {
            try {
              const data = JSON.parse(e.data);
              appendLog(data);
            } catch {}
          });
        </script>
      </body>
    </html>
    """

    @app.route("/")
    def index():
        return render_template_string(INDEX_HTML)

    @app.route("/events")
    def events():
        def gen():
            for sse in globalBroker.subscribe():
                yield sse
        return Response(gen(), mimetype="text/event-stream")

    @app.route("/status")
    def status():
        snap: Dict[str, Any] = {}
        for k, v in globalBroker.categories.items():
            snap[k] = {
                "status": v.status,
                "last_message": v.last_message,
                "last_level": v.last_level,
                "last_ts": v.last_ts,
            }
        return jsonify(snap)

    return app


class SseLoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            category = "misc"
            raw = record.getMessage()
            if raw.startswith("[") and "]" in raw:
                category = raw.split("]", 1)[0].lstrip("[")
            evt = LogEvent(category=category, level=record.levelname.lower(), message=raw)
            globalBroker.publish(evt)
        except Exception:
            pass


def adminServer(host: str = "127.0.0.1", port: int = 6942):
    app = create_app()

    def _run():
        app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t