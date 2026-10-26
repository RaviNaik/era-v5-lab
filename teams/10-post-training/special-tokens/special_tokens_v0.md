# Special tokens v0

Shared G10 special-token file (`teams/10-post-training/special-tokens/special_tokens_v0.md`). Due Wednesday 28 Oct, and sent to the Tokenizer team (**Team 3 / G3**) by **Saturday 31 Oct** so G3 reserves all 256 token IDs before tokenizer training starts on 1 Nov. Team 9 delivers fingerprints v1 on 28 Oct.

## Rule for ChatML `v0` markers (G10 -> G3 handoff)

- **ChatML style is used for `v0`.**
- **One rule:** every chat marker must be **one atomic special token** in the tokenizer, **never plain text** (the BPE/unigram tokenizer must never split a chat marker into subword pieces, and plain-text tags like `<think>` or `<tool_call>` are rejected).
- **256 reserved token IDs (`0..255`):** G3 reserves the full 256-ID block. Assigned IDs below are frozen; unassigned IDs in `0..255` are reserved (`<|reserved_004|>` .. `<|reserved_255|>`).

## Team workflow (Core Team · 12 members)

- Keep this **one shared file** (`teams/10-post-training/special-tokens/special_tokens_v0.md`).
- Each of the 12 G10 Core Team members has their own dataset section below (for example `StarCoder`, `Stack Exchange`, `Indic web`).
- Each member adds the markers of their own dataset in their own section by pull request to the lead's branch (`g10-week1-post-training`).
- The team lead (Sai Teja) merges the member PRs, removes duplicates in the consolidated 256-token table, and opens one PR to `theschoolofai/era-v5-lab` `main`.

---

## Consolidated 256-token block for Team 3 (G3)

TSAI reserves 256 token IDs (`0..255`). Every chat marker below is registered as **one special token** in the tokenizer, never plain text:

| Token ID | Name | Special token surface (atomic) | Role in ChatML `v0` |
| --- | --- | --- | --- |
| `000` | `endoftext` | `<\|endoftext\|>` | End of document / transcript |
| `001` | `im_start` | `<\|im_start\|>` | Start of a ChatML turn |
| `002` | `im_end` | `<\|im_end\|>` | End of a ChatML turn |
| `003` | `pad` | `<\|pad\|>` | Padding for batched training; never appears in a rendered transcript |
| `016` | `effort_1k` | `<\|effort_1k\|>` | Effort budget: 1,024 tokens (think + tool trace) |
| `017` | `effort_4k` | `<\|effort_4k\|>` | Effort budget: 4,096 tokens (think + tool trace) |
| `018` | `effort_16k` | `<\|effort_16k\|>` | Effort budget: 16,384 tokens (think + tool trace) |
| `019` | `effort_64k` | `<\|effort_64k\|>` | Effort budget: 65,536 tokens (think + tool trace) |
| `020` | `tools` | `<\|tools\|>` | Start of the tool-declaration block (tool schemas) in the system turn |
| `021` | `tools_end` | `<\|/tools\|>` | End of the tool-declaration block |
| `024` | `think` | `<\|think\|>` | Start of reasoning trace (1 special token, never plain `<think>`) |
| `025` | `think_end` | `<\|/think\|>` | End of reasoning trace (1 special token, never plain `</think>`) |
| `026` | `tool_call` | `<\|tool_call\|>` | Start of tool call JSON payload (1 special token) |
| `027` | `tool_call_end` | `<\|/tool_call\|>` | End of tool call JSON payload (1 special token) |
| `028` | `tool_result` | `<\|tool_result\|>` | Start of tool output span inside a tool turn (1 special token) |
| `029` | `tool_result_end` | `<\|/tool_result\|>` | End of tool output span inside a tool turn (1 special token) |

Machine-readable list of assigned markers for G3 (`ID Name Surface`):

```text
000 endoftext <|endoftext|>
001 im_start <|im_start|>
002 im_end <|im_end|>
003 pad <|pad|>
016 effort_1k <|effort_1k|>
017 effort_4k <|effort_4k|>
018 effort_16k <|effort_16k|>
019 effort_64k <|effort_64k|>
020 tools <|tools|>
021 tools_end <|/tools|>
024 think <|think|>
025 think_end <|/think|>
026 tool_call <|tool_call|>
027 tool_call_end <|/tool_call|>
028 tool_result <|tool_result|>
029 tool_result_end <|/tool_result|>
```

