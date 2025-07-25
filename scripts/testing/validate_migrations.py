#!/usr/bin/env python3
"""
Migration Validation Script
Validates Django migration sequence and dependencies without requiring Django to be installed.

Usage:
python scripts/testing/validate_migrations.py

This script:
- Checks migration file naming sequence
- Validates migration dependencies
- Reports any conflicts or issues
- Provides migration graph visualization

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

class MigrationValidator:
"""Validates Django migration files and dependencies"""

def __init__(self, app_name: str = "stocks"):
self.app_name = app_name
self.migrations_dir = Path(f"{app_name}/migrations")
self.migrations = {}
self.dependency_graph = {}
self.issues = []

print(f" Django Migration Validator")
print(f" App: {app_name}")
print(f" Directory: {self.migrations_dir}")
print("=" * 50)

def scan_migrations(self):
"""Scan and parse migration files"""
if not self.migrations_dir.exists():
self.issues.append(f" Migration directory not found: {self.migrations_dir}")
return False

migration_files = [f for f in self.migrations_dir.glob("*.py") if f.name != "__init__.py"]
migration_files.sort()

print(f" Found {len(migration_files)} migration files:")

for migration_file in migration_files:
self.parse_migration_file(migration_file)

return True

def parse_migration_file(self, migration_file: Path):
"""Parse a single migration file"""
try:
with open(migration_file, 'r', encoding='utf-8') as f:
content = f.read()

# Extract migration number and name
filename = migration_file.name
match = re.match(r'^(\d{4})_(.+)\.py$', filename)

if not match:
self.issues.append(f" Invalid migration filename: {filename}")
return

migration_number = match.group(1)
migration_name = match.group(2)

# Extract dependencies
dependencies = self.extract_dependencies(content)

# Extract operations
operations = self.extract_operations(content)

self.migrations[migration_number] = {
'filename': filename,
'name': migration_name,
'dependencies': dependencies,
'operations': operations,
'path': migration_file
}

print(f" {filename} - Dependencies: {len(dependencies)}, Operations: {len(operations)}")

except Exception as e:
self.issues.append(f" Error parsing {migration_file}: {e}")

def extract_dependencies(self, content: str) -> List[str]:
"""Extract migration dependencies from file content"""
dependencies = []

# Find dependencies section
dep_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
if dep_match:
dep_content = dep_match.group(1)

# Extract individual dependencies
dep_pattern = r'\([\'"]([^\'",]+)[\'"],\s*[\'"]([^\'",]+)[\'"]\)'
for match in re.finditer(dep_pattern, dep_content):
app_name = match.group(1)
migration_name = match.group(2)
dependencies.append(f"{app_name}.{migration_name}")

return dependencies

def extract_operations(self, content: str) -> List[str]:
"""Extract migration operations from file content"""
operations = []

# Find operations section
ops_match = re.search(r'operations\s*=\s*\[(.*?)\]', content, re.DOTALL)
if ops_match:
ops_content = ops_match.group(1)

# Extract operation types
operation_patterns = [
r'migrations\.CreateModel',
r'migrations\.DeleteModel',
r'migrations\.AddField',
r'migrations\.RemoveField',
r'migrations\.AlterField',
r'migrations\.RenameField',
r'migrations\.AddIndex',
r'migrations\.RemoveIndex',
r'migrations\.RunPython',
r'migrations\.RunSQL'
]

for pattern in operation_patterns:
matches = re.findall(pattern, ops_content)
operations.extend([op.split('.')[-1] for op in matches])

return operations

def validate_sequence(self):
"""Validate migration number sequence"""
print("\n Validating Migration Sequence:")
print("-" * 40)

migration_numbers = sorted(self.migrations.keys())
expected_sequence = [f"{i:04d}" for i in range(1, len(migration_numbers) + 1)]

if migration_numbers == expected_sequence:
print(" Migration sequence is correct")
return True
else:
print(" Migration sequence issues detected:")
for i, (actual, expected) in enumerate(zip(migration_numbers, expected_sequence)):
if actual != expected:
print(f" Position {i+1}: Found {actual}, expected {expected}")

# Check for duplicates
duplicates = set([x for x in migration_numbers if migration_numbers.count(x) > 1])
if duplicates:
print(f" Duplicate numbers: {duplicates}")
self.issues.append(f"Duplicate migration numbers: {duplicates}")

# Check for gaps
numbers = [int(num) for num in migration_numbers]
for i in range(1, max(numbers)):
if i not in numbers:
print(f" Missing migration: {i:04d}")

return False

def validate_dependencies(self):
"""Validate migration dependencies"""
print("\n Validating Migration Dependencies:")
print("-" * 40)

all_valid = True

for number, migration in self.migrations.items():
print(f"\n {migration['filename']}:")

if not migration['dependencies']:
if number != "0001":
print(f" No dependencies (unusual for non-initial migration)")
else:
print(f" Initial migration (no dependencies expected)")
continue

for dep in migration['dependencies']:
if dep.startswith(f"{self.app_name}."):
# Internal dependency
dep_number = dep.split('.')[-1]
if dep_number in self.migrations:
print(f" {dep} - Found")
else:
print(f" {dep} - Missing!")
self.issues.append(f"Missing dependency: {dep}")
all_valid = False
else:
# External dependency (other app)
print(f" {dep} - External (not validated)")

return all_valid

def check_for_conflicts(self):
"""Check for migration conflicts"""
print("\n Checking for Migration Conflicts:")
print("-" * 40)

conflicts_found = False

# Group migrations by number
by_number = {}
for number, migration in self.migrations.items():
if number not in by_number:
by_number[number] = []
by_number[number].append(migration)

# Check for conflicts
for number, migrations in by_number.items():
if len(migrations) > 1:
print(f" Conflict detected for migration {number}:")
for migration in migrations:
print(f" • {migration['filename']}")
conflicts_found = True
self.issues.append(f"Migration number conflict: {number}")

if not conflicts_found:
print(" No migration conflicts detected")

return not conflicts_found

def create_dependency_graph(self):
"""Create a visual dependency graph"""
print("\n Migration Dependency Graph:")
print("-" * 40)

for number in sorted(self.migrations.keys()):
migration = self.migrations[number]
deps = [dep.split('.')[-1] for dep in migration['dependencies'] if dep.startswith(f"{self.app_name}.")]

if deps:
dep_str = " ← " + ", ".join(deps)
else:
dep_str = " (initial)"

print(f"{number}_{migration['name']}{dep_str}")

def generate_report(self):
"""Generate final validation report"""
print("\n" + "=" * 60)
print(" MIGRATION VALIDATION REPORT")
print("=" * 60)

print(f" App: {self.app_name}")
print(f" Migrations found: {len(self.migrations)}")
print(f" Issues found: {len(self.issues)}")

if self.issues:
print("\n ISSUES TO FIX:")
for i, issue in enumerate(self.issues, 1):
print(f" {i}. {issue}")
else:
print("\n NO ISSUES FOUND!")

print("\n MIGRATION SUMMARY:")
for number in sorted(self.migrations.keys()):
migration = self.migrations[number]
ops = len(migration['operations'])
deps = len(migration['dependencies'])
print(f" {number}_{migration['name']} - {ops} operations, {deps} dependencies")

# Overall status
if not self.issues:
print("\n ALL VALIDATIONS PASSED!")
print(" Migration sequence is ready for Django")
else:
print(f"\n {len(self.issues)} ISSUES NEED ATTENTION")
print(" Fix the issues above before running Django migrations")

def run_validation(self):
"""Run all validation checks"""
if not self.scan_migrations():
print(" Could not scan migrations")
return False

if not self.migrations:
print(" No migrations found")
return False

# Run all validation checks
sequence_ok = self.validate_sequence()
deps_ok = self.validate_dependencies()
conflicts_ok = self.check_for_conflicts()

# Create visual graph
self.create_dependency_graph()

# Generate report
self.generate_report()

return sequence_ok and deps_ok and conflicts_ok

def main():
"""Main function"""
if len(sys.argv) > 1 and sys.argv[1] == '--help':
print(__doc__)
return

# Change to project directory
script_dir = Path(__file__).parent
project_dir = script_dir.parent.parent
os.chdir(project_dir)

# Run validation
validator = MigrationValidator("stocks")
success = validator.run_validation()

# Exit with appropriate code
sys.exit(0 if success else 1)

if __name__ == "__main__":
main()