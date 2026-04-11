import json
import re

files = [
"J20211130.html", "J20211202.html", "J20211203.html", "J20211208.html", "J20211213.html", "J20211214.html", "J20211216.html", "J20211218.html", "J20211223.html", "J20211224.html", "J20211226.html", "J20211227.html", "J20211228.html", "J20211229.html", "J20220103.html", "J20220105.html", "J20220106.html", "J20220111.html", "J20220112.html", "J20220122.html", "J20220126.html", "J20220131.html", "J20220202.html", "J20220204.html", "J20220208.html", "J20220210.html", "J20220211.html", "J20220213.html", "J20220214.html", "J20220218.html", "J20220219.html", "J20220220.html", "J20220222.html", "J20220223.html", "J20220224.html", "J20220226.html", "J20220228.html", "J20220302.html", "J20220303.html", "J20220307.html", "J20220308.html", "J20220311.html", "J20220313.html", "J20220314.html", "J20220315.html", "J20220318.html", "J20220321.html", "J20220322.html", "J20220323.html", "J20220324.html"
]

data = []
for f in files:
    try:
        with open("/Users/admin/journalOfDisquiet/" + f, "r") as fp:
            content = fp.read()
            date_match = re.search(r'<p class="date">Date: (.*?)</p>', content)
            date = date_match.group(1).split(" ")[0] if date_match else f.replace(".html", "")
            
            text_match = re.search(r'<div class="outline-text-2"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*<div id="postamble"', content, re.DOTALL)
            text = text_match.group(1).strip() if text_match else ""
            
            data.append({"file": f, "date": date, "text": text})
    except Exception as e:
        print(f"Error reading {f}: {e}")

with open("/Users/admin/journalOfDisquiet/extracted.json", "w") as fp:
    json.dump(data, fp)
print("Extracted to extracted.json")
