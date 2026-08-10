import html
import secrets

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "richarddzh/tiny-qwen3-30m"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.float32,
)
model.eval()
model.config.use_cache = True


def tokenize_text(text):
    if not text:
        return "<em>Enter text to inspect its tokens.</em>", []

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
        + f'</div><div class="token-count">{len(token_ids)} input tokens</div>'
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
        raise gr.Error("Please enter some text.")

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
            f"{input_length} input tokens + {max_new_tokens} new tokens exceeds "
            f"the model context limit of {context_limit}."
        )

    seed_text = seed_text.strip()
    if seed_text:
        try:
            seed = int(seed_text)
        except ValueError as exc:
            raise gr.Error("Random seed must be an integer or left blank.") from exc
        if not 0 <= seed < 2**63:
            raise gr.Error("Random seed must be between 0 and 2^63 - 1.")
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
        "# Tiny Qwen3 30M Completion\n"
        "Inspect how the tokenizer splits the source text, then generate a "
        "continuation on CPU."
    )

    prompt = gr.Textbox(
        label="Input text",
        value="Once upon a time,",
        lines=5,
    )

    with gr.Row():
        seed = gr.Textbox(
            label="Random seed (optional)",
            placeholder="Leave blank for a random seed",
        )
        max_new_tokens = gr.Slider(
            1,
            256,
            value=80,
            step=1,
            label="Max new tokens",
        )
        do_sample = gr.Checkbox(value=True, label="Sampling")

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
            label="Repetition penalty",
        )

    run = gr.Button("Tokenize and complete", variant="primary")
    actual_seed = gr.Textbox(label="Seed used", interactive=False)
    token_html = gr.HTML(label="Source-text tokenization")
    token_table = gr.Dataframe(
        headers=[
            "Index",
            "Source text",
            "Tokenizer token",
            "Token ID",
            "Start",
            "End",
        ],
        datatype=["number", "str", "str", "number", "number", "number"],
        interactive=False,
        label="Token details",
    )
    continuation = gr.Textbox(
        label="Generated continuation",
        lines=10,
        interactive=False,
    )
    full_text = gr.Textbox(
        label="Full text",
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
