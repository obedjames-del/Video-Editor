# CLAUDE.MD - Video Editor Project

## Project Overview

This is a Video Editor application designed to provide video editing capabilities. The project is in its early stages of development.

## Project Purpose

The Video Editor aims to provide:
- Video playback and preview
- Video trimming and cutting
- Video effects and filters
- Timeline-based editing interface
- Export capabilities in various formats

## Project Structure

```
Video-Editor/
├── README.md           # Project documentation
└── CLAUDE.MD          # This file - Claude Code context
```

## Technology Stack

To be determined based on implementation choices:
- Frontend: (e.g., React, Vue, or vanilla JavaScript)
- Video Processing: (e.g., FFmpeg, Web APIs)
- Build Tools: (e.g., Webpack, Vite, or Parcel)
- Testing: (e.g., Jest, Vitest, Playwright)

## Development Guidelines

### Code Style
- Use consistent indentation (2 or 4 spaces)
- Follow language-specific best practices
- Write clear, self-documenting code
- Add comments only when logic isn't self-evident
- Use meaningful variable and function names

### Git Workflow
- Work on feature branches with descriptive names
- Write clear, concise commit messages
- Keep commits atomic and focused
- Test before committing

### Testing
- Write unit tests for core functionality
- Test video processing edge cases
- Ensure cross-browser compatibility
- Test with various video formats and sizes

## Common Tasks

### Setup Development Environment
```bash
# Install dependencies (once package.json is created)
npm install
# or
yarn install
```

### Running the Application
```bash
# Start development server
npm run dev
# or
yarn dev
```

### Building for Production
```bash
# Create production build
npm run build
# or
yarn build
```

### Running Tests
```bash
# Run test suite
npm test
# or
yarn test
```

## Key Features to Implement

1. **Video Upload & Preview**
   - Support multiple video formats (MP4, WebM, AVI, MOV)
   - Generate thumbnails
   - Display video metadata

2. **Timeline Editor**
   - Drag-and-drop interface
   - Multiple video tracks
   - Audio tracks
   - Precise frame-by-frame control

3. **Editing Tools**
   - Cut, trim, and split clips
   - Transitions between clips
   - Speed adjustment (slow-mo, time-lapse)
   - Text overlays and titles

4. **Effects & Filters**
   - Color correction
   - Filters (brightness, contrast, saturation)
   - Visual effects
   - Audio effects

5. **Export Options**
   - Multiple format support
   - Quality/resolution settings
   - Compression options
   - Progress tracking

## Performance Considerations

- Handle large video files efficiently
- Implement lazy loading for video previews
- Use Web Workers for heavy processing
- Optimize memory usage
- Consider streaming for large files

## Browser Compatibility

- Target modern browsers with Media Source Extensions support
- Test on Chrome, Firefox, Safari, and Edge
- Consider fallbacks for older browsers

## Security Considerations

- Validate uploaded file types
- Implement file size limits
- Sanitize user inputs
- Handle errors gracefully
- Don't expose sensitive paths or system information

## Future Enhancements

- Real-time collaboration
- Cloud storage integration
- AI-powered editing suggestions
- Mobile responsive design
- Keyboard shortcuts for power users
- Plugin/extension system

## Notes for Claude Code

- This project is in early development stages
- Architecture and technology decisions are flexible
- Focus on creating a solid foundation
- Prioritize core functionality before advanced features
- Keep the codebase maintainable and well-documented

## Resources

- FFmpeg Documentation: https://ffmpeg.org/documentation.html
- Web Video Standards: https://developer.mozilla.org/en-US/docs/Web/Media
- HTML5 Video: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video
- Canvas API: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

---

Last Updated: 2026-02-05
Project Status: Initial Setup
