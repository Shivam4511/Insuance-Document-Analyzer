/**
 * Insurance Document Analyzer — Frontend Logic
 * Handles file upload, API communication, and dynamic results rendering.
 */

// ==================== CONFIGURATION ====================

const API_BASE = "http://localhost:8000";
const ANALYZE_URL = `${API_BASE}/analyze-document/`;
const ACCEPTED_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
];
const MAX_FILE_SIZE_MB = 20;

// ==================== DOM ELEMENTS ====================

const uploadArea = document.getElementById("upload-area");
const fileInput = document.getElementById("file-input");
const fileSelected = document.getElementById("file-selected");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const removeFileBtn = document.getElementById("remove-file");
const analyzeBtn = document.getElementById("analyze-btn");
const btnText = document.getElementById("btn-text");
const btnLoader = document.getElementById("btn-loader");
const loadingSection = document.getElementById("loading-section");
const errorSection = document.getElementById("error-section");
const errorMessage = document.getElementById("error-message");
const resultsSection = document.getElementById("results-section");
const newAnalysisBtn = document.getElementById("new-analysis-btn");
const mainHeader = document.getElementById("main-header");

// Result elements
const gaugeCircle = document.getElementById("gauge-circle");
const gaugeValue = document.getElementById("gauge-value");
const statusBadge = document.getElementById("status-badge");
const complianceRatio = document.getElementById("compliance-ratio");
const analyzedCount = document.getElementById("analyzed-count");
const totalSections = document.getElementById("total-sections");
const flaggedCount = document.getElementById("flagged-count");
const severitySummary = document.getElementById("severity-summary");
const pricingText = document.getElementById("pricing-text");
const legalText = document.getElementById("legal-text");
const coverageText = document.getElementById("coverage-text");
const flaggedContainer = document.getElementById("flagged-clauses-container");
const noFlagged = document.getElementById("no-flagged");
const sectionsAccordion = document.getElementById("sections-accordion");

// State
let selectedFile = null;

// ==================== HEADER SCROLL SHADOW ====================

window.addEventListener("scroll", () => {
    if (window.scrollY > 10) {
        mainHeader.classList.add("header-scrolled");
    } else {
        mainHeader.classList.remove("header-scrolled");
    }
});

// ==================== FILE UPLOAD HANDLING ====================

// Click to browse
uploadArea.addEventListener("click", () => fileInput.click());
uploadArea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        fileInput.click();
    }
});

// File selected via browse
fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Drag and drop events
uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("drag-over");
});

uploadArea.addEventListener("dragleave", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("drag-over");
});

uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
    }
});

// Remove file
removeFileBtn.addEventListener("click", () => {
    resetFileSelection();
});

/**
 * Process the selected file and show it in the UI.
 */
function handleFile(file) {
    // Validate type
    if (!ACCEPTED_TYPES.includes(file.type) && !file.name.toLowerCase().endsWith(".pdf")) {
        showError("Unsupported file type. Please upload a PDF, PNG, JPG, or TIFF file.");
        return;
    }

    // Validate size
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        showError(`File is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`);
        return;
    }

    selectedFile = file;

    // Show file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileSelected.classList.remove("hidden");

    // Show analyze button
    analyzeBtn.classList.remove("hidden");
    analyzeBtn.disabled = false;

    // Hide previous results/errors
    hideError();
    resultsSection.classList.add("hidden");
}

function resetFileSelection() {
    selectedFile = null;
    fileInput.value = "";
    fileSelected.classList.add("hidden");
    analyzeBtn.classList.add("hidden");
    analyzeBtn.disabled = true;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
}

// ==================== ANALYSIS ====================

analyzeBtn.addEventListener("click", () => {
    if (!selectedFile) return;
    startAnalysis();
});

async function startAnalysis() {
    // UI: enter loading state
    setLoading(true);
    hideError();
    resultsSection.classList.add("hidden");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
        const response = await fetch(ANALYZE_URL, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            setLoading(false);
            return;
        }

        renderResults(data);
        setLoading(false);
        resultsSection.classList.remove("hidden");

        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 200);

    } catch (err) {
        setLoading(false);
        if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
            showError("Cannot connect to the backend server. Make sure the FastAPI server is running on localhost:8000.");
        } else {
            showError(err.message || "An unexpected error occurred.");
        }
    }
}

