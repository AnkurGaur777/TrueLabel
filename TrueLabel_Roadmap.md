# Project: TrueLabel — Food Label Scanner & Ingredient Risk Analyzer
### CV + NLP + API Project for Resume/Portfolio (Real-Product Track)

---

## Project Overview

**What you're building:** A scanner (barcode or photo-based) that tells a user exactly what's in their food — nutrition breakdown (carbs, protein, fat, sugar) and an ingredient risk analysis (additives, allergens, ultra-processed markers) — pulling real data from Open Food Facts, with OCR for reading physical labels and NLP for parsing ingredient lists. When a product is flagged for something like high sugar, the user can click through to see healthier alternatives in the same category.

**Why this matters for your resume:** This single project combines Computer Vision (OCR), NLP (ingredient parsing), real API integration, a recommendation feature, and a consumer-facing product with a real custom frontend — replacing what would otherwise be several separate narrower projects, while being demo-able, memorable, and closer to an actual shippable product than a typical portfolio piece.

**Time estimate:** ~18–22 days working part-time (1–2 hrs/day) — adjusted up from the original 14–18 days to account for the custom frontend (Option B) and the healthy alternatives feature.

**Product name:** TrueLabel

---

## Locked-In Tech Decisions

| Layer | Tool | Notes |
|---|---|---|
| Language | Python | — |
| API framework | FastAPI | with Pydantic for validation |
| HTTP requests | `requests` | for Open Food Facts calls |
| Database | **MySQL** | not SQLite/Postgres — matches existing SQL skills |
| ORM | **SQLAlchemy** | database-agnostic, standard pairing with FastAPI |
| DB driver | `pymysql` | |
| Containerization | Docker + **Docker Compose** | two services: FastAPI app + MySQL container |
| Version control | Git / GitHub | public repo: `TrueLabel` |
| OCR | `pytesseract` (or EasyOCR) + OpenCV/Pillow for preprocessing | |
| NLP | spaCy or regex/string matching | ingredient flag matching |
| Data handling | pandas, numpy | |
| **Frontend** | **Custom HTML5 + CSS3 (Tailwind via CDN) + JavaScript** | not Streamlit — real-product track, needs CORS enabled on FastAPI |
| Visualization (optional) | matplotlib/seaborn | for README charts only |

---

## Phase 1: Planning & Setup (Day 1)

### Step 1.1 — Understand your data source
- Explore the **Open Food Facts API** manually (browser/Postman) — look up real products by barcode and by name search to see the JSON structure: `nutriments`, `ingredients_text`, `nutriscore_grade`, `allergens_tags`, `categories`
- No API key needed — it's fully open and free (no cost, no rate-limit billing; just set a proper `User-Agent` header identifying the app, e.g. `"TrueLabel - Student Portfolio Project - contact@youremail.com"`)

### Step 1.2 — Decide your two input modes
- **Mode A: Barcode/text search** — user types a product name or barcode, fetch data from the API directly (build first, simpler)
- **Mode B: Photo scan (OCR)** — user uploads/takes a photo of a nutrition label, extract text from the image (build second, harder)

### Step 1.3 — Set up your environment
- Install: Python, FastAPI, Tesseract OCR (`pytesseract`) or EasyOCR, spaCy, requests, MySQL, SQLAlchemy, Docker Desktop
- Project folder: `TrueLabel/`
  ```
  TrueLabel/
  ├── backend/
  │   ├── app/
  │   │   ├── api/
  │   │   ├── ocr/
  │   │   ├── nlp/
  │   │   ├── models/       # SQLAlchemy models
  │   │   ├── schemas/      # Pydantic schemas
  │   │   ├── services/     # Open Food Facts client, scoring logic, alternatives logic
  │   │   └── main.py
  │   ├── requirements.txt
  │   └── .env.example
  ├── frontend/
  │   ├── index.html
  │   ├── css/
  │   ├── js/
  │   └── assets/
  ├── docker/
  │   └── docker-compose.yml
  ├── .gitignore
  └── README.md
  ```
- Initialize a Git repository — commit from day 1, push to GitHub under your own account

### Step 1.4 — requirements.txt
- `fastapi`, `uvicorn`, `pydantic`, `requests`, `sqlalchemy`, `pymysql`, `python-dotenv`, `pytesseract`, `pillow`, `opencv-python`, `spacy`, `python-multipart`

---

## Phase 2: Build Mode A — Barcode/Text Search (Day 2–3)

### Step 2.1 — Write a function to query Open Food Facts
- Given a barcode or product name, call the API and return the raw product data
- Set the required `User-Agent` header

### Step 2.2 — Parse the response into clean structure
- Extract: product name, nutrition facts (carbs, protein, fat, sugar, calories), ingredient list (raw text), Nutri-Score, allergen tags, **category tags** (needed later for Phase 4.5 alternatives)

