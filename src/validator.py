"""
PII Validator Module
Responsible for detecting and filtering sensitive Dutch personal data (BSN, phone numbers, etc.)
to ensure GDPR/AVG compliance before data reaches AI processing.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PIIDetection:
    """Represents a detected PII violation."""
    type: str
    value: str
    position: int


class PIIValidator:
    """
    Validates user input for Personally Identifiable Information (PII)
    according to Dutch GDPR/AVG regulations.
    """

    # BSN (Burgerservicenummer) pattern: 9 digits with 11-proof validation
    BSN_PATTERN = re.compile(r'\b\d{9}\b')

    # Dutch phone numbers: +31, 06, 031, various formats
    PHONE_PATTERN = re.compile(
        r'(\+31[\s\-]?|0031[\s\-]?|0)(\d[\s\-]?){8,9}\d\b'
    )

    # Dutch postal code: 1234 AB format
    POSTAL_CODE_PATTERN = re.compile(r'\b\d{4}\s?[A-Z]{2}\b')

    # Email addresses
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )

    # IBAN numbers (Dutch format)
    IBAN_PATTERN = re.compile(r'\bNL\d{2}[A-Z]{4}\d{10}\b')

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the PII validator.

        Args:
            strict_mode: If True, blocks postal codes and emails as well
        """
        self.strict_mode = strict_mode

    def validate(self, text: str) -> Tuple[bool, List[PIIDetection], str]:
        """
        Validate text for PII violations.

        Args:
            text: The user input to validate

        Returns:
            Tuple of (is_safe, list_of_detections, sanitized_text)
        """
        detections: List[PIIDetection] = []
        sanitized_text = text

        # Check for BSN numbers
        bsn_matches = self.BSN_PATTERN.finditer(text)
        for match in bsn_matches:
            bsn = match.group()
            if self._validate_bsn(bsn):
                detections.append(PIIDetection(
                    type="BSN (Burgerservicenummer)",
                    value=self._mask_value(bsn),
                    position=match.start()
                ))
                sanitized_text = sanitized_text.replace(bsn, "[BSN_VERWIJDERD]")

        # Check for phone numbers
        phone_matches = self.PHONE_PATTERN.finditer(text)
        for match in phone_matches:
            phone = match.group()
            detections.append(PIIDetection(
                type="Telefoonnummer",
                value=self._mask_value(phone),
                position=match.start()
            ))
            sanitized_text = sanitized_text.replace(phone, "[TELEFOON_VERWIJDERD]")

        # Check for IBAN
        iban_matches = self.IBAN_PATTERN.finditer(text)
        for match in iban_matches:
            iban = match.group()
            detections.append(PIIDetection(
                type="IBAN",
                value=self._mask_value(iban),
                position=match.start()
            ))
            sanitized_text = sanitized_text.replace(iban, "[IBAN_VERWIJDERD]")

        if self.strict_mode:
            # Check for postal codes (less sensitive, but can be identifying)
            postal_matches = self.POSTAL_CODE_PATTERN.finditer(text)
            for match in postal_matches:
                postal = match.group()
                detections.append(PIIDetection(
                    type="Postcode",
                    value=self._mask_value(postal),
                    position=match.start()
                ))
                sanitized_text = sanitized_text.replace(postal, "[POSTCODE_VERWIJDERD]")

            # Check for email addresses
            email_matches = self.EMAIL_PATTERN.finditer(text)
            for match in email_matches:
                email = match.group()
                detections.append(PIIDetection(
                    type="E-mailadres",
                    value=self._mask_value(email),
                    position=match.start()
                ))
                sanitized_text = sanitized_text.replace(email, "[EMAIL_VERWIJDERD]")

        is_safe = len(detections) == 0
        return is_safe, detections, sanitized_text

    def get_safety_report(self, detections: List[PIIDetection]) -> Dict[str, any]:
        """
        Generate a safety report for transparency.

        Args:
            detections: List of PII detections

        Returns:
            Dictionary with safety report details
        """
        return {
            "scan_performed": True,
            "pii_detected": len(detections) > 0,
            "violations_count": len(detections),
            "violations": [
                {
                    "type": d.type,
                    "masked_value": d.value,
                    "position": d.position
                }
                for d in detections
            ],
            "compliance_notes": "Gecontroleerd volgens AVG/GDPR richtlijnen",
            "strict_mode": self.strict_mode
        }

    def _validate_bsn(self, bsn: str) -> bool:
        """
        Validate BSN using the 11-proof test.

        Args:
            bsn: 9-digit string to validate

        Returns:
            True if valid BSN, False otherwise
        """
        if len(bsn) != 9 or not bsn.isdigit():
            return False

        # 11-proof: multiply each digit by 9,8,7,6,5,4,3,2,-1 and sum
        multipliers = [9, 8, 7, 6, 5, 4, 3, 2, -1]
        total = sum(int(digit) * multiplier for digit, multiplier in zip(bsn, multipliers))

        return total % 11 == 0

    def _mask_value(self, value: str) -> str:
        """
        Mask a sensitive value for logging (show first and last 2 chars).

        Args:
            value: The value to mask

        Returns:
            Masked string
        """
        if len(value) <= 4:
            return "***"
        return f"{value[:2]}...{value[-2:]}"
