"""
Unit tests for PII Validator
Run with: pytest tests/test_validator.py -v
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validator import PIIValidator


def test_valid_bsn_detection():
    """Test that valid BSN numbers are detected."""
    validator = PIIValidator(strict_mode=True)

    # Valid BSN (passes 11-proof)
    is_safe, detections, _ = validator.validate("Mijn BSN is 45350983535")

    assert is_safe is False
    assert len(detections) == 1
    assert detections[0].type == "BSN (Burgerservicenummer)"


def test_invalid_bsn_not_detected():
    """Test that invalid BSN numbers (failing 11-proof) are not flagged."""
    validator = PIIValidator(strict_mode=True)

    # Invalid BSN (fails 11-proof)
    is_safe, detections, _ = validator.validate("Random number 123456789")

    # Should not detect as BSN because it fails validation
    bsn_detections = [d for d in detections if "BSN" in d.type]
    assert len(bsn_detections) == 0


def test_phone_number_detection():
    """Test Dutch phone number detection."""
    validator = PIIValidator(strict_mode=True)

    test_cases = [
        "Bel me op 0612345678",
        "Mijn nummer is +31612345678",
        "Contact: 0031612345678"
    ]

    for text in test_cases:
        is_safe, detections, _ = validator.validate(text)
        assert is_safe is False
        assert any("Telefoonnummer" in d.type for d in detections)


def test_iban_detection():
    """Test Dutch IBAN detection."""
    validator = PIIValidator(strict_mode=True)

    is_safe, detections, _ = validator.validate("IBAN: NL91ABNA0417164300")

    assert is_safe is False
    assert any("IBAN" in d.type for d in detections)


def test_email_detection_strict_mode():
    """Test email detection in strict mode."""
    validator = PIIValidator(strict_mode=True)

    is_safe, detections, _ = validator.validate("Contact me at john@example.com")

    assert is_safe is False
    assert any("E-mailadres" in d.type for d in detections)


def test_email_allowed_in_non_strict_mode():
    """Test that emails are allowed in non-strict mode."""
    validator = PIIValidator(strict_mode=False)

    is_safe, detections, _ = validator.validate("Contact me at john@example.com")

    # Email should not be detected in non-strict mode
    assert is_safe is True
    assert len(detections) == 0


def test_postal_code_detection_strict_mode():
    """Test postal code detection in strict mode."""
    validator = PIIValidator(strict_mode=True)

    is_safe, detections, _ = validator.validate("Ik woon in 1234 AB")

    assert is_safe is False
    assert any("Postcode" in d.type for d in detections)


def test_clean_text_passes():
    """Test that clean text without PII passes validation."""
    validator = PIIValidator(strict_mode=True)

    clean_texts = [
        "Wat is het weer vandaag?",
        "Hoe werkt deze AI gateway?",
        "Ik heb een vraag over het RIVM"
    ]

    for text in clean_texts:
        is_safe, detections, _ = validator.validate(text)
        assert is_safe is True
        assert len(detections) == 0


def test_sanitization():
    """Test that detected PII is properly sanitized."""
    validator = PIIValidator(strict_mode=True)

    text = "Mijn BSN is 111222333 en telefoon 0612345678"
    is_safe, detections, sanitized = validator.validate(text)

    assert "[BSN_VERWIJDERD]" in sanitized
    assert "[TELEFOON_VERWIJDERD]" in sanitized
    assert "111222333" not in sanitized
    assert "0612345678" not in sanitized


def test_safety_report_generation():
    """Test safety report generation."""
    validator = PIIValidator(strict_mode=True)

    is_safe, detections, _ = validator.validate("Bel 0612345678")
    report = validator.get_safety_report(detections)

    assert report["scan_performed"] is True
    assert report["pii_detected"] is True
    assert report["violations_count"] == 1
    assert len(report["violations"]) == 1
    assert report["strict_mode"] is True


def test_multiple_violations():
    """Test detection of multiple PII types in one text."""
    validator = PIIValidator(strict_mode=True)

    text = "BSN 111222333, tel 0612345678, IBAN NL91ABNA0417164300"
    is_safe, detections, _ = validator.validate(text)

    assert is_safe is False
    assert len(detections) >= 3

    types = [d.type for d in detections]
    assert any("BSN" in t for t in types)
    assert any("Telefoonnummer" in t for t in types)
    assert any("IBAN" in t for t in types)


def test_masking():
    """Test that values are properly masked in detections."""
    validator = PIIValidator(strict_mode=True)

    is_safe, detections, _ = validator.validate("BSN: 111222333")

    assert detections[0].value == "11...33"
    assert "111222333" not in detections[0].value


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
