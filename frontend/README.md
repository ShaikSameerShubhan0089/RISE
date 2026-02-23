# Autism Risk CDSS - Frontend

React frontend for the Clinical Decision Support System with role-based dashboards.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Create `.env` file (optional):

```env
VITE_API_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend will start on http://localhost:3000

## Features

### Authentication
- JWT-based authentication
- Automatic token refresh
- Protected routes with role validation

### Role-Based Dashboards

**6 Different User Roles:**

1. **System Admin** - Full system access
2. **State Admin** - State-level management  
3. **District Officer** - District operations
4. **Supervisor** - Mandal-level oversight
5. **Anganwadi Worker** - Center-level child care
6. **Parent** - View own children only

### Current Implementation

✅ Login page with test credentials
✅ Role-based navigation sidebar
✅ Protected route system
✅ Anganwadi Worker dashboard with:
   - Stats cards (children, assessments, high risk)
   - Recent children list
   - Recent assessments
   - Quick action buttons

### Coming Soon

- Children management (registration, profiles)
- Assessment submission forms
- Risk prediction visualization with SHAP
- Referral management interface
- Intervention tracking
- Analytics dashboards
- Parent portal

## Project Structure

```
src/
├── components/
│   ├── Layout.jsx           # Main layout with sidebar
│   ├── Sidebar.jsx          # Role-based navigation
│   └── ProtectedRoute.jsx   # Auth guard
├── pages/
│   ├── Login.jsx            # Login page
│   └── dashboards/
│       ├── Dashboard.jsx    # Role router
│       └── AnganwadiWorkerDashboard.jsx
├── context/
│   └── AuthContext.jsx      # Auth state management
├── utils/
│   └── api.js              # Axios API client
├── App.jsx                 # Main app with routing
└── main.jsx               # Entry point
```

## Technology Stack

- **React 18** - UI library
- **Vite** - Build tool & dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Chart.js** - Data visualization (ready to use)
- **Lucide React** - Icons

## Test Login Credentials

From seed data (backend must be running):

| Email | Password | Role |
|-------|----------|------|
| admin@cdss.gov.in | admin123 | system_admin |
| worker@awc001.gov.in | worker123 | anganwadi_worker |
| parent1@example.com | parent123 | parent |

## API Integration

All API calls are centralized in `src/utils/api.js`:

```javascript
import { childrenAPI, assessmentsAPI, predictionsAPI } from './utils/api';

// Example usage
const children = await childrenAPI.list();
const prediction = await predictionsAPI.generate(assessmentId);
```

## Development

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Next Steps

1. Build children management UI
2. Create assessment forms with validation
3. Implement risk prediction visualization
4. Add SHAP feature importance charts
5. Build referral workflow UI
6. Create intervention tracking interface
7. Develop analytics dashboards for each role
