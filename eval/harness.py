import json
import anthropic

client = anthropic.Anthropic()

JUDGE_PROMPT = """Compare the expected answer and actual answer. 
Is the actual answer correct and consistent with the expected answer?

Expected: {expected}
Actual: {actual}

Score from 1-5 where 5 is perfect. Return only the number."""

def judge(expected: str, actual: str) -> int:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=5,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            expected=expected,
            actual=actual
        )}]
    )
    try:
        return int(message.content[0].text.strip())
    except:
        return 3

def run_eval(answer_fn, chunks):
    with open("eval/dataset.json") as f:
        dataset = json.load(f)

    results = []
    for item in dataset:
        result = answer_fn(item["query"], chunks)
        score = judge(item["expected"], result["answer"])
        routing_correct = result["route"] == item["route"]
        results.append({
            "query": item["query"],
            "expected_route": item["route"],
            "actual_route": result["route"],
            "routing_correct": routing_correct,
            "score": score,
            "iterations": result["iterations"],
            "faithfulness": all(
                r["score"] == "fully_supported"
                for r in (result["critique"] or [])
            )
        })
        print(f"Q: {item['query'][:50]}")
        print(f"   route: {result['route']} ({'✓' if routing_correct else '✗'})")
        print(f"   score: {score}/5")
        print(f"   iterations: {result['iterations']}")
        print()

    avg_score = sum(r["score"] for r in results) / len(results)
    routing_accuracy = sum(r["routing_correct"] for r in results) / len(results)
    print(f"avg answer score:  {avg_score:.1f}/5")
    print(f"routing accuracy:  {routing_accuracy*100:.0f}%")
    return results
