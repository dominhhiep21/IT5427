# Project Structure

## Directory Organization

```
aidlc-workflows/
├── aidlc-rules/                    # Core AI-DLC workflow rules
│   ├── aws-aidlc-rules/            # Main workflow definition
│   │   └── core-workflow.md        # Primary workflow orchestration
│   └── aws-aidlc-rule-details/     # Detailed stage implementations
│       ├── common/                 # Shared rules across all phases
│       ├── inception/              # Inception phase stage rules
│       ├── construction/           # Construction phase stage rules
│       └── operations/             # Operations phase rules (placeholder)
├── assets/                         # Documentation assets
│   └── images/                     # Screenshots and diagrams
├── .github/                        # GitHub workflows and templates
├── CHANGELOG.md                    # Version history
├── cliff.toml                      # Changelog generation config
├── CODE_OF_CONDUCT.md              # Community guidelines
├── CONTRIBUTING.md                 # Contribution guidelines
├── LICENSE                         # MIT-0 License
└── README.md                       # Project documentation
```

## Rule Organization

### Core Workflow
`aidlc-rules/aws-aidlc-rules/core-workflow.md` - Main orchestration file that:
- Defines three-phase workflow structure
- Specifies stage execution order and conditions
- Establishes adaptive execution principles
- References detailed stage implementations

### Common Rules
`aidlc-rules/aws-aidlc-rule-details/common/` - Shared guidance:
- `process-overview.md` - Workflow overview
- `terminology.md` - Standard terminology definitions
- `depth-levels.md` - Adaptive depth explanation
- `question-format-guide.md` - Question formatting standards
- `content-validation.md` - Content validation requirements
- `session-continuity.md` - Session resumption guidance
- `ascii-diagram-standards.md` - Diagram formatting rules
- `error-handling.md` - Error handling patterns
- `overconfidence-prevention.md` - Quality assurance
- `welcome-message.md` - Initial user greeting
- `workflow-changes.md` - Workflow modification guidance

### Phase-Specific Rules

**Inception Phase** (`inception/`):
- `workspace-detection.md` - Initial workspace analysis
- `reverse-engineering.md` - Brownfield codebase analysis
- `requirements-analysis.md` - Requirements gathering
- `user-stories.md` - User story generation
- `workflow-planning.md` - Execution plan creation
- `application-design.md` - Component design
- `units-generation.md` - Work unit decomposition

**Construction Phase** (`construction/`):
- `functional-design.md` - Business logic design (per-unit)
- `nfr-requirements.md` - Non-functional requirements (per-unit)
- `nfr-design.md` - NFR pattern incorporation (per-unit)
- `infrastructure-design.md` - Infrastructure mapping (per-unit)
- `code-generation.md` - Code implementation (per-unit)
- `build-and-test.md` - Build and test instructions

**Operations Phase** (`operations/`):
- `operations.md` - Placeholder for future deployment workflows

## File Naming Conventions

- **Kebab-case**: All filenames use lowercase with hyphens (e.g., `requirements-analysis.md`)
- **Descriptive names**: Filenames clearly indicate content purpose
- **Markdown extension**: All rule files use `.md` extension

## Content Structure Patterns

### Rule Detail Files
Each stage rule file follows this structure:
1. **Role assumption** (if applicable)
2. **Stage classification** (ALWAYS/CONDITIONAL/ADAPTIVE)
3. **Prerequisites** - Required prior stages
4. **Execution Steps** - Numbered step-by-step instructions
5. **State Tracking** - aidlc-state.md update format
6. **Completion Message** - User-facing output format

### Common Rules
Common rule files provide:
- **Purpose statement** - What the rule addresses
- **Guidelines** - How to apply the rule
- **Examples** - Concrete usage patterns
- **References** - Links to related rules

## Single Source of Truth

- **Core workflow**: `core-workflow.md` is the authoritative workflow definition
- **No duplication**: Shared guidance lives in `common/` and is referenced
- **Generated files**: Platform-specific files (if any) are generated from source
- **Documentation**: README.md provides user-facing documentation
