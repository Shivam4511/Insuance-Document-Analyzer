from typing import Dict, List
import re

from chunker import chunk_document
from retriever import Retriever
from llm_engine import LLMEngine

# Sections that matter most for compliance — analyze these first
_PRIORITY_KEYWORDS = [
    "exclusion", "terms and conditions", "cancellation",
    "premium", "limitation", "coverage", "claim",
    "third party", "own damage", "renewal", "grievance",
]


def _section_priority(chunk: str) -> int:
    """Lower number = higher priority. Critical sections come first."""
    lower = chunk.lower()
    for idx, kw in enumerate(_PRIORITY_KEYWORDS):
        if kw in lower:
            return idx
    return len(_PRIORITY_KEYWORDS)  # metadata / other sections last


def _deduplicate_notes(notes: List[str]) -> str:
    """Pick the most informative, non-redundant summary sentences."""
    if not notes:
        return "Not enough information in the analyzed sections."

    # Filter out 'Not applicable' / empty entries
    meaningful = [n for n in notes if n and "not applicable" not in n.lower()]
    if not meaningful:
        return "Not applicable for the analyzed sections."

    # Keep unique sentences (simple dedup by normalized text)
    seen = set()
    unique: List[str] = []
    for note in meaningful:
        key = re.sub(r"\s+", " ", note.strip().lower())
        if key not in seen:
            seen.add(key)
            unique.append(note.strip())

    # Return the longest (most detailed) note, or join up to 2
    unique.sort(key=len, reverse=True)
    return " ".join(unique[:2])


class ComplianceEngine:
    """Engine to analyze insurance documents for compliance issues."""

    def __init__(
            self,
            retriever: Retriever,
            llm_engine: LLMEngine,
            confidence_threshold: float = 0.6
    ):
        self.retriever = retriever
        self.llm_engine = llm_engine
        self.confidence_threshold = confidence_threshold


    def analyze_document(self, document_text: str) -> Dict:
        """
        Assess the entire insurance document for compliance issues.
        Returns a clean, frontend-friendly response with:
        - confidence_score, final_compliance_status
        - summary (pricing / legal / coverage) — deduplicated
        - flagged_clauses sorted by severity, validated against document
        - analyzed_sections (priority-ordered)
        """
        # step 1 : chunk the document
        chunks = chunk_document(document_text)

        # step 1b : sort chunks so critical sections are analyzed first
        chunks.sort(key=_section_priority)

        compliant_count = 0
        non_compliant_count = 0

        # Collectors for aggregation
        confidence_scores: List[int] = []
        pricing_notes: List[str] = []
        legal_notes: List[str] = []
        coverage_notes: List[str] = []
        all_flagged_clauses: List[Dict] = []
        analyzed_sections: List[Dict] = []

        # step 2 : process each chunk (up to TPM limit)
        # IMPORTANT: Groq free/on_demand tiers are TPM-limited.
        max_llm_chunks = 5
        processed_chunks = 0

        for chunk in chunks:
            if not chunk or not chunk.strip():
                continue

            if processed_chunks >= max_llm_chunks:
                break

            # Retrieve relevant law clauses for this chunk
            retrieved = self.retriever.retrieve(chunk)
            law_texts = [item[0] for item in retrieved]

            # Always send to LLM — even without matching laws, the LLM can
            # flag inherently problematic or unfair clauses.
            llm_result = self.llm_engine.assess_compliance(
                policy_text=chunk,
                law_clauses=law_texts
            )

            status = llm_result.get("compliance_status", "Insufficient Information")

            if status == "Compliant":
                compliant_count += 1
            elif status == "Non-Compliant":
                non_compliant_count += 1

            # Collect per-chunk data for aggregation
            score = llm_result.get("confidence_score", 0)
            if isinstance(score, (int, float)):
                confidence_scores.append(int(score))

            pa = llm_result.get("pricing_assessment", "")
            if pa:
                pricing_notes.append(pa)

            la = llm_result.get("legal_assessment", "")
            if la:
                legal_notes.append(la)

            ca = llm_result.get("coverage_assessment", "")
            if ca:
                coverage_notes.append(ca)

            for clause in llm_result.get("flagged_clauses", []):
                if isinstance(clause, dict) and clause not in all_flagged_clauses:
                    all_flagged_clauses.append(clause)

            analyzed_sections.append({
                "section_text": chunk[:200] + ("..." if len(chunk) > 200 else ""),
                "status": status,
                "matched_laws": llm_result.get("matched_laws", []),
            })
            processed_chunks += 1

        # step 3 : aggregate results
        total_chunks = len(chunks)
        analyzed_count = len(analyzed_sections)

        compliance_ratio = (
            compliant_count / analyzed_count if analyzed_count > 0 else 0
        )

        if compliance_ratio >= self.confidence_threshold:
            final_status = "Compliant"
        elif non_compliant_count > 0:
            final_status = "Non-Compliant"
        else:
            final_status = "Insufficient Information"

        overall_confidence = (
            round(sum(confidence_scores) / len(confidence_scores))
            if confidence_scores else 0
        )

        # Sort flagged clauses: high → medium → low
        severity_order = {"high": 0, "medium": 1, "low": 2}
        all_flagged_clauses.sort(
            key=lambda c: severity_order.get(c.get("severity", "low"), 3)
        )

        # Filter flagged clauses — keep only those whose text actually
        # appears in the original document (removes LLM fabrications)
        doc_lower = document_text.lower()
        verified_clauses: List[Dict] = []
        for clause in all_flagged_clauses:
            ct = clause.get("clause_text", "")
            # Accept if a meaningful substring (8+ chars) appears in document
            if ct and len(ct) >= 8 and ct.lower()[:60] in doc_lower:
                verified_clauses.append(clause)

        return {
            "confidence_score": overall_confidence,
            "final_compliance_status": final_status,
            "compliance_ratio": round(compliance_ratio, 2),
            "summary": {
                "pricing": _deduplicate_notes(pricing_notes),
                "legal": _deduplicate_notes(legal_notes),
                "coverage": _deduplicate_notes(coverage_notes),
            },
            "flagged_clauses": verified_clauses,
            "total_sections": total_chunks,
            "analyzed_sections_count": analyzed_count,
            "analyzed_sections": analyzed_sections
        }