All remaining 240 IDs in `0..255` (`004..015`, `022..023`, `030..255`) are reserved by TSAI as `<|reserved_004|>` through `<|reserved_255|>`.

### Effort budgets

- `effort_1k`: 1024 tokens
- `effort_4k`: 4096 tokens
- `effort_16k`: 16384 tokens
- `effort_64k`: 65536 tokens

The budget covers the think span and the tool trace. It does not cover the visible reply.

---

## Dataset sections by G10 Core Team member (12)

### 1. Sai Teja (Lead) — StarCoder (`code-python` · `bigcode/starcoderdata`)

- **Core team:** 10. Post-training and Agentic (Lead) · **Week 2:** 9. Evaluation · **Week 3:** 12. Quantization and Serving
- **Pack:** `code-python`
- **Language:** `Code`
- **Source:** `bigcode/starcoderdata`
- **Licence decision:** `TSAI reserves` (commercial-use data only)
- **Chat & ghost markers found in dataset (`B3`):** `<|endoftext|>`, `<|im_start|>`, `<|im_end|>`, `[INST]`, `[/INST]`, `### Assistant:`, `<think>`, `</think>`
- **Dataset-specific markers in `bigcode/starcoderdata`:**
  - Repository & file headers: `<reponame>`, `<filename>`, `<gh_stars>`
  - Notebook markers: `<jupyter_start>`, `<jupyter_text>`, `<jupyter_code>`, `<jupyter_output>`, `<empty_output>`
  - Commit & issue markers: `<commit_before>`, `<commit_msg>`, `<commit_after>`, `<issue_start>`, `<issue_comment>`
  - Redaction placeholders: `<NAME>`, `<EMAIL>`, `<KEY>`, `<PASSWORD>`
- **Action:** Strip `B3` ghost chat markers from pre-training text so the model never learns to emit control markers as plain text; register every ChatML `v0` marker above as **one special token** in G3's tokenizer.

### 2. Ajay Kumar — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Ajay Kumar via PR)*
- **Dataset markers:** *(to be added by Ajay Kumar via PR; deduplicated into consolidated list on merge)*

### 3. Amit T — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Amit T via PR)*
- **Dataset markers:** *(to be added by Amit T via PR; deduplicated into consolidated list on merge)*

### 4. Anirudh Narla — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Anirudh Narla via PR)*
- **Dataset markers:** *(to be added by Anirudh Narla via PR; deduplicated into consolidated list on merge)*

### 5. Ashish Kamble — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Ashish Kamble via PR)*
- **Dataset markers:** *(to be added by Ashish Kamble via PR; deduplicated into consolidated list on merge)*

### 6. Hema Varshini Palpandian — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Hema Varshini Palpandian via PR)*
- **Dataset markers:** *(to be added by Hema Varshini Palpandian via PR; deduplicated into consolidated list on merge)*

### 7. Lokesh Arundathi — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Lokesh Arundathi via PR)*
- **Dataset markers:** *(to be added by Lokesh Arundathi via PR; deduplicated into consolidated list on merge)*

### 8. Rammohan Madhusudan — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Rammohan Madhusudan via PR)*
- **Dataset markers:** *(to be added by Rammohan Madhusudan via PR; deduplicated into consolidated list on merge)*

### 9. Ranjani Chandrasekaran — Indic web (`ind-hi-indiccorp`) *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** `ind-hi-indiccorp` (`Indic` — to be confirmed/completed by Ranjani Chandrasekaran via PR)
- **Dataset markers:** *(to be added by Ranjani Chandrasekaran via PR; note per `diagnosis/DISEASES.md` that `U+200D` ZWJ and `U+200C` ZWNJ are valid script joiners, not special tokens or diseases)*

### 10. Ravi Naik — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Ravi Naik via PR)*
- **Dataset markers:** *(to be added by Ravi Naik via PR; deduplicated into consolidated list on merge)*

### 11. Syed Abdul — Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Syed Abdul via PR)*
- **Dataset markers:** *(to be added by Syed Abdul via PR; deduplicated into consolidated list on merge)*

### 12. Vikash Ranjan — Stack Exchange / Dataset section *(placeholder for PR to `g10-week1-post-training`)*

- **Pack / Language / Source:** *(to be added by Vikash Ranjan via PR)*
- **Dataset markers:** *(to be added by Vikash Ranjan via PR; deduplicated into consolidated list on merge)*
