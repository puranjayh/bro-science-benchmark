#!/usr/bin/env python3
"""
Publish BroScienceBench to the Hugging Face Hub as a dataset.

Creates/updates a dataset repo under your account (start --private, flip public
in HF settings once verified). Run it yourself so it uses your token.

    pip install huggingface_hub
    huggingface-cli login                       # or set HF_TOKEN
    python huggingface/push_to_hub.py --repo pur4nj41y/bro-science-benchmark --private
"""
import argparse, os
from huggingface_hub import HfApi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="e.g. puranjayh/bro-science-benchmark")
    ap.add_argument("--private", action="store_true")
    args = ap.parse_args()
    api = HfApi(token=os.environ.get("HF_TOKEN"))
    api.create_repo(args.repo, repo_type="dataset", private=args.private, exist_ok=True)
    for local, remote in [
        ("huggingface/README.md", "README.md"),
        ("data/brosciencebench.jsonl", "data/brosciencebench.jsonl"),
        ("DATASHEET.md", "DATASHEET.md"),
        ("LICENSE", "LICENSE"),
    ]:
        api.upload_file(path_or_fileobj=os.path.join(ROOT, local),
                        path_in_repo=remote, repo_id=args.repo, repo_type="dataset")
        print(f"  uploaded {remote}")
    print(f"\nDone: https://huggingface.co/datasets/{args.repo}")

if __name__ == "__main__":
    main()
