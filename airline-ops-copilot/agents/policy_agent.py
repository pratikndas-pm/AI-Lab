"""
Policy Agent - Reads and interprets airline playbook policies
"""

import os
from pathlib import Path
from typing import Dict, List, Any


class PolicyAgent:
    """Loads and queries airline operational policies from local playbook"""

    def __init__(self, playbook_dir: str = None):
        """
        Initialize Policy Agent

        Args:
            playbook_dir: Path to playbook directory (auto-detects if None)
        """
        if playbook_dir is None:
            # Auto-detect playbook directory
            current_dir = Path(__file__).parent.parent
            playbook_dir = current_dir / 'playbook'

        self.playbook_dir = Path(playbook_dir)
        self.policies = {}
        self.load_playbook()

    def load_playbook(self):
        """Load all policy documents from playbook directory"""

        if not self.playbook_dir.exists():
            raise FileNotFoundError(f"Playbook directory not found: {self.playbook_dir}")

        policy_files = {
            'irrops': 'irrops_basics.md',
            'rebooking': 'rebooking_rules.md',
            'crew': 'crew_legality.md',
            'baggage': 'baggage_disruption.md',
            'escalation': 'escalation_matrix.md',
            'customer_tiers': 'customer_tiers.md',
            'comms': 'comms_tone.md'
        }

        for key, filename in policy_files.items():
            filepath = self.playbook_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.policies[key] = f.read()
            else:
                print(f"Warning: Policy file not found: {filename}")

    def get_policy(self, policy_name: str) -> str:
        """Get full policy document"""
        return self.policies.get(policy_name, "")

    def get_delay_actions(self, delay_minutes: int) -> Dict[str, Any]:
        """Get allowed actions based on delay duration"""

        actions = {
            'monitor_only': False,
            'proactive_communication': False,
            'offer_rebooking': False,
            'mandatory_rebooking': False,
            'provide_care': False,
            'hotel_accommodation': False,
            'response_level': 'NONE'
        }

        if delay_minutes < 30:
            actions['monitor_only'] = True
            actions['response_level'] = 'MINOR'

        elif delay_minutes < 120:
            actions['proactive_communication'] = True
            actions['offer_rebooking'] = True
            actions['response_level'] = 'MODERATE'

        elif delay_minutes < 360:
            actions['proactive_communication'] = True
            actions['mandatory_rebooking'] = True
            actions['provide_care'] = True
            actions['response_level'] = 'MAJOR'

        else:  # 360+ minutes or overnight
            actions['proactive_communication'] = True
            actions['mandatory_rebooking'] = True
            actions['provide_care'] = True
            actions['hotel_accommodation'] = True
            actions['response_level'] = 'CRITICAL'

        return actions

    def get_rebooking_rules(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Get rebooking rules for scenario"""

        rules = {
            'auto_rebook': False,
            'protect_connections': False,
            'keep_groups_together': False,
            'priority_order': [],
            'same_day_required': False
        }

        # Auto-rebook for misconnections
        if scenario.get('num_misconnects', 0) > 0:
            rules['auto_rebook'] = True
            rules['protect_connections'] = True

        # Delay-based rebooking
        if scenario.get('delay_minutes', 0) >= 180:
            rules['auto_rebook'] = True
            rules['same_day_required'] = True

        # Special passenger priorities
        special_pax = scenario.get('special_passengers', [])
        priority = []

        if any('UMNR' in p for p in special_pax):
            priority.append('UMNR - Must supervise at all times')
        if any('Wheelchair' in p for p in special_pax):
            priority.append('Wheelchair - Coordinate assistance')
        if any('Medical' in p for p in special_pax):
            priority.append('Medical - Assess urgency')
        if any('Platinum' in p for p in special_pax):
            priority.append('Platinum - Priority rebooking')
        if any('infant' in p.lower() for p in special_pax):
            priority.append('Family with infant - Keep together')

        rules['priority_order'] = priority

        return rules

    def get_escalation_level(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Determine required escalation level"""

        escalation = {
            'level': 0,
            'level_name': 'Frontline Agent',
            'reasons': [],
            'contact': 'Handle directly',
            'response_time': 'Immediate'
        }

        delay = scenario.get('delay_minutes', 0)
        special_pax = scenario.get('special_passengers', [])
        num_affected = scenario.get('num_passengers', 0)

        # Level 1: Duty Manager
        level_1_triggers = []

        if 30 <= delay <= 120 and num_affected > 50:
            level_1_triggers.append('Delay 30-120 min affecting >50 pax')

        if any('UMNR' in p or 'Wheelchair' in p or 'Medical' in p for p in special_pax):
            level_1_triggers.append('Special assistance passengers present')

        if level_1_triggers:
            escalation['level'] = 1
            escalation['level_name'] = 'Duty Manager'
            escalation['reasons'] = level_1_triggers
            escalation['contact'] = 'Radio/Phone Duty Manager'
            escalation['response_time'] = '5-10 minutes'

        # Level 2: OCC (Operations Control Center)
        level_2_triggers = []

        if delay > 120:
            level_2_triggers.append(f'Delay > 120 minutes ({delay} min)')

        if scenario.get('num_misconnects', 0) > 20:
            level_2_triggers.append(f"High misconnect count ({scenario['num_misconnects']})")

        if level_2_triggers:
            escalation['level'] = 2
            escalation['level_name'] = 'OCC (Operations Control Center)'
            escalation['reasons'] = level_2_triggers
            escalation['contact'] = 'Notify OCC immediately'
            escalation['response_time'] = '10-20 minutes'

        return escalation

    def get_customer_handling(self, passenger_type: str) -> Dict[str, Any]:
        """Get handling instructions for passenger type"""

        handling = {
            'priority_level': 'Standard',
            'special_actions': [],
            'communication': 'Email + gate announcements',
            'restrictions': []
        }

        pax_lower = passenger_type.lower()

        if 'umnr' in pax_lower or 'unaccompanied minor' in pax_lower:
            handling['priority_level'] = 'CRITICAL'
            handling['special_actions'] = [
                'Must be supervised at all times',
                'Cannot be left alone in airport',
                'Contact parent/guardian immediately',
                'Assign airline staff escort if connection missed',
                'NEVER put on flight without confirmed supervision'
            ]
            handling['communication'] = 'Direct contact + parent/guardian notification'
            handling['restrictions'] = ['Cannot leave unattended', 'Requires escort']

        elif 'wheelchair' in pax_lower:
            handling['priority_level'] = 'HIGH'
            handling['special_actions'] = [
                'Ensure wheelchair available at destination',
                'Coordinate with special services team',
                'Priority boarding and deplaning',
                'Cannot leave without mobility aid'
            ]
            handling['communication'] = 'Personal contact + confirm assistance'

        elif 'medical' in pax_lower:
            handling['priority_level'] = 'HIGH'
            handling['special_actions'] = [
                'Assess urgency of travel',
                'Priority rebooking if time-sensitive',
                'Ensure medical equipment/medication accessible'
            ]
            handling['communication'] = 'Personal contact + medical team consult'

        elif 'platinum' in pax_lower:
            handling['priority_level'] = 'HIGH'
            handling['special_actions'] = [
                'Priority rebooking (first in queue)',
                'Complimentary lounge access',
                'Proactive updates',
                'Waive change fees automatically'
            ]
            handling['communication'] = 'Personal call or SMS'

        elif 'gold' in pax_lower:
            handling['priority_level'] = 'MEDIUM'
            handling['special_actions'] = [
                'Priority rebooking (after Platinum)',
                'Lounge voucher if delay > 3h',
                'Waive change fees'
            ]
            handling['communication'] = 'SMS + email'

        return handling

    def get_communication_template(self, situation: str, scenario: Dict[str, Any]) -> Dict[str, str]:
        """Get communication templates for situation"""

        templates = {}

        if situation == 'delay':
            templates['passenger'] = f"""We apologize for the delay to flight {scenario.get('flight_number', 'XX123')}.

Due to {scenario.get('cause', 'operational reasons')}, your flight will now depart at [NEW TIME], approximately {scenario.get('delay_minutes', 0)} minutes later than scheduled.

We've kept your existing booking. Please arrive at gate [XX] by [BOARDING TIME].

If you need assistance, please visit our service desk or call [NUMBER].

Thank you for your patience."""

            templates['agent_script'] = f"""SITUATION: Flight {scenario.get('flight_number', 'XX123')} delayed {scenario.get('delay_minutes', 0)} min

CAUSE: {scenario.get('cause', 'Unknown')}

ACTIONS:
- Monitor departure updates
- Inform passengers via SMS/email
- Check connection impacts
- Prepare rebooking if delay extends

CONTACT: [Duty Manager if escalated]"""

        elif situation == 'misconnection':
            templates['passenger'] = f"""We apologize - due to the delay, you'll miss your connection.

We've automatically rebooked you on flight [XX456] departing at [TIME].

Your baggage will be transferred to the new flight.

Please proceed to gate [XX]. Our team will assist you.

Ref: [PNR/BOOKING NUMBER]"""

            templates['agent_script'] = f"""MISCONNECTION HANDLING

Affected passengers: {scenario.get('num_misconnects', 0)}
Special assistance: {', '.join(scenario.get('special_passengers', ['None']))}

ACTIONS:
- Auto-rebook on next available flights
- Retag baggage
- Issue new boarding passes
- Coordinate with destination station

PRIORITY: Handle special assistance passengers first"""

        return templates

    def extract_action_constraints(self, scenario: Dict[str, Any]) -> List[str]:
        """Extract policy constraints for scenario"""

        constraints = []

        # Delay-based constraints
        delay = scenario.get('delay_minutes', 0)
        if delay < 60:
            constraints.append("No rebooking required for delay < 60 min")
        elif delay >= 180:
            constraints.append("Mandatory rebooking + care provisions for delay >= 180 min")

        # Special passenger constraints
        special_pax = scenario.get('special_passengers', [])

        if any('UMNR' in p for p in special_pax):
            constraints.append("UMNR: Must maintain supervision at all times - NEVER leave unattended")
            constraints.append("UMNR: Escalate to Duty Manager immediately")

        if any('Wheelchair' in p for p in special_pax):
            constraints.append("Wheelchair: Coordinate assistance at origin and destination")
            constraints.append("Wheelchair: Cannot leave passenger without mobility aid")

        if any('Medical' in p for p in special_pax):
            constraints.append("Medical: Assess urgency and consult medical team if needed")

        # Misconnection constraints
        if scenario.get('num_misconnects', 0) > 0:
            constraints.append("Protect connections: Auto-rebook misconnecting passengers")
            constraints.append("Update baggage tags for new routing")

        # Escalation constraints
        if scenario.get('severity') in ['HIGH', 'CRITICAL']:
            constraints.append("Escalation required: Notify Duty Manager or OCC")

        return constraints

    def get_checklist(self, scenario: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate operational checklist"""

        checklist = []

        # Initial assessment
        checklist.append({
            'category': 'Assessment',
            'task': 'Identify root cause and estimate delay duration',
            'priority': 'CRITICAL'
        })

        checklist.append({
            'category': 'Assessment',
            'task': 'Count affected passengers and identify special assistance needs',
            'priority': 'HIGH'
        })

        # Communication
        if scenario.get('delay_minutes', 0) >= 30:
            checklist.append({
                'category': 'Communication',
                'task': 'Send proactive passenger notifications (SMS/Email)',
                'priority': 'HIGH'
            })

        # Rebooking
        if scenario.get('num_misconnects', 0) > 0:
            checklist.append({
                'category': 'Rebooking',
                'task': f"Auto-rebook {scenario.get('num_misconnects')} misconnecting passengers",
                'priority': 'CRITICAL'
            })

        # Special assistance
        special_pax = scenario.get('special_passengers', [])
        if any('UMNR' in p for p in special_pax):
            checklist.append({
                'category': 'Special Assistance',
                'task': 'Assign UMNR escort and contact parent/guardian',
                'priority': 'CRITICAL'
            })

        if any('Wheelchair' in p for p in special_pax):
            checklist.append({
                'category': 'Special Assistance',
                'task': 'Coordinate wheelchair assistance at all touchpoints',
                'priority': 'HIGH'
            })

        # Baggage
        if scenario.get('num_misconnects', 0) > 0:
            checklist.append({
                'category': 'Baggage',
                'task': 'Retag baggage with new flight routing',
                'priority': 'HIGH'
            })

        # Escalation
        if scenario.get('requires_escalation'):
            checklist.append({
                'category': 'Escalation',
                'task': 'Notify Duty Manager/OCC of situation',
                'priority': 'CRITICAL'
            })

        return checklist
