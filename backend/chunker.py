import re
from typing  import List

def split_into_sections(text: str) -> List[str]:
    """
    Docstring for split_into_sections
    
    :param text: Description
    :type text: str
    :return: Description
    :rtype: List[str]

    split document text into sections based on ALL-CAPS headings commonly found 
    in motor insurance documents.
    Case-sensitive matching ensures mid-sentence words like "coverage" or
    "Third Party" do NOT trigger a split — only true headings do.
    """

    # ALL-CAPS headings found in typical motor insurance documents

    section_patterns=[
        r"POLICY\s+DETAILS",
        r"POLICY\s+PERIOD",
        r"INSURED\s+DETAILS",
        r"VEHICLE\s+DETAILS",
        r"COVERAGE",
        r"OWN\s+DAMAGE",
        r"THIRD\s+PARTY",
        r"PREMIUM\s+BREAKUP",
        r"IDV",
        r"EXCLUSIONS",
        r"TERMS\s+AND\s+CONDITIONS",
        r"LIMITATIONS",
        r"CANCELLATION",
        r"RENEWAL",
        r"CLAIM\s+PROCEDURE",
        r"GRIEVANCE"
    ]

    # this is a regex pattern that will split when a section keyword appears
    # NO re.IGNORECASE — we only match ALL-CAPS headings

    pattern="(" + "|".join(section_patterns) + ")"
    splits=re.split(pattern, text)

    sections=[]
    buffer=""

    for part in splits:
        stripped = part.strip()
        # Check if this part matches any section pattern (case-sensitive)
        is_section = any(re.fullmatch(p, stripped) for p in section_patterns)
        
        if is_section:
            if buffer.strip():
                sections.append(buffer.strip())
            buffer=part
        else:
            buffer+=" "+part
    
    # Append the last buffer if it exists
    if buffer.strip():
        sections.append(buffer.strip())

    return sections


def chunk_text_by_length(text: str, max_words: int = 200) -> List[str]:
    """
    Docstring for chunk_text_by_length
    
    :param text: Description
    :type text: str
    :param max_words: Description
    :type max_words: int
    :return: Description
    :rtype: List[str]

    further split sections into small chunks 
    based on limit this helps to do better tuning and good understanding.
    """

    words=text.split()
    chunks=[]

    for i in range(0, len(words), max_words):
        chunk=" ".join(words[i:i+max_words])
        chunks.append(chunk)

    return chunks

def chunk_document(text: str) -> List[str]:
    """
    Docstring for chunk_document
    
    :param text: Description
    :type text: str
    :return: Description
    :rtype: List[str]

    main function for this file
    entry point for this file.
    """

    sections=split_into_sections(text)

    final_chunks=[]

    for section in sections:
        if len(section.split()) > 250:
            final_chunks.extend(chunk_text_by_length(section))
        else:
            final_chunks.append(section)

    return final_chunks