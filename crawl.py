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

        # Lấy câu hỏi: chỉ lấy văn bản ngoài phần <small>
        question_text = ""
        for child in h5.children:
            if child.name == "small":
                continue  # Bỏ qua các phần tử <small>
            if isinstance(child, str):  # Lấy văn bản
                question_text += child.strip()

        question_text = question_text.strip()

        # Lọc chỉ lấy ảnh trong phần câu hỏi (thẻ h5), không lấy ảnh trong các thẻ <small>
        question_image_tags = h5.find_all("img")
        question_image_urls = []
        for img in question_image_tags:
            if not img.find_parent("small"):  # Kiểm tra ảnh không nằm trong thẻ <small>
                question_image_urls.append(img["src"].strip())

        # Lấy đáp án và các hình ảnh trong đáp án
        options_tags = h5.find_all("small")
        options = {}
        correct_answer = None

        for idx, opt_tag in enumerate(options_tags, start=1):
            opt_html = str(opt_tag)

            # Xóa icon trước khi lấy text
            for icon in opt_tag.find_all("i"):
                icon.decompose()

            opt_text = opt_tag.get_text(strip=True)

            # Lấy tất cả ảnh trong phần đáp án
            option_image_tags = opt_tag.find_all("img")
            option_image_urls = [img["src"].strip() for img in option_image_tags if img.get("src")]

            if "#4caf50" in opt_html or "check_box" in opt_html:
                correct_answer = idx

            options[str(idx)] = {
                "text": opt_text.replace("\xa0", " ").strip(),
                "images": option_image_urls  # Thêm ảnh vào đáp án
            }

        questions_data.append({
            "question": question_text,
            "question_images": question_image_urls,  # Chỉ lấy ảnh trong phần câu hỏi
            "options": options,
            "correctAnswer": correct_answer if correct_answer is not None else None
        })

    return questions_data


# ====== MAIN ======
url = "http://ehou.online/dap-an-mon-hoc-ehou/IT11"

os.makedirs("html", exist_ok=True)
os.makedirs("json", exist_ok=True)

filename = os.path.join("html", url.rstrip("/").split("/")[-1] + ".html")

# Lấy HTML từ URL
response = requests.get(url)
response.encoding = 'utf-8'
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.text)
print(f"✅ Đã lưu HTML vào {filename}")

# Phân tích HTML và lưu dữ liệu vào JSON
output_file = os.path.join("json", os.path.splitext(os.path.basename(filename))[0] + ".json")
questions = parse_html_to_json(filename)

# Lưu kết quả dưới dạng JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"✅ Đã chuyển {filename} → {output_file}")
