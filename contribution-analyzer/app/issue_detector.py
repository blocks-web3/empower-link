from typing import Optional, List
from app.issue_detector_prompt import ISSUE_CLASSIFIER_PROMPT
from pydantic import BaseModel, Field
import re
from app.llm import Llm, DEFAULT_LLM


class IssueDetector(BaseModel):
    llm: Llm = Field(default=DEFAULT_LLM)

    def evaluate(self, messages) -> List[str]:
        results = []
        for i in range(0, len(messages), 10):
            batch = messages[i : i + 10]
            results.extend(self._inner_evaluate(batch))
        return results

    def _inner_evaluate(self, messages) -> List[str]:
        input_data = self._format_messages(messages)
        prompt = ISSUE_CLASSIFIER_PROMPT.format(messages=input_data)
        result = self.llm.predict(prompt)
        # プロンプトで出力フォーマットを指示する方法もあるが、結果が安定しないケースがあるためルールベースで変換する。
        return self._format_result(result)

    def _format_messages(self, messages) -> str:
        text = ""
        for m in messages:
            id = m["id"]
            message = m["content"]
            message = message.replace("\n", "\\n")
            text += f"id: {id}, message: {message}\n"
        return text

    def _format_result(self, result_text: Optional[str]) -> List[str]:
        results = []
        if result_text is None or len(result_text) == 0:
            return results
        for row in result_text.split("\n"):
            match = re.search(r"id: (\d+)", row)
            if not match:
                continue
            results.append(match.group(1))
        return results


if __name__ == "__main__":
    testee = IssueDetector()
    sample = [
        {"id": 10, "content": "新しいプロジェクトが開始した"},
        {"id": 11, "content": "どんなプロジェクトですか？"},
        {"id": 12, "content": "6/12のイベント会場はどこですか"},
    ]
    print(testee._format_messages(sample))
    r = testee.evaluate(sample)
    print(r)