### Step 2.3 — Handle missing/incomplete data
- Open Food Facts is crowdsourced, so many products have incomplete data — show "data not available" rather than crashing or guessing

### Step 2.4 — Test with real products
- Try 10–15 different real products (snacks, drinks, packaged meals) to see how consistent the data is

---

## Phase 3: Build Mode B — OCR Label Scanning (Day 4–6)

### Step 3.1 — Set up OCR
- Install and test Tesseract or EasyOCR on a sample nutrition label photo

### Step 3.2 — Extract raw text from the image
- Run OCR on the label photo, inspect the raw text output

### Step 3.3 — Parse OCR text into structured nutrition data
- Regex/pattern matching to pull specific values: "Total Carbohydrate 24g" → `carbs: 24`
- Hardest part of the whole project — expect to iterate

### Step 3.4 — Improve OCR accuracy
- Image preprocessing (grayscale, contrast, resizing) before OCR
- Test on multiple real product photos, not just one

### Step 3.5 — Handle OCR failures gracefully
- When OCR can't confidently extract a value, say so clearly rather than showing a wrong number

---

## Phase 4: Ingredient Risk Analysis (NLP) (Day 7–8)

### Step 4.1 — Build an ingredient flag list
- Categories to flag: high-sugar indicators, common artificial additives, common allergens, ultra-processed markers
- Keep as a config file/list, not hardcoded logic

### Step 4.2 — Parse the ingredient list text
- spaCy or simple text matching against the flag list
- Handle naming variations (e.g., "sugar," "cane sugar," "high fructose corn syrup")

### Step 4.3 — Generate a readable summary
- "Contains 3 artificial additives," "Contains common allergen: peanuts," "High sugar content"

### Step 4.4 — Test against real ingredient lists
- Run against 10+ real products' ingredient lists, sanity-check the flags

---

## Phase 4.5 — Healthy Alternatives (NEW) (Day 9)

### Step 4.5.1 — Design the matching logic (Option A: category + score comparison)
- For each triggered flag on a product (e.g., high sugar), take the product's `categories` field from Open Food Facts
- Query Open Food Facts search API filtered to the **same category**
- Filter/sort candidates for a **better Nutri-Score** or **lower value on that specific flagged metric** (e.g., lower sugar per 100g)
- Return top 3–5 alternatives: name, image URL, key nutrient that's better, Nutri-Score

### Step 4.5.2 — Handle the "no good alternative found" case
- Same honesty principle as OCR failures — if nothing better exists in-category, say so clearly rather than forcing a weak match

### Step 4.5.3 — Structure the API response
- Add an `alternatives: [...]` field to the response, populated per flagged nutrient

### Step 4.5.4 — Note future upgrade path (for README "what I'd improve")
- Option B (later, not now): similarity matching via cosine similarity on nutrient vectors instead of same-category-only, for more genuinely comparable alternatives

---

## Phase 5: Build the Health Score (Day 10)

### Step 5.1 — Design a simple scoring approach
- Rules-based score (not ML) — deduct points for high sugar, artificial additives, high sodium; add points for high protein/fiber
- Simple, defensible in an interview as long as the logic is explainable

### Step 5.2 — (Optional upgrade) Compare against Nutri-Score
- Compare your own score against Open Food Facts' Nutri-Score as a sanity check; discuss differences in the README

### Step 5.3 — Clearly label it as an estimate
- Output must explicitly say this is an approximate/generated score, not an official health rating

---

## Phase 6: Build the API (Day 11–12)

### Step 6.1 — Set up FastAPI project structure
- Basic FastAPI app with a health-check endpoint (`/health`)
- **Enable CORS** so the custom JS frontend can call the API

### Step 6.2 — Build the search endpoint
- `/search` — accepts a product name or barcode, returns nutrition data + ingredient flags + health score + alternatives (Mode A)

### Step 6.3 — Build the scan endpoint
- `/scan` — accepts an uploaded image, runs OCR + parsing + NLP + scoring + alternatives, returns the same structured output (Mode B)

### Step 6.4 — Add input validation
- Pydantic models for the search endpoint; validate image uploads (file type, size limits) for the scan endpoint

### Step 6.5 — Test both endpoints
- Use FastAPI's Swagger UI (`/docs`) to test with real product names and real label photos

---

## Phase 7: Log Scans to MySQL via SQLAlchemy (Day 13)

### Step 7.1 — Design a scan log table (SQLAlchemy model)
- Schema idea: `scan_id, timestamp, input_type (search/photo), product_name, nutrition_data (JSON), flags (JSON), health_score, alternatives_shown (JSON)`
- Use MySQL's native `JSON` column type

### Step 7.2 — Log every scan/search
- Every time `/search` or `/scan` is hit, log the result via SQLAlchemy session
- Useful later for showing usage patterns or most-scanned products

---

## Phase 8: Build the Custom Frontend (Day 14–17)

