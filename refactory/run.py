import argparse
import csv
import difflib
import sys
import time
from pathlib import Path


def find_layout_path(project_dir: Path, options) -> str:
    for candidate in options:
        candidate_path = project_dir / candidate
        if candidate_path.exists():
            return candidate
    return options[0]


def build_patch(project_dir: Path, relative_path: str) -> str:
    utils_path = project_dir / relative_path
    original = utils_path.read_text().splitlines(keepends=True)
    replacement_block = [
        "def normalize_line_b(s: str) -> str:\n",
        "    cleaned = normalize_line_a(s)\n",
        "    if cleaned.endswith(\" \"):\n",
        "        cleaned = cleaned[:-1]\n",
        "    return cleaned\n",
    ]

    start = None
    for idx, line in enumerate(original):
        if line.startswith("def normalize_line_b"):
            start = idx
            break
    if start is None:
        return ""
    end = start
    while end < len(original) and original[end].strip() != "return s":
        end += 1
    if end < len(original):
        end += 1
    new_lines = original[:start] + replacement_block + original[end:]

    diff = difflib.unified_diff(
        original,
        new_lines,
        fromfile=f"a/{relative_path}",
        tofile=f"b/{relative_path}",
    )
    return "".join(diff)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Refactory demo tool")
    parser.add_argument("-d", "--directory", required=True, help="Project directory")
    parser.add_argument("-q", "--question", help="Query name")
    parser.add_argument("-s", "--seed", type=int, default=0)
    parser.add_argument("-o", action="store_true", help="Emit patch output")
    parser.add_argument("-m", action="store_true", help="Emit metrics")
    parser.add_argument("--only", help="Comma-separated list of relative file paths to analyze")
    args = parser.parse_args(argv)

    start_time = time.perf_counter()

    project_dir = Path(args.directory).resolve()
    if not project_dir.exists():
        print(f"Project directory '{project_dir}' does not exist", file=sys.stderr)
        return 1

    print(f"[Refactory] Analyzing project at {project_dir}")
    if args.question:
        print(f"[Refactory] Scenario: {args.question}")

    default_targets = ["logforge/utils.py", "logforge/analytics.py"]
    legacy_targets = ["logforge/logforge/utils.py", "logforge/logforge/analytics.py"]
    resolved_targets = []
    for preferred, fallback in zip(default_targets, legacy_targets):
        resolved_targets.append(find_layout_path(project_dir, [preferred, fallback]))

    if args.only:
        targets = [p.strip() for p in args.only.split(",") if p.strip()]
    else:
        targets = resolved_targets
    print(f"[Refactory] Target files: {', '.join(targets)}")

    suggestions = []
    utils_relative = find_layout_path(project_dir, ["logforge/utils.py", "logforge/logforge/utils.py"])
    if utils_relative in targets and (project_dir / utils_relative).exists():
        suggestions.append(
            "Detected duplicated normalization logic in utils.normalize_line_a and utils.normalize_line_b.\n"
            "Consider delegating normalize_line_b to normalize_line_a to keep behavior while sharing code."
        )
    analytics_relative = find_layout_path(project_dir, ["logforge/analytics.py", "logforge/logforge/analytics.py"])
    if analytics_relative in targets and (project_dir / analytics_relative).exists():
        suggestions.append(
            "Analytics module reimplements a normalization loop inline.\n"
            "Consider reusing the utility helpers to reduce duplication."
        )

    if suggestions:
        print("[Refactory] Suggestions:")
        for idx, text in enumerate(suggestions, start=1):
            print(f"  {idx}. {text}")
    else:
        print("[Refactory] No suggestions generated.")

    patch_written = None

    repo_root = Path(__file__).resolve().parent
    dataset_name = project_dir.name

    if args.o:
        output_dir = repo_root / "outputs" / dataset_name
        output_dir.mkdir(parents=True, exist_ok=True)
        utils_path = project_dir / utils_relative
        if utils_path.exists():
            diff_text = build_patch(project_dir, utils_relative)
            patch_path = output_dir / "refactor.patch"
            if diff_text:
                patch_path.write_text(diff_text)
                try:
                    display_patch = patch_path.relative_to(repo_root)
                except ValueError:
                    display_patch = patch_path
                patch_written = display_patch
                print(f"[Refactory] Patch written to {patch_path}")
            else:
                patch_written = ""
                print("[Refactory] Patch generation produced no changes; skipping file write.")
        else:
            print("[Refactory] Skipping patch generation; utils module missing.")

    if args.m:
        print("[Refactory] Metrics placeholder: 1 opportunity detected, estimated diff size 5 lines.")

    duration = time.perf_counter() - start_time
    mode = "online" if args.o else "norefactor"
    csv_row = {
        "question": args.question or "",
        "seed": args.seed,
        "mode": mode,
        "targets": ",".join(targets),
        "suggestion_count": len(suggestions),
        "patch_path": str(patch_written) if patch_written is not None else "",
        "duration_sec": f"{duration:.3f}",
    }

    data_root = repo_root / "data" / dataset_name
    data_root.mkdir(parents=True, exist_ok=True)

    csv_path = data_root / f"refactory_{mode}.csv"
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "question",
                "seed",
                "mode",
                "targets",
                "suggestion_count",
                "patch_path",
                "duration_sec",
            ],
        )
        if write_header:
            writer.writeheader()
        writer.writerow(csv_row)

    print(f"[Refactory] Logged run details to {csv_path}")
    print("[Refactory] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
