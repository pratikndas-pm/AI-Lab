"""
Scenario Agent - Generates realistic airline disruption scenarios
"""

import random
from typing import Dict, List, Any


class ScenarioAgent:
    """Generates synthetic IROP scenarios for testing and evaluation"""

    DELAY_CAUSES = [
        "ATC restrictions",
        "Weather (thunderstorms)",
        "Weather (fog)",
        "Technical issue",
        "Crew delay",
        "Aircraft swap",
        "Late inbound aircraft",
        "Ground handling delay",
        "Fueling delay",
        "Catering delay"
    ]

    PASSENGER_TYPES = [
        "Standard",
        "Platinum frequent flyer",
        "Gold frequent flyer",
        "Wheelchair passenger",
        "UMNR (Unaccompanied minor)",
        "Medical passenger",
        "Pregnant passenger",
        "Family with infant"
    ]

    def __init__(self):
        self.scenarios_generated = 0

    def generate_scenario(self,
                         delay_minutes: int = None,
                         cause: str = None,
                         num_passengers: int = None,
                         special_passengers: List[str] = None,
                         has_misconnects: bool = None) -> Dict[str, Any]:
        """
        Generate a disruption scenario

        Args:
            delay_minutes: Delay duration (random if None)
            cause: Delay cause (random if None)
            num_passengers: Number of passengers (random if None)
            special_passengers: List of special passenger types (random if None)
            has_misconnects: Whether there are misconnecting passengers (random if None)

        Returns:
            Dictionary containing scenario details
        """

        # Generate random values if not provided
        if delay_minutes is None:
            delay_minutes = random.choice([30, 60, 90, 120, 180, 240, 300])

        if cause is None:
            cause = random.choice(self.DELAY_CAUSES)

        if num_passengers is None:
            num_passengers = random.randint(50, 250)

        if has_misconnects is None:
            has_misconnects = delay_minutes >= 60 and random.random() > 0.4

        num_misconnects = 0
        if has_misconnects:
            num_misconnects = random.randint(5, min(50, num_passengers // 2))

        # Generate special passengers
        if special_passengers is None:
            special_passengers = []
            num_special = random.randint(0, 3)
            for _ in range(num_special):
                special_passengers.append(random.choice(self.PASSENGER_TYPES))

        # Generate flight details
        flight_number = f"{random.choice(['XY', 'AB', 'CD', 'EF'])}{random.randint(100, 999)}"
        origin = random.choice(['JFK', 'DXB', 'LHR', 'SIN', 'SYD'])
        destination = random.choice(['LAX', 'AUH', 'CDG', 'HKG', 'BKK'])

        # Determine severity
        severity = self._calculate_severity(delay_minutes, special_passengers, num_misconnects)

        self.scenarios_generated += 1

        scenario = {
            'scenario_id': f"IROP-{self.scenarios_generated:04d}",
            'flight_number': flight_number,
            'origin': origin,
            'destination': destination,
            'delay_minutes': delay_minutes,
            'cause': cause,
            'num_passengers': num_passengers,
            'num_misconnects': num_misconnects,
            'special_passengers': special_passengers,
            'severity': severity,
            'requires_escalation': self._check_escalation(severity, special_passengers, delay_minutes)
        }

        return scenario

    def generate_from_text(self, text: str) -> Dict[str, Any]:
        """
        Parse a text description and generate scenario

        Example: "Flight XY123 delayed 3h due to ATC. 18 passengers misconnecting at DXB.
                  1 wheelchair passenger, 2 unaccompanied minors."
        """

        scenario = {
            'scenario_id': f"IROP-{self.scenarios_generated + 1:04d}",
            'flight_number': self._extract_flight_number(text),
            'origin': self._extract_airport(text, position='from'),
            'destination': self._extract_airport(text, position='to'),
            'delay_minutes': self._extract_delay(text),
            'cause': self._extract_cause(text),
            'num_passengers': self._extract_passenger_count(text),
            'num_misconnects': self._extract_misconnects(text),
            'special_passengers': self._extract_special_passengers(text),
            'severity': 'unknown',
            'requires_escalation': False,
            'raw_input': text
        }

        # Calculate severity after extraction
        scenario['severity'] = self._calculate_severity(
            scenario['delay_minutes'],
            scenario['special_passengers'],
            scenario['num_misconnects']
        )

        scenario['requires_escalation'] = self._check_escalation(
            scenario['severity'],
            scenario['special_passengers'],
            scenario['delay_minutes']
        )

        self.scenarios_generated += 1

        return scenario

    def _calculate_severity(self, delay_minutes: int, special_passengers: List[str],
                           num_misconnects: int) -> str:
        """Calculate scenario severity"""

        score = 0

        # Delay scoring
        if delay_minutes < 60:
            score += 1
        elif delay_minutes < 120:
            score += 2
        elif delay_minutes < 180:
            score += 3
        else:
            score += 4

        # Special passengers
        critical_pax = ['UMNR', 'Wheelchair', 'Medical']
        for pax in special_passengers:
            if any(crit in pax for crit in critical_pax):
                score += 2
            else:
                score += 1

        # Misconnects
        if num_misconnects > 20:
            score += 3
        elif num_misconnects > 10:
            score += 2
        elif num_misconnects > 0:
            score += 1

        if score <= 2:
            return 'LOW'
        elif score <= 5:
            return 'MEDIUM'
        elif score <= 8:
            return 'HIGH'
        else:
            return 'CRITICAL'

    def _check_escalation(self, severity: str, special_passengers: List[str],
                         delay_minutes: int) -> bool:
        """Determine if escalation is required"""

        if severity in ['HIGH', 'CRITICAL']:
            return True

        if delay_minutes >= 120:
            return True

        critical_pax = ['UMNR', 'Wheelchair', 'Medical']
        for pax in special_passengers:
            if any(crit in pax for crit in critical_pax):
                return True

        return False

    # Text parsing helpers
    def _extract_flight_number(self, text: str) -> str:
        """Extract flight number from text"""
        import re
        match = re.search(r'[A-Z]{2}\d{3,4}', text)
        return match.group(0) if match else f"XY{random.randint(100, 999)}"

    def _extract_delay(self, text: str) -> int:
        """Extract delay minutes from text"""
        import re

        # Look for patterns like "3h", "180 min", "2 hours"
        hour_match = re.search(r'(\d+)\s*h(?:our)?s?', text, re.IGNORECASE)
        if hour_match:
            return int(hour_match.group(1)) * 60

        min_match = re.search(r'(\d+)\s*min', text, re.IGNORECASE)
        if min_match:
            return int(min_match.group(1))

        return 120  # Default

    def _extract_cause(self, text: str) -> str:
        """Extract delay cause from text"""
        text_lower = text.lower()

        for cause in self.DELAY_CAUSES:
            if cause.lower() in text_lower or cause.split()[0].lower() in text_lower:
                return cause

        return "Unknown"

    def _extract_passenger_count(self, text: str) -> int:
        """Extract total passenger count"""
        import re
        match = re.search(r'(\d+)\s*passengers', text, re.IGNORECASE)
        return int(match.group(1)) if match else 150

    def _extract_misconnects(self, text: str) -> int:
        """Extract number of misconnecting passengers"""
        import re
        match = re.search(r'(\d+)\s*(?:passengers?\s+)?misconnect', text, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    def _extract_special_passengers(self, text: str) -> List[str]:
        """Extract special passenger types from text"""
        special = []
        text_lower = text.lower()

        if 'wheelchair' in text_lower or 'wchr' in text_lower:
            count = self._extract_count_for_type(text, 'wheelchair')
            for _ in range(count):
                special.append('Wheelchair passenger')

        if 'unaccompanied minor' in text_lower or 'umnr' in text_lower:
            count = self._extract_count_for_type(text, 'unaccompanied minor')
            for _ in range(count):
                special.append('UMNR (Unaccompanied minor)')

        if 'medical' in text_lower or 'meda' in text_lower:
            count = self._extract_count_for_type(text, 'medical')
            for _ in range(count):
                special.append('Medical passenger')

        if 'vip' in text_lower or 'platinum' in text_lower:
            count = self._extract_count_for_type(text, 'vip|platinum')
            for _ in range(count):
                special.append('Platinum frequent flyer')

        return special

    def _extract_count_for_type(self, text: str, passenger_type: str) -> int:
        """Extract count for a specific passenger type"""
        import re
        pattern = rf'(\d+)\s*{passenger_type}'
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else 1

    def _extract_airport(self, text: str, position: str = 'to') -> str:
        """Extract airport code"""
        import re
        airports = re.findall(r'\b[A-Z]{3}\b', text)

        if position == 'to' and len(airports) > 1:
            return airports[1]
        elif airports:
            return airports[0]

        return "XXX"

    def describe_scenario(self, scenario: Dict[str, Any]) -> str:
        """Generate human-readable description of scenario"""

        desc = f"Flight {scenario['flight_number']} "
        desc += f"from {scenario['origin']} to {scenario['destination']} "
        desc += f"delayed {scenario['delay_minutes']} minutes due to {scenario['cause']}.\n"
        desc += f"Total passengers: {scenario['num_passengers']}\n"

        if scenario['num_misconnects'] > 0:
            desc += f"Misconnecting passengers: {scenario['num_misconnects']}\n"

        if scenario['special_passengers']:
            desc += f"Special assistance: {', '.join(scenario['special_passengers'])}\n"

        desc += f"Severity: {scenario['severity']}\n"
        desc += f"Escalation required: {'Yes' if scenario['requires_escalation'] else 'No'}"

        return desc
