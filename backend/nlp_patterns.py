
MONTHS = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

WORD_COMMA_WORD =  [    
    {"IS_ASCII": True},    
    {"IS_SPACE": True, "OP": "?"},     
    {"IS_ASCII": True, "OP": "?"},    
    {"IS_SPACE": True, "OP": "?"},     
    {"IS_ASCII": True, "OP": "?"},       
    {"TEXT": ","},
    {"IS_SPACE": True, "OP": "?"},
    {"IS_ASCII": True},           
    {"IS_SPACE": True, "OP": "?"},     
    {"IS_ASCII": True, "OP": "?"},    
    {"IS_SPACE": True, "OP": "?"},     
    {"IS_ASCII": True, "OP": "?"},    
    {"IS_SPACE": True, "OP": "?"},     
    {"IS_ASCII": True, "OP": "?"}      
]


DATE_RANGE_ENDING_WITH_YEAR = [
    {"TEXT": {"IN": MONTHS}},           # Start month
    {"IS_SPACE": True, "OP": "?"},
    {"SHAPE": "dddd"},                  # Start year
    {"IS_SPACE": True, "OP": "?"},
    {"TEXT": "–"},
    {"IS_SPACE": True, "OP": "?"},
    {"TEXT": {"IN": MONTHS}},           # End month
    {"IS_SPACE": True, "OP": "?"},
    {"SHAPE": "dddd"}                   # End year
]

DATE_RANGE_ENDING_WITH_PRESENT = [
    {"TEXT": {"IN": MONTHS}},           # Start month
    {"IS_SPACE": True, "OP": "?"},
    {"SHAPE": "dddd"},                  # Start year
    {"IS_SPACE": True, "OP": "?"},
    {"TEXT": "–"},
    {"IS_SPACE": True, "OP": "?"},
    {"TEXT": {"REGEX":"(\d{4}|Present)"}}                 
]

SINGLE_BULLET = [
    {"TEXT": "●"},              # Bullet point character
    {"IS_SPACE": True},         # Space after bullet
    {"IS_ASCII": True},         # First word
    {"IS_ASCII": True, "OP": "+"},  # More words
    {"TEXT": ".", "OP": "?"}    # Optional period at end
]

JOB_PATTERN_1 = WORD_COMMA_WORD + [{"IS_SPACE": True, "OP": "?"}] + DATE_RANGE_ENDING_WITH_YEAR + [{"IS_SPACE": True, "OP": "?"}] + SINGLE_BULLET
JOB_PATTERN_2 = WORD_COMMA_WORD + [{"IS_SPACE": True, "OP": "?"}] + DATE_RANGE_ENDING_WITH_PRESENT + [{"IS_SPACE": True, "OP": "?"}] + SINGLE_BULLET

EDUCATION_PATTERN = [
    {"IS_ASCII": True, "OP":"+"},
    {"TEXT": ","},
] + DATE_RANGE_ENDING_WITH_YEAR

REGEX_DATE = [
    {"TEXT": {"REGEX":"((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|Present)"}}              
    {"IS_SPACE": True, "OP": "?"},
    {"TEXT": "–"},
    {"IS_SPACE": True, "OP": "+"},
    {"TEXT": {"REGEX":"((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|Present)"}}                
]