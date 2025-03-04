# CLAUDE.md - Repository Guidelines

## Build Commands
- Frontend: `cd frontend && npm run dev` - Start development server
- Frontend build: `cd frontend && npm run build` - Build for production
- Frontend typecheck: `cd frontend && npm run check` - Type checking
- Frontend preview: `cd frontend && npm run preview` - Preview production build
- Backend: `cd backend && python main.py` - Run backend server
- Backend with Gunicorn: `cd backend && gunicorn -c gunicorn_config.py main:app` - Production server
- Run single test: `cd backend && python -m unittest tests/test_env.py` - Run specific test
- Full environment test: `cd backend && python tests/test_env.py` - Test environment setup

## Code Style Guidelines
### Frontend (TypeScript/Svelte)
- Use TypeScript with strict typing for all components
- Organize imports alphabetically
- Follow Svelte component structure: `<script>`, markup, `<style>`
- Use camelCase for variables/functions, PascalCase for components
- Prefer async/await over promise chains
- Use Tailwind CSS for styling with @skeletonlabs components

### Backend (Python)
- Use Python 3.10+ features
- Follow PEP 8 conventions for formatting
- Organize imports: standard library, third-party, local modules
- Use type hints for function parameters and return values
- Log errors appropriately with context information
- Use environment variables for configuration (via python-dotenv)
- Include docstrings for functions, classes, and modules

## Error Handling
- Frontend: Use CustomEvent for error propagation
- Backend: Return JSON responses with error details and appropriate HTTP status codes
- Always validate user input both on frontend and backend