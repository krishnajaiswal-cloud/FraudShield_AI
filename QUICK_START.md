# FraudShield AI - Frontend Quick Start Guide

## 🚀 30-Second Quick Start

### Prerequisites
- Node.js 16+ installed
- Backend running on `http://localhost:8000`

### Installation & Run
```bash
cd frontend
npm install
npm run dev
```

**Done!** Frontend runs at `http://localhost:5173`

---

## 📋 Complete Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Configure Environment
Create `.env` file in `frontend/` directory:
```
VITE_API_URL=http://localhost:8000
```

### Step 3: Start Development Server
```bash
npm run dev
```

### Step 4: Open Browser
Navigate to: `http://localhost:5173`

---

## 🎯 Available Commands

```bash
# Start development server (hot reload enabled)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Type check (optional)
npm run type-check

# Lint code (optional)
npm run lint
```

---

## 📍 Page URLs

Once running, access these pages:

| Page | URL | Description |
|------|-----|-------------|
| Landing | `http://localhost:5173/` | Home page with features |
| Upload | `http://localhost:5173/scan` | APK upload interface |
| Analysis | `http://localhost:5173/analysis/{id}` | Progress tracking |
| Dashboard | `http://localhost:5173/dashboard/{id}` | Results & analysis |
| Chat | `http://localhost:5173/chat/{id}` | AI chat interface |

---

## 🔧 Project Structure Highlights

```
src/
├── pages/         → Page components (5 files)
├── components/    → Reusable UI components (10+ files)
├── api/           → API integration (4 files)
├── hooks/         → Custom React hooks (3 files)
├── types/         → TypeScript definitions (1 file)
├── utils/         → Helper functions (1 file)
├── layouts/       → Layout wrappers (3 files)
├── App.tsx        → Main router
├── main.tsx       → Entry point
└── index.css      → Global styles
```

---

## 🌐 API Integration

### API Endpoints Used

The frontend connects to these backend endpoints:

```
POST   /api/v1/upload              Upload APK file
POST   /api/v1/analysis            Create analysis
POST   /api/v1/analysis/{id}/run   Start analysis
GET    /api/v1/analysis/{id}       Get analysis status
POST   /api/v1/chat                Send chat message
```

### API Configuration

The API base URL is set in `.env`:
```
VITE_API_URL=http://localhost:8000
```

All API calls automatically use this URL via `src/api/client.ts`

---

## 🎨 Key Features

### 1. **Upload & Analysis**
- Drag-and-drop APK upload
- Real-time progress tracking
- Auto-redirect to results

### 2. **Security Dashboard**
- Risk score visualization
- Interactive charts
- Permission analysis
- URL extraction
- Filterable findings

### 3. **AI Chat**
- ChatGPT-style interface
- Question-answering about APK
- Real-time responses

### 4. **Responsive Design**
- Mobile, tablet, desktop
- Touch-friendly on mobile
- Responsive navigation

### 5. **Type Safety**
- 100% TypeScript
- Full API type definitions
- Component prop types

---

## 🎯 Component Overview

### Pages (5 components)
- `LandingPage` - Home page
- `UploadPage` - APK upload
- `AnalysisProgressPage` - Progress tracking
- `SecurityDashboard` - Main results page
- `ChatPage` - AI chat

### UI Components (15+ reusable)
- `Card` - Generic card container
- `Badge` - Severity badges
- `LoadingSpinner` - Loading indicator
- `RiskScoreCard` - Risk visualization
- `FindingCard` - Finding display
- `PermissionCard` - Permission info
- `ChatWindow` - Chat interface
- And more...

### Hooks (3 custom)
- `useAnalysis` - Analysis queries
- `useUpload` - File upload
- `useChat` - Chat functionality

---

## 🎨 Styling System

### Colors
```
Safe:     #10b981 (green)
Low:      #3b82f6 (blue)
Medium:   #f59e0b (yellow)
High:     #ef5350 (orange)
Critical: #dc2626 (red)
```

### Dark Theme
- Background: `#0f1419`
- Cards: `#1a1f2e`
- Borders: `#2a3142`

---

## 🔍 Debugging

### Browser DevTools
- Open: `F12` or right-click → Inspect
- Console: See errors and logs
- Network: Monitor API calls

