from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


from .tracing import langfuse_context, observe

class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(as_type="generation", name="mock-claude-generation", capture_input=False, capture_output=False)
    def generate(self, prompt: str) -> FakeResponse:
        langfuse_context.update_current_observation(input=prompt, model=self.model)
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
            
        # Extract context and query from prompt
        # Prompt format: Feature={feature}\nDocs={docs}\nQuestion={message}
        lines = prompt.split("\n")
        docs_line = next((l for l in lines if l.startswith("Docs=")), "Docs=[]")
        docs = eval(docs_line[5:]) # Safe enough for mock data
        
        if docs and "No domain document matched" not in docs[0]:
            recommendation = random.choice(docs)
            answer = f"Dựa trên yêu cầu của bạn, tôi gợi ý bộ phim: {recommendation} Hy vọng bạn sẽ thích nó!"
        else:
            answer = "Tôi xin lỗi, tôi không tìm thấy bộ phim nào phù hợp với thể loại bạn yêu cầu. Bạn có thể thử các thể loại như hành động (action), hài hước (comedy) hoặc khoa học viễn tưởng (sci-fi) không?"

        langfuse_context.update_current_observation(
            usage={"input": input_tokens, "output": output_tokens},
            output=answer
        )
        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
