# TrueLabel — Project Notes (single source of truth)

## What this is
Food label scanner + ingredient risk analyzer. Portfolio project for
data scientist / data engineer roles. Built with FastAPI + MySQL backend,
custom HTML/Tailwind/vanilla-JS frontend, Docker Compose. Roadmap doc:
TrueLabel_Roadmap.md (re-attach this in new chats).

## How I work
I write/run all code myself via Antigravity (AI coding tool) and PowerShell
on my own Windows PC. Claude has no direct access to my machine — it gives
copy-pasteable code/commands, I run them and paste back the output.

## Current phase
Frontend complete and tested (search, scan, classify all working).
Next: Docker Compose for the full app (backend + MySQL together).

## Ports (IMPORTANT — avoid conflicts with other local projects)
- Backend API: http://127.0.0.1:8001  (NOT 8000 — that's taken by another
  local Docker project: churn-detection-mlops-api)
- Frontend (local dev server): http://127.0.0.1:5500 (python -m http.server)
- MySQL (Docker): localhost:3307 (mapped from container's 3306, to avoid
  clashing with a separate local MySQL Workbench connection on ~3306)

## Design: Aether palette (dark theme only, no light mode)
- Background: #060416
- Card surface: #130C49
- Elevated surface / bar track: #1F137D
- Accent (buttons, highlights): #874AD7
- Accent strong (gradients): #5C21C3
- Text: #F1ECFB, dim text: #A79CC9
- Semantic (separate from accent):
  - Good/healthy: #4FE3A0 (green)
  - Warning/moderate: #F6B94D (amber)
  - Bad/high-risk: #F26B6B (red)
- Fonts: Sora (display/headings), Manrope (body), JetBrains Mono (numbers/data)
- Nutrient bars change color (green/amber/red) based on the health_score
  breakdown array returned by the backend — not a client-side guess.
- Approved mockup artifact: https://claude.ai/artifact/8JVhSL8rB8txrso7uQMHrq

## Backend structure (all committed, working)
backend/
  app/
    main.py            — FastAPI app, CORS enabled (allow_origins=["*"])
    config.py           — loads .env (USDA key, DB creds)
    database.py         — SQLAlchemy engine/session/init_db
    api/
      search.py          — GET /search?query=X&is_barcode=bool
      scan.py            — POST /scan (label photo OCR)
      classify.py        — POST /classify (produce photo)
      logs.py            — GET /logs?limit=N
    services/
      result_builder.py   — enrich_raw_food(), ocr_to_product() — unify
                             product shape across all 3 endpoints
      health_score.py     — calculate_health_score()
      alternatives_finder.py
      product_parser.py   — parses Open Food Facts
      usda_parser.py       — parses USDA FoodData Central
      scan_logger.py       — log_scan(), log_search() (never raises)
    nlp/
      ingredient_flagger.py, flag_config.py — multilingual keyword flagging
      (allergens returned as [{allergen: "milk", matched_terms: [...]}], not
      plain strings — frontend must read the .allergen field)
    ocr/
      extractor.py, nutrition_parser.py
    classifier/
      produce_classifier.py — HuggingFace 36-class fruit/veg classifier
    models/
      scan_log.py — SQLAlchemy ScanLog model

## Frontend structure (all committed, working)
frontend/
  index.html — Tailwind CDN + custom Aether color config, 3 tabs
               (Search / Scan Label / Identify Produce)
  style.css  — bar/swatch/gauge color classes, scrollbar styling
  app.js     — tab switching, fetch calls to backend (API_BASE = port 8001),
               renderProduct() shared card renderer used by all 3 tabs
  Run locally with: python -m http.server 5500 (from inside frontend/)
  File inputs use capture="environment" so mobile browsers open the camera
  directly (desktop just opens the file picker — no camera API there).

## API response shapes (confirmed working)
GET /search (name search):
  { packaged_products: {source, results:[...], error},
    raw_generic_foods: {source, results:[...], error} }
GET /search (barcode): { source, result: <product> }
POST /scan: { input_type, source, product: <product|null>, raw_text, warnings:[] }
POST /classify: { filename, predictions, best_guess, nutrition: <product|null>,
                   nutrition_error, note }

<product> shape (all 3 endpoints now return this consistently):
  product_name, brands, categories, nutriscore_grade, ingredients_text,
  allergens, nutrition_per_100g {energy_kcal, carbs_g, sugars_g, protein_g,
  fat_g, sodium_g}, ingredient_flags {...}, health_score {score, rating,
  breakdown, data_used, missing_nutrients, confidence, score_note,
  disclaimer}, alternatives {can_search, reason, alternatives}

Note: values can be the string "not available" instead of a number when
OCR/data is missing or was rejected as implausible.

health_score.rating can be: "green" | "yellow" | "red" | "uncertain"
(uncertain = missing key nutrients, treat as provisional)

## Known limitations (confirmed, for README later)
- OCR imperfect even on clean photos (digit "g"/"9" confusion, e.g. read
  "3.34g" as "334g" — caught and rejected by _checked() safety logic)
- Open Food Facts has frequent 503 downtime — app degrades gracefully,
  confirmed in real testing (banana search: OFF down, USDA still worked)
- Alternatives matching is category-only (not semantic similarity)
- Scanned labels and produce photos have NO healthy-alternatives
  recommendation, by design — no category data available from OCR/image
  classification to match against. Decided to document as a limitation
  rather than build a nutrient-based fallback (see roadmap tradeoffs).
- Image classifier struggles on cluttered/angled/dim real photos
- Health score is a heuristic estimate, not an official rating

## Git status
Latest commit: e3e504d — "Open camera directly on mobile for scan and
classify uploads"
(Run `git log --oneline` fresh each session and paste it to confirm current state)

## Not yet started
- Docker Compose for full app — only MySQL is Dockerized so far; FastAPI
  needs its own Dockerfile with Tesseract OCR system dependencies bundled
  in (this is the main risk area — expect some debugging)
- README, architecture diagram, screenshots, interview prep