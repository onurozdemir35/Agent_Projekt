# prompt_utils.py
def build_missing_prompt(file_name, missing_items_string):
    items = [i.strip() for i in missing_items_string.split(",") if i.strip()]
    if not items:
        return ""

    item_list = "\n".join(
        f"* {item}: Lütfen bu bölümün içeriğini varsayım veya tipik bir 10-K yapısına göre özetle."
        for item in items
    )

    prompt = f"""
Bu dosyada aşağıdaki Item başlıkları eksik. Lütfen tipik bir 10-K yapısına göre bu başlıkların neleri içermesi gerektiğini açıklayıcı şekilde tahmin et ve özetle:

{item_list}
"""
    return prompt
