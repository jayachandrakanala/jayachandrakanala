def index_transcript(transcript_text: str) -> str:
    """
    Prepends line numbers to each non-empty line of the transcript
    to facilitate line-level grounding and citation.
    """
    lines = transcript_text.strip().split("\n")
    indexed_lines = []
    line_num = 1
    for line in lines:
        cleaned = line.strip()
        if cleaned:
            indexed_lines.append(f"Line {line_num:02d}: {cleaned}")
            line_num += 1
    return "\n".join(indexed_lines)