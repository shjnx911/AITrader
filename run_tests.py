#!/usr/bin/env python
"""
Test runner script for the AITradeStrategist application.

This script runs all tests or specific test types based on command line arguments.
"""
import argparse
import os
import sys
import subprocess


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run tests for the AITradeStrategist application.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Test type options
    test_type_group = parser.add_argument_group('Test Types')
    test_type_group.add_argument(
        '--unit', action='store_true',
        help='Run unit tests only'
    )
    test_type_group.add_argument(
        '--integration', action='store_true',
        help='Run integration tests only'
    )
    test_type_group.add_argument(
        '--functional', action='store_true',
        help='Run functional tests only'
    )
    
    # Coverage options
    coverage_group = parser.add_argument_group('Coverage Options')
    coverage_group.add_argument(
        '--cov', action='store_true',
        help='Generate a coverage report'
    )
    coverage_group.add_argument(
        '--html', action='store_true',
        help='Generate an HTML coverage report'
    )
    
    # Other options
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Increase verbosity'
    )
    parser.add_argument(
        '-k', '--keyword', type=str,
        help='Only run tests that match the given keyword expression'
    )
    
    return parser.parse_args()


def run_tests(args):
    """Run the tests based on the command line arguments."""
    # Build the pytest command
    cmd = ['pytest']
    
    # Add verbosity if requested
    if args.verbose:
        cmd.append('-v')
    
    # Add test type filtering
    if args.unit:
        cmd.append('tests/unit')
    elif args.integration:
        cmd.append('tests/integration')
    elif args.functional:
        cmd.append('tests/functional')
    
    # Add keyword filtering
    if args.keyword:
        cmd.extend(['-k', args.keyword])
    
    # Add coverage options
    if args.cov:
        cmd.append('--cov=.')
        
        if args.html:
            cmd.append('--cov-report=html')
        else:
            cmd.append('--cov-report=term')
    
    # Run the tests
    print(f'Running command: {" ".join(cmd)}')
    result = subprocess.run(cmd)
    
    return result.returncode


def main():
    """Main entry point."""
    args = parse_args()
    
    # Run the tests
    return_code = run_tests(args)
    
    # Check if any tests were failed
    if return_code != 0:
        print('Tests failed')
        sys.exit(return_code)
    
    print('All tests passed')
    

if __name__ == '__main__':
    main()