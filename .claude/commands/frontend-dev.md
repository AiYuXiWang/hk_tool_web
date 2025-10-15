# Frontend Development Commands

## Overview
This command set provides comprehensive frontend development utilities for Vue.js projects, including development server management, building, testing, code quality, and dependency management.

## Available Commands

### 🚀 Development Commands

#### `/frontend-dev dev`
Start the development server with hot reload
```bash
cd frontend && npm run dev
```
**Aliases**: `start`, `serve`

#### `/frontend-dev build`
Build the application for production
```bash
cd frontend && npm run build
```
**Aliases**: `build:prod`

#### `/frontend-dev preview`
Preview the production build locally
```bash
cd frontend && npm run preview
```

### 🧪 Testing Commands

#### `/frontend-dev test`
Run all frontend tests (unit + integration)
```bash
cd frontend && npm run test
```
**Aliases**: `test:unit`

#### `/frontend-dev test:e2e`
Run end-to-end tests
```bash
cd frontend && npm run test:e2e
```

#### `/frontend-dev test:coverage`
Run tests with coverage report
```bash
cd frontend && npm run test:coverage
```

### 🔍 Code Quality Commands

#### `/frontend-dev lint`
Run ESLint to check code quality
```bash
cd frontend && npm run lint
```

#### `/frontend-dev lint:fix`
Automatically fix linting issues
```bash
cd frontend && npm run lint:fix
```

#### `/frontend-dev format`
Format code using Prettier
```bash
cd frontend && npm run format
```

#### `/frontend-dev type-check`
Run TypeScript type checking
```bash
cd frontend && npm run type-check
```
**Aliases**: `check`

### 📊 Analysis Commands

#### `/frontend-dev analyze`
Analyze bundle size and dependencies
```bash
cd frontend && npm run analyze
```

#### `/frontend-dev profile`
Profile the application for performance bottlenecks
```bash
cd frontend && npm run profile
```

### 🧹 Maintenance Commands

#### `/frontend-dev clean`
Remove all build artifacts and dependencies
```bash
cd frontend && rm -rf node_modules dist .nuxt .output .vite
```

#### `/frontend-dev deps:check`
Check for outdated dependencies
```bash
cd frontend && npm outdated
```

#### `/frontend-dev deps:update`
Update dependencies to latest versions
```bash
cd frontend && npm update
```

#### `/frontend-dev security:audit`
Audit dependencies for security vulnerabilities
```bash
cd frontend && npm audit
```

## Workflows

### 🛠️ Setup Workflow
Run this when setting up the project for the first time:
```bash
/frontend-dev setup
```
**Includes**:
- Install dependencies
- Fix linting issues
- Type checking
- Run tests

### 🚀 Deploy Workflow
Run this before deploying to production:
```bash
/frontend-dev deploy
```
**Includes**:
- Clean artifacts
- Install dependencies
- Lint code
- Type checking
- Run tests
- Build for production

### ✅ Quality Check Workflow
Run this for comprehensive code quality check:
```bash
/frontend-dev quality-check
```
**Includes**:
- Linting
- Type checking
- Testing
- Bundle analysis

## Usage Examples

### Start Development
```
/frontend-dev dev
```
Starts the Vite development server with hot reload at http://localhost:5173

### Fix Code Issues
```
/frontend-dev lint:fix
/frontend-dev format
```
Automatically fixes ESLint issues and formats code with Prettier

### Prepare for Deployment
```
/frontend-dev deploy
```
Runs the complete deployment pipeline to ensure production readiness

### Check Security
```
/frontend-dev security:audit
```
Scans dependencies for known security vulnerabilities

### Update Project
```
/frontend-dev deps:check
/frontend-dev deps:update
/frontend-dev test
```
Check for updates, apply them, and ensure everything still works

## Project Specific Configuration

This command set is optimized for the hk_tool_web project with:

- **Vue 3 + TypeScript** frontend stack
- **Element Plus** UI component library
- **Vite** build tool and development server
- **ESLint + Prettier** code formatting
- **Vitest** unit testing framework
- **Cypress** for E2E testing

## Environment Variables

Make sure these are set in your `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=环控平台维护工具
VITE_APP_VERSION=1.0.0
```

## Common Issues & Solutions

### Port Already in Use
If port 5173 is occupied, Vite will automatically try the next available port.

### TypeScript Errors
Run `/frontend-dev type-check` to identify and fix TypeScript issues.

### Build Failures
1. Run `/frontend-dev clean` to clear artifacts
2. Run `/frontend-dev deps:update` to update dependencies
3. Check `/frontend-dev lint` for code issues

### Test Failures
1. Ensure all dependencies are installed
2. Check test configuration files
3. Run tests individually to identify specific issues

## Tips & Best Practices

1. **Before committing**: Always run `lint:fix` and `format`
2. **Before deploying**: Run the complete `deploy` workflow
3. **Regular maintenance**: Run `deps:check` weekly
4. **Security**: Run `security:audit` regularly
5. **Performance**: Use `analyze` after major changes to monitor bundle size

## Integration with IDE

These commands can be integrated into VS Code tasks or other IDE command palettes for quick access during development.