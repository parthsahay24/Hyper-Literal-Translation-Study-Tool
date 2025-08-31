import os
from datetime import datetime, timezone

# Input files
html_file = "ght-i-raw.html"
js_file = "script.js"
css_file = "styles.css"
base_file = "base.json"
lookups_file = "lookups.json"

# Helper: file modification time
def file_mtime(file):
    return os.path.getmtime(file)

# Read sources
with open(html_file, encoding="utf-8") as f:
    html = f.read()
with open(js_file, encoding="utf-8") as f:
    js = f.read()
with open(css_file, encoding="utf-8") as f:
    css = f.read()
with open(base_file, encoding="utf-8") as f:
    base_json = f.read()
with open(lookups_file, encoding="utf-8") as f:
    lookups_json = f.read()

# Remove dynamic loader script
import re
html = re.sub(
    r"<script>\s*const script[\s\S]*?</script>", "", html, flags=re.MULTILINE
)

# Remove let baseData; and let lookupdb; from JS
js = re.sub(r"^\s*let\s+baseData\s*;\s*$", "", js, flags=re.MULTILINE)
js = re.sub(r"^\s*let\s+lookupdb\s*;\s*$", "", js, flags=re.MULTILINE)

# Compute timestamps
data_mtime = max(file_mtime(base_file), file_mtime(lookups_file))
tool_mtime = max(file_mtime(html_file), file_mtime(js_file), file_mtime(css_file))

def fmt(ts):
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

data_compile = fmt(data_mtime)
tool_compile = fmt(tool_mtime)

# Prepare injection
inject = f"""
<style>
{css}
</style>
<script>
// JSON data embedded
let baseData = {base_json};
let lookupdb = {lookups_json};

// Compile-time timestamps
document.getElementById("data_last_updated")?.setAttribute("data-compile-lastmod", "{data_compile}");
document.getElementById("tool_last_updated")?.setAttribute("data-compile-lastmod", "{tool_compile}");

// App code
{js}
</script>
"""

# Insert before </body> if it exists, else append
if "</body>" in html:
    html = html.replace("</body>", inject + "\n</body>")
else:
    html += inject

# Output file
out_file = "ght-i.html"
with open(out_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built {out_file}")
