import os
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    tools = [
        ("PyMuPDF (fitz)", "fitz"),
        ("Pillow (PIL)", "PIL"),
        ("Llama Cloud", "llama_cloud"),
        ("Pydantic", "pydantic"),
        ("Streamlit", "streamlit"),
        ("python-dotenv", "dotenv")
    ]
    
    print("=" * 45)
    print(f"{'CÔNG CỤ':<25} | {'TRẠNG THÁI':<10}")
    print("=" * 45)
    
    all_pass = True
    for name, module in tools:
        try:
            __import__(module)
            print(f"{name:<25} | PASS")
        except ImportError:
            print(f"{name:<25} | FAIL")
            all_pass = False
            
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if api_key and api_key != 'dien_api_key_llama_cloud_cua_ban_vao_day':
        print(f"{'LLAMA_CLOUD_API_KEY':<25} | PASS")
    else:
        print(f"{'LLAMA_CLOUD_API_KEY':<25} | FAIL (Chưa cấu hình .env)")
        all_pass = False
        
    print("=" * 45)
    if not all_pass:
        print("KHẮC PHỤC: Hãy chạy `pip install pymupdf pillow llama-cloud pydantic streamlit python-dotenv` và bổ sung API Key vào file src/.env.")

if __name__ == "__main__":
    check_environment()
