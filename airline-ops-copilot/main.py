#!/usr/bin/env python3
"""
Offline Airline Ops Copilot - Main CLI Interface

A multi-agent system for airline disruption management that runs 100% offline.
"""

import sys
import argparse
from pathlib import Path

from orchestrator import AirlineOpsOrchestrator


def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        OFFLINE AIRLINE OPS COPILOT                           ║
║        Multi-Agent Disruption Resolution System              ║
║                                                               ║
║        100% Offline • No APIs • No External Datasets         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def interactive_mode(orchestrator: AirlineOpsOrchestrator):
    """Run in interactive mode"""

    print("\n🎯 Interactive Mode")
    print("=" * 70)
    print("Enter a disruption scenario, or type 'help' for examples.")
    print("Type 'random' for a random scenario, 'quit' to exit.\n")

    while True:
        try:
            user_input = input("📝 Disruption: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == 'help':
                print_examples()
                continue

            if user_input.lower() == 'random':
                print("\n🎲 Generating random scenario...\n")
                scenario = orchestrator.generate_random_scenario()
                user_input = orchestrator.scenario_agent.describe_scenario(scenario)
                print("Generated scenario:")
                print(user_input)
                print()

            # Process the disruption
            print("\n" + "=" * 70)
            response = orchestrator.process_disruption(user_input, auto_critique=True)

            # Display output
            output = orchestrator.format_output(response)
            print(output)

            # Ask if user wants to continue
            print("\n" + "=" * 70)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.\n")


def batch_mode(orchestrator: AirlineOpsOrchestrator, scenarios: list):
    """Process multiple scenarios in batch"""

    print(f"\n📦 Batch Mode - Processing {len(scenarios)} scenarios")
    print("=" * 70)

    results = []

    for i, scenario_text in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] Processing: {scenario_text[:60]}...")

        response = orchestrator.process_disruption(scenario_text, auto_critique=True)
        results.append(response)

        # Brief summary
        if response.get('critique'):
            score = response['critique']['overall_score']
            status = "✓" if response['critique']['passed'] else "✗"
            print(f"   {status} Score: {score}/10")

    print("\n" + "=" * 70)
    print(f"✅ Batch complete: {len(results)} scenarios processed")

    # Summary stats
    passed = sum(1 for r in results if r.get('critique', {}).get('passed', False))
    avg_score = sum(r.get('critique', {}).get('overall_score', 0) for r in results) / len(results)

    print(f"   Passed: {passed}/{len(results)}")
    print(f"   Average Score: {avg_score:.2f}/10")

    return results


def print_examples():
    """Print example scenarios"""

    examples = """
EXAMPLE SCENARIOS:

1. Simple delay:
   "Flight XY123 delayed 45 minutes due to ATC restrictions"

2. Misconnection:
   "Flight AB456 delayed 2 hours due to weather. 12 passengers misconnecting at DXB"

3. Complex scenario:
   "Flight EF789 delayed 3h due to technical issue. 18 passengers misconnecting at LHR.
    1 wheelchair passenger, 2 unaccompanied minors"

4. Major disruption:
   "Flight CD321 cancelled due to crew legality. 150 passengers affected. 1 pregnant
    passenger, 3 platinum frequent flyers, 1 medical passenger"

5. Minimal delay:
   "Flight GH654 delayed 20 minutes due to late inbound aircraft"

Type 'random' to generate a random scenario automatically.
"""
    print(examples)


def demo_mode(orchestrator: AirlineOpsOrchestrator):
    """Run demonstration with predefined scenarios"""

    print("\n🎬 Demo Mode - Showcasing System Capabilities")
    print("=" * 70)

    demo_scenarios = [
        "Flight XY123 delayed 3h due to ATC. 18 passengers misconnecting at DXB. 1 wheelchair passenger, 2 unaccompanied minors.",
        "Flight AB456 cancelled due to crew duty time limits. 120 passengers affected. 2 platinum frequent flyers.",
        "Flight CD789 delayed 45 minutes due to weather. No misconnects."
    ]

    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{'='*70}")
        print(f"DEMO SCENARIO {i}/{len(demo_scenarios)}")
        print(f"{'='*70}")
        print(f"\nInput: {scenario}\n")

        response = orchestrator.process_disruption(scenario, auto_critique=True)

        # Show abbreviated output
        sections = ['scenario', 'decision', 'checklist', 'risks']
        output = orchestrator.format_output(response, sections=sections)
        print(output)

        if i < len(demo_scenarios):
            input("\n[Press Enter to continue to next scenario...]")

    print("\n✅ Demo complete!")


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description='Offline Airline Ops Copilot - Multi-Agent Disruption Resolution',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'scenario',
        nargs='*',
        help='Disruption scenario text (if not provided, enters interactive mode)'
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demonstration mode with example scenarios'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch mode - process multiple scenarios from stdin'
    )

    parser.add_argument(
        '--no-critique',
        action='store_true',
        help='Disable automatic critique/quality check'
    )

    parser.add_argument(
        '--playbook',
        type=str,
        help='Path to custom playbook directory'
    )

    parser.add_argument(
        '--sections',
        nargs='+',
        choices=['scenario', 'decision', 'communications', 'checklist', 'risks', 'critique'],
        help='Output sections to display (default: all)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output (no banner, no progress messages)'
    )

    args = parser.parse_args()

    # Print banner
    if not args.quiet:
        print_banner()

    # Initialize orchestrator
    try:
        if not args.quiet:
            print("🚀 Initializing Airline Ops Copilot...")

        orchestrator = AirlineOpsOrchestrator(playbook_dir=args.playbook)

        if not args.quiet:
            stats = orchestrator.get_summary_stats()
            print(f"   ✓ {stats['policies_loaded']} policy documents loaded")
            print("   ✓ All agents initialized")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return 1

    # Determine mode
    if args.demo:
        demo_mode(orchestrator)

    elif args.batch:
        # Read scenarios from stdin
        scenarios = [line.strip() for line in sys.stdin if line.strip()]
        if scenarios:
            batch_mode(orchestrator, scenarios)
        else:
            print("❌ No scenarios provided via stdin")
            return 1

    elif args.scenario:
        # Single scenario mode
        scenario_text = ' '.join(args.scenario)

        if not args.quiet:
            print(f"\n📝 Processing scenario: {scenario_text}\n")

        response = orchestrator.process_disruption(
            scenario_text,
            auto_critique=not args.no_critique
        )

        # Display output
        output = orchestrator.format_output(response, sections=args.sections)
        print(output)

    else:
        # Interactive mode
        interactive_mode(orchestrator)

    return 0


if __name__ == '__main__':
    sys.exit(main())
