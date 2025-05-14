import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm

# MODEL_NAME = "Salesforce/codet5-base"
MODEL_NAME = "../../codet5-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_summary(code: str, max_input_length=512, max_output_length=32) -> str:
    input_text = f"summarize: {code.strip()}"
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=max_input_length,
        truncation=True,
        padding=True
    ).to(device)

    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=4,
        max_length=max_output_length,
        early_stopping=True
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return f"// {summary}"

def annotate_chunks(input_json: str, output_json: str):
    with open(input_json, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    annotated = []
    for chunk in tqdm(chunks, desc="📝 AST 기반 요약 생성 중"):
        code = f"""<template>
{chunk.get('template', '')}

<script lang="ts">
// 클래스명: {chunk.get('className', '')}
// 속성: {', '.join(chunk.get('properties', []))}
# 메서드: {', '.join(chunk.get('methods', []))}
# emits: {', '.join(chunk.get('emits', []))}

{chunk.get('script', '')}
"""
        summary = generate_summary(code)
        annotated_code = summary + "\n" + code

        annotated.append({
            "filePath": chunk["filePath"],
            "name": chunk.get("className", "unknown"),
            "code": annotated_code
        })

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(annotated, f, indent=2, ensure_ascii=False)

    print(f"✅ AST 주석 + 전체 코드 저장 완료 → {output_json}")

annotate_chunks("vue_chunks_ast.json", "../data/vue_chunks_annotated.json")
