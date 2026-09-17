# General Domain Knowledge Cards

This directory contains general-purpose knowledge cards that can be applied across multiple domains.

## Newly Added Knowledge Cards

### 1. CLI Fault Classification (`tools/cli_fault_classification/`)

**Purpose**: Provides knowledge for CLI non-interactive execution and fault classification.

**Key Content**:
- 6 fault categories: Startup, Timeout, Exit Code, Output Parsing, Resource, and Environment failures
- Diagnostic workflows for each fault type
- Best practices for command execution and error handling
- Monitoring and alerting recommendations

**When to Use**:
- Automated script execution
- Batch processing tasks
- CI/CD pipeline command execution
- Remote server execution
- Containerized environment commands

**Boundaries**:
- Focuses on CLI execution layer faults only
- Does not cover business logic errors or domain-specific failures

### 2. JSON Schema Report Contract (`contracts/json_schema_report_contract/`)

**Purpose**: Defines the format, validation rules, and delivery requirements for structured JSON reports.

**Key Content**:
- Report structure requirements (root node, required fields, array constraints)
- JSON Schema validation rules
- Identity consistency validation
- Validation workflow and failure handling
- Delivery requirements

**When to Use**:
- Attribution analysis reports
- Task execution reports
- Validation result reports
- Diagnostic analysis reports
- Assessment result reports

**Boundaries**:
- Focuses on report format and delivery specifications only
- Does not guarantee scientific correctness of report content
- Does not cover business logic validity

## Knowledge Card Structure

Each knowledge card follows the standard structure:
- `metadata.json`: Basic information (name, type, domain, description, tags, version)
- `knowledge.md`: Complete knowledge content in flexible single-document format

## Usage in OneScience System

These knowledge cards are designed to be:
1. Retrieved by `onescience-primitives` skill when needed
2. Used by execution skills (coder, runtime, etc.) for reference
3. Applied during task planning and execution phases
4. Referenced for fault diagnosis and report generation