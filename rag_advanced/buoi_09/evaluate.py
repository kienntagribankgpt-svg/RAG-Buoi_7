import json
from pathlib import Path
from hierarchical_rag import run_query_pipeline

BASE_DIR = Path(__file__).resolve().parent

def run_evaluation():
    q_file = BASE_DIR / "eval" / "questions.json"
    if not q_file.exists():
        print("Không tìm thấy tệp câu hỏi eval/questions.json")
        return
        
    with open(q_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"=== BẮT ĐẦU ĐÁNH GIÁ PIPELINE (Tổng số câu hỏi: {len(questions)}) ===")
    
    modes = ["single_flat", "multi_flat", "single_parent", "multi_parent"]
    for mode in modes:
        print(f"\n--- Chế độ: {mode} ---")
        for q in questions:
            res = run_query_pipeline(q["question"], mode=mode)
            accepted = len(res.get("accepted_evidence", []))
            print(f"[{q['question_id']}] Evidence chấp nhận: {accepted} | Status: {res.get('status')}")

if __name__ == "__main__":
    run_evaluation()