function setLoading(isLoading) {
    if (isLoading) {
        loadingSection.classList.remove("hidden");
        analyzeBtn.disabled = true;
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");
        uploadArea.style.pointerEvents = "none";
    } else {
        loadingSection.classList.add("hidden");
        analyzeBtn.disabled = false;
        btnText.classList.remove("hidden");
        btnLoader.classList.add("hidden");
        uploadArea.style.pointerEvents = "auto";
    }
}

// ==================== ERROR HANDLING ====================

function showError(msg) {
    errorMessage.textContent = msg;
    errorSection.classList.remove("hidden");
}

function hideError() {
    errorSection.classList.add("hidden");
}

// ==================== RENDER RESULTS ====================

function renderResults(data) {
    // -- Confidence gauge --
    const score = data.confidence_score || 0;
    animateGauge(score);

    // -- Counts --
    analyzedCount.textContent = data.analyzed_sections_count || 0;
    totalSections.textContent = data.total_sections || 0;

    // -- Compliance status badge --
    const status = data.final_compliance_status || "Unknown";
    statusBadge.textContent = status;
    statusBadge.className = "status-badge px-5 py-2.5 rounded-full text-sm font-bold mb-3";
    if (status === "Compliant") {
        statusBadge.classList.add("status-badge-compliant");
    } else if (status === "Non-Compliant") {
        statusBadge.classList.add("status-badge-noncompliant");
    } else {
        statusBadge.classList.add("status-badge-insufficient");
    }

    // -- Compliance ratio --
    complianceRatio.textContent = data.compliance_ratio != null
        ? data.compliance_ratio.toFixed(2)
        : "N/A";

    // -- Flagged count + severity summary --
    const clauses = data.flagged_clauses || [];
    flaggedCount.textContent = clauses.length;
    renderSeveritySummary(clauses);

    // -- Summary cards --
    const summary = data.summary || {};
    pricingText.textContent = summary.pricing || "No data available.";
    legalText.textContent = summary.legal || "No data available.";
    coverageText.textContent = summary.coverage || "No data available.";

    // -- Flagged clauses --
    renderFlaggedClauses(clauses);

    // -- Analyzed sections accordion --
    renderSections(data.analyzed_sections || []);
}

// ==================== GAUGE ANIMATION ====================

function animateGauge(score) {
    const circumference = 2 * Math.PI * 50; // r=50
    const target = (score / 100) * circumference;

    // Choose colour based on score
    let color = "#2b6cb0"; // default trust blue
    if (score >= 70) color = "#38a169";       // green
    else if (score >= 40) color = "#dd6b20";  // amber
    else color = "#e53e3e";                    // red

    gaugeCircle.style.stroke = color;

    // Animate from 0
    gaugeCircle.setAttribute("stroke-dasharray", `0 ${circumference}`);

    // Force reflow then animate
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            gaugeCircle.setAttribute("stroke-dasharray", `${target} ${circumference}`);
        });
    });

    // Animate number counter
    animateCounter(gaugeValue, 0, score, 1000);
}

