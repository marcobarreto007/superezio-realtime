import os
from pathlib import Path
from huggingface_hub import hf_hub_download

def download_gguf_model():
    """
    Downloads the Qwen2.5-7B-Instruct GGUF model from Hugging Face Hub.
    """
    project_root = Path(__file__).parent.parent.resolve()
    output_dir = project_root / "models"
    output_dir.mkdir(exist_ok=True)
    
    repo_id = "Qwen/Qwen2.5-7B-Instruct-GGUF"
    # Q4_K_M is a good balance of quality and performance
    filename = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    
    output_path = output_dir / filename
    
    if output_path.exists():
        print(f"✅ GGUF model already exists: {output_path}")
        return

    print(f"⬇️  Downloading GGUF model: {repo_id}/{filename}")
    print(f"   Saving to: {output_path}")
    
    try:
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(output_dir),
            local_dir_use_symlinks=False
        )
        print(f"✅ Model downloaded successfully!")
    except Exception as e:
        print(f"❌ Failed to download model: {e}")

if __name__ == "__main__":
    download_gguf_model()
