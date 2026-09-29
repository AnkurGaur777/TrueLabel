/**
 * TrueLabel Frontend Application
 * Vanilla JavaScript implementation for searching products, scanning labels with OCR,
 * and identifying produce from images.
 */

const API_BASE = "http://127.0.0.1:8001";

// Cache DOM elements
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const isBarcodeCheckbox = document.getElementById("is-barcode");

const scanInput = document.getElementById("scan-input");
const scanChooseBtn = document.getElementById("scan-choose");
const scanFilename = document.getElementById("scan-filename");
const scanSubmitBtn = document.getElementById("scan-submit");

const classifyInput = document.getElementById("classify-input");
const classifyChooseBtn = document.getElementById("classify-choose");
const classifyFilename = document.getElementById("classify-filename");
const classifySubmitBtn = document.getElementById("classify-submit");

/**
 * Escapes unsafe characters for HTML injection.
 */
function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

/**
 * Checks whether a value is a valid finite number.
 */
function isNumeric(value) {
    return typeof value === "number" && !isNaN(value) && isFinite(value);
}

/**
 * Displays status message with loading indicator styling.
 */
function setStatus(message) {
    if (message) {
        statusEl.textContent = message;
        statusEl.classList.remove("hidden");
    } else {
        statusEl.textContent = "";
        statusEl.classList.add("hidden");
    }
}

/**
 * Renders an error message box into #results.
 */
function renderError(message) {
    resultsEl.innerHTML = `
        <div class="p-4 rounded-xl border border-bad/30 bg-bad/10 text-bad text-sm font-medium leading-relaxed">
            ${escapeHtml(message)}
        </div>
    `;
}

/**
 * Triggers width transitions for all nutrient progress bars.
 */
function animateNutrientBars() {
    requestAnimationFrame(() => {
        const fills = resultsEl.querySelectorAll(".bar-fill[data-target-width]");
        fills.forEach((fill) => {
            fill.style.width = fill.getAttribute("data-target-width");
        });
    });
}

/* ==========================================================================
   1. Tab Switching
   ========================================================================== */

/**
 * Activates a tab by name, showing its panel and clearing current results.
 */
function switchTab(targetTab) {
    tabButtons.forEach((btn) => {
        if (btn.dataset.tab === targetTab) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    tabPanels.forEach((panel) => {
        if (panel.id === `panel-${targetTab}`) {
            panel.classList.remove("hidden");
        } else {
            panel.classList.add("hidden");
        }
    });

    // Clear results and status when switching tabs
    resultsEl.innerHTML = "";
    setStatus(null);
}

tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        switchTab(btn.dataset.tab);
    });
});

// Set default tab on page load
switchTab("search");

/* ==========================================================================
   2. File Inputs (Scan & Classify)
   ========================================================================== */

// Scan panel file selection
scanChooseBtn.addEventListener("click", () => {
    scanInput.click();
});

scanInput.addEventListener("change", () => {
    const file = scanInput.files && scanInput.files[0];
    if (file) {
        scanFilename.textContent = file.name;
        scanSubmitBtn.disabled = false;
    } else {
        scanFilename.textContent = "";
        scanSubmitBtn.disabled = true;
    }
});

// Classify panel file selection
classifyChooseBtn.addEventListener("click", () => {
    classifyInput.click();
});

classifyInput.addEventListener("change", () => {
    const file = classifyInput.files && classifyInput.files[0];
    if (file) {
        classifyFilename.textContent = file.name;
        classifySubmitBtn.disabled = false;
    } else {
        classifyFilename.textContent = "";
        classifySubmitBtn.disabled = true;
    }
});

/* ==========================================================================
   4. Core Product Card Renderer
   ========================================================================== */

/**
 * Determines nutrient color class based on the health score breakdown rules.
 */
function getNutrientColorClass(nutrientKey, breakdown) {
    if (!Array.isArray(breakdown)) {
        return "good";
    }

    const keywordMap = {
        sugars_g: ["sugar"],
        sodium_g: ["sodium"],
        fat_g: ["fat"],
        energy_kcal: ["energy", "kcal"],
        protein_g: ["protein"],
        carbs_g: ["carb", "carbohydrate"],
    };

    const keywords = keywordMap[nutrientKey] || [];
    const matched = breakdown.find((item) => {
        const reason = (item.reason || "").toLowerCase();
        return keywords.some((kw) => reason.includes(kw));
    });

    if (!matched) {
        return "good";
    }

    const points = matched.points;
    if (points < 0) {
        return points <= -15 ? "bad" : "warn";
    }
    if (points > 0) {
        return "good";
    }

    return "good";
}

