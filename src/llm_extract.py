import json
import re
from groq_client import client

def extract_bill(text):
    prompt = f"""
You are a strict JSON generator.

Extract bill details from the text below.
Return ONLY valid JSON. No explanation. No extra text.

JSON format:
{{
  "bill_type": "Medical/Grocery/Fuel/Clothing",
  "vendor": "",
  "bill_date": "YYYY-MM-DD",
  "amount": 0
}}

Bill text:
{text[:3000]}
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = res.choices[0].message.content.strip()

    # -------- CLEAN COMMON LLM NOISE --------
    raw = raw.replace("```json", "").replace("```", "").strip()

    # -------- FIND JSON OBJECT --------
    match = re.search(r"\{[\s\S]*\}", raw)

    if not match:
        # 🔁 SAFE FALLBACK (do not crash app)
        return {
            "bill_type": "Unknown",
            "vendor": "",
            "bill_date": "",
            "amount": 0
        }

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        # 🔁 SECOND FALLBACK
        return {
            "bill_type": "Unknown",
            "vendor": "",
            "bill_date": "",
            "amount": 0
        }
