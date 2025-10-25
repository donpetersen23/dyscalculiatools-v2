#!/usr/bin/env python3
"""
Test script to validate generated static HTML files.
Run after build_static_pages.py to verify output.
"""
from pathlib import Path

def test_file_exists(filepath, description):
    """Check if file exists."""
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"[OK] {description}: {filepath.name} ({size:,} bytes)")
        return True
    else:
        print(f"[FAIL] {description}: {filepath.name} NOT FOUND")
        return False

def test_file_content(filepath, required_strings):
    """Check if file contains required content."""
    if not filepath.exists():
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing = []
    for required in required_strings:
        if required not in content:
            missing.append(required)
    
    if missing:
        print(f"  [WARN] Missing content: {', '.join(missing)}")
        return False
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing Static Build Output")
    print("=" * 50)
    
    static_dir = Path('static')
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check files exist
    print("\n1. Checking files exist...")
    files_to_check = [
        (static_dir / 'index.html', 'Homepage'),
        (static_dir / 'about.html', 'About page'),
        (static_dir / 'contact.html', 'Contact page'),
    ]
    
    for filepath, description in files_to_check:
        if test_file_exists(filepath, description):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Test 2: Check homepage content
    print("\n2. Checking homepage content...")
    if test_file_content(static_dir / 'index.html', [
        'Dyscalculia Tools',
        'Tools & Strategies',
        'Research & Evidence',
        'styles.css'
    ]):
        print("  [OK] Homepage has required content")
        tests_passed += 1
    else:
        print("  [FAIL] Homepage missing required content")
        tests_failed += 1
    
    # Test 3: Check about page content
    print("\n3. Checking about page content...")
    if test_file_content(static_dir / 'about.html', [
        'Building Solutions for Dyscalculia',
        'styles.css'
    ]):
        print("  [OK] About page has required content")
        tests_passed += 1
    else:
        print("  [FAIL] About page missing required content")
        tests_failed += 1
    
    # Test 4: Check contact page content
    print("\n4. Checking contact page content...")
    if test_file_content(static_dir / 'contact.html', [
        'Contact Us',
        'styles.css'
    ]):
        print("  [OK] Contact page has required content")
        tests_passed += 1
    else:
        print("  [FAIL] Contact page missing required content")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("=" * 50)
    
    if tests_failed == 0:
        print("[OK] All tests passed! Static pages are ready.")
        return 0
    else:
        print("[FAIL] Some tests failed. Review output above.")
        return 1

if __name__ == '__main__':
    exit(main())