/**
 * Generates HTML string for the product card.
 */
function renderProduct(product) {
    if (!product || typeof product !== "object") {
        return "";
    }

    const productName = product.product_name || "Unnamed Product";
    const subMeta = [product.brands, product.categories].filter(Boolean).join(" | ");

    // Health Score section
    let scoreSectionHtml = "";
    const healthScore = product.health_score;

    if (healthScore && healthScore.can_score) {
        const score = isNumeric(healthScore.score) ? Math.round(healthScore.score) : 0;
        const rating = (healthScore.rating || "").toLowerCase();

        let strokeColor = "#F26B6B"; // red / uncertain default
        if (rating === "green") {
            strokeColor = "#4FE3A0";
        } else if (rating === "yellow") {
            strokeColor = "#F6B94D";
        }

        const radius = 32;
        const circumference = 2 * Math.PI * radius;
        const dashoffset = circumference * (1 - Math.max(0, Math.min(100, score)) / 100);

        const ratingLabel = rating ? rating.charAt(0).toUpperCase() + rating.slice(1) : "Rating";
        const scoreNoteHtml = healthScore.score_note
            ? `<span class="text-xs text-textDim italic leading-snug">${escapeHtml(healthScore.score_note)}</span>`
            : "";

        scoreSectionHtml = `
            <div class="flex items-center gap-4 p-4 rounded-xl bg-surface2/40 border border-line">
                <div class="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
                    <svg class="gauge-ring w-20 h-20" viewBox="0 0 80 80">
                        <circle cx="40" cy="40" r="${radius}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="6" />
                        <circle class="gauge-fill" cx="40" cy="40" r="${radius}" fill="none"
                            stroke="${strokeColor}" stroke-width="6" stroke-linecap="round"
                            stroke-dasharray="${circumference.toFixed(2)}"
                            style="stroke-dashoffset: ${dashoffset.toFixed(2)}" />
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center font-mono font-bold text-lg text-textMain">
                        ${score}
                    </div>
                </div>
                <div class="flex flex-col gap-1">
                    <span class="font-display font-bold text-base text-textMain">${escapeHtml(ratingLabel)} Health Score</span>
                    ${scoreNoteHtml}
                </div>
            </div>
        `;
    }

    // Nutrient Bars section
    const nutrition = product.nutrition_per_100g || {};
    const breakdown = (healthScore && healthScore.breakdown) || [];

    const nutrientConfig = [
        { key: "energy_kcal", label: "Energy", unit: "kcal", max: 600 },
        { key: "carbs_g", label: "Carbs", unit: "g", max: 100 },
        { key: "sugars_g", label: "Sugars", unit: "g", max: 100 },
        { key: "protein_g", label: "Protein", unit: "g", max: 50 },
        { key: "fat_g", label: "Fat", unit: "g", max: 100 },
        { key: "sodium_g", label: "Sodium", unit: "g", max: 2 },
    ];

    const nutrientRows = [];

    nutrientConfig.forEach((cfg) => {
        const val = nutrition[cfg.key];
        if (val === undefined || val === null || val === "not available") {
            return;
        }

        const numVal = typeof val === "number" ? val : parseFloat(val);
        if (isNaN(numVal)) {
            return;
        }

        const colorClass = getNutrientColorClass(cfg.key, breakdown);
        const percentage = Math.max(0, Math.min(100, (numVal / cfg.max) * 100));

        nutrientRows.push(`
            <div class="flex flex-col gap-1.5">
                <div class="flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                        <span class="swatch ${colorClass}"></span>
                        <span class="text-textDim font-medium">${escapeHtml(cfg.label)}</span>
                    </div>
                    <span class="font-mono text-textMain tabular-nums">${numVal} ${cfg.unit}</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill ${colorClass}" style="width: 0%" data-target-width="${percentage.toFixed(1)}%"></div>
                </div>
            </div>
        `);
    });

    const nutrientsSectionHtml = nutrientRows.length > 0
        ? `
            <div class="flex flex-col gap-3">
                <span class="text-xs font-mono tracking-wider uppercase text-textDim">Nutrition per 100g</span>
                <div class="flex flex-col gap-3">
                    ${nutrientRows.join("")}
                </div>
            </div>
        `
        : "";

    // Ingredient Flags section
    let flagsSectionHtml = "";
    const flags = product.ingredient_flags;

    if (flags && flags.can_analyze) {
        const flagItems = [];

        if (Array.isArray(flags.allergens) && flags.allergens.length > 0) {
            const allergenNames = flags.allergens
                .map((a) => (a.allergen || "").replace(/_/g, " "))
                .join(", ");
            flagItems.push(`
                <div class="flag-chip">
                    <span class="swatch bad"></span>
                    <span><b>Allergens:</b> ${escapeHtml(allergenNames)}</span>
                </div>
            `);
        }

        if (Array.isArray(flags.artificial_additives) && flags.artificial_additives.length > 0) {
            flagItems.push(`
                <div class="flag-chip">
                    <span class="swatch warn"></span>
                    <span><b>Artificial additives:</b> ${escapeHtml(flags.artificial_additives.join(", "))}</span>
                </div>
            `);
        }

        if (Array.isArray(flags.high_sugar_indicators) && flags.high_sugar_indicators.length > 0) {
            flagItems.push(`
                <div class="flag-chip">
                    <span class="swatch warn"></span>
                    <span><b>High sugar indicators:</b> ${escapeHtml(flags.high_sugar_indicators.join(", "))}</span>
                </div>
            `);
        }

        if (Array.isArray(flags.ultra_processed_markers) && flags.ultra_processed_markers.length > 0) {
            flagItems.push(`
                <div class="flag-chip">
                    <span class="swatch warn"></span>
                    <span><b>Ultra-processed markers:</b> ${escapeHtml(flags.ultra_processed_markers.join(", "))}</span>
                </div>
            `);
        }

        if (flagItems.length > 0) {
            flagsSectionHtml = `
                <div class="flex flex-col gap-2">
                    <span class="text-xs font-mono tracking-wider uppercase text-textDim">Ingredient Flags</span>
                    <div class="flex flex-wrap gap-2">
                        ${flagItems.join("")}
                    </div>
                </div>
            `;
        }
    }

    // Healthier Alternatives section
    let alternativesSectionHtml = "";
    const alts = product.alternatives;

    if (alts && alts.can_search && Array.isArray(alts.alternatives) && alts.alternatives.length > 0) {
        const cards = alts.alternatives.map((alt) => {
            let badgeClass = "neutral";
            let badgeLabel = "";

            if (alt.health_score && typeof alt.health_score === "object") {
                const s = alt.health_score.score;
                const r = alt.health_score.rating || (s >= 70 ? "green" : s >= 50 ? "yellow" : "red");
                badgeClass = r === "green" ? "good" : (r === "yellow" ? "warn" : "bad");
                badgeLabel = isNumeric(s) ? `Score ${Math.round(s)}` : (r ? r.toUpperCase() : "Better");
            } else if (alt.nutriscore_grade && !["not-applicable", "unknown"].includes(alt.nutriscore_grade.toLowerCase())) {
                const grade = alt.nutriscore_grade.toLowerCase();
                badgeClass = ["a", "b"].includes(grade) ? "good" : (grade === "c" ? "warn" : "bad");
                badgeLabel = `Nutri-Score ${alt.nutriscore_grade.toUpperCase()}`;
            } else if (isNumeric(alt.health_score)) {
                badgeClass = alt.health_score >= 70 ? "good" : (alt.health_score >= 50 ? "warn" : "bad");
                badgeLabel = `Score ${Math.round(alt.health_score)}`;
            } else {
                badgeClass = "good";
                badgeLabel = "Healthier";
            }

            const altMeta = [alt.brands, alt.why_better].filter(Boolean).join(" | ");

            return `
                <div class="flex-shrink-0 w-52 p-3 rounded-xl bg-surface2/60 border border-line flex flex-col justify-between gap-2">
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center justify-between gap-2">
                            <span class="text-[11px] font-mono uppercase px-2 py-0.5 rounded-full border border-line flex items-center gap-1.5 text-textMain">
                                <span class="swatch ${badgeClass}"></span>
                                ${escapeHtml(badgeLabel)}
                            </span>
                        </div>
                        <span class="text-sm font-semibold text-textMain line-clamp-2 leading-snug">${escapeHtml(alt.product_name)}</span>
                    </div>
                    ${altMeta ? `<span class="text-[11px] text-textDim leading-tight line-clamp-2">${escapeHtml(altMeta)}</span>` : ""}
                </div>
            `;
        });

        alternativesSectionHtml = `
            <div class="flex flex-col gap-2">
                <span class="text-xs font-mono tracking-wider uppercase text-textDim">Healthier Alternatives</span>
                <div class="flex gap-3 overflow-x-auto pb-2 pt-1">
                    ${cards.join("")}
                </div>
            </div>
        `;
    }

    // Disclaimer
    const disclaimerHtml = healthScore && healthScore.disclaimer
        ? `<p class="text-[11px] text-textDim/60 italic">${escapeHtml(healthScore.disclaimer)}</p>`
        : "";

    return `
        <article class="p-5 sm:p-6 rounded-2xl bg-surface border border-line flex flex-col gap-5 shadow-lg">
            <!-- Header row -->
            <div class="flex flex-col gap-1">
                <h3 class="font-display font-bold text-lg text-textMain leading-tight">${escapeHtml(productName)}</h3>
                ${subMeta ? `<p class="text-xs text-textDim leading-relaxed">${escapeHtml(subMeta)}</p>` : ""}
            </div>

            <!-- Score -->
            ${scoreSectionHtml}

            <!-- Nutrient bars -->
            ${nutrientsSectionHtml}

            <!-- Ingredient Flags -->
            ${flagsSectionHtml}

            <!-- Alternatives -->
            ${alternativesSectionHtml}

            <!-- Disclaimer -->
            ${disclaimerHtml}
        </article>
    `;
}