function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    const range = end - start;

    function tick(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        element.textContent = Math.round(start + range * eased);
        if (progress < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
}

// ==================== SEVERITY SUMMARY ====================

function renderSeveritySummary(clauses) {
    const counts = { high: 0, medium: 0, low: 0 };
    clauses.forEach(c => {
        const s = (c.severity || "low").toLowerCase();
        if (counts[s] !== undefined) counts[s]++;
    });

    severitySummary.innerHTML = "";

    if (counts.high > 0) {
        severitySummary.innerHTML += `<span class="severity-high text-xs font-semibold px-2.5 py-1 rounded-full">${counts.high} High</span>`;
    }
    if (counts.medium > 0) {
        severitySummary.innerHTML += `<span class="severity-medium text-xs font-semibold px-2.5 py-1 rounded-full">${counts.medium} Medium</span>`;
    }
    if (counts.low > 0) {
        severitySummary.innerHTML += `<span class="severity-low text-xs font-semibold px-2.5 py-1 rounded-full">${counts.low} Low</span>`;
    }
}

// ==================== FLAGGED CLAUSES ====================

function renderFlaggedClauses(clauses) {
    flaggedContainer.innerHTML = "";

    if (clauses.length === 0) {
        noFlagged.classList.remove("hidden");
        return;
    }

    noFlagged.classList.add("hidden");

    clauses.forEach((clause, idx) => {
        const severity = (clause.severity || "low").toLowerCase();
        const severityClass = `severity-${severity}`;

        const row = document.createElement("div");
        row.className = "clause-row px-6 py-4";
        row.innerHTML = `
            <div class="flex items-start gap-3">
                <span class="flex-shrink-0 mt-0.5 ${severityClass} text-xs font-bold px-2.5 py-1 rounded-full uppercase">${severity}</span>
                <div class="flex-1 min-w-0">
                    <p class="text-sm text-navy-700 font-medium leading-relaxed mb-1.5">"${escapeHTML(clause.clause_text || "")}"</p>
                    <p class="text-xs text-navy-500 leading-relaxed">
                        <span class="font-semibold text-navy-600">Issue:</span> ${escapeHTML(clause.issue || "No details provided.")}
                    </p>
                </div>
            </div>
        `;
        flaggedContainer.appendChild(row);
    });
}

// ==================== ANALYZED SECTIONS ACCORDION ====================

function renderSections(sections) {
    sectionsAccordion.innerHTML = "";

    sections.forEach((section, idx) => {
        const status = section.status || "Unknown";
        let dotClass = "section-dot-insufficient";
        if (status === "Compliant") dotClass = "section-dot-compliant";
        else if (status === "Non-Compliant") dotClass = "section-dot-noncompliant";

        const laws = (section.matched_laws || []).join(", ") || "None";

        const item = document.createElement("div");
        item.className = "accordion-item";
        item.innerHTML = `
            <button class="accordion-trigger w-full px-6 py-4 flex items-center justify-between text-left hover:bg-navy-50/50 transition-colors" aria-expanded="false">
                <div class="flex items-center gap-3 min-w-0">
                    <span class="w-2.5 h-2.5 rounded-full flex-shrink-0 ${dotClass}"></span>
                    <span class="text-sm text-navy-700 font-medium truncate">Section ${idx + 1}: ${escapeHTML(truncate(section.section_text || "", 80))}</span>
                </div>
                <svg class="accordion-chevron w-4 h-4 text-navy-400 flex-shrink-0 ml-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <div class="accordion-content px-6 pb-0">
                <div class="pl-5 border-l-2 border-navy-100 ml-0.5">
                    <p class="text-xs text-navy-400 mb-1"><span class="font-semibold">Status:</span> <span class="font-semibold ${status === 'Compliant' ? 'text-emerald-600' : status === 'Non-Compliant' ? 'text-red-500' : 'text-amber-600'}">${status}</span></p>
                    <p class="text-xs text-navy-400 mb-2"><span class="font-semibold">Matched Laws:</span> ${escapeHTML(laws)}</p>
                    <p class="text-xs text-navy-500 leading-relaxed">${escapeHTML(section.section_text || "")}</p>
                </div>
            </div>
        `;

        // Toggle accordion
        const trigger = item.querySelector(".accordion-trigger");
        const content = item.querySelector(".accordion-content");
        const chevron = item.querySelector(".accordion-chevron");

        trigger.addEventListener("click", () => {
            const isOpen = content.classList.contains("open");
            // Close all others
            sectionsAccordion.querySelectorAll(".accordion-content.open").forEach(c => {
                c.classList.remove("open");
                c.parentElement.querySelector(".accordion-chevron").classList.remove("open");
                c.parentElement.querySelector(".accordion-trigger").setAttribute("aria-expanded", "false");
            });
            if (!isOpen) {
                content.classList.add("open");
                chevron.classList.add("open");
                trigger.setAttribute("aria-expanded", "true");
            }
        });

        sectionsAccordion.appendChild(item);
    });
}

// ==================== NEW ANALYSIS ====================

newAnalysisBtn.addEventListener("click", () => {
    resultsSection.classList.add("hidden");
    resetFileSelection();
    hideError();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
});

// ==================== UTILITIES ====================

function escapeHTML(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function truncate(str, maxLen) {
    if (str.length <= maxLen) return str;
    return str.substring(0, maxLen).trim() + "…";
}