### Step 8.1 — Frontend stack
- HTML5 + Tailwind CSS (via CDN) + vanilla JavaScript (`fetch` to call the FastAPI backend)
- `FileReader` API for image upload/preview

### Step 8.2 — Design direction
- Visual identity: clean, trustworthy, slightly clinical (food/health context) — not flashy or gamey
- Core screens: search/landing screen, results screen (nutrition + flags + score + alternatives), photo upload screen
- "Wow" moment: the health score reveal — a big colored badge/gauge, traffic-light style (green/yellow/red)
- **A visual mockup will be reviewed together before full build-out**

### Step 8.3 — Build the search interface
- Text input for product name/barcode, button, clean results display (nutrition table, flags, score badge)

### Step 8.4 — Build the photo upload interface
- File upload with image preview, showing OCR-extracted results in the same layout as search results

### Step 8.5 — Build the "healthy alternatives" interaction
- On a flagged item (e.g., "High sugar"), a clickable element reveals a small card row of 2–3 alternative products (image, name, why it's better)
- Graceful empty state when no alternatives are found

### Step 8.6 — Polish the results display
- Color-coded flags, score badge/gauge, consistent spacing and typography — should look like a real consumer product, not raw JSON

---

## Phase 9: Containerize with Docker Compose (Day 18)

### Step 9.1 — Write Docker Compose config
- Two services: FastAPI backend + MySQL container
- Include environment variables for DB connection via `.env`

### Step 9.2 — Write the Dockerfile for the backend
- Package FastAPI app with all dependencies including Tesseract/OCR libraries

### Step 9.3 — Build and run via Docker Compose
- Confirm search, scan, and alternatives all work identically inside Docker as they did locally
- Note: OCR libraries can be finicky in Docker — budget extra time for dependency issues

---

## Phase 10: Documentation & Polish (Day 19–22)

### Step 10.1 — Write a README for GitHub
Include:
- Project overview (1–2 sentences)
- Architecture diagram (boxes: User Input (search/photo) → OCR (if photo) → Open Food Facts API / Parsed Data → NLP Ingredient Analysis → Health Score → Healthy Alternatives Lookup → FastAPI → Custom Frontend)
- How to run it (including `docker compose up`)
- Screenshots: a search result, a photo-scan result, and the alternatives interaction
- Known limitations (e.g., "OCR accuracy depends on photo quality and label layout," "health score is a heuristic estimate, not medical advice," "alternatives are category-matched, not nutrient-similarity-matched — see future work")
- Tech stack used (MySQL + SQLAlchemy, custom frontend, etc.)

### Step 10.2 — Push everything to GitHub
- Clean commit history
- `.gitignore` for `.env`, uploaded test images, and large data files

### Step 10.3 — Prepare your interview story
Be ready to explain in 60 seconds:
- The real problem this solves
- Why you combined CV + NLP + a recommendation feature instead of doing them separately
- The hardest technical part (OCR parsing accuracy) and how you handled it
- Why you chose MySQL/SQLAlchemy and a custom frontend over the simpler defaults (shows deliberate, resume-relevant decision-making, not just following a tutorial)
- What you'd improve with more time (e.g., custom OCR model, ML-based health score, nutrient-similarity alternatives matching, user accounts)

---

## Final Deliverable Checklist

- [ ] Working search mode (Open Food Facts API integration)
- [ ] Working OCR photo-scan mode
- [ ] Ingredient risk flagging (NLP)
- [ ] Healthy alternatives feature (category + score comparison)
- [ ] Health score generation, clearly labeled as an estimate
- [ ] FastAPI service with `/search`, `/scan`, `/health` endpoints, CORS enabled
- [ ] Scan/search logging to MySQL via SQLAlchemy
- [ ] Custom HTML/CSS (Tailwind)/JS frontend — not Streamlit
- [ ] Dockerized application via Docker Compose (app + MySQL)
- [ ] GitHub repo (`TrueLabel`) with clean README, architecture diagram, and screenshots
- [ ] 60-second interview explanation ready

---

## Suggested Order to Tackle If You Get Stuck
1. Get Mode A (search) fully working first — API call, parse response, print it (Phase 2)
2. Add ingredient flagging on top of that working search (Phase 4)
3. Add healthy alternatives on top of flagging (Phase 4.5) — you now have a working text-only product with a differentiating feature
4. THEN tackle OCR separately as its own mini-project — get it extracting text from ONE test image reliably before integrating (Phase 3)
5. Merge OCR output into the same parsing/flagging/alternatives pipeline you already built for search
6. THEN wrap all modes in FastAPI with CORS enabled (Phase 6)
7. THEN build the custom frontend (Phase 8) so you have something visual to show
8. THEN Dockerize with Docker Compose (Phase 9)

Getting the simpler, API-based mode fully working before touching OCR means you'll have a demo-able product even if OCR takes longer than expected — a good safety net given OCR is genuinely the hardest part of this project.
