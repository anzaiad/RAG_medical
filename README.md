
# Medical QA System: RAG + Mistral-7B Fine-tuning

本项目构建了一个结合 **检索增强生成 (RAG)** 与 **监督微调 (SFT)** 的专业医疗问答系统。基于 PubMed 论文数据，利用 Mistral-7B 模型提供具备可溯源性的医学咨询服务。

## 📂 项目目录结构

根据您的 VS Code 实际环境整理，建议保持如下层级：

```text
RAG/
├── chroma_medical_db_final/   # 持久化向量数据库
├── LLaMA-Factory/             # 微调框架目录
│   └── saves/Mistral-7B/lora/medical_sft_v1/  # 训练生成的 LoRA 权重
├── models/                    # 基座模型与嵌入模型
│   ├── Mistral-7B-v0.1/       # 基础 LLM
│   └── e5-large-unsupervised/ # Embedding 模型
├── download_pubmed.py         # 数据爬虫脚本
├── medical_data.json          # 爬取的原始数据
├── data_process.py            # SFT 数据格式转换脚本
├── rag_usecase.ipynb          # RAG 实验与演示 Notebook
└── README.md                  # 本文档

```

 🚀 核心技术流程

### 1. 数据处理与 RAG 构建

* **数据清洗**：通过 `data_process.py` 对从 PubMed 爬取的原始 JSON 进行过滤，提取有效摘要与标题。
* **文档分块**：采用 `TokenTextSplitter` 进行切分（`chunk_size=128`, `chunk_overlap=64`），确保医疗语义的连续性。
* **向量检索**：使用本地 `e5-large-unsupervised` 模型进行编码，并配置 CUDA 加速。
* **持久化存储**：采用 **ChromaDB** 存储，索引存放于 `chroma_medical_db_final/`。
### 2. 监督微调 (SFT) 数据工程
* **指令构造**：将 PubMed 数据转换为指令对（标题作为 Input，摘要作为 Output）。
* **质量过滤**：脚本自动过滤摘要长度小于 50 字符或标题过短的条目，确保训练集质量。
### 3. LoRA 微调实验
使用 **LLaMA-Factory** 框架对 Mistral-7B 进行轻量化更新：
核心参数：秩 `r=8`，`lora_alpha=16`，覆盖全量投影矩阵（`q_proj`, `v_proj` 等）。
训练指标：经历 3.0 Epochs（共 936 个 Step），Loss 从 **1.42** 稳步下降至 **1.18** 左右。
训练效率：总耗时约 55 分钟，吞吐量为 2.252 样本/秒。

### 4. vLLM 高性能部署

利用 vLLM 引擎挂载 LoRA 模块进行标准 OpenAI API 部署：

```bash
python -m vllm.entrypoints.openai.api_server \
    --model /home/janie/RAG/models/Mistral-7B-v0.1 \
    --enable-lora \
    --lora-modules my-med-lora=/home/janie/RAG/LLaMA-Factory/LLaMA-Factory-main/saves/Mistral-7B/lora/medical_sft_v1 \
    --served-model-name mistral-7b-med \
    --gpu-memory-utilization 0.8

```

## 🛠️ 快速开始

1. **环境安装**：
```bash
pip install -r requirements.txt

```

2. **构建向量库**：
运行 `rag_usecase.ipynb` 或对应 Python 脚本初始化 ChromaDB。
3. **模型推理**：
启动 vLLM 服务后，通过标准 API 调用 `mistral-7b-med` 模型。
## 📊 实验结论

通过 **RAG + SFT** 的双轨驱动，系统在保持学术严谨性的同时，显著提升了医学术语的表达精度，有效缓解了大模型的“幻觉”现象。

### 推送指南（针对当前进度）

既然您已经完成了 `git commit`，请执行以下指令完成推送：

```bash
git remote add origin https://github.com/anzaiad/RAG_medical.git
git branch -M main
git push -u origin main
