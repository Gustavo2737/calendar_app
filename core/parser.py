import re
from datetime import datetime, timedelta

def parse_quick_add(text):
    """Interpreta textos como 'Estudar amanhã às 19:30'."""
    title = text
    due_date = None
    due_time = None
    
    # Extrai data
    if re.search(r'\bamanh[aã]\b', text, re.IGNORECASE):
        due_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        title = re.sub(r'\bamanh[aã]\b', '', title, flags=re.IGNORECASE)
    elif re.search(r'\bhoje\b', text, re.IGNORECASE):
        due_date = datetime.now().strftime("%Y-%m-%d")
        title = re.sub(r'\bhoje\b', '', title, flags=re.IGNORECASE)
        
    # Extrai hora (ex: às 19h ou 19:30)
    time_match = re.search(r'(?:às|as)?\s*(\d{1,2})(?:h|:)(\d{2})?', title, re.IGNORECASE)
    if time_match:
        h = int(time_match.group(1))
        m = int(time_match.group(2)) if time_match.group(2) else 0
        due_time = (h * 60) + m
        title = title.replace(time_match.group(0), '')
        
    return title.strip(), due_date, due_time