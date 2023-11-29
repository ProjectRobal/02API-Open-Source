import re

# It validates login to avoid characters likes emoicons
login_regex=re.compile(r"^[A-Za-z0-9 :-@[-`{-~!-\\]+$")

# It looks for HTML code, it is useful to avoid code injection
html_regex=re.compile(r"<(\"[^\"]*?\"|'[^']*?'|[^'\">])*>")

# It ensures that topic path has a form of /...
topic_regex=re.compile(r"^/+[\w /]+(?<!/)$")