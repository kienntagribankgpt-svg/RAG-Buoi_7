import os
from openai import OpenAI

token = 'hf_OEfaTqtwKRZMZlzrny1rSdiZxjtzCHYNgX'

client = OpenAI(
    base_url='https://router.huggingface.co/v1',
    api_key=token,
)

GENERATOR_MODEL = 'Qwen/Qwen3.5-9B:deepinfra'

print('=' * 80)
print('🚀 ĐANG GỬI REQUEST TRỰC TIẾP LÊN HUGGING FACE ROUTER API...')
print(f'Token: {token[:8]}... | Model: {GENERATOR_MODEL}')
print('=' * 80)

test_prompts = [
    'Thẩm quyền quyết định phê duyệt cấp tín dụng thuộc về ai theo quy định?',
    'Quy định về niêm phong tiền mặt theo Thông tư 01/2014/TT-NHNN?',
    'Hạn mức tối đa cho vay đối với một khách hàng không có tài sản bảo đảm?'
]

for idx, p in enumerate(test_prompts, 1):
    print(f'[*] Request {idx}/{len(test_prompts)}: Gửi prompt đến {GENERATOR_MODEL}...')
    try:
        res = client.chat.completions.create(
            model=GENERATOR_MODEL,
            messages=[{'role': 'user', 'content': p}],
            max_tokens=150,
            temperature=0.1
        )
        ans = res.choices[0].message.content.strip()
        print(f'    -> [THÀNH CÔNG] Phản hồi: {ans[:80]}...\n')
    except Exception as e:
        print(f'    -> [LỖI API]: {e}\n')

print('✔ ĐÃ HOÀN TẤT GỬI CÁC REQUESTS THỰC TẾ!')