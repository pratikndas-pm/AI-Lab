"""
Orchestrator - Coordinates all agents in the workflow
"""

from typing import Dict, Any, Optional
from pathlib import Path

from agents import (
    ScenarioAgent,
    PolicyAgent,
    PlannerAgent,
    CommsAgent,
    CriticAgent
)


class AirlineOpsOrchestrator:
    """Main orchestrator for the Airline Ops Copilot system"""

    def __init__(self, playbook_dir: Optional[str] = None):
        """
        Initialize orchestrator and all agents

        Args:
            playbook_dir: Path to playbook directory (auto-detects if None)
        """

        # Initialize agents
        self.scenario_agent = ScenarioAgent()
        self.policy_agent = PolicyAgent(playbook_dir)
        self.planner_agent = PlannerAgent(self.policy_agent)
        self.comms_agent = CommsAgent(self.policy_agent)
        self.critic_agent = CriticAgent(self.policy_agent)

        self.last_scenario = None
        self.last_plan = None
        self.last_communications = None
        self.last_critique = None

    def process_disruption(self, disruption_text: str,
                          auto_critique: bool = True,
                          max_revisions: int = 2) -> Dict[str, Any]:
        """
        Main workflow: Process a disruption scenario end-to-end

        Args:
            disruption_text: Text description of disruption
            auto_critique: Whether to automatically run critic
            max_revisions: Maximum number of revision attempts

        Returns:
            Complete response package
        """

        response = {
            'scenario': None,
            'plans': None,
            'selected_plan': None,
            'decision_reasoning': None,
            'communications': None,
            'critique': None,
            'checklist': None,
            'risk_flags': None,
            'revision_count': 0
        }

        # Step 1: Parse/Generate Scenario
        print("🔍 Scenario Agent: Analyzing disruption...")
        scenario = self.scenario_agent.generate_from_text(disruption_text)
        self.last_scenario = scenario
        response['scenario'] = scenario

        print(f"   ✓ {scenario['scenario_id']} - {scenario['severity']} severity")

        # Step 2: Generate Resolution Plans
        print("\n📋 Planner Agent: Generating resolution plans...")
        plans = self.planner_agent.generate_plans(scenario)
        response['plans'] = plans

        print(f"   ✓ Generated {len(plans)} resolution plans")

        # Step 3: Select Best Plan
        print("\n⚖️  Planner Agent: Evaluating plans...")
        best_plan, all_evaluations = self.planner_agent.select_best_plan(plans, scenario)
        self.last_plan = best_plan
        response['selected_plan'] = best_plan
        response['all_plan_evaluations'] = all_evaluations

        if best_plan:
            print(f"   ✓ Selected Plan {best_plan['plan_id']}: {best_plan['name']}")

            # Generate decision explanation
            decision_reasoning = self.planner_agent.explain_decision(
                best_plan, all_evaluations, scenario
            )
            response['decision_reasoning'] = decision_reasoning

        # Step 4: Generate Communications
        print("\n📧 Comms Agent: Generating communications...")
        communications = self.comms_agent.generate_all_communications(scenario, best_plan)
        self.last_communications = communications
        response['communications'] = communications

        print(f"   ✓ Generated {len(communications)} communication templates")

        # Step 5: Generate Checklist and Risk Flags
        print("\n✅ Policy Agent: Creating operational checklist...")
        checklist = self.policy_agent.get_checklist(scenario)
        response['checklist'] = checklist

        print(f"   ✓ {len(checklist)} checklist items")

        print("\n⚠️  Policy Agent: Identifying risk flags...")
        risk_flags = self.policy_agent.extract_action_constraints(scenario)
        escalation = self.policy_agent.get_escalation_level(scenario)

        response['risk_flags'] = {
            'constraints': risk_flags,
            'escalation': escalation
        }

        print(f"   ✓ {len(risk_flags)} constraints identified")

        # Step 6: Critic Evaluation (if enabled)
        if auto_critique:
            print("\n🔎 Critic Agent: Evaluating response quality...")

            for revision in range(max_revisions + 1):
                critique = self.critic_agent.critique_full_response(
                    scenario, best_plan, communications
                )
                self.last_critique = critique
                response['critique'] = critique
                response['revision_count'] = revision

                print(f"   Score: {critique['overall_score']}/10")

                if critique['passed']:
                    print("   ✓ Quality check PASSED")
                    break
                else:
                    print(f"   ✗ Quality check FAILED ({len(critique['critical_issues'])} critical issues)")

                    if revision < max_revisions:
                        print(f"\n   🔄 Attempting revision {revision + 1}/{max_revisions}...")

                        # Simple revision: Try next-best plan if available
                        if len(all_evaluations) > revision + 1:
                            best_plan = all_evaluations[revision + 1][0]
                            response['selected_plan'] = best_plan

                            print(f"   Trying alternative Plan {best_plan['plan_id']}: {best_plan['name']}")

                            # Regenerate communications with new plan
                            communications = self.comms_agent.generate_all_communications(scenario, best_plan)
                            response['communications'] = communications
                        else:
                            print("   No alternative plans available")
                            break
                    else:
                        print("   Max revisions reached")

        print("\n✅ Workflow complete!\n")

        return response

    def generate_random_scenario(self) -> Dict[str, Any]:
        """Generate a random scenario for testing"""

        scenario = self.scenario_agent.generate_scenario()
        self.last_scenario = scenario
        return scenario

    def format_output(self, response: Dict[str, Any],
                     sections: Optional[list] = None) -> str:
        """
        Format response for display

        Args:
            response: Response dictionary from process_disruption
            sections: List of sections to include (None = all)

        Returns:
            Formatted output string
        """

        if sections is None:
            sections = ['scenario', 'decision', 'communications', 'checklist', 'risks', 'critique']

        output_parts = []

        output_parts.append("=" * 80)
        output_parts.append("AIRLINE OPS COPILOT - DISRUPTION RESOLUTION")
        output_parts.append("=" * 80)

        # Scenario
        if 'scenario' in sections and response.get('scenario'):
            scenario = response['scenario']

            output_parts.append("\n📍 SCENARIO")
            output_parts.append("-" * 80)
            output_parts.append(self.scenario_agent.describe_scenario(scenario))

        # Decision
        if 'decision' in sections and response.get('selected_plan'):
            plan = response['selected_plan']

            output_parts.append("\n\n🎯 DECISION")
            output_parts.append("-" * 80)
            output_parts.append(f"Selected: Plan {plan['plan_id']} - {plan['name']}")
            output_parts.append(f"Description: {plan['description']}")
            output_parts.append(f"Timeline: {plan['timeline']}")
            output_parts.append(f"Cost Estimate: {plan['cost_estimate']}")
            output_parts.append(f"Passenger Impact: {plan['passenger_impact']}")

            output_parts.append("\nAction Plan:")
            for action in plan.get('actions', []):
                output_parts.append(f"  {action['step']}. {action['action']}")
                output_parts.append(f"     Owner: {action['owner']} | {action['duration']}")

            if plan.get('risks'):
                output_parts.append("\n⚠️  Risks to Monitor:")
                for risk in plan['risks']:
                    output_parts.append(f"  - {risk}")

            # Decision reasoning
            if response.get('decision_reasoning'):
                output_parts.append("\n" + response['decision_reasoning'])

        # Communications
        if 'communications' in sections and response.get('communications'):
            comms = response['communications']

            output_parts.append("\n\n📧 COMMUNICATIONS")
            output_parts.append("-" * 80)

            if comms.get('passenger_sms'):
                output_parts.append("\n[PASSENGER SMS]")
                output_parts.append(comms['passenger_sms'])

            if comms.get('passenger_email'):
                output_parts.append("\n\n[PASSENGER EMAIL]")
                output_parts.append(comms['passenger_email'])

            if comms.get('agent_script'):
                output_parts.append("\n\n[AGENT SCRIPT]")
                output_parts.append(comms['agent_script'])

            if comms.get('special_assistance_note'):
                output_parts.append("\n\n[SPECIAL ASSISTANCE NOTE]")
                output_parts.append(comms['special_assistance_note'])

        # Checklist
        if 'checklist' in sections and response.get('checklist'):
            output_parts.append("\n\n✅ OPERATIONAL CHECKLIST")
            output_parts.append("-" * 80)

            for item in response['checklist']:
                priority_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(item['priority'], '⚪')

                output_parts.append(f"{priority_icon} [{item['category']}] {item['task']}")

        # Risk Flags
        if 'risks' in sections and response.get('risk_flags'):
            risks = response['risk_flags']

            output_parts.append("\n\n⚠️  RISK FLAGS & ESCALATION")
            output_parts.append("-" * 80)

            if risks.get('constraints'):
                output_parts.append("\nPolicy Constraints:")
                for constraint in risks['constraints']:
                    output_parts.append(f"  • {constraint}")

            if risks.get('escalation'):
                escalation = risks['escalation']
                output_parts.append(f"\nEscalation Level: {escalation['level']} - {escalation['level_name']}")

                if escalation.get('reasons'):
                    output_parts.append("Reasons:")
                    for reason in escalation['reasons']:
                        output_parts.append(f"  • {reason}")

                output_parts.append(f"Contact: {escalation['contact']}")
                output_parts.append(f"Response Time: {escalation['response_time']}")

        # Critique
        if 'critique' in sections and response.get('critique'):
            output_parts.append("\n\n🔎 QUALITY ASSESSMENT")
            output_parts.append("-" * 80)
            output_parts.append(self.critic_agent.generate_critique_report(response['critique']))

        output_parts.append("\n" + "=" * 80)

        return "\n".join(output_parts)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""

        return {
            'scenarios_generated': self.scenario_agent.scenarios_generated,
            'policies_loaded': len(self.policy_agent.policies),
            'last_scenario': self.last_scenario.get('scenario_id') if self.last_scenario else None,
            'last_plan': self.last_plan.get('plan_id') if self.last_plan else None,
            'last_critique_score': self.last_critique.get('overall_score') if self.last_critique else None
        }
