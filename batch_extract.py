import json
import re
import os

files = [
"J20220325.html", "J20220327.html", "J20220328.html", "J20220329.html", "J20220401.html", "J20220404.html", "J20220405.html", "J20220406.html", "J20220407.html", "J20220408.html", "J20220409.html", "J20220411.html", "J20220412.html", "J20220413.html", "J20220414.html", "J20220415.html", "J20220418.html", "J20220419.html", "J20220421.html", "J20220422.html", "J20220424.html", "J20220425.html", "J20220427.html", "J20220428.html", "J20220501.html", "J20220502.html", "J20220503.html", "J20220505.html", "J20220506.html", "J20220509.html", "J20220510.html", "J20220511.html", "J20220512.html", "J20220513.html", "J20220514.html", "J20220515.html", "J20220516.html", "J20220517.html", "J20220519.html", "J20220520.html", "J20220521.html", "J20220522.html", "J20220523.html", "J20220524.html", "J20220525.html", "J20220526.html", "J20220528.html", "J20220530.html", "J20220531.html", "J20220601.html", "J20220602.html", "J20220604.html", "J20220606.html", "J20220608.html", "J20220610.html", "J20220613.html", "J20220615.html", "J20220616.html", "J20220618.html", "J20220619.html", "J20220620.html", "J20220621.html", "J20220622.html", "J20220623.html", "J20220624.html", "J20220626.html", "J20220627.html", "J20220628.html", "J20220629.html", "J20220630.html", "J20220701.html", "J20220706.html", "J20220708.html", "J20220709.html", "J20220710.html", "J20220713.html", "J20220719.html", "J20220721.html", "J20220722.html", "J20220723.html", "J20220724.html", "J20220726.html", "J20220729.html", "J20220801.html", "J20220802.html", "J20220803.html", "J20220804.html", "J20220809.html", "J20220815.html", "J20220816.html", "J20220829.html", "J20220830.html", "J20220831.html", "J20220901.html", "J20220904.html", "J20220917.html", "J20220922.html", "J20220924.html", "J20220926.html", "J20220927.html"
]

data = []
for f in files:
    path = os.path.join("/Users/admin/journalOfDisquiet/", f)
    try:
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
            # Extract date
            date_match = re.search(r'<p class="date">Date: (.*?)</p>', content)
            date = date_match.group(1).split(" ")[0] if date_match else f.replace(".html", "")
            
            # Extract main content - between <div id="content" ...> and <div id="postamble" ...>
            # Looking specifically for the text in outline-text-2
            text_match = re.search(r'<div class="outline-text-2"[^>]*>(.*?)</div>', content, re.DOTALL)
            text = text_match.group(1).strip() if text_match else ""
            
            # Also check for outline-4 Thought if it exists
            thought_match = re.search(r'<div id="outline-container-org[^"]*" class="outline-4">.*?<div class="outline-text-4"[^>]*>(.*?)</div>', content, re.DOTALL)
            if thought_match:
                text += "\n\n" + thought_match.group(1).strip()
            
            data.append({"file": f, "date": date, "text": text})
    except Exception as e:
        print(f"Error reading {f}: {e}")

with open("/Users/admin/journalOfDisquiet/batch_data.json", "w", encoding="utf-8") as fp:
    json.dump(data, fp, indent=2)
print("Extracted to batch_data.json")
