import os
import json
from bs4 import BeautifulSoup

def parse_html_to_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    questions_data = []

    # Lấy tất cả thẻ h5 nằm trong 2 dạng div chính
    h5_tags = soup.select("div.card-body h5, div.col-md-12.ml-auto.mr-auto h5")

    for index, h5 in enumerate(h5_tags, start=1):
        # ===== Lấy câu hỏi (bỏ <small>) =====
        question_text = "".join(
            child.strip() for child in h5.children if child.name != "small" and isinstance(child, str)
        ).strip()

        # ===== Lấy ảnh trong câu hỏi =====
        question_image_tags = [img["src"].strip() for img in h5.find_all("img") if not img.find_parent("small")]

        # ===== Lấy đáp án =====
        options_tags = h5.find_all("small")
        options = {}
        correct_answer = None

        for idx, opt_tag in enumerate(options_tags, start=1):
            opt_html = str(opt_tag)
            for icon in opt_tag.find_all("i"):
                icon.decompose()

            opt_text = opt_tag.get_text(strip=True).replace("\xa0", " ")

            option_image_urls = [img["src"].strip() for img in opt_tag.find_all("img") if img.get("src")]

            if "#4caf50" in opt_html or "check_box" in opt_html:
                correct_answer = idx

            options[str(idx)] = {
                "text": opt_text,
                "images": option_image_urls
            }

        questions_data.append({
            "index": index,
            "question": question_text,
            "question_images": question_image_tags,
            "options": options,
            "correctAnswer": correct_answer
        })

    return questions_data



# ===== MAIN =====
if __name__ == "__main__":
    input_file = "html/EG10-1.html"   # ✅ Thay tên file HTML nếu cần
    output_file = "json/EG10-1.json"

    os.makedirs("json", exist_ok=True)

    if not os.path.exists(input_file):
        print("❌ File HTML không tồn tại:", input_file)
        exit(1)

    print(f"📂 Đang phân tích file: {input_file}")
    data = parse_html_to_json(input_file)

    print(f"✅ Phân tích xong, số câu hỏi: {len(data)}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Đã lưu kết quả vào: {output_file}")
