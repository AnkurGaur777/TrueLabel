# \# TrueLabel

# 

# A food label scanner and ingredient-risk analyzer. Search any packaged product or raw ingredient, scan a nutrition label with your camera, or photograph a fruit/vegetable to identify it — and get an instant, color-coded health score with flagged ingredient risks and healthier alternatives.

# 

# Built as a portfolio project to demonstrate a full-stack, production-shaped data application: two external data sources, OCR, an image classifier, a rules-based scoring engine, and a containerized deployment.

# 

# \## Screenshots

# 

# \*\*Search\*\* — packaged products and raw foods side by side, each with a color-coded health score

# !\[Search results](screenshots/search.png)

# 

# \*\*Scan Label\*\* — OCR reads a physical nutrition label photo

# !\[Scan label](screenshots/scan.png)

# 

# \*\*Identify Produce\*\* — an image classifier recognizes fruits/vegetables from a photo

# !\[Identify produce](screenshots/classify.png)

# 

# \## Features

# 

# \- \*\*Search by name or barcode\*\* — queries Open Food Facts (packaged products) and USDA FoodData Central (raw/generic foods) in parallel, so a search for "banana" returns both a banana-flavored yogurt \*and\* a plain raw banana, clearly labeled by source.

# \- \*\*Scan a nutrition label\*\* — upload or photograph a label; OCR (Tesseract) extracts the printed nutrition values, with implausible OCR misreads (e.g. a missed decimal point) automatically caught and flagged rather than silently trusted.

# \- \*\*Identify raw produce from a photo\*\* — a HuggingFace image classifier recognizes 36 common fruits/vegetables, then looks up its nutrition data from USDA.

# \- \*\*Health score\*\* — a rules-based score (0–100, green/yellow/red) from sugar, sodium, fat, energy, and protein per 100g, with an honest "uncertain" rating when key nutrients are missing rather than presenting a false score.

# \- \*\*Ingredient risk flags\*\* — allergens, artificial additives, high-sugar indicators, and ultra-processed markers, matched against multilingual keyword lists (English/French/German/Spanish) since Open Food Facts often returns non-English ingredient text.

# \- \*\*Healthier alternatives\*\* — for packaged products, suggests same-category items with a meaningfully better Nutri-Score or at least 20% less sugar.

# \- \*\*Every request logged\*\* to MySQL for basic usage analytics.

# 

# \## Architecture

# 

# ```mermaid

# flowchart TB

# &#x20;   subgraph Client

# &#x20;       FE\[Frontend<br/>HTML + Tailwind + Vanilla JS]

# &#x20;   end

# 

# &#x20;   subgraph Backend\["FastAPI Backend (Docker)"]

# &#x20;       API\[REST API<br/>/search /scan /classify /logs]

# &#x20;       OCR\[OCR Pipeline<br/>OpenCV + Tesseract]

# &#x20;       CLF\[Image Classifier<br/>HuggingFace Transformers]

# &#x20;       SCORE\[Health Score +<br/>Ingredient Flagging]

# &#x20;   end

# 

# &#x20;   subgraph External\["External Data"]

# &#x20;       OFF\[Open Food Facts API]

# &#x20;       USDA\[USDA FoodData Central API]

# &#x20;   end

# 

# &#x20;   DB\[(MySQL<br/>Docker)]

# 

# &#x20;   FE -->|fetch| API

# &#x20;   API --> OCR

# &#x20;   API --> CLF

# &#x20;   API --> SCORE

# &#x20;   API --> OFF

# &#x20;   API --> USDA

# &#x20;   API -->|log every request| DB

# ```

# 

# The frontend runs as a plain static site (no build step) and talks to the backend over CORS-enabled REST calls. The backend and MySQL run together via Docker Compose; the frontend is intentionally left un-containerized since a static site needs no runtime.

# 

# \## Tech stack

# 

# | Layer | Technology |

# |---|---|

# | Backend | Python, FastAPI, SQLAlchemy |

# | Database | MySQL 8 |

