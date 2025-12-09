<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0 (MINOR: Added new principles for UI design and PowerShell commands)
Modified principles: None (all new principles added)
Added sections: User Interface Design, PowerShell Command Standards
Removed sections: None
Templates requiring updates: 
- ✅ plan-template.md (updated to reflect UI design requirements)
- ✅ spec-template.md (updated to reflect UI design requirements) 
- ✅ tasks-template.md (updated to remove test requirements)
Follow-up TODOs: None
-->

# agendamento_max Constitution

## Core Principles

### I. User-Centric Interface Design
All interfaces must be designed for users with an average age of 50 years. Components must be large, clear, and intuitive. Text must be readable with appropriate contrast and sizing. Navigation flows must be simple and predictable with minimal cognitive load. User feedback must be immediate and clear for all actions.

### II. PowerShell-First Development
All automation scripts and commands must follow Windows PowerShell standards. Scripts must use PowerShell naming conventions, proper error handling, and structured output. Command-line interfaces must support both interactive and programmatic use. All operations must be executable through PowerShell scripts.

### III. No Automated Testing
No automated tests shall be implemented in the project. Quality assurance must be performed through manual testing and code review. All functionality must be verified through user acceptance testing rather than automated test suites.

### IV. Accessibility Compliance
All interfaces must comply with accessibility standards suitable for users aged 50 and above. This includes high contrast modes, scalable fonts, keyboard navigation, and screen reader compatibility. Color choices must account for age-related vision changes.

### V. Simplicity and Clarity
All functionality must be implemented with maximum simplicity. Features must be self-evident and require minimal training. Error messages must be clear, actionable, and written in plain language. Complex workflows must be broken into simple, sequential steps.

## Development Standards

### User Interface Requirements
- Minimum font size: 14px for body text, 18px for headers
- Minimum clickable target size: 44×44 pixels
- High contrast color schemes with minimum 4.5:1 contrast ratio
- Clear visual hierarchy with consistent spacing
- Progressive disclosure of information to avoid overwhelming users
- Confirmation dialogs for destructive actions
- Undo functionality where technically feasible

### PowerShell Command Requirements
- All scripts must use .ps1 extension and proper PowerShell headers
- Commands must support standard PowerShell parameters (-Verbose, -WhatIf, -Confirm)
- Output must be structured (objects when possible, formatted tables otherwise)
- Error handling must use PowerShell try/catch blocks with meaningful error messages
- Scripts must include comment-based help following PowerShell standards
- All external dependencies must be checked and installed via PowerShell Gallery when possible

## Quality Assurance

### Manual Testing Protocol
- All features must be tested manually by developers before submission
- User acceptance testing must be performed with actual target users
- Accessibility testing must be performed with accessibility tools
- Cross-browser compatibility testing for web interfaces
- PowerShell scripts must be tested in different Windows environments

### Code Review Requirements
- All code changes must undergo peer review
- Review must focus on user interface clarity and intuitiveness
- PowerShell scripts must be reviewed for standards compliance
- Accessibility compliance must be verified during review
- Documentation must be clear and complete

## Governance

This constitution supersedes all other development practices. Amendments require documentation, approval, and a migration plan. All pull requests and reviews must verify compliance with these principles. Any complexity must be justified with a clear user benefit. Use this constitution as the primary guidance for all development decisions.

**Version**: 1.1.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
