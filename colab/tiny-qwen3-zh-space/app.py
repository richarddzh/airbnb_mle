import html
import os
import secrets

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = os.getenv("MODEL_ID", "richarddzh/tiny-qwen3-30m-zh")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.float32,
)
model.eval()
model.config.use_cache = True


def tokenize_text(text):
    if not text:
        return "<em>请输入需要分析的文本。</em>", []

    encoded = tokenizer(
        text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    token_ids = encoded["input_ids"]
    offsets = encoded["offset_mapping"]
    tokens = tokenizer.convert_ids_to_tokens(token_ids)

    spans = []
    rows = []
    for index, (token_id, token, offset) in enumerate(
        zip(token_ids, tokens, offsets)
    ):
        start, end = offset
        source_piece = text[start:end]
        color = f"hsl({index * 47 % 360} 75% 88%)"
        label = html.escape(source_piece or token)
        tooltip = html.escape(
            f"token={token!r}, id={token_id}, offset=({start}, {end})",
            quote=True,
        )
        spans.append(
            f'<span class="token" style="background:{color}" '
            f'title="{tooltip}">{label}<sub>{token_id}</sub></span>'
        )
        rows.append([index, source_piece, token, token_id, start, end])

    visualization = (
        '<div class="tokenization">'
        + "".join(spans)
        + f'</div><div class="token-count">输入共 {len(token_ids)} 个 token</div>'
    )
    return visualization, rows


def complete(
    prompt,
    seed_text,
    max_new_tokens,
    do_sample,
    temperature,
    top_p,
    top_k,
    repetition_penalty,
):
    if not prompt:
        raise gr.Error("请输入文本。")

    token_html, token_rows = tokenize_text(prompt)
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        add_special_tokens=False,
    )

    input_length = inputs["input_ids"].shape[1]
    max_new_tokens = int(max_new_tokens)
    context_limit = model.config.max_position_embeddings
    if input_length + max_new_tokens > context_limit:
        raise gr.Error(
            f"输入 {input_length} 个 token，加上 {max_new_tokens} 个新 token，"
            f"超过模型 {context_limit} 个 token 的上下文上限。"
        )

    seed_text = seed_text.strip()
    if seed_text:
        try:
            seed = int(seed_text)
        except ValueError as exc:
            raise gr.Error("随机种子必须是整数，或留空自动生成。") from exc
        if not 0 <= seed < 2**63:
            raise gr.Error("随机种子必须在 0 到 2^63 - 1 之间。")
    else:
        seed = secrets.randbelow(2**63)

    torch.manual_seed(seed)
    generation_args = {
        "max_new_tokens": max_new_tokens,
        "do_sample": bool(do_sample),
        "repetition_penalty": float(repetition_penalty),
        "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": tokenizer.pad_token_id,
    }
    if do_sample:
        generation_args.update(
            temperature=float(temperature),
            top_p=float(top_p),
            top_k=int(top_k),
        )

    with torch.inference_mode():
        output_ids = model.generate(**inputs, **generation_args)

    generated_ids = output_ids[0, input_length:]
    continuation = tokenizer.decode(generated_ids, skip_special_tokens=True)
    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return token_html, token_rows, continuation, full_text, str(seed)


CSS = """
html,
body {
    height: auto !important;
    min-height: 100% !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
}
gradio-app,
.gradio-container {
    height: auto !important;
    min-height: 100vh !important;
    overflow: visible !important;
}
.tokenization {
    line-height: 2.8;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    white-space: pre-wrap;
}
.token {
    display: inline;
    padding: 3px 5px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 5px;
}
.token sub {
    margin-left: 4px;
    color: #555;
    font-size: 10px;
}
.token-count {
    margin-top: 12px;
    color: #666;
    font-size: 13px;
}
"""

with gr.Blocks() as demo:
    gr.Markdown(
        "# Tiny Qwen3 30M 中文续写\n"
        "查看中文 tokenizer 的切分结果，并在 CPU 上运行文本续写。"
    )

    prompt = gr.Textbox(
        label="输入文本",
        value="问题：太阳是地球的什么？回答：太阳是",
        lines=5,
    )

    with gr.Row():
        seed = gr.Textbox(
            label="随机种子（可选）",
            placeholder="留空则自动生成",
        )
        max_new_tokens = gr.Slider(
            1,
            256,
            value=80,
            step=1,
            label="最大新 token 数",
        )
        do_sample = gr.Checkbox(value=True, label="采样")

    with gr.Row():
        temperature = gr.Slider(
            0.01,
            2.0,
            value=0.8,
            label="Temperature",
        )
        top_p = gr.Slider(0.01, 1.0, value=0.9, label="Top-p")
        top_k = gr.Slider(0, 200, value=50, step=1, label="Top-k")
        repetition_penalty = gr.Slider(
            0.5,
            2.0,
            value=1.1,
            label="重复惩罚",
        )

    run = gr.Button("分析并续写", variant="primary")
    actual_seed = gr.Textbox(label="本次使用的随机种子", interactive=False)
    token_html = gr.HTML(label="输入文本的 token 切分")
    token_table = gr.Dataframe(
        headers=["序号", "原文", "Tokenizer token", "Token ID", "起点", "终点"],
        datatype=["number", "str", "str", "number", "number", "number"],
        interactive=False,
        label="Token 明细",
    )
    continuation = gr.Textbox(
        label="生成的续写",
        lines=10,
        interactive=False,
    )
    full_text = gr.Textbox(
        label="完整文本",
        lines=12,
        interactive=False,
    )

    run.click(
        complete,
        inputs=[
            prompt,
            seed,
            max_new_tokens,
            do_sample,
            temperature,
            top_p,
            top_k,
            repetition_penalty,
        ],
        outputs=[
            token_html,
            token_table,
            continuation,
            full_text,
            actual_seed,
        ],
    )

demo.queue(default_concurrency_limit=1).launch(
    css=CSS,
    ssr_mode=False,
)
