# toc_utils.py
print("📦 toc_utils.py yüklendi")
def extract_toc_from_data(data, file_name):
    toc_candidates = [
        d for d in data
        if d["type"] in ("text", "table")
        and d["file"] == file_name
        and any("Item " in line for line in d["content"].splitlines())
    ]

    lines = []
    for entry in toc_candidates:
        for line in entry["content"].splitlines():
            if line.strip().lower().startswith("item"):
                lines.append(line.strip())

    # Aynı başlığı birden çok kez toplama
    unique = sorted(set(lines), key=lambda x: lines.index(x))
    return "\n".join(unique)
