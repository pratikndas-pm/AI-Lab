"""
Comms Agent - Generates passenger and staff communications
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class CommsAgent:
    """Generates communication templates for passengers and staff"""

    def __init__(self, policy_agent):
        """
        Initialize Comms Agent

        Args:
            policy_agent: PolicyAgent instance for tone/template guidance
        """
        self.policy_agent = policy_agent

    def generate_all_communications(self, scenario: Dict[str, Any],
                                   plan: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all communications for a scenario

        Args:
            scenario: Disruption scenario
            plan: Selected resolution plan

        Returns:
            Dictionary with different communication types
        """

        comms = {}

        # Passenger-facing communications
        comms['passenger_sms'] = self.generate_passenger_sms(scenario, plan)
        comms['passenger_email'] = self.generate_passenger_email(scenario, plan)

        # Staff communications
        comms['agent_script'] = self.generate_agent_script(scenario, plan)
        comms['internal_ops_note'] = self.generate_ops_note(scenario, plan)

        # Special communications
        if scenario.get('special_passengers'):
            comms['special_assistance_note'] = self.generate_special_assistance_note(scenario, plan)

        return comms

    def generate_passenger_sms(self, scenario: Dict[str, Any],
                              plan: Dict[str, Any]) -> str:
        """Generate brief SMS for passengers"""

        flight = scenario.get('flight_number', 'XX123')
        delay = scenario.get('delay_minutes', 0)
        cause = scenario.get('cause', 'operational reasons')

        # Calculate new time (placeholder)
        new_time = "[NEW TIME]"

        sms = f"Flight {flight} update: "

        if delay < 60:
            sms += f"Delayed {delay} min due to {cause}. New departure: {new_time}. "
            sms += f"Please arrive at gate [XX] by [TIME]. "

        elif delay < 180:
            sms += f"Delayed approx {delay//60}h due to {cause}. "
            sms += f"New departure: {new_time}. "

            if scenario.get('num_misconnects', 0) > 0:
                sms += f"If connecting, we've rebooked you automatically. Check email for details. "

            sms += f"Visit service desk for assistance. "

        else:
            sms += f"Significant delay due to {cause}. "
            sms += f"We've rebooked you on flight [XX456] at {new_time}. "
            sms += f"Meal vouchers available at service desk. "
            sms += f"Ref: [PNR]. More info via email."

        return sms

    def generate_passenger_email(self, scenario: Dict[str, Any],
                                plan: Dict[str, Any]) -> str:
        """Generate detailed email for passengers"""

        flight = scenario.get('flight_number', 'XX123')
        origin = scenario.get('origin', 'XXX')
        destination = scenario.get('destination', 'YYY')
        delay = scenario.get('delay_minutes', 0)
        cause = scenario.get('cause', 'operational reasons')

        email_parts = []

        # Subject line
        subject = f"Flight {flight} - Important Update"
        email_parts.append(f"Subject: {subject}\n")
        email_parts.append("=" * 60)

        # Greeting and apology
        email_parts.append("\nDear Valued Passenger,\n")

        if delay < 120:
            email_parts.append(f"We apologize for the delay to flight {flight} from {origin} to {destination}.\n")
        else:
            email_parts.append(f"We sincerely apologize for the significant disruption to flight {flight} from {origin} to {destination}.\n")

        # Situation explanation
        email_parts.append("SITUATION:")
        email_parts.append(f"Due to {cause}, your flight is delayed by approximately {delay} minutes ({delay//60} hours {delay%60} minutes).\n")

        # What we've done (based on plan)
        email_parts.append("WHAT WE'VE ARRANGED:")

        if 'auto-reprotect' in plan['name'].lower() or 'rebook' in plan['description'].lower():
            if scenario.get('num_misconnects', 0) > 0:
                email_parts.append("✓ You've been automatically rebooked on the next available flight")
                email_parts.append("  New flight: [XX456]")
                email_parts.append("  Departure: [NEW DATE/TIME]")
                email_parts.append("  Arrival: [NEW ARRIVAL TIME]")
                email_parts.append("  Your baggage will be transferred automatically\n")
            else:
                email_parts.append("✓ Your existing booking is confirmed on the delayed flight")
                email_parts.append("  New departure: [NEW TIME]\n")

        if delay >= 180:
            email_parts.append("✓ Meal voucher available at service desk")
            email_parts.append("  Location: [SERVICE DESK LOCATION]")
            email_parts.append("  Valid at: [RESTAURANT LIST]\n")

        if delay >= 360 or 'accommodation' in plan['description'].lower():
            email_parts.append("✓ Hotel accommodation arranged (overnight delay)")
            email_parts.append("  Hotel: [HOTEL NAME]")
            email_parts.append("  Address: [ADDRESS]")
            email_parts.append("  Shuttle: Departs every 30 minutes from Terminal")
            email_parts.append("  Check-out: Please return 2 hours before new flight time\n")

        # Next steps
        email_parts.append("YOUR NEXT STEPS:")

        if delay < 120:
            email_parts.append("1. Proceed to gate [XX] by [BOARDING TIME]")
            email_parts.append("2. Check airport monitors for any further updates")
            email_parts.append("3. Contact us if you need assistance (details below)\n")
        else:
            email_parts.append("1. Visit our service desk at [LOCATION] to collect:")
            email_parts.append("   - New boarding pass")
            email_parts.append("   - Meal vouchers")
            if delay >= 360:
                email_parts.append("   - Hotel voucher and shuttle information")
            email_parts.append("2. Check email for further updates")
            email_parts.append("3. Ensure you're at the gate 45 minutes before new departure\n")

        # Reference number
        email_parts.append("BOOKING REFERENCE: [PNR NUMBER]")
        email_parts.append("Disruption Case ID: " + scenario.get('scenario_id', 'N/A'))
        email_parts.append("")

        # Contact information
        email_parts.append("NEED HELP?")
        email_parts.append("Service Desk: [LOCATION]")
        email_parts.append("Phone: [PHONE NUMBER]")
        email_parts.append("Email: [EMAIL ADDRESS]")
        email_parts.append("Live Chat: [WEBSITE]\n")

        # Closing
        email_parts.append("We understand this disrupts your plans, and we're committed to getting you to your destination as smoothly as possible.")
        email_parts.append("\nThank you for your patience and understanding.\n")
        email_parts.append("Sincerely,")
        email_parts.append("[AIRLINE NAME] Operations Team")

        return "\n".join(email_parts)

    def generate_agent_script(self, scenario: Dict[str, Any],
                             plan: Dict[str, Any]) -> str:
        """Generate script for airport agents"""

        script_parts = []

        script_parts.append("=== AGENT SCRIPT ===")
        script_parts.append("")

        # Situation summary
        script_parts.append("SITUATION:")
        script_parts.append(f"Flight: {scenario.get('flight_number', 'XX123')}")
        script_parts.append(f"Route: {scenario.get('origin', 'XXX')} → {scenario.get('destination', 'YYY')}")
        script_parts.append(f"Delay: {scenario.get('delay_minutes', 0)} minutes")
        script_parts.append(f"Cause: {scenario.get('cause', 'Unknown')}")
        script_parts.append(f"Severity: {scenario.get('severity', 'UNKNOWN')}")
        script_parts.append(f"Affected passengers: {scenario.get('num_passengers', 0)}")

        if scenario.get('num_misconnects', 0) > 0:
            script_parts.append(f"Misconnecting passengers: {scenario.get('num_misconnects', 0)}")

        script_parts.append("")

        # Special assistance
        if scenario.get('special_passengers'):
            script_parts.append("⚠️  SPECIAL ASSISTANCE:")
            for pax in scenario.get('special_passengers', []):
                script_parts.append(f"   - {pax}")
                handling = self.policy_agent.get_customer_handling(pax)
                script_parts.append(f"     Priority: {handling['priority_level']}")
                if handling['special_actions']:
                    script_parts.append(f"     Action: {handling['special_actions'][0]}")
            script_parts.append("")

        # Selected plan
        script_parts.append("SELECTED PLAN:")
        script_parts.append(f"Plan {plan['plan_id']}: {plan['name']}")
        script_parts.append(f"Description: {plan['description']}")
        script_parts.append(f"Timeline: {plan['timeline']}")
        script_parts.append("")

        # Action checklist
        script_parts.append("IMMEDIATE ACTIONS:")
        for action in plan.get('actions', []):
            script_parts.append(f"{action['step']}. {action['action']}")
            script_parts.append(f"   Owner: {action['owner']} | Duration: {action['duration']}")

        script_parts.append("")

        # Passenger communication points
        script_parts.append("WHAT TO TELL PASSENGERS:")
        script_parts.append("✓ Acknowledge the inconvenience")
        script_parts.append(f"✓ Explain cause: {scenario.get('cause', 'operational issue')}")
        script_parts.append("✓ Share what we've done (rebooking, arrangements)")
        script_parts.append("✓ Give clear next steps (gate, service desk)")
        script_parts.append("✓ Provide contact info for further assistance")
        script_parts.append("")

        # Escalation info
        escalation = self.policy_agent.get_escalation_level(scenario)
        if escalation['level'] > 0:
            script_parts.append("⚠️  ESCALATION REQUIRED:")
            script_parts.append(f"Level: {escalation['level']} - {escalation['level_name']}")
            script_parts.append(f"Reason: {', '.join(escalation['reasons'])}")
            script_parts.append(f"Contact: {escalation['contact']}")
            script_parts.append(f"Response time: {escalation['response_time']}")
            script_parts.append("")

        # Risks to watch
        if plan.get('risks'):
            script_parts.append("⚠️  RISKS TO MONITOR:")
            for risk in plan['risks']:
                script_parts.append(f"   - {risk}")
            script_parts.append("")

        # Contact info
        script_parts.append("NEED SUPPORT:")
        script_parts.append("Duty Manager: [NAME] ext [XXXX]")
        if escalation['level'] >= 2:
            script_parts.append("OCC Hotline: [PHONE]")
        script_parts.append("")

        script_parts.append("Case ID: " + scenario.get('scenario_id', 'N/A'))

        return "\n".join(script_parts)

    def generate_ops_note(self, scenario: Dict[str, Any],
                         plan: Dict[str, Any]) -> str:
        """Generate internal operations note"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        note_parts = []

        note_parts.append("=== INTERNAL OPS NOTE ===")
        note_parts.append(f"Timestamp: {timestamp}")
        note_parts.append(f"Case ID: {scenario.get('scenario_id', 'N/A')}")
        note_parts.append("")

        note_parts.append("INCIDENT:")
        note_parts.append(f"Flight {scenario.get('flight_number')} - {scenario.get('origin')} to {scenario.get('destination')}")
        note_parts.append(f"Delay: {scenario.get('delay_minutes')} min | Cause: {scenario.get('cause')}")
        note_parts.append(f"Severity: {scenario.get('severity')} | PAX: {scenario.get('num_passengers')}")
        note_parts.append("")

        note_parts.append("RESOLUTION:")
        note_parts.append(f"Plan {plan['plan_id']}: {plan['name']}")
        note_parts.append(f"Cost estimate: {plan.get('cost_estimate', 'Unknown')}")
        note_parts.append(f"Timeline: {plan.get('timeline', 'Unknown')}")
        note_parts.append("")

        note_parts.append("ACTIONS TAKEN:")
        for action in plan.get('actions', []):
            note_parts.append(f"- {action['action']} ({action['owner']})")

        note_parts.append("")

        note_parts.append("NOTIFICATIONS SENT:")
        note_parts.append(f"- Passengers: SMS + Email ({scenario.get('num_passengers', 0)} pax)")

        escalation = self.policy_agent.get_escalation_level(scenario)
        if escalation['level'] > 0:
            note_parts.append(f"- Escalated to: {escalation['level_name']}")

        note_parts.append("")

        note_parts.append("OUTSTANDING ITEMS:")
        if plan.get('risks'):
            note_parts.append("- Monitor: " + "; ".join(plan['risks'][:2]))

        note_parts.append("- Follow up on passenger satisfaction")
        note_parts.append("- Close case when flight departs")

        note_parts.append("")
        note_parts.append("AGENT: [AGENT ID]")

        return "\n".join(note_parts)

    def generate_special_assistance_note(self, scenario: Dict[str, Any],
                                        plan: Dict[str, Any]) -> str:
        """Generate note for special assistance team"""

        note_parts = []

        note_parts.append("=== SPECIAL ASSISTANCE COORDINATION ===")
        note_parts.append(f"Flight: {scenario.get('flight_number', 'XX123')}")
        note_parts.append(f"Case ID: {scenario.get('scenario_id', 'N/A')}")
        note_parts.append("")

        note_parts.append("SPECIAL ASSISTANCE PASSENGERS:")

        special_pax = scenario.get('special_passengers', [])

        for pax_type in special_pax:
            handling = self.policy_agent.get_customer_handling(pax_type)

            note_parts.append(f"\n{pax_type.upper()}:")
            note_parts.append(f"Priority Level: {handling['priority_level']}")

            note_parts.append("Required Actions:")
            for action in handling['special_actions']:
                note_parts.append(f"  ✓ {action}")

            if handling['restrictions']:
                note_parts.append("Restrictions:")
                for restriction in handling['restrictions']:
                    note_parts.append(f"  ⚠️  {restriction}")

            note_parts.append(f"Communication: {handling['communication']}")

        note_parts.append("\n" + "=" * 50)
        note_parts.append("COORDINATION REQUIRED:")

        if any('UMNR' in p for p in special_pax):
            note_parts.append("- UMNR: Assign dedicated escort immediately")
            note_parts.append("- Contact parent/guardian: [CONTACT INFO]")

        if any('Wheelchair' in p for p in special_pax):
            note_parts.append("- Wheelchair: Coordinate pickup at arrival gate")
            note_parts.append("- If rebooking: Ensure wheelchair on new flight")

        if any('Medical' in p for p in special_pax):
            note_parts.append("- Medical: Consult with medical team on urgency")

        note_parts.append("\nEscalate any issues to Duty Manager immediately.")

        return "\n".join(note_parts)

    def format_for_channel(self, message: str, channel: str) -> str:
        """
        Format message for specific communication channel

        Args:
            message: Original message
            channel: 'sms', 'email', 'app', 'gate_announcement'

        Returns:
            Formatted message
        """

        if channel == 'sms':
            # SMS: Keep under 160 characters ideally, 300 max
            if len(message) > 300:
                # Truncate and add link
                message = message[:280] + "... Full details via email."

        elif channel == 'gate_announcement':
            # Gate announcement: Clear, slow-paced
            message = message.replace("approx", "approximately")
            message = message.replace("min", "minutes")
            message = "Attention passengers for flight " + message

        elif channel == 'app':
            # App notification: Brief headline + expandable details
            lines = message.split('\n')
            headline = lines[0] if lines else message[:100]
            message = f"📢 {headline}\n\nTap for full details"

        return message
