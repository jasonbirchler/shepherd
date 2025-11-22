#!/usr/bin/env python3
"""
Test runner for pyshepherd backend tests

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --integration      # Run integration tests only
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --verbose          # Verbose output
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test selection
    if args.integration:
        cmd.append('test_integration.py')
    elif args.unit:
        cmd.extend([
            'test_sequencer.py',
            'test_session.py', 
            'test_track.py',
            'test_clip.py',
            'test_musical_context.py',
            'test_hardware_device.py'
        ])
    else:
        cmd.append('.')  # All tests
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            '--cov=pyshepherd.backend',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # Add other pytest options
    cmd.extend([
        '--tb=short',
        '--strict-markers'
    ])
    
    print(f"Running: {' '.join(cmd)}")
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if args.coverage and result.returncode == 0:
        print("\nCoverage report generated in htmlcov/index.html")
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run pyshepherd backend tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Check for conflicting options
    if args.integration and args.unit:
        print("Error: Cannot specify both --integration and --unit")
        return 1
    
    return run_tests(args)


if __name__ == '__main__':
    sys.exit(main())