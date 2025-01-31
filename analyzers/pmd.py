from dataclasses import dataclass
import os
import subprocess
from typing import List, Optional
import json
from pathlib import Path

from analyzers.model import AnalysisResult, CodeViolation

class PMDViolationsParser:
    """Parser for code analysis violation reports."""
    
    def __init__(self):
        self.supported_tools = ['pmd']  # Can be extended for other tools
        
    def _map_pmd_priority_to_severity(self, priority: int) -> str:
        """Maps PMD priority levels to standardized severity levels."""
        priority_map = {
            1: "BLOCKER",
            2: "CRITICAL",
            3: "MAJOR",
            4: "MINOR",
            5: "INFO"
        }
        return priority_map.get(priority, "UNKNOWN")

    def parse_pmd_json(self, file_path: str) -> AnalysisResult:
        """
        Parses a PMD JSON report file and returns a standardized AnalysisResult.
        
        Args:
            file_path: Path to the PMD JSON report file
        
        Returns:
            AnalysisResult object containing the parsed data
        
        Raises:
            FileNotFoundError: If the input file doesn't exist
            json.JSONDecodeError: If the input file is not valid JSON
            KeyError: If the JSON structure is not as expected
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            violations = []
            errors = []
            
            # Process configuration errors
            if 'configurationErrors' in data:
                for error in data['configurationErrors']:
                    errors.append(f"Configuration Error - {error['rule']}: {error['message']}")
            
            # Process processing errors
            if 'processingErrors' in data:
                errors.extend(data['processingErrors'])
            
            # Process violations
            for file_entry in data['files']:
                file_path = file_entry['filename']
                
                for violation in file_entry['violations']:
                    violations.append(CodeViolation(
                        file_path=file_path,
                        line_start=violation['beginline'],
                        line_end=violation['endline'],
                        column_start=violation['begincolumn'],
                        column_end=violation['endcolumn'],
                        rule=violation['rule'],
                        category=violation['ruleset'],
                        description=violation['description'],
                        severity=self._map_pmd_priority_to_severity(violation['priority']),
                        url=violation.get('externalInfoUrl')
                    ))
            
            return AnalysisResult(
                tool_name="PMD",
                tool_version=data['pmdVersion'],
                timestamp=data['timestamp'],
                violations=violations,
                errors=errors
            )
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Report file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {file_path}")
        except KeyError as e:
            raise KeyError(f"Missing required field in JSON structure: {str(e)}")

    def parse_file(self, file_path: str, tool: str = 'pmd') -> AnalysisResult:
        """
        Parse a violation report file based on the specified tool.
        
        Args:
            file_path: Path to the report file
            tool: Name of the tool that generated the report (default: 'pmd')
            
        Returns:
            AnalysisResult object containing the parsed data
            
        Raises:
            ValueError: If the specified tool is not supported
        """
        tool = tool.lower()
        if tool not in self.supported_tools:
            raise ValueError(f"Unsupported tool: {tool}. Supported tools: {', '.join(self.supported_tools)}")
        
        if tool == 'pmd':
            return self.parse_pmd_json(file_path)


# Launch PMD
def launch_pmd(input_file: str, tools_config) -> AnalysisResult:
    """
    Launch PMD on the Java file to get a list of warnings / errors to fix
    """
    try:        
        # Run PMD
        print("Running PMD...")
        
        cmd_template = tools_config.get("Tools", "pmd.cmd")
        cmd = cmd_template.format(input_file=input_file)
        subprocess.run(cmd, shell=True)

        parser = PMDViolationsParser()
        
        # Parse the violations file
        violations = parser.parse_file("violations.json", "pmd")
    

    except Exception as e:
        print(f"Error while executing PMD: {str(e)}")
    return violations 