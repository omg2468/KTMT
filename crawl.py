import requests
import os
import json
from bs4 import BeautifulSoup

def parse_html_to_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    questions_data = []

    card_blocks = soup.find_all("div", class_="card card-pricing text-left")

    for card in card_blocks:
        h5 = card.find("h5")
        if not h5:
            continue

        # Lấy câu hỏi: phần text trước small đầu tiên
        first_small = h5.find("small")
        question_text = h5.get_text(separator="\n", strip=True)
        if first_small:
            question_text = question_text.split("\n")[0].strip()

        # Lấy tất cả ảnh trong card
        image_tags = card.find_all("img")
        image_urls = [img["src"].strip() for img in image_tags if img.get("src")]

        # Lấy đáp án
        options_tags = h5.find_all("small")
        options = {}
        correct_answer = None

        for idx, opt_tag in enumerate(options_tags, start=1):
            opt_html = str(opt_tag)

            # Xóa icon trước khi lấy text
            for icon in opt_tag.find_all("i"):
                icon.decompose()

            opt_text = opt_tag.get_text(strip=True)

            if "#4caf50" in opt_html or "check_box" in opt_html:
                correct_answer = idx

            options[str(idx)] = opt_text.replace("\xa0", " ").strip()

        questions_data.append({
            "question": question_text,
            "image": image_urls,
            "options": options,
            "correctAnswer": correct_answer if correct_answer is not None else None
        })

    return questions_data


# ====== MAIN ======
url = "http://ehou.online/dap-an-mon-hoc-ehou/EG10-1"

os.makedirs("html", exist_ok=True)
os.makedirs("json", exist_ok=True)

filename = os.path.join("html", url.rstrip("/").split("/")[-1] + ".html")

response = requests.get(url)
response.encoding = 'utf-8'
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.text)
print(f"✅ Đã lưu HTML vào {filename}")

output_file = os.path.join("json", os.path.splitext(os.path.basename(filename))[0] + ".json")
questions = parse_html_to_json(filename)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"✅ Đã chuyển {filename} → {output_file}")
