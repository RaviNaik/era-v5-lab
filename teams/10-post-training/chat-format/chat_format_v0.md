# Chat format v0

Team G10. ChatML-style template for Team 3 (G3 Tokenizer) and Team 12 (G12 Quantization and Serving) by Saturday 31 Oct.

## Core rule: every chat marker is one special token, never plain text

- ChatML style is used for `v0`: turns open with `<|im_start|>{role}\n` and close with `<|im_end|>\n`, and the transcript ends with `<|endoftext|>`.
- **Every chat marker in `v0` is one atomic special token in the tokenizer, never plain text:**
  - Turn & document markers: `<|endoftext|>` (`000`), `<|im_start|>` (`001`), `<|im_end|>` (`002`)
  - Padding marker: `<|pad|>` (`003`)
  - Effort budget markers: `<|effort_1k|>` (`016`), `<|effort_4k|>` (`017`), `<|effort_16k|>` (`018`), `<|effort_64k|>` (`019`)
  - Tool declaration markers: `<|tools|>` (`020`), `<|/tools|>` (`021`)
  - Reasoning & tool markers: `<|think|>` (`024`), `<|/think|>` (`025`), `<|tool_call|>` (`026`), `<|/tool_call|>` (`027`), `<|tool_result|>` (`028`), `<|/tool_result|>` (`029`)
- Plain-text XML look-alikes (`<think>`, `</think>`, `<tool_call>`, `</tool_call>`, `<tool_result>`, `</tool_result>`) are rejected by `render.py`.
- `<|pad|>` is for padding batches during training and never appears in a rendered transcript. `<|tools|>` and `<|/tools|>` are for wrapping the tool schemas in the system turn; `render.py` does not emit them yet, and this change only reserves them.
- All 16 assigned markers and 240 reserved slots (`0..255`) are listed in `teams/10-post-training/special-tokens/special_tokens_v0.md` for Team 3 (G3) to reserve by Saturday 31 Oct.

## Turn structure

Roles are `system`, `user`, `assistant`, and `tool`.

1. **`system` / `user` turn:**
   `<|im_start|>system\n{content}<|im_end|>\n`
   `<|im_start|>user\n{content}<|im_end|>\n`
2. **`assistant` turn:**
   Starts with `<|im_start|>assistant\n` followed immediately by one effort special token (`<|effort_1k|>`, `<|effort_4k|>`, `<|effort_16k|>`, or `<|effort_64k|>`). Every assistant turn in a transcript uses the same effort budget (`1024`, `4096`, `16384`, or `65536` tokens covering think + tool trace, excluding the final visible reply).
   After `<|effort_{budget}|>\n`, the turn body contains (in order, omitting empty optional sections):
   - Optional reasoning span wrapped in atomic special tokens: `<|think|>\n{think}\n<|/think|>\n`
   - Zero or more tool calls, each wrapped in atomic special tokens: `<|tool_call|>\n{"arguments":{...},"name":"..."}\n<|/tool_call|>\n`
   - Optional visible reply text: `{content}`
   Closed by `<|im_end|>\n`.
3. **`tool` turn:**
   `<|im_start|>tool\n<|tool_result|>\n{content}\n<|/tool_result|><|im_end|>\n` (tool output `content` is required).
4. **End of transcript:**
   `<|endoftext|>`

`render.py` renders messages to a string, `parse()` reconstructs the messages and effort budget, and `tokenize_markers()` splits a rendered transcript into atomic special-token IDs (`0..255`) and text spans to verify that no marker is ever left as plain text.

## Example

Effort `4k`.

```text
<|im_start|>system
You edit code and you report only what a tool returned.<|im_end|>
<|im_start|>user
test_add fails in calc.py. Fix add.<|im_end|>
<|im_start|>assistant
<|effort_4k|>
<|think|>
The return adds one too many.
<|/think|>
<|tool_call|>
{"arguments":{"path":"calc.py"},"name":"read_file"}
<|/tool_call|>
I am reading calc.py before editing it.<|im_end|>
<|im_start|>tool
<|tool_result|>
def add(a, b):
    return a + b + 1

<|/tool_result|><|im_end|>
<|im_start|>assistant
<|effort_4k|>
<|tool_call|>
{"arguments":{"patch":"return a + b","path":"calc.py"},"name":"apply_patch"}
<|/tool_call|>
Removed the extra increment.<|im_end|>
<|endoftext|>
```
