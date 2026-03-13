import os
import json
import requests
from typing import List, Dict

class LLMEngine:
    """
    Docstring for LLMEngine

    LLM-based reasoning engine for insurance compliance assessment , 
    we have done here system prompting to minimize hallucination also did temprature 
    tuning setting to min 
    """

    def __init__(
            self,
            model_name: str="llama-3.1-8b-instant",
            temperature: float=0.1,
            max_output_tokens: int = 512,
            max_law_clauses: int = 1,
            max_clause_chars: int = 350,
    ):
        """
        Docstring for __init__
        
        :param self: Description
        :param model_name: Description
        :type model_name: str
        :param temperature: Description
        :type temperature: float
        """

        self.model_name=model_name
        self.temperature=temperature
        self.max_output_tokens = max_output_tokens
        self.max_law_clauses = max_law_clauses
        self.max_clause_chars = max_clause_chars
        self.api_key=os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.api_url="https://api.groq.com/openai/v1/chat/completions"

    def _build_prompt(
            self,
            policy_text: str,
            law_clauses: List[str],
    ) -> List[Dict[str, str]]:
        
        """
        Docstring for _build_prompt
        
        :param self: Description
        :param policy_text: Description
        :type policy_text: str
        :param law_clauses: Description
        :type law_clauses: List[str]
        :return: Description
        :rtype: List[Dict[str, str]]
        """

        # Reduce token usage: keep only top-N clauses and truncate each clause
        trimmed_laws: List[str] = []
        for clause in (law_clauses or [])[: self.max_law_clauses]:
            if not clause:
                continue
            c = clause.strip()
            if len(c) > self.max_clause_chars:
                c = c[: self.max_clause_chars].rstrip() + "..."
            trimmed_laws.append(c)

        law_context="\n\n".join(
            [f"[LAW {i+1}] {clause}" for i, clause in enumerate(trimmed_laws)]
        ) if trimmed_laws else "No specific legal clauses available for this section."

        system_prompt=(
            "You are an expert compliance analyst for Indian motor insurance."
            " Analyze the policy text against the provided legal context."
            " Assess pricing fairness, legal compliance, and coverage adequacy."
            " Flag any problematic or unfair clauses you find in the policy text."
            " Even if no legal context is provided, still flag clauses that are"
            " inherently problematic, misleading, or unfair to policyholders."
            " Output STRICT JSON only (no markdown fences)."
        )

        user_prompt= f"""
POLICY TEXT:
{policy_text}

LEGAL CONTEXT:
{law_context}

TASK:
Analyze the POLICY TEXT against the LEGAL CONTEXT. Assess compliance, pricing, legal adherence, and coverage.
Flag ONLY clauses from the POLICY TEXT that are genuinely problematic, unfair, or misleading to the policyholder.
If no legal context is available, still flag any clauses that appear inherently unfair based on standard Indian motor insurance practices.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "compliance_status": "Compliant | Non-Compliant | Insufficient Information",
  "confidence_score": 85,
  "pricing_assessment": "1-2 sentence assessment of pricing/premium fairness. Say 'Not applicable' if no pricing info in this section.",
  "legal_assessment": "1-2 sentence assessment of adherence to Motor Vehicles Act / IRDAI guidelines.",
  "coverage_assessment": "1-2 sentence assessment of coverage adequacy. Say 'Not applicable' if no coverage info in this section.",
  "flagged_clauses": [
    {{
      "clause_text": "Copy-paste the EXACT problematic sentence from POLICY TEXT",
      "issue": "Specific reason why this harms or misleads the policyholder",
      "severity": "high | medium | low"
    }}
  ],
  "matched_laws": ["LAW 1"]
}}

RULES:
- confidence_score must be an integer 0-100.
- clause_text MUST be a direct quote from the POLICY TEXT above. NEVER quote from LEGAL CONTEXT.
- Do NOT flag purely informational fields (names, addresses, dates, vehicle details, policy numbers).
- Do NOT flag a policy type being what it is (e.g. "Third Party Insurance" is not misleading).
- Only flag clauses that have REAL impact on policyholder rights, obligations, or financial exposure.
- If no problematic clauses exist, return an empty flagged_clauses array.
- If no legal context is available, set matched_laws to [] and compliance_status to "Insufficient Information".
"""
        
        return [
            {"role": "system","content": system_prompt},
            {"role": "user","content": user_prompt}
        ]
    

    def assess_compliance(
            self,
            policy_text: str,
            law_clauses: List[str]
    ) -> Dict[str, str]:
        
        """
        Docstring for assess_compliance
        
        :param self: Description
        :param policy_text: Description
        :type policy_text: str
        :param law_clauses: Description
        :type law_clauses: List[str]
        :return: Description
        :rtype: Dict[str, str]
        """

        message=self._build_prompt(policy_text, law_clauses)

        payload={
            "model": self.model_name,
            "messages": message,
            "temperature": self.temperature,
            "max_tokens": self.max_output_tokens
        }
        
        headers={
            "Authorization":f"Bearer {self.api_key}",
            "Content-Type":"application/json"
        }

        response=requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Provide error information
            error_msg = f"Groq API request failed: {e}"
            try:
                error_detail = response.json()
                error_msg += f"\nAPI Response: {error_detail}"
            except:
                error_msg += f"\nResponse text: {response.text}"
            raise requests.exceptions.HTTPError(error_msg, response=response) from e

        try:
            response_data = response.json()
            if "choices" not in response_data or not response_data["choices"]:
                raise ValueError("No choices in API response")
            
            raw_output = response_data["choices"][0]["message"]["content"]
            
            if not raw_output:
                raise ValueError("Empty response from API")
            
            try:
                return json.loads(raw_output)
            except json.JSONDecodeError:
                #fallback : return explanation without breaking pipeline
                return {
                    "compliance_status": "Error",
                    "confidence_score": 0,
                    "pricing_assessment": "Unable to parse LLM response.",
                    "legal_assessment": "Unable to parse LLM response.",
                    "coverage_assessment": "Unable to parse LLM response.",
                    "flagged_clauses": [],
                    "matched_laws": [],
                    "raw_output": raw_output
                }
        except (KeyError, IndexError, ValueError) as e:
            raise ValueError(f"Invalid API response format: {e}")
        