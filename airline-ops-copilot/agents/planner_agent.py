"""
Planner Agent - Generates and evaluates resolution plans
"""

from typing import Dict, List, Any, Tuple


class PlannerAgent:
    """Proposes resolution plans and selects the best option"""

    def __init__(self, policy_agent):
        """
        Initialize Planner Agent

        Args:
            policy_agent: PolicyAgent instance for querying rules
        """
        self.policy_agent = policy_agent

    def generate_plans(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate multiple resolution plans for scenario

        Args:
            scenario: Disruption scenario dictionary

        Returns:
            List of resolution plans
        """

        plans = []

        # Get policy guidance
        delay_actions = self.policy_agent.get_delay_actions(scenario['delay_minutes'])
        rebooking_rules = self.policy_agent.get_rebooking_rules(scenario)

        # Plan A: Auto-reprotect (if applicable)
        if scenario.get('num_misconnects', 0) > 0 or delay_actions['mandatory_rebooking']:
            plan_a = self._create_auto_reprotect_plan(scenario, delay_actions, rebooking_rules)
            plans.append(plan_a)

        # Plan B: Monitor and wait (if delay is minor)
        if scenario['delay_minutes'] < 120 and scenario.get('num_misconnects', 0) == 0:
            plan_b = self._create_monitor_plan(scenario, delay_actions)
            plans.append(plan_b)

        # Plan C: Manual rebooking with care provisions
        if scenario['delay_minutes'] >= 120:
            plan_c = self._create_full_care_plan(scenario, delay_actions, rebooking_rules)
            plans.append(plan_c)

        # Plan D: Hold connection (if feasible)
        if scenario.get('num_misconnects', 0) > 0 and scenario['delay_minutes'] < 30:
            plan_d = self._create_hold_connection_plan(scenario)
            plans.append(plan_d)

        return plans

    def _create_auto_reprotect_plan(self, scenario: Dict[str, Any],
                                   delay_actions: Dict[str, Any],
                                   rebooking_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Create auto-reprotection plan"""

        plan = {
            'plan_id': 'A',
            'name': 'Auto-Reprotect + Priority Handling',
            'description': 'Automatically rebook affected passengers on next available flights with priority handling',
            'actions': [],
            'timeline': '15-30 minutes',
            'cost_estimate': 'Low-Medium',
            'passenger_impact': 'Minimal (proactive resolution)',
            'risks': []
        }

        # Actions
        plan['actions'].append({
            'step': 1,
            'action': f"Auto-rebook {scenario.get('num_misconnects', 0)} misconnecting passengers",
            'owner': 'Rebooking system',
            'duration': '5 min'
        })

        plan['actions'].append({
            'step': 2,
            'action': 'Generate priority handling list for special assistance passengers',
            'owner': 'Station agent',
            'duration': '5 min'
        })

        plan['actions'].append({
            'step': 3,
            'action': 'Retag and transfer baggage to new flights',
            'owner': 'Baggage team',
            'duration': '10 min'
        })

        plan['actions'].append({
            'step': 4,
            'action': 'Send rebooking confirmation to passengers (SMS/Email)',
            'owner': 'Automated system',
            'duration': '2 min'
        })

        # Special assistance handling
        special_pax = scenario.get('special_passengers', [])
        if special_pax:
            plan['actions'].append({
                'step': 5,
                'action': f"Coordinate special assistance: {', '.join(special_pax[:3])}",
                'owner': 'Station agent + Special services',
                'duration': '10 min'
            })

        # Risks
        if scenario.get('num_misconnects', 0) > 50:
            plan['risks'].append('High volume may exceed next flight capacity')

        if any('UMNR' in p for p in special_pax):
            plan['risks'].append('UMNR requires continuous supervision - assign escort')

        return plan

    def _create_monitor_plan(self, scenario: Dict[str, Any],
                            delay_actions: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitor and wait plan"""

        plan = {
            'plan_id': 'B',
            'name': 'Monitor + Minimal Intervention',
            'description': 'Monitor delay progression, inform passengers, intervene only if delay extends',
            'actions': [],
            'timeline': '10-15 minutes',
            'cost_estimate': 'Minimal',
            'passenger_impact': 'Low (minor inconvenience)',
            'risks': []
        }

        plan['actions'].append({
            'step': 1,
            'action': 'Send delay notification to passengers',
            'owner': 'Automated system',
            'duration': '2 min'
        })

        plan['actions'].append({
            'step': 2,
            'action': 'Monitor delay progression every 15 minutes',
            'owner': 'Station agent',
            'duration': 'Ongoing'
        })

        plan['actions'].append({
            'step': 3,
            'action': 'Check downstream connection impacts',
            'owner': 'Station agent',
            'duration': '5 min'
        })

        plan['actions'].append({
            'step': 4,
            'action': 'Prepare rebooking options (standby)',
            'owner': 'Station agent',
            'duration': '5 min'
        })

        plan['risks'].append('Delay may extend - be ready to escalate to rebooking')
        plan['risks'].append('Passenger frustration if delay extends without action')

        return plan

    def _create_full_care_plan(self, scenario: Dict[str, Any],
                              delay_actions: Dict[str, Any],
                              rebooking_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Create full care plan (major delay/cancellation)"""

        plan = {
            'plan_id': 'C',
            'name': 'Full Care + Accommodation',
            'description': 'Comprehensive rebooking with meals, accommodation, and compensation',
            'actions': [],
            'timeline': '45-60 minutes',
            'cost_estimate': 'High',
            'passenger_impact': 'Moderate (significant delay mitigated)',
            'risks': []
        }

        plan['actions'].append({
            'step': 1,
            'action': 'Notify all passengers of delay/cancellation',
            'owner': 'Station agent',
            'duration': '5 min'
        })

        plan['actions'].append({
            'step': 2,
            'action': f"Rebook {scenario.get('num_passengers', 0)} passengers on alternative flights",
            'owner': 'Rebooking team',
            'duration': '20 min'
        })

        plan['actions'].append({
            'step': 3,
            'action': 'Issue meal vouchers (all passengers)',
            'owner': 'Service desk',
            'duration': '10 min'
        })

        if delay_actions.get('hotel_accommodation'):
            plan['actions'].append({
                'step': 4,
                'action': 'Arrange hotel accommodation (overnight delay)',
                'owner': 'Ground services',
                'duration': '15 min'
            })

        plan['actions'].append({
            'step': 5,
            'action': 'Process care claim documentation',
            'owner': 'Customer service',
            'duration': '10 min'
        })

        plan['actions'].append({
            'step': 6,
            'action': 'Coordinate baggage transfer and delivery',
            'owner': 'Baggage services',
            'duration': '15 min'
        })

        plan['risks'].append('High operational cost')
        plan['risks'].append('Hotel availability may be limited')
        plan['risks'].append('Complex coordination across multiple teams')

        return plan

    def _create_hold_connection_plan(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Create hold connection plan"""

        plan = {
            'plan_id': 'D',
            'name': 'Hold Connection + Gate Coordination',
            'description': 'Attempt to hold connecting flight if inbound delay is minimal',
            'actions': [],
            'timeline': '10-20 minutes',
            'cost_estimate': 'Low',
            'passenger_impact': 'Minimal (connection preserved)',
            'risks': []
        }

        plan['actions'].append({
            'step': 1,
            'action': 'Contact destination station to request connection hold',
            'owner': 'Station coordinator',
            'duration': '5 min'
        })

        plan['actions'].append({
            'step': 2,
            'action': f"Notify {scenario.get('num_misconnects', 0)} connecting passengers of situation",
            'owner': 'Station agent',
            'duration': '5 min'
        })

        plan['actions'].append({
            'step': 3,
            'action': 'Arrange priority deplaning for connecting passengers',
            'owner': 'Ground services',
            'duration': '3 min'
        })

        plan['actions'].append({
            'step': 4,
            'action': 'Coordinate fast-track through security/immigration if needed',
            'owner': 'Station coordinator',
            'duration': '5 min'
        })

        plan['risks'].append('Connection hold may delay other passengers')
        plan['risks'].append('If hold not feasible, need immediate Plan A activation')
        plan['risks'].append('Tight connection may cause passenger stress')

        return plan

    def evaluate_plan(self, plan: Dict[str, Any], scenario: Dict[str, Any]) -> Tuple[float, str]:
        """
        Score a plan based on effectiveness

        Args:
            plan: Resolution plan
            scenario: Disruption scenario

        Returns:
            Tuple of (score, reasoning)
        """

        score = 0.0
        reasoning_parts = []

        # Scoring criteria
        criteria = {
            'passenger_impact': 3.0,
            'compliance': 3.0,
            'cost': 2.0,
            'timeline': 1.5,
            'risk_management': 2.5
        }

        # 1. Passenger Impact (0-3 points)
        impact_str = plan.get('passenger_impact', '').lower()
        if 'minimal' in impact_str:
            impact_score = 3.0
            reasoning_parts.append("Minimal passenger impact (+3.0)")
        elif 'low' in impact_str:
            impact_score = 2.5
            reasoning_parts.append("Low passenger impact (+2.5)")
        elif 'moderate' in impact_str:
            impact_score = 1.5
            reasoning_parts.append("Moderate passenger impact (+1.5)")
        else:
            impact_score = 0.5
            reasoning_parts.append("High passenger impact (+0.5)")

        score += impact_score

        # 2. Compliance with policies (0-3 points)
        compliance_score = 0.0

        # Check delay response alignment
        delay_actions = self.policy_agent.get_delay_actions(scenario['delay_minutes'])

        if scenario['delay_minutes'] >= 180 and 'rebook' in plan['description'].lower():
            compliance_score += 2.0
            reasoning_parts.append("Mandatory rebooking requirement met (+2.0)")
        elif scenario['delay_minutes'] < 60 and 'monitor' in plan['description'].lower():
            compliance_score += 2.0
            reasoning_parts.append("Appropriate minimal intervention (+2.0)")

        # Check special passenger handling
        special_pax = scenario.get('special_passengers', [])
        if special_pax:
            if any('special assistance' in str(action).lower() for action in plan.get('actions', [])):
                compliance_score += 1.0
                reasoning_parts.append("Special assistance handling included (+1.0)")
            else:
                compliance_score -= 1.0
                reasoning_parts.append("Missing special assistance handling (-1.0)")

        score += compliance_score

        # 3. Cost efficiency (0-2 points)
        cost_str = plan.get('cost_estimate', '').lower()
        if 'minimal' in cost_str or 'low' in cost_str:
            cost_score = 2.0
            reasoning_parts.append("Cost-efficient solution (+2.0)")
        elif 'medium' in cost_str:
            cost_score = 1.0
            reasoning_parts.append("Moderate cost (+1.0)")
        else:
            cost_score = 0.0
            reasoning_parts.append("High cost (+0.0)")

        score += cost_score

        # 4. Timeline efficiency (0-1.5 points)
        timeline = plan.get('timeline', '')
        try:
            # Extract minutes from timeline
            import re
            minutes_match = re.search(r'(\d+)', timeline)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                if minutes <= 20:
                    timeline_score = 1.5
                    reasoning_parts.append("Fast execution (<20 min) (+1.5)")
                elif minutes <= 40:
                    timeline_score = 1.0
                    reasoning_parts.append("Moderate timeline (20-40 min) (+1.0)")
                else:
                    timeline_score = 0.5
                    reasoning_parts.append("Longer timeline (>40 min) (+0.5)")
            else:
                timeline_score = 0.5
        except:
            timeline_score = 0.5

        score += timeline_score

        # 5. Risk management (0-2.5 points)
        risks = plan.get('risks', [])
        num_risks = len(risks)

        if num_risks == 0:
            risk_score = 2.5
            reasoning_parts.append("No significant risks (+2.5)")
        elif num_risks <= 2:
            risk_score = 1.5
            reasoning_parts.append("Minor risks identified (+1.5)")
        else:
            risk_score = 0.5
            reasoning_parts.append("Multiple risks present (+0.5)")

        score += risk_score

        # Bonus/penalty adjustments
        # Bonus for handling UMNR correctly
        if any('UMNR' in p for p in special_pax):
            has_umnr_handling = any('UMNR' in str(action) or 'escort' in str(action).lower()
                                   for action in plan.get('actions', []))
            if has_umnr_handling:
                score += 1.0
                reasoning_parts.append("UMNR handling included (bonus +1.0)")
            else:
                score -= 2.0
                reasoning_parts.append("CRITICAL: Missing UMNR handling (penalty -2.0)")

        # Penalty for not escalating when required
        if scenario.get('requires_escalation') and 'escalat' not in plan['description'].lower():
            score -= 1.0
            reasoning_parts.append("Missing required escalation (penalty -1.0)")

        reasoning = " | ".join(reasoning_parts)

        # Normalize score to 0-10
        max_score = sum(criteria.values()) + 1.0  # +1 for UMNR bonus
        normalized_score = min(10.0, (score / max_score) * 10)

        return round(normalized_score, 2), reasoning

    def select_best_plan(self, plans: List[Dict[str, Any]],
                        scenario: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Tuple[Dict, float, str]]]:
        """
        Select the best plan based on scoring

        Args:
            plans: List of resolution plans
            scenario: Disruption scenario

        Returns:
            Tuple of (best_plan, all_evaluations)
        """

        evaluations = []

        for plan in plans:
            score, reasoning = self.evaluate_plan(plan, scenario)
            evaluations.append((plan, score, reasoning))

        # Sort by score (descending)
        evaluations.sort(key=lambda x: x[1], reverse=True)

        best_plan = evaluations[0][0] if evaluations else None

        return best_plan, evaluations

    def explain_decision(self, best_plan: Dict[str, Any],
                        all_evaluations: List[Tuple[Dict, float, str]],
                        scenario: Dict[str, Any]) -> str:
        """Generate explanation for plan selection"""

        explanation = []

        explanation.append("=== DECISION REASONING ===\n")

        explanation.append(f"Selected Plan: {best_plan['plan_id']} - {best_plan['name']}\n")

        # Show all plan scores
        explanation.append("Plan Comparison:")
        for plan, score, _ in all_evaluations:
            explanation.append(f"  Plan {plan['plan_id']}: {score}/10 - {plan['name']}")

        explanation.append("")

        # Explain why best plan was chosen
        _, best_score, best_reasoning = all_evaluations[0]

        explanation.append(f"Why Plan {best_plan['plan_id']} (Score: {best_score}/10):")
        explanation.append(f"  {best_reasoning}")

        explanation.append("")

        # Context from scenario
        explanation.append("Scenario Context:")
        explanation.append(f"  - Delay: {scenario['delay_minutes']} minutes ({scenario['severity']} severity)")
        explanation.append(f"  - Affected passengers: {scenario['num_passengers']}")
        if scenario.get('num_misconnects', 0) > 0:
            explanation.append(f"  - Misconnects: {scenario['num_misconnects']}")
        if scenario.get('special_passengers'):
            explanation.append(f"  - Special assistance: {', '.join(scenario['special_passengers'])}")
        explanation.append(f"  - Escalation required: {'Yes' if scenario['requires_escalation'] else 'No'}")

        return "\n".join(explanation)
