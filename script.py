#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from config import config
import logging
from typing import Optional
from analyzers.pmd import launch_pmd
from corrections import fix_corrections


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_file_path(file_path: str) -> Path:
    try:
        path = Path(file_path).resolve()
        if not path.exists():
            raise ValueError(f"File does not exist")
        if not path.is_file():
            raise ValueError(f"Path is not a file")
        return path
    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        raise

def secure_file_operations(input_path: Path, output_path: Optional[Path] = None) -> Path:
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.fixed{input_path.suffix}"
    
    # Ensure output directory exists with secure permissions
    output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    
    # Validate write permissions
    if output_path.exists() and not os.access(output_path.parent, os.W_OK):
        raise PermissionError(f"No write permission for {output_path}")
        
    return output_path

# This script is calling a code linter, obtain the list of problems and use GenAI to fix them.
def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Process Java files with specified tool (default: PMD)'
    )

    # Required input file argument
    parser.add_argument(
        'input_file',
        type=str,
        help='Input Java file to process'
    )

    # Optional tool argument with default value
    parser.add_argument(
        '--tool',
        type=str,
        default='pmd',
        help='Tool to use for processing (default: pmd)'
    )

    # Optional output file argument
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: input_file.fixed)'
    )

    args = parser.parse_args()

    try:
        input_path = validate_file_path(args.input_file)
        if input_path.suffix.lower() != '.java':
            raise ValueError("File must have .java extension")
            
        args.input_file = str(input_path)
        args.output = str(secure_file_operations(input_path))
        
    except Exception as e:
        parser.error(str(e))
        
    return args

def main():
    args = parse_arguments()

    # Print the arguments (for demonstration)
    #print(f"Input file: {args.input_file}")
    #print(f"Tool: {args.tool}")
    #print(f"Output file: {args.output}")

    # Read tool configuration stored in tool.ini in a dictionary
    print("Check the source file for code violations)")
    violations =  check_violations(args.input_file, args.tool)

    # Add your processing logic her        
    fix_corrections(args.input_file, args.output, violations)
    
    print("Control the violations fixed in the output file")
    violations = check_violations(args.output, args.tool)
    

        
    sys.exit(0)
    
def check_violations(input_file, tool):
    if tool == 'pmd':
        print("Using PMD")
        violations = launch_pmd(input_file, config)

    elif tool == 'checkstyle':
        print("Using Checkstyle")

    else:
        print(f"Unknown tool: {tool}")
        sys.exit(1)

    
    # Print summary
    print(f"Analysis Results from {violations.tool_name} {violations.tool_version}")
    print(f"Timestamp: {violations.timestamp}")
    print(f"Total violations found: {len(violations.violations)}")
    #Print the number by severity
    print(f"Number of violations by severity:")
    # Calculate violations by severity from violations list
    severity_counts = {}
    for violation in violations.violations:
        severity = violation.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
    # Print severity counts
    for severity, count in severity_counts.items():
        print(f"  {severity}: {count}")
    return violations
    

if __name__ == "__main__":
    main()