### Frontend Logs
```bash
# Clear browser cache
⌘ + ⇧ + Delete  (macOS)
Ctrl + Shift + Delete (Windows)
```

### Check Backend Connection
Visit `http://localhost:8000/docs` to verify backend is running

---

## 📦 Dependencies (Key)

```json
{
  "react": "18.2.0",
  "react-router-dom": "6.15.0",
  "@tanstack/react-query": "5.0.0",
  "axios": "1.5.0",
  "tailwindcss": "3.3.0",
  "recharts": "2.10.0",
  "lucide-react": "0.292.0"
}
```

---

## 🚨 Troubleshooting

### Issue: Port 5173 already in use
**Solution:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9  # macOS/Linux
# or specify different port:
npm run dev -- --port 3000
```

### Issue: API connection errors
**Solution:**
1. Check backend is running: `http://localhost:8000/docs`
2. Verify `.env` has correct `VITE_API_URL`
3. Check browser console for CORS errors

### Issue: Blank page
**Solution:**
1. Hard refresh: `Ctrl+Shift+R` (Windows) or `⌘+⇧+R` (macOS)
2. Clear cache and reload
3. Check browser console for JavaScript errors

### Issue: Node modules errors
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 🎬 Typical Workflow

1. **Start** → `npm run dev` → Frontend opens at port 5173
2. **Upload** → Go to `/scan` → Upload APK
3. **Progress** → Auto-redirects to `/analysis/{id}` → Wait for completion
4. **Results** → Auto-redirects to `/dashboard/{id}` → View full report
5. **Chat** → Click "Chat with AI" → Ask questions
6. **Done** → View, export, or analyze another APK

---

## 📊 File Sizes (Approximate)

After `npm run build`:
```
dist/
├── index.html               ~2 KB
├── assets/
│   ├── index-xxx.js        ~150 KB (gzipped ~50 KB)
│   ├── vendor-xxx.js       ~200 KB (gzipped ~70 KB)
│   └── index-xxx.css       ~50 KB (gzipped ~10 KB)
```

---

## 🌍 Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | Latest | ✅ Full |
| Firefox | Latest | ✅ Full |
| Safari | Latest | ✅ Full |
| Edge | Latest | ✅ Full |
| Mobile | iOS 13+ / Android 8+ | ✅ Full |

---

## 🔐 Security Notes

1. **API URL** - Keep `.env` with correct backend URL
2. **File Upload** - Backend validates APK files
3. **Sensitive Data** - Uses HTTPS in production
4. **CORS** - Backend should configure CORS properly

---

## 📈 Performance Tips

### Development
- Hot Module Replacement (HMR) enabled
- Fast refresh on file changes
- CSS not duplicated

### Production Build
```bash
npm run build
```

Build optimizations:
- Code splitting by feature
- Tree shaking unused code
- Minification and compression
- CSS purging

---

## 🆘 Getting Help

### Check These Resources
1. **Browser Console** - `F12` → Console tab
2. **Network Tab** - Check API requests
3. **README.md** - In frontend folder
4. **SETUP_GUIDE.md** - Complete setup
5. **Backend Docs** - `http://localhost:8000/docs`

### Common Issues
```bash
# Issue: npm install fails
# Solution: Update npm
npm install -g npm@latest

# Issue: Port already in use
# Solution: Use different port
npm run dev -- --port 3001

# Issue: Slow development
# Solution: Check browser DevTools
# Disable extensions that might interfere
```

---

## 📝 Development Workflow Example

### Starting Development
```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Making Changes
1. Edit React component in `src/`
2. Save file → HMR automatically refreshes
3. Check browser for changes

### Building for Production
```bash
npm run build
# Output: dist/ folder ready for deployment
```

---

## 🎉 Next Steps

1. ✅ Run `npm run dev`
2. ✅ Open `http://localhost:5173` in browser
3. ✅ Click "Analyze APK"
4. ✅ Upload a test APK
5. ✅ View results in dashboard
6. ✅ Chat with AI about the analysis

**Enjoy FraudShield AI!** 🛡️

---

## 📞 Support

For issues or questions:
1. Check browser console for errors
2. Verify backend is running
3. Check `.env` configuration
4. Review SETUP_GUIDE.md for detailed info
5. Check API docs at `http://localhost:8000/docs`

---

**Frontend Ready!** 🚀