/* ==========================================================================
   3. API Calls & Form Handlers
   ========================================================================== */

/**
 * Handles product / barcode search form submission.
 */
searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const query = searchInput.value.trim();
    const isBarcode = isBarcodeCheckbox.checked;

    if (!query) return;

    resultsEl.innerHTML = "";
    setStatus("Searching...");

    try {
        const url = `${API_BASE}/search?query=${encodeURIComponent(query)}&is_barcode=${isBarcode}`;
        const response = await fetch(url);

        if (!response.ok) {
            let errorMsg = `Server error (${response.status})`;
            try {
                const errData = await response.json();
                if (errData && errData.detail) {
                    errorMsg = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
                }
            } catch (_) {
                // Ignore JSON parse failure on error body
            }
            renderError(errorMsg);
            return;
        }

        const data = await response.json();

        if (isBarcode) {
            const product = data.result;
            if (product) {
                resultsEl.innerHTML = renderProduct(product);
                animateNutrientBars();
            } else {
                resultsEl.innerHTML = `<p class="text-sm text-textDim">No product found for this barcode.</p>`;
            }
        } else {
            const packagedResults = (data.packaged_products && data.packaged_products.results) || [];
            const rawResults = (data.raw_generic_foods && data.raw_generic_foods.results) || [];

            if (packagedResults.length === 0 && rawResults.length === 0) {
                const fallbackMsg = (data.packaged_products && data.packaged_products.error)
                    || (data.raw_generic_foods && data.raw_generic_foods.error)
                    || "No results found.";
                resultsEl.innerHTML = `<p class="text-sm text-textDim">${escapeHtml(fallbackMsg)}</p>`;
                return;
            }

            let html = "";

            if (packagedResults.length > 0) {
                html += `
                    <div class="flex flex-col gap-4">
                        <h2 class="font-display font-bold text-base text-textMain border-b border-line pb-2">Packaged Products</h2>
                        <div class="flex flex-col gap-5">
                            ${packagedResults.map((p) => renderProduct(p)).join("")}
                        </div>
                    </div>
                `;
            }

            if (rawResults.length > 0) {
                html += `
                    <div class="flex flex-col gap-4">
                        <h2 class="font-display font-bold text-base text-textMain border-b border-line pb-2">Raw / Generic Foods</h2>
                        <div class="flex flex-col gap-5">
                            ${rawResults.map((p) => renderProduct(p)).join("")}
                        </div>
                    </div>
                `;
            }

            resultsEl.innerHTML = html;
            animateNutrientBars();
        }
    } catch (err) {
        if (err instanceof TypeError) {
            renderError("Couldn't reach the server. Is the backend running on port 8001?");
        } else {
            renderError(`Network request failed: ${err.message}`);
        }
    } finally {
        setStatus(null);
    }
});

