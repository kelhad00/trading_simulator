# TradeSim: handover note

State of the project at the end of Eugene Oppong Okyere's internship (May to November 2026), for
the next intern or developer. How to use the app is in the [README](../README.md); every setting is
explained in the [WIKI](../WIKI.md#settings-and-features) ([français](../WIKI_FR.md)).

## 1. Start here

| | |
|---|---|
| Code | `trading_simulator/` (Python 3.10, Dash 2.10, Dash Mantine Components 0.12, Plotly) |
| Configurator (researchers) | `cd trade` then `python app_config.py` → http://127.0.0.1:8050 |
| Runtime (participants) | `cd trade` then `python app_runtime.py` → http://127.0.0.1:8051 |
| Data folder | `trading_simulator/data` (`trade/defaults.py`, `data_path`) |
| Logs of the sessions | `data/exports/<session id>/` |
| Default values | `trade/defaults.py` |
| Texts (English / French) | `trade/locales/en.py`, `trade/locales/fr.py` |
| Tests | from `trading_simulator`: `.\trade\venv\Scripts\python.exe -m pytest` (about 300, all passing on 30 Oct 2026) |

### Branches
- `main`: the stable version.
- `intern/develop`: the development branch; all the internship's work is merged here.
- Way of working: one small branch per change, created from `intern/develop`, merged back once the
  tests pass. Each fix comes with a test that fails without it.

### How an experiment runs
1. The researcher prepares everything in the Configurator and clicks **Export Session** → `session.zip`.
2. Each participant uses **their own computer** with the Runtime, and imports `session.zip` on the
   home page (Start is disabled until then).
3. Each session writes its logs to its own folder, with `log-info.json` (session ID, code version,
   settings).

### Where to look
| I want to change... | Look in (under `trade/`) |
|---|---|
| a default value | `defaults.py` |
| a text, in English or French | `locales/en.py`, `locales/fr.py` (always both: `tests/test_translations.py` checks) |
| the chart | `utils/graph/candlestick_charts.py` (drawing), `callbacks/dashboard/graph.py` (updates, clock, pause) |
| how orders are placed or executed | `callbacks/dashboard/request.py`, `utils/orders.py`, `utils/fees.py` |
| moving candles | `utils/candle_steps.py` |
| discrete mode | `utils/trials.py`, `callbacks/dashboard/trials.py` |
| the news list and pop-ups | `callbacks/dashboard/news.py`, `utils/news_timing.py` |
| news generation | `utils/news_generation/` (writing: `news_creation.py`, FinBERT check: `verify.py`) |
| market data generation | `callbacks/settings/charts/`, `utils/settings/` |
| the logs | `utils/export.py`, `callbacks/dashboard/export.py` |
| the session file | `utils/session.py`, `callbacks/settings/session_export.py`, `callbacks/home_import.py` |
| the page layouts | `layouts/` (one folder per page) |

### Adding a new setting (checklist)
1. `app.py`: a `dcc.Store(id="my-setting", data=<default>, storage_type="local")`.
2. `layouts/settings/sections/<tab>.py`: the input box.
3. `callbacks/settings/<tab>.py`: show the saved value in the box, and save the box into the store
   (check the value: refuse negative or empty values).
4. `locales/en.py` and `locales/fr.py`: the label and help text.
5. The session file: `utils/session.py` (`build_session_zip` and `extract_session_zip`, with a default
   for older files), `callbacks/settings/session_export.py` (a `State`) and `callbacks/home_import.py`
   (an `Output`; keep the number of returned values equal to the number of Outputs).
6. Where the setting is used: add `State("my-setting", "data")` at the **end** of the callback, with
   a default parameter, so the existing tests keep working.
7. Tests: the setting is saved, refused when wrong, carried by the session file, and does what it
   should. `tests/test_session_zip.py` fails if step 5 is forgotten.

## 2. Built during the internship
All on `intern/develop`, each with its tests. Each one is **off until the researcher turns it on**
(decision 7 below); news pop-ups and news tags existed before and stay on.
- moving candles (`trade/utils/candle_steps.py`), with a Simple or Random price path inside the
  forming candle;
- discrete mode with trials (`trade/utils/trials.py`, `trade/callbacks/dashboard/trials.py`):
  confirmation before the next trial, no news pop-ups, zoom on the first candles;
- leaderboard against 20 robot traders (`trade/utils/leaderboard.py`);
- commission fee (`trade/utils/fees.py`);
- news notifications: filter, delay, sentiment tags on/off; time reminders;
- news generation with Groq or Ollama, checked by FinBERT (`trade/utils/news_generation/`);
- chart Autoscale / Reset axes buttons (shown only when switched on); fixed candle slots, date labels;
- one log folder per session; session file carries every setting and the three data files;
- "Updating…" screen in the Configurator (`trade/app.py`, `_loading_overlay`);
- works offline (local `tailwind.css` and icons); English and French.

## 3. Decisions taken with the supervisors (29–30 Oct 2026, Fan)

| # | Question | Decision | Done |
|---|---|---|---|
| 1 | 40 damaged log files from old sessions | Delete them | Deleted (686 log files remain) |
| 2 | Discrete mode: moving to the next trial too fast | No time limit; a window "Are you sure you have finished?" with Yes / No | Yes |
| 3 | Discrete mode: many news pop-ups at once | Hide pop-ups in discrete mode; news stays in the list | Yes |
| 4 | Discrete mode: first trials look tiny | Zoom while fewer than N candles are shown; N set in the interface; tested 20–200 candles, N = 100 | Yes |
| 5 | Commission fee default | Keep 0 | Yes |
| 6 | One shared server or one computer per participant | Each participant uses their own computer | Workflow above |
| 7 | Prices inside a forming candle: keep the simple path or add a random one | Add the random path, as a setting; every feature added during the internship off by default | Yes (1dc5e0b): Settings → Advanced "Price movement inside a forming candle" (Simple by default) and "Show the Autoscale and Reset axes buttons" (off); moving candles and time reminders now off by default |

The "Updating…" screen is for the Configurator only, on purpose: the Runtime updates every few
seconds, so it would flash all the time.

## 4. Open issues
From a full review of the Configurator and the Runtime (Oct 2026). "Likely" means it was found by
reading the code and still needs a check in the browser. Paths are under `trade/`.

### Fixed (30 Oct 2026), each with tests
| # | Problem | Commit |
|---|---|---|
| 1 | The session file looked for `revenues.csv` (real name `revenue.csv`): revenue never reached the participants | 06618e7 |
| 2 | Notification filter and delay not carried by the session file | 06618e7 |
| 3 | Saving revenue crashed with 2 or more companies | 576941a |
| 4 | Editing a waiting order could make cash negative | 1b95c9c |
| 5 | The results window ignored money put aside for waiting buy orders | 1b95c9c |
| 6 | With moving candles, the leaderboard robots were valued at the forming candle's final Close (a future price) | 576941a |

The open items are below.

### Medium: a feature misbehaves
| # | Problem | Where |
|---|---|---|
| 7 | Update interval is free text: "abc" or "5 s" crashes the Runtime; 0 and negative accepted | `layouts/settings/sections/advanced.py`, `callbacks/settings/advanced.py`, `callbacks/dashboard/graph.py` |
| 8 | Any click on the chart (also the toolbar buttons) overwrites the price box | `callbacks/dashboard/request.py` (chart click callback) |
| 9 | The results window can be closed and trading goes on after the end (likely) | `layouts/dashboard/layout.py` (`dmc.Modal`) |
| 10 | Pause is lost on reload or language switch; the paused time then counts | `callbacks/dashboard/graph.py`, `components/menu.py` |
| 11 | Importing a new session in the same tab keeps the old waiting orders, cost basis, pause time, reminders | `callbacks/home_import.py` |
| 12 | Uploading a charts CSV doesn't clear the company cache (likely) | `callbacks/settings/upload.py` |
| 13 | "Layoffs" is used for positive news, but the positive-news rules forbid mentioning layoffs | `utils/news_generation/news_creation.py` |
| 14 | News of deactivated companies still shown (likely) | `callbacks/dashboard/news.py` |
| 15 | `news.csv` uses the company name: renaming a company leaves its old articles | `utils/news_generation/news_creation.py` |
| 16 | Switching company may redraw with the old zoom (likely) | `callbacks/dashboard/graph.py` |

### Small
| # | Problem | Where |
|---|---|---|
| 17 | Quantity preview says 0 shares but Submit places 1 | `callbacks/dashboard/request.py` |
| 18 | Sell preview ignores the fee; not refreshed on company change | `callbacks/dashboard/request.py` |
| 19 | Waiting-order lines can be off the visible chart | `utils/graph/candlestick_charts.py` |
| 20 | English text for French users: Pause/Resume/Reset, "Date", "share(s)", chart Buy/Sell, tag badges | `components/menu.py`, `callbacks/dashboard/graph.py`, `request.py`, `news.py` |
| 21 | Pop-ups: the same headline can pop twice; the filter still applies when tags are hidden | `callbacks/dashboard/news.py` |
| 22 | Max-orders check uses `==` not `>=`; fee missing from request logs; Reset creates empty `exports/<n>` folders; "-0.00€" after selling everything | `request.py`, `utils/export.py`, `callbacks/reset.py`, `utils/orders.py` |
| 23 | Discrete mode silently replaces "Candles of history"; edited trials discarded when discrete mode is off | `callbacks/settings/advanced.py` |
| 24 | Dark-mode default differs in 4 places; `color-scheme` exported but unused | `app.py`, `utils/session.py` |
| 25 | Import doesn't check the zip (missing files/keys, ranges); Start stays enabled after a failed import | `utils/session.py`, `callbacks/home_import.py` |
| 26 | Empty alpha/delta boxes crash "Generate news"; an empty ticker crashes "Add" | `callbacks/settings/news.py`, `callbacks/settings/stocks.py` |
| 27 | Without FinBERT every article is tagged "neutral" | `utils/news_generation/verify.py` |
| 28 | Saving revenue fails if `data/revenue.csv` doesn't exist (the Configurator downloads it at start-up, so only when that download failed, e.g. offline) | `callbacks/settings/revenues.py`, `utils/market.py` (`get_revenues_dataframe`) |

### Not merged
- Branch `develop_By_Intern` (9 June 2026, on GitHub): news prompts that use the start price and size
  each article to the price move. Never merged; the later commit "Remove price_start from LLM
  prompt" (03d6ce7) probably went the other way on purpose. Check with the supervisors before
  porting it by hand.

### Known slowness
The Configurator takes about 14 s to open the Settings page and 8–9 s to switch tabs. The server
answers in about 0.3 s; the time is the browser drawing the Dash Mantine components. The
"Updating…" screen makes the wait visible; making it faster would mean drawing fewer components
per tab.
