#!/usr/bin/env python3
"""
Quick test script for OpenAI integration
Tests both mock mode and real API (if configured)
"""

import os
from src.ai_service import AIService


def test_mock_mode():
    """Test mock AI service (no API key)."""
    print("=" * 60)
    print("TEST 1: Mock Mode (No API Key)")
    print("=" * 60)

    service = AIService(api_key=None)

    test_text = "Wat zijn de gezondheidsrisicos van roken?"
    print(f"\nInput: {test_text}\n")

    result = service.analyze(test_text)
    print(result)

    info = service.get_service_info()
    print(f"\nService Info: {info}")
    print("\n[OK] Mock mode test passed!\n")


def test_openai_mode():
    """Test OpenAI API (if key is configured)."""
    print("=" * 60)
    print("TEST 2: OpenAI Mode (With API Key)")
    print("=" * 60)

    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("\n[WARNING] OPENAI_API_KEY not set. Skipping OpenAI test.")
        print("          To test with real API:")
        print("          1. Get key from https://platform.openai.com/api-keys")
        print("          2. Run: export OPENAI_API_KEY='sk-...'")
        print("          3. Run this test again\n")
        return

    print(f"\n[OK] API Key found: {api_key[:20]}...\n")

    service = AIService(api_key=api_key, model="gpt-3.5-turbo")

    test_text = "Leg in één zin uit wat het RIVM doet."
    print(f"Input: {test_text}\n")

    try:
        result = service.analyze(test_text)
        print(result)

        info = service.get_service_info()
        print(f"\nService Info: {info}")
        print("\n[OK] OpenAI mode test passed!\n")
    except Exception as e:
        print(f"\n[ERROR] OpenAI test failed: {e}\n")
        print("Possible issues:")
        print("- Invalid API key")
        print("- No credits remaining")
        print("- Network issue")
        print("\nCheck: https://platform.openai.com/usage\n")


def main():
    """Run all tests."""
    print("\nAI Service Integration Tests\n")

    # Test 1: Mock mode (always works)
    test_mock_mode()

    # Test 2: OpenAI mode (only if configured)
    test_openai_mode()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