/**
 * Handles label scanning via OCR.
 */
scanSubmitBtn.addEventListener("click", async () => {
    const file = scanInput.files && scanInput.files[0];
    if (!file) return;

    resultsEl.innerHTML = "";
    setStatus("Analyzing label...");

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/scan`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            let errorMsg = `Server error (${response.status})`;
            try {
                const errData = await response.json();
                if (errData && errData.detail) {
                    errorMsg = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
                }
            } catch (_) {}
            renderError(errorMsg);
            return;
        }

        const data = await response.json();
        const product = data.product;
        const warnings = Array.isArray(data.warnings) ? data.warnings : [];
        const rawText = data.raw_text || "";

        if (!product) {
            const emptyMessage = warnings.length > 0
                ? warnings.join(" ")
                : "No nutrition label could be recognized in this image.";
            resultsEl.innerHTML = `
                <div class="p-5 rounded-2xl bg-surface border border-line text-sm text-textDim leading-relaxed">
                    ${escapeHtml(emptyMessage)}
                </div>
            `;
            return;
        }

        let warningsHtml = "";
        if (warnings.length > 0) {
            warningsHtml = `
                <div class="flex flex-col gap-2">
                    ${warnings
                        .map(
                            (w) => `
                                <div class="px-4 py-2.5 rounded-xl border border-warn/30 bg-warn/10 text-warn text-xs leading-relaxed font-medium">
                                    ${escapeHtml(w)}
                                </div>
                            `
                        )
                        .join("")}
                </div>
            `;
        }

        const rawTextHtml = `
            <details class="group rounded-xl border border-line bg-surface p-4 text-xs">
                <summary class="cursor-pointer font-mono font-medium text-textDim hover:text-textMain transition select-none">
                    Show raw OCR text
                </summary>
                <pre class="mt-3 p-3 rounded-lg bg-bg border border-line font-mono text-textDim overflow-x-auto whitespace-pre-wrap leading-relaxed">${escapeHtml(rawText)}</pre>
            </details>
        `;

        resultsEl.innerHTML = `
            <div class="flex flex-col gap-5">
                ${warningsHtml}
                ${renderProduct(product)}
                ${rawTextHtml}
            </div>
        `;

        animateNutrientBars();
    } catch (err) {
        if (err instanceof TypeError) {
            renderError("Couldn't reach the server. Is the backend running on port 8001?");
        } else {
            renderError(`Network request failed: ${err.message}`);
        }
    } finally {
        setStatus(null);
    }
});

/**
 * Handles produce classification.
 */
classifySubmitBtn.addEventListener("click", async () => {
    const file = classifyInput.files && classifyInput.files[0];
    if (!file) return;

    resultsEl.innerHTML = "";
    setStatus("Identifying produce...");

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/classify`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            let errorMsg = `Server error (${response.status})`;
            try {
                const errData = await response.json();
                if (errData && errData.detail) {
                    errorMsg = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
                }
            } catch (_) {}
            renderError(errorMsg);
            return;
        }

        const data = await response.json();

        // Support both direct fields and nested identification structure
        const bestGuess = data.best_guess || (data.identification && data.identification.best_guess);
        const nutrition = data.nutrition !== undefined ? data.nutrition : data.product;
        const nutritionError = data.nutrition_error || (data.warnings && data.warnings.find((w) => w.includes("USDA") || w.includes("Nutrition")));
        const note = data.note || (data.warnings && data.warnings.length > 0 ? data.warnings[data.warnings.length - 1] : "");

        let headingHtml = "";
        if (bestGuess && bestGuess.label) {
            const confPct = isNumeric(bestGuess.confidence) ? Math.round(bestGuess.confidence * 100) : 0;
            const labelCapitalized = bestGuess.label.charAt(0).toUpperCase() + bestGuess.label.slice(1);
            headingHtml = `
                <div class="p-4 rounded-xl bg-surface border border-line flex items-center justify-between">
                    <span class="font-display font-bold text-base text-textMain">Best guess: ${escapeHtml(labelCapitalized)}</span>
                    <span class="font-mono text-xs text-textDim bg-surface2 px-2.5 py-1 rounded-full border border-line">${confPct}% confident</span>
                </div>
            `;
        }

        let nutritionHtml = "";
        if (nutrition) {
            nutritionHtml = renderProduct(nutrition);
        } else {
            const fallback = nutritionError || "No nutrition information available for this item.";
            nutritionHtml = `
                <div class="p-4 rounded-xl bg-surface border border-line text-sm text-textDim">
                    ${escapeHtml(fallback)}
                </div>
            `;
        }

        const noteHtml = note
            ? `<p class="text-xs text-textDim leading-relaxed px-1">${escapeHtml(note)}</p>`
            : "";

        resultsEl.innerHTML = `
            <div class="flex flex-col gap-4">
                ${headingHtml}
                ${nutritionHtml}
                ${noteHtml}
            </div>
        `;

        animateNutrientBars();
    } catch (err) {
        if (err instanceof TypeError) {
            renderError("Couldn't reach the server. Is the backend running on port 8001?");
        } else {
            renderError(`Network request failed: ${err.message}`);
        }
    } finally {
        setStatus(null);
    }
});
