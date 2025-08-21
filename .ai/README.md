# AI Context Directory

This directory contains modular context files designed to provide comprehensive project understanding for AI coding assistants.

## Modern AI Context Approach

This structure follows modern best practices for AI context establishment:

1. **Modular Context Files** - Each file focuses on a specific domain
2. **Retrieval-Augmented Generation (RAG)** - Structured information for better AI responses
3. **Context Window Management** - Focused files prevent token limit issues
4. **Reusable Components** - Version-controlled, maintainable context

## File Structure

| File | Purpose | When to Reference |
|------|---------|-------------------|
| `context.md` | Project overview and index | Always (project orientation) |
| `architecture.md` | Technical architecture | System design, tech stack questions |
| `guidelines.md` | Development standards | Code quality, best practices |
| `project-structure.md` | File organization | Navigation, file structure |
| `workflows.md` | Development processes | Git, testing, deployment |
| `features.md` | Feature specifications | Requirements, functionality |
| `security.md` | Security practices | Authentication, data protection |
| `performance.md` | Optimization strategies | Performance issues, scaling |

## Usage in AI Tools

### Cursor IDE
- Use `@.ai/` to reference the entire context directory
- Use `@.ai/filename.md` for specific context files
- The `.cursorrules` file automatically references this structure

### Other AI Tools
- Include relevant context files in your prompts
- Start with `context.md` for project overview
- Add specific files based on the task at hand

## Maintenance

- Update context files when project structure changes
- Keep documentation synchronized with actual implementation
- Review and update quarterly or when major changes occur

## Benefits

1. **Reduced Token Usage** - Only include relevant context
2. **Better AI Understanding** - Structured, focused information
3. **Consistent Responses** - Standardized project knowledge
4. **Easier Maintenance** - Modular, version-controlled context
5. **Team Collaboration** - Shared understanding of project standards