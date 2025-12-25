"""
Critic Agent - Validates and critiques outputs
"""

from typing import Dict, List, Any, Tuple


class CriticAgent:
    """Validates resolution outputs and identifies issues"""

    def __init__(self, policy_agent):
        """
        Initialize Critic Agent

        Args:
            policy_agent: PolicyAgent instance for policy compliance checks
        """
        self.policy_agent = policy_agent

    def critique_full_response(self, scenario: Dict[str, Any],
                               plan: Dict[str, Any],
                               communications: Dict[str, str]) -> Dict[str, Any]:
        """
        Perform comprehensive critique of entire response

        Args:
            scenario: Disruption scenario
            plan: Selected resolution plan
            communications: Generated communications

        Returns:
            Critique results with score, issues, and suggestions
        """

        critique = {
            'overall_score': 0.0,
            'passed': False,
            'critical_issues': [],
            'warnings': [],
            'suggestions': [],
            'checks_performed': {},
            'needs_revision': False
        }

        # Run all checks
        checks = [
            self._check_special_assistance(scenario, plan, communications),
            self._check_misconnect_handling(scenario, plan, communications),
            self._check_policy_compliance(scenario, plan),
            self._check_escalation(scenario, plan),
            self._check_communication_quality(scenario, communications),
            self._check_contradictions(scenario, plan),
            self._check_completeness(scenario, plan, communications)
        ]

        # Aggregate results
        total_score = 0.0
        total_weight = 0.0

        for check_name, score, weight, issues, warnings, suggestions in checks:
            critique['checks_performed'][check_name] = {
                'score': score,
                'weight': weight,
                'passed': score >= 7.0
            }

            total_score += score * weight
            total_weight += weight

            critique['critical_issues'].extend(issues)
            critique['warnings'].extend(warnings)
            critique['suggestions'].extend(suggestions)

        # Calculate overall score
        critique['overall_score'] = round(total_score / total_weight, 2) if total_weight > 0 else 0.0

        # Determine pass/fail
        critique['passed'] = (
            critique['overall_score'] >= 7.0 and
            len(critique['critical_issues']) == 0
        )

        critique['needs_revision'] = not critique['passed']

        return critique

    def _check_special_assistance(self, scenario: Dict[str, Any],
                                  plan: Dict[str, Any],
                                  communications: Dict[str, str]) -> Tuple:
        """Check special assistance passenger handling"""

        check_name = "Special Assistance Handling"
        score = 10.0
        weight = 3.0  # Critical check
        issues = []
        warnings = []
        suggestions = []

        special_pax = scenario.get('special_passengers', [])

        if not special_pax:
            return (check_name, score, weight, issues, warnings, suggestions)

        # Check for UMNR handling
        if any('UMNR' in p for p in special_pax):
            has_umnr_mention = False

            # Check in plan actions
            for action in plan.get('actions', []):
                if 'UMNR' in str(action) or 'escort' in str(action).lower():
                    has_umnr_mention = True
                    break

            # Check in communications
            agent_script = communications.get('agent_script', '')
            if 'UMNR' in agent_script or 'unaccompanied minor' in agent_script.lower():
                has_umnr_mention = True

            if not has_umnr_mention:
                issues.append("CRITICAL: UMNR passenger present but no handling procedure mentioned")
                score -= 5.0

            # Check for supervision mention
            if has_umnr_mention:
                if 'supervis' not in agent_script.lower() and 'escort' not in agent_script.lower():
                    issues.append("CRITICAL: UMNR handling missing supervision/escort requirement")
                    score -= 3.0

        # Check for wheelchair handling
        if any('wheelchair' in p.lower() for p in special_pax):
            has_wheelchair_mention = False

            agent_script = communications.get('agent_script', '')
            special_note = communications.get('special_assistance_note', '')

            if 'wheelchair' in agent_script.lower() or 'wheelchair' in special_note.lower():
                has_wheelchair_mention = True

            if not has_wheelchair_mention:
                issues.append("CRITICAL: Wheelchair passenger present but no assistance coordination mentioned")
                score -= 4.0
            else:
                if 'coordinat' not in (agent_script + special_note).lower():
                    warnings.append("Wheelchair assistance should mention coordination with special services")
                    score -= 1.0

        # Check for medical passenger
        if any('medical' in p.lower() for p in special_pax):
            agent_script = communications.get('agent_script', '')

            if 'medical' not in agent_script.lower():
                warnings.append("Medical passenger present - should be flagged in agent script")
                score -= 1.0

        # General special assistance check
        if special_pax and not communications.get('special_assistance_note'):
            suggestions.append("Consider generating dedicated special assistance coordination note")

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def _check_misconnect_handling(self, scenario: Dict[str, Any],
                                  plan: Dict[str, Any],
                                  communications: Dict[str, str]) -> Tuple:
        """Check misconnection handling"""

        check_name = "Misconnection Handling"
        score = 10.0
        weight = 2.5
        issues = []
        warnings = []
        suggestions = []

        num_misconnects = scenario.get('num_misconnects', 0)

        if num_misconnects == 0:
            return (check_name, score, weight, issues, warnings, suggestions)

        # Check for rebooking mention
        plan_desc = plan.get('description', '').lower()
        has_rebooking = 'rebook' in plan_desc or 'reprotect' in plan_desc

        if not has_rebooking:
            issues.append(f"CRITICAL: {num_misconnects} passengers misconnecting but no rebooking plan")
            score -= 6.0

        # Check for baggage handling
        agent_script = communications.get('agent_script', '')
        has_baggage = 'baggage' in agent_script.lower() or 'bag' in agent_script.lower()

        if not has_baggage:
            warnings.append("Misconnection present - should mention baggage retagging")
            score -= 2.0

        # Check passenger communication
        passenger_email = communications.get('passenger_email', '')

        if num_misconnects > 0:
            if 'rebook' not in passenger_email.lower() and 'new flight' not in passenger_email.lower():
                warnings.append("Passenger email should clearly state rebooking for misconnection")
                score -= 1.5

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def _check_policy_compliance(self, scenario: Dict[str, Any],
                                plan: Dict[str, Any]) -> Tuple:
        """Check compliance with airline policies"""

        check_name = "Policy Compliance"
        score = 10.0
        weight = 2.5
        issues = []
        warnings = []
        suggestions = []

        delay = scenario.get('delay_minutes', 0)

        # Check delay response
        delay_actions = self.policy_agent.get_delay_actions(delay)

        if delay >= 180 and not delay_actions['mandatory_rebooking']:
            issues.append("Policy violation: Delay >= 180 min requires mandatory rebooking")
            score -= 3.0

        # Check if plan aligns with delay actions
        plan_desc = plan.get('description', '').lower()

        if delay_actions['hotel_accommodation']:
            if 'hotel' not in plan_desc and 'accommodation' not in plan_desc:
                warnings.append("Long delay should include hotel accommodation consideration")
                score -= 1.5

        if delay_actions['provide_care']:
            if 'meal' not in plan_desc and 'voucher' not in plan_desc:
                has_meal_in_actions = any('meal' in str(action).lower() or 'voucher' in str(action).lower()
                                         for action in plan.get('actions', []))
                if not has_meal_in_actions:
                    warnings.append("Delay duration requires care provisions (meals/vouchers)")
                    score -= 1.0

        # Check escalation compliance
        if scenario.get('requires_escalation'):
            escalation = self.policy_agent.get_escalation_level(scenario)

            agent_script = str(plan.get('actions', []))

            if escalation['level'] > 0:
                if 'escalat' not in plan_desc and 'escalat' not in agent_script.lower():
                    warnings.append(f"Should escalate to {escalation['level_name']}")
                    score -= 1.0

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def _check_escalation(self, scenario: Dict[str, Any],
                         plan: Dict[str, Any]) -> Tuple:
        """Check escalation is appropriate"""

        check_name = "Escalation Assessment"
        score = 10.0
        weight = 2.0
        issues = []
        warnings = []
        suggestions = []

        escalation = self.policy_agent.get_escalation_level(scenario)

        if escalation['level'] == 0:
            # No escalation needed - that's fine
            return (check_name, score, weight, issues, warnings, suggestions)

        # Escalation is required
        agent_script = str(plan.get('actions', []))
        plan_text = plan.get('description', '') + agent_script

        has_escalation_mention = 'escalat' in plan_text.lower() or 'duty manager' in plan_text.lower() or 'occ' in plan_text.lower()

        if not has_escalation_mention:
            issues.append(f"Missing escalation to {escalation['level_name']}: {', '.join(escalation['reasons'])}")
            score -= 4.0

        # Check for critical escalation triggers
        special_pax = scenario.get('special_passengers', [])

        if any('UMNR' in p for p in special_pax):
            if 'duty manager' not in plan_text.lower() and 'escalat' not in plan_text.lower():
                issues.append("UMNR present - must escalate to Duty Manager")
                score -= 3.0

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def _check_communication_quality(self, scenario: Dict[str, Any],
                                    communications: Dict[str, str]) -> Tuple:
        """Check quality of communications"""

        check_name = "Communication Quality"
        score = 10.0
        weight = 1.5
        issues = []
        warnings = []
        suggestions = []

        passenger_email = communications.get('passenger_email', '')
        agent_script = communications.get('agent_script', '')

        # Check for empathy in passenger communication
        empathy_words = ['apologize', 'apologise', 'sorry', 'understand', 'inconvenience']
        has_empathy = any(word in passenger_email.lower() for word in empathy_words)

        if not has_empathy:
            warnings.append("Passenger communication should include empathetic language")
            score -= 1.5

        # Check for clear next steps
        if 'next step' not in passenger_email.lower() and 'please' not in passenger_email.lower():
            warnings.append("Passenger communication should have clear next steps")
            score -= 1.0

        # Check tone (avoid jargon)
        jargon_terms = ['pnr', 'pax', 'mct', 'irop', 'ops', 'fdp']
        jargon_in_passenger_msg = [term for term in jargon_terms if term in passenger_email.lower()]

        if jargon_in_passenger_msg:
            warnings.append(f"Avoid airline jargon in passenger messages: {', '.join(jargon_in_passenger_msg)}")
            score -= 0.5

        # Check agent script has essential info
        if not agent_script:
            issues.append("Missing agent script")
            score -= 3.0
        else:
            essential_info = ['flight', 'delay', 'action']
            missing_info = [info for info in essential_info if info.lower() not in agent_script.lower()]

            if missing_info:
                warnings.append(f"Agent script should include: {', '.join(missing_info)}")
                score -= 1.0

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def _check_contradictions(self, scenario: Dict[str, Any],
                             plan: Dict[str, Any]) -> Tuple:
        """Check for contradictions in the plan"""

        check_name = "Contradiction Check"
        score = 10.0
        weight = 2.0
        issues = []
        warnings = []
        suggestions = []

        delay = scenario.get('delay_minutes', 0)
        plan_desc = plan.get('description', '').lower()
        plan_actions = str(plan.get('actions', [])).lower()

        # Check: Hotel offered for short delay
        if delay < 180 and ('hotel' in plan_desc or 'accommodation' in plan_desc):
            warnings.append("Contradiction: Offering hotel for delay < 3 hours is unusual")
            score -= 2.0

        # Check: Monitor-only for critical delay
        if delay >= 180 and 'monitor' in plan['name'].lower() and 'rebook' not in plan_desc:
            issues.append("Contradiction: Cannot just 'monitor' a 3+ hour delay - action required")
            score -= 4.0

        # Check: Rebooking without misconnects on short delay
        if delay < 60 and scenario.get('num_misconnects', 0) == 0 and 'rebook' in plan_desc:
            warnings.append("May be over-reacting: Rebooking for <60 min delay with no misconnects")
            score -= 1.0

        # Check: Missing steps
        if scenario.get('num_misconnects', 0) > 0:
            if 'rebook' in plan_desc and 'baggage' not in plan_actions and 'bag' not in plan_actions:
                warnings.append("Missing step: Rebooking passengers but not retagging baggage")
                score -= 1.5

        # Check: Timeline vs actions
        timeline = plan.get('timeline', '')
        num_actions = len(plan.get('actions', []))

        if '15-20' in timeline and num_actions > 5:
            suggestions.append("Timeline may be optimistic for number of actions required")

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def _check_completeness(self, scenario: Dict[str, Any],
                           plan: Dict[str, Any],
                           communications: Dict[str, str]) -> Tuple:
        """Check if response is complete"""

        check_name = "Completeness"
        score = 10.0
        weight = 1.5
        issues = []
        warnings = []
        suggestions = []

        # Check required components exist
        if not plan.get('actions'):
            issues.append("Plan has no actions defined")
            score -= 5.0

        if not communications.get('passenger_email'):
            issues.append("Missing passenger email communication")
            score -= 3.0

        if not communications.get('agent_script'):
            issues.append("Missing agent script")
            score -= 3.0

        # Check action completeness
        actions = plan.get('actions', [])

        if actions:
            # Should have owner and duration
            for action in actions:
                if not action.get('owner'):
                    warnings.append("Action missing owner assignment")
                    score -= 0.5
                    break

                if not action.get('duration'):
                    suggestions.append("Actions should include time estimates")
                    break

        # Check special passenger completeness
        special_pax = scenario.get('special_passengers', [])

        if special_pax and not communications.get('special_assistance_note'):
            suggestions.append("Consider adding dedicated special assistance note for special passengers")

        score = max(0.0, score)

        return (check_name, score, weight, issues, warnings, suggestions)

    def generate_critique_report(self, critique: Dict[str, Any]) -> str:
        """Generate human-readable critique report"""

        report_parts = []

        report_parts.append("=" * 60)
        report_parts.append("CRITIC EVALUATION REPORT")
        report_parts.append("=" * 60)

        # Overall assessment
        report_parts.append("")
        report_parts.append(f"OVERALL SCORE: {critique['overall_score']}/10")
        report_parts.append(f"STATUS: {'✓ PASSED' if critique['passed'] else '✗ FAILED'}")
        report_parts.append(f"NEEDS REVISION: {'Yes' if critique['needs_revision'] else 'No'}")

        # Checks performed
        report_parts.append("")
        report_parts.append("CHECKS PERFORMED:")

        for check_name, result in critique['checks_performed'].items():
            status = "✓" if result['passed'] else "✗"
            report_parts.append(f"{status} {check_name}: {result['score']}/10 (weight: {result['weight']})")

        # Critical issues
        if critique['critical_issues']:
            report_parts.append("")
            report_parts.append("⚠️  CRITICAL ISSUES:")
            for issue in critique['critical_issues']:
                report_parts.append(f"  - {issue}")

        # Warnings
        if critique['warnings']:
            report_parts.append("")
            report_parts.append("⚠️  WARNINGS:")
            for warning in critique['warnings']:
                report_parts.append(f"  - {warning}")

        # Suggestions
        if critique['suggestions']:
            report_parts.append("")
            report_parts.append("💡 SUGGESTIONS:")
            for suggestion in critique['suggestions']:
                report_parts.append(f"  - {suggestion}")

        # Summary
        report_parts.append("")
        report_parts.append("=" * 60)

        if critique['passed']:
            report_parts.append("✓ Response meets quality standards and can be used.")
        else:
            report_parts.append("✗ Response requires revision before use.")
            report_parts.append("   Focus on addressing critical issues first.")

        report_parts.append("=" * 60)

        return "\n".join(report_parts)
