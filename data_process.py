import json
import os

# 1. 读取爬虫原始结果
input_path = '/home/janie/RAG/RAG_Mistral-main/RAG_Mistral-main/medical_data.json'
with open(input_path, 'r', encoding='utf-8') as f:
    raw_articles = json.load(f)

sft_list = []

# 2. 构造微调对
for item in raw_articles:
    title = item.get('article_title', '').strip()
    abstract = item.get('article_abstract', '').strip()
    
    # 过滤掉没有摘要或标题太短的无效数据
    if len(abstract) > 50 and len(title) > 5:
        sft_list.append({
            "instruction": "Summarize the following medical research title into a professional academic abstract.",
            "input": title,
            "output": abstract
        })

# 3. 保存到 LLaMA-Factory 的数据路径
output_path = '/home/janie/RAG/LLaMA-Factory/LLaMA-Factory-main/data/medical_sft_data.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sft_list, f, ensure_ascii=False, indent=2)

print(f"✅ SFT 数据处理完成！共生成 {len(sft_list)} 条微调数据。")