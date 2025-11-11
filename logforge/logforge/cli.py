import argparse
from .readers import read_log_file
from .analytics import summarize_log

def main():
    p = argparse.ArgumentParser(prog="logforge", description="Simple log analytics CLI")
    p.add_argument("logfile", help="Path to log file")
    p.add_argument("--top", type=int, default=3, help="Show top-N messages")
    args = p.parse_args()

    entries = read_log_file(args.logfile)
    report = summarize_log(entries, top_n=args.top)
    for k, v in report.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
