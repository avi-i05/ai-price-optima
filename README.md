# AI PriceOptima - Dynamic Pricing System

A full-stack application implementing AI-powered dynamic pricing to maximize revenue and maintain competitiveness.

## Architecture

- **Backend**: Python FastAPI with ML-based pricing optimization
- **Frontend**: React with modern UI using Tailwind CSS
- **Features**: Real-time price optimization, analytics dashboard, product management

## Project Structure

```
AI-PriceOptima-feature-riya-gupta/
├── backend/                 # FastAPI backend
│   ├── main.py            # Main FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.js        # Main App component
│   │   ├── index.js      # Entry point
│   │   └── index.css     # Global styles
│   ├── package.json      # Node.js dependencies
│   └── tailwind.config.js # Tailwind configuration
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Products
- `GET /api/products` - Get all products
- `GET /api/products/{id}` - Get specific product

### Pricing
- `POST /api/pricing/optimize` - Get optimized pricing for a product

### Analytics
- `GET /api/analytics/dashboard` - Get dashboard analytics

## Features

### Dashboard
- Overview of key metrics
- Price optimization insights
- Quick action buttons

### Product Management
- View product catalog
- Real-time price optimization
- Price history tracking

### Pricing Optimizer
- AI-powered price recommendations
- Adjustable parameters (demand, inventory, competition)
- Confidence scoring and reasoning

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **scikit-learn**: Machine learning library for price optimization
- **pandas**: Data manipulation and analysis
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React**: JavaScript library for building user interfaces
- **React Router**: Declarative routing for React
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: Promise-based HTTP client
- **Lucide React**: Beautiful & consistent icon toolkit
- **Recharts**: Composable charting library

## Development

### Running Both Services

For development, you'll need to run both the backend and frontend simultaneously:

1. Terminal 1 (Backend):
```bash
cd backend
python main.py
```

2. Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

### Environment Variables

The application is configured to work with:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

CORS is configured to allow requests from the frontend to the backend.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
