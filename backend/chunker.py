import re
from typing  import List

def split_into_sections(text: str) -> List[str]:
    """
    Docstring for split_into_sections
    
    :param text: Description
    :type text: str
    :return: Description
    :rtype: List[str]

    split document text into sections based on headings commonly found 
    in motor insurances.
    Best use case is in this scenario because here
    splitting is not like normal paragraphs and should be based on headings that are common.
    """

    # common headings found 

    section_patterns=[
        r"policy\s+details",
        r"policy\s+period",
        r"insured\s+details",
        r"veichle\s+deails",
        r"coverage",
        r"own\s+damage",
        r"third\s+party",
        r"premium\s+breakup",
        r"idv",
        r"exclusions",
        r"terms\s+and\s+conditions",
        r"limitations",
        r"cancellation",
        r"renewal",
        r"claim\s+procedure",
        r"grievance"
    ]

    # this is a regex pattern that will split  when a section keyword appears

    pattern="(" + "|".join(section_patterns) + ")"
    splits=re.split(pattern,text, flags=re.IGNORECASE)

    sections=[]
    buffer=""

    for part in splits:
        if part.strip().lower() in [p.replace("\\s+"," ") for p in section_patterns]:
            if buffer.strip():
                sections.append(buffer.strip())
            buffer=part

        else:
            buffer+=" "+part
        
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