# | OCR | Tesseract, OpenCV (preprocessing: CLAHE, bilateral filtering, adaptive thresholding) |

# | Image classification | HuggingFace Transformers, PyTorch (CPU) |

# | NLP | Multilingual keyword matching, langdetect |

# | Frontend | HTML5, Tailwind CSS (CDN), vanilla JavaScript |

# | Data sources | Open Food Facts API, USDA FoodData Central API |

# | Deployment | Docker, Docker Compose |

# 

# \## Running it

# 

# \*\*Requirements:\*\* Docker Desktop, a free \[USDA FoodData Central API key](https://fdc.nal.usda.gov/api-key-signup.html)

# 

# 1\. Clone the repo and set up your environment file:

# ```bash

# &#x20;  cd docker

# &#x20;  cp .env.example .env

# &#x20;  # edit .env: set MYSQL\_ROOT\_PASSWORD and USDA\_FDC\_API\_KEY

# ```

# 

# 2\. Build and start the backend + database:

# ```bash

# &#x20;  docker compose -f docker-compose.yml --env-file .env up -d --build

# ```

# &#x20;  First build takes several minutes (downloading PyTorch and other ML dependencies). The API will be available at `http://127.0.0.1:8001` — check `http://127.0.0.1:8001/health`.

# 

# 3\. Serve the frontend (a static site, no build needed):

# ```bash

# &#x20;  cd ../frontend

# &#x20;  python -m http.server 5500

# ```

# &#x20;  Open `http://127.0.0.1:5500`.

# 

# \## API reference

# 

# | Endpoint | Method | Description |

# |---|---|---|

# | `/search?query=X\&is\_barcode=bool` | GET | Search by name (returns packaged + raw results) or barcode |

# | `/scan` | POST | Upload a nutrition label photo (`file`, multipart) |

# | `/classify` | POST | Upload a fruit/vegetable photo (`file`, multipart) |

# | `/logs?limit=N` | GET | Recent request history (max 100) |

# | `/health` | GET | Service health check |

# 

# Interactive docs (Swagger UI) at `http://127.0.0.1:8001/docs`.

# 

# \## Known limitations

# 

# \- \*\*OCR accuracy\*\* is imperfect even on clean, well-lit photos — common misreads include "g" read as "9" or a missed decimal point (e.g. "3.34g" read as "334g"). The backend detects and rejects physically impossible values rather than trusting them, but this means some nutrients may show as "not available" on a scan rather than a wrong number.

# \- \*\*Open Food Facts has frequent downtime\*\* (observed regularly during development, 503 errors). The app is deliberately built to degrade gracefully — a name search still returns USDA raw-food results even when Open Food Facts is unreachable.

# \- \*\*Healthier-alternatives matching is category-only\*\*, not semantic similarity — it can occasionally suggest a same-category product that isn't a great substitute. A future version could use embedding-based similarity instead.

# \- \*\*No alternatives for scanned labels or produce photos\*\* — OCR and image classification don't return a product category, so there's nothing to match alternatives against. This was a deliberate scope decision rather than building a lower-confidence nutrient-based fallback.

# \- \*\*The image classifier\*\* (36 fruit/vegetable classes, \~99% accuracy on clean stock photos) is noticeably less reliable on cluttered backgrounds, unusual angles, or poor lighting — realistic phone photos, not curated ones.

# \- \*\*The health score is a heuristic\*\*, not a certified nutritional rating — it's built from simple, transparent threshold rules on five nutrients, not a validated clinical model.

# 

# \## What I'd improve next

# 

# \- Semantic (embedding-based) matching for healthier alternatives instead of category + threshold rules

# \- Fine-tune or swap the produce classifier for better real-world (non-stock-photo) accuracy

# \- Cache Open Food Facts responses to reduce impact of its downtime

# \- Add automated tests for the OCR plausibility checks and health scoring rules

# 

# \## License

# 

# Personal portfolio project. Not affiliated with Open Food Facts or USDA.

