# Technology Stack

## Project Type

Documentation and workflow rules repository - no application code.

## File Format

- **Primary Format**: Markdown (.md files)
- **Configuration**: TOML (cliff.toml for changelog generation)
- **Structure**: Hierarchical directory organization for rule definitions

## Build & Release Tools

### git-cliff
Changelog generation tool using conventional commits.

**Configuration**: `cliff.toml`

**Commit Convention**: Follows conventional commits format
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `ci:` - CI/CD changes
- `chore:` - Miscellaneous changes

**Generate Changelog**:
```bash
git cliff -o CHANGELOG.md
```

## Common Commands

### Repository Setup
```bash
# Clone repository
git clone <repo-url>

# Copy rules to Amazon Q project
mkdir -p .amazonq/rules
cp -R ../aidlc-workflows/aidlc-rules/aws-aidlc-rules .amazonq/rules/
cp -R ../aidlc-workflows/aidlc-rules/aws-aidlc-rule-details .amazonq/

# Copy rules to Kiro project
mkdir -p .kiro/steering
cp -R ../aidlc-workflows/aidlc-rules/aws-aidlc-rules .kiro/steering/
cp -R ../aidlc-workflows/aidlc-rules/aws-aidlc-rule-details .kiro/
```

### Changelog Management
```bash
# Generate changelog from git history
git cliff -o CHANGELOG.md

# Generate changelog for specific tag range
git cliff --tag v1.0.0..v2.0.0
```

## Dependencies

No runtime dependencies - this is a pure documentation/rules repository.

## Version Control

- **Platform**: Git
- **Commit Style**: Conventional commits
- **Tag Pattern**: `v[0-9].*` (e.g., v1.0.0, v2.1.3)
