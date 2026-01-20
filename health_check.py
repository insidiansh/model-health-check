import os
import json
import datetime
import random
import requests
import base64
from openai import OpenAI


API_KEY = os.getenv("SIMPLISMART_API_KEY")
if not API_KEY:
    raise RuntimeError("SIMPLISMART_API_KEY not set")

BASE_URL = "https://api.simplismart.live"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# METADATA

today = datetime.date.today().isoformat()
run_time = datetime.datetime.now().strftime("%H:%M")

report = {
    "date": today,
    "run_time": run_time,
    "results": {}
}
# GPT-OSS-120B (TEXT)
try:
    text_sources = [
        "https://www.gutenberg.org/files/84/84-0.txt",
        "https://www.gutenberg.org/files/1342/1342-0.txt",
        "https://www.gutenberg.org/files/11/11-0.txt"
    ]

    text_url = random.choice(text_sources)
    text = requests.get(text_url, timeout=20).text[:1500]

    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        default_headers={"id": "524436ef-5d4c-4d55-9351-71d67036b92b"}
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": f"Summarize this text:\n{text}"}],
        max_tokens=200,
        temperature=0
    )

    summary = response.choices[0].message.content

    print("\n[GPT-OSS SUMMARY]")
    print(summary[:300])

    report["results"]["openai/gpt-oss-120b"] = {
        "status": 200,
        "input": text_url,
        "output_preview": summary[:300]
    }

except Exception as e:
    report["results"]["openai/gpt-oss-120b"] = {
        "status": 500,
        "error": str(e)
    }
# DEEPSEEK OCR (IMAGE)
try:
    image_sources = [
        "https://commons.wikimedia.org/wiki/Special:FilePath/ReceiptSwiss.jpg",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Fax2.png"
    ]

    image_url = random.choice(image_sources)
    image_bytes = requests.get(
        image_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    ).content

    image_b64 = base64.b64encode(image_bytes).decode()

    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        default_headers={"id": "81095ce8-515a-442a-8514-d4424ec84ce2"}
    )

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-OCR",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract all readable text from this image"},
                {"type": "image_base64", "image_base64": image_b64}
            ]
        }],
        max_tokens=300,
        temperature=0
    )

    ocr_text = response.choices[0].message.content

    print("\n[DEEPSEEK OCR OUTPUT]")
    print(ocr_text[:300])

    report["results"]["deepseek-ai/DeepSeek-OCR"] = {
        "status": 200,
        "input": image_url,
        "output_preview": ocr_text[:300]
    }

except Exception as e:
    report["results"]["deepseek-ai/DeepSeek-OCR"] = {
        "status": 500,
        "error": str(e)
    }
# SAVE REPORT
output_file = f"{OUTPUT_DIR}/daily_model_health_{today}.json"
with open(output_file, "w") as f:
    json.dump(report, f, indent=2)

print("\n[FINAL REPORT]")
print(json.dumps(report, indent=2))
