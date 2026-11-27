"""python -m diyvideo run --sheet sheet.json --provider mock|gemini [--tier batch|standard]"""
import argparse, os, sys
from . import config, ledger as ledgermod, prompts, providers, run as runmod, sheets


def make_providers(name, tier, ledger):
    if name == "mock":
        return runmod.Providers(providers.MockText(), providers.MockImage(w=768, h=1376), providers.MockVerifier(), "batch")
    from . import gemini
    return runmod.Providers(gemini.GeminiText(config.SCRIPT_MODEL),
                            gemini.GeminiImage(config.IMAGE_MODEL, ledger=ledger, tier=tier),
                            gemini.GeminiVerifier(config.VERIFY_MODEL, prompts.load(config.PROMPT_VERSIONS["verify"])), tier)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="diyvideo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--sheet", required=True, help="local sheet JSON (Google Sheets adapter comes later)")
    r.add_argument("--provider", choices=["mock", "gemini"], default="mock")
    r.add_argument("--tier", choices=["batch", "standard"], default="batch")
    r.add_argument("--state", default=".diy/state.sqlite")
    r.add_argument("--out", default="out/diy")
    r.add_argument("--work", default=".diy/work")
    a = ap.parse_args(argv)
    if a.provider == "gemini" and os.environ.get("DIY_ALLOW_SPEND") != "1":
        print("refusing paid provider: set DIY_ALLOW_SPEND=1 only after the user approved the spend", file=sys.stderr)
        return 2
    L = ledgermod.Ledger(a.state)
    n = runmod.run(sheets.LocalSheetStore(a.sheet), L, make_providers(a.provider, a.tier, L), a.out, a.work)
    print(f"processed {n} new guide(s); month-to-date {L.spent_vnd():.0f} VND")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
