"""Command Line Interface for Multi-Agent Equity Research Platform."""

import argparse
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from stock_analyzer.pipeline.orchestrator import ResearchOrchestrator

console = Console()


def run_cli():
    parser = argparse.ArgumentParser(
        description="Multi-Agent AI Equity Research and Validation Platform (US & Canada)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    analyze_parser = subparsers.add_parser("analyze", help="Run full multi-agent research on a ticker")
    analyze_parser.add_argument("symbol", type=str, help="Ticker symbol (e.g. AAPL, MSFT, SHOP.TO, RY.TO)")
    analyze_parser.add_argument("--horizon", type=str, default="6-12 months", help="Investment horizon")

    args = parser.parse_args()

    if not args.command or args.command != "analyze":
        parser.print_help()
        sys.exit(0)

    symbol = args.symbol.strip().upper()
    console.print(Panel.fit(
        f"[bold cyan]Multi-Agent AI Equity Research System[/bold cyan]\n"
        f"[green]Target Symbol:[/green] {symbol} | [yellow]Horizon:[/yellow] {args.horizon}",
        border_style="cyan",
    ))

    orchestrator = ResearchOrchestrator()
    console.print(f"[cyan]Executing 8-Phase Gated Pipeline for {symbol}...[/cyan]")
    result = asyncio.run(orchestrator.run(symbol, horizon=args.horizon))

    if result.get("status") == "COMPLETE":
        scores = result["scores"]
        console.print("\n[bold green][PASS] Research Pipeline Completed Successfully! (All 12 Gates Passed)[/bold green]\n")

        # Scorecard Table
        table = Table(title=f"Institutional AI Scorecard — {result['company_name']} ({result['symbol']})")
        table.add_column("Dimension", justify="left", style="cyan", no_wrap=True)
        table.add_column("Score (1–10)", justify="right", style="bold magenta")

        for k, v in scores.sub_scores.items():
            table.add_row(k.replace("_", " ").title(), f"{v:.1f}")

        table.add_section()
        table.add_row("Base AI Score", f"{scores.base_ai_score:.1f} / 10.0", style="bold green")
        table.add_row("Normalized Score", f"{scores.normalized_100_score:.1f} / 100", style="bold green")
        table.add_row("Confidence Score", f"{scores.confidence_score:.2f} / 1.00", style="bold yellow")

        console.print(table)
        console.print(f"\n[bold]Full Report:[/bold] [underline]{result['report_path']}[/underline]")
        console.print(f"[bold]In Plain English:[/bold] [underline]{result['plain_english_path']}[/underline]\n")
    else:
        console.print(f"\n[bold red]✗ Pipeline Failed Gate Check:[/bold red] {result.get('gate_failed')}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
