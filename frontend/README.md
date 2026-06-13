# FraudShield AI Frontend

Production-ready React + TypeScript + TailwindCSS frontend for APK security analysis.

## Project Structure

```
frontend/
├── src/
│   ├── pages/              # Page components
│   ├── components/         # Reusable UI components
│   ├── api/               # API integration layer
│   ├── hooks/             # Custom React hooks
│   ├── types/             # TypeScript interfaces
│   ├── utils/             # Utility functions
│   ├── layouts/           # Layout components
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
├── tailwind.config.js     # TailwindCSS config
└── postcss.config.js      # PostCSS config
```

## Features

- **Landing Page** - Hero section with features and CTA
- **Upload Page** - Drag-and-drop APK upload with validation
- **Analysis Progress** - Real-time analysis status tracking
- **Security Dashboard** - Comprehensive analysis results with charts
- **Chat Interface** - AI-powered Q&A about APK analysis
- **Responsive Design** - Works on desktop, tablet, mobile
- **Dark Theme** - Cybersecurity-themed dark UI
- **Type Safety** - 100% TypeScript coverage
- **Performance** - Optimized with code splitting and caching

## Quick Start

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Server runs at `http://localhost:5173`

### Build

```bash
npm run build
npm run preview
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Key Components

### Pages
- `LandingPage` - Landing/home page
- `UploadPage` - APK upload interface
- `AnalysisProgressPage` - Real-time analysis tracking
- `SecurityDashboard` - Full analysis results
- `ChatPage` - AI chat interface

### Components
- `Card` - Generic card container
- `RiskScoreCard` - Risk visualization
- `FindingCard` - Security finding display
- `PermissionCard` - Permission explanation
- `URLCard` - URL/domain display
- `ChatWindow` - Chat interface
- `Charts` - Risk distribution visualizations

### Hooks
- `useAnalysis` - Analysis API queries
- `useUpload` - File upload mutations
- `useChat` - Chat API integration

## API Integration

All API calls go through centralized `apiClient` (src/api/client.ts).

Endpoints:
- `POST /api/v1/upload` - Upload APK
- `POST /api/v1/analysis` - Create analysis
- `POST /api/v1/analysis/{id}/run` - Run analysis
- `GET /api/v1/analysis/{id}` - Get analysis status
- `POST /api/v1/chat` - Send chat message

## Styling

- **TailwindCSS** - Utility-first CSS framework
- **Responsive** - Mobile-first design
- **Dark Theme** - Custom cybersecurity theme
- **Animations** - Smooth transitions and loading states

Colors:
- `risk-safe` - Green (#10b981)
- `risk-low` - Blue (#3b82f6)
- `risk-medium` - Yellow (#f59e0b)
- `risk-high` - Orange (#ef5350)
- `risk-critical` - Red (#dc2626)

## State Management

- **React Query** - Server state management
- **React Hooks** - Local state management
- **Automatic Caching** - 5-minute stale time by default

## TypeScript

Full type safety with:
- API response types
- Component prop types
- Custom hook types
- Utility function types

## Performance

- Code splitting by feature
- Lazy loading routes
- Image optimization
- CSS minification
- Gzip compression

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Development

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build
npm run build

# Preview production build
npm run preview
```

## Production Deployment

```bash
npm run build
# Deploy contents of 'dist' folder
```

## Contributing

Follow the project structure and maintain TypeScript types for all new features.

## License

MIT
