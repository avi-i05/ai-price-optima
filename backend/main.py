from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

app = FastAPI(title="AI PriceOptima API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Product(BaseModel):
    id: int
    name: str
    current_price: float
    inventory: int
    sales_history: List[float]
    competitor_price: Optional[float] = None

class CustomProduct(BaseModel):
    name: str
    category: str

class PricingRequest(BaseModel):
    product_id: Optional[int] = None
    custom_product: Optional[CustomProduct] = None
    current_price: float
    inventory: int
    demand_factor: float
    competitor_price: Optional[float] = None
    season: Optional[str] = "Summer"
    weather: Optional[str] = "Sunny"
    holiday: Optional[bool] = False
    discount: Optional[int] = 10
    visitors: Optional[int] = 50

class PricingResponse(BaseModel):
    optimal_price: float
    confidence_score: float
    price_change_percentage: float
    reasoning: str

# Sample data - expanded to match dataset categories
products = [
    Product(
        id=1,
        name="Laptop",
        current_price=999.99,
        inventory=50,
        sales_history=[899.99, 949.99, 999.99, 979.99, 999.99],
        competitor_price=959.99
    ),
    Product(
        id=2,
        name="Smartphone",
        current_price=699.99,
        inventory=120,
        sales_history=[649.99, 679.99, 699.99, 689.99, 699.99],
        competitor_price=679.99
    ),
    Product(
        id=3,
        name="Office Chair",
        current_price=249.99,
        inventory=85,
        sales_history=[229.99, 239.99, 249.99, 259.99, 249.99],
        competitor_price=239.99
    ),
    Product(
        id=4,
        name="Desk Lamp",
        current_price=79.99,
        inventory=200,
        sales_history=[69.99, 74.99, 79.99, 84.99, 79.99],
        competitor_price=74.99
    ),
    Product(
        id=5,
        name="Winter Jacket",
        current_price=189.99,
        inventory=65,
        sales_history=[169.99, 179.99, 189.99, 199.99, 189.99],
        competitor_price=179.99
    ),
    Product(
        id=6,
        name="Running Shoes",
        current_price=129.99,
        inventory=150,
        sales_history=[119.99, 124.99, 129.99, 134.99, 129.99],
        competitor_price=125.99
    ),
    Product(
        id=7,
        name="Board Game",
        current_price=39.99,
        inventory=300,
        sales_history=[34.99, 37.99, 39.99, 41.99, 39.99],
        competitor_price=36.99
    ),
    Product(
        id=8,
        name="LEGO Set",
        current_price=89.99,
        inventory=95,
        sales_history=[79.99, 84.99, 89.99, 94.99, 89.99],
        competitor_price=85.99
    ),
    Product(
        id=9,
        name="Organic Apples",
        current_price=4.99,
        inventory=500,
        sales_history=[4.49, 4.79, 4.99, 5.19, 4.99],
        competitor_price=4.79
    ),
    Product(
        id=10,
        name="Whole Milk",
        current_price=3.49,
        inventory=400,
        sales_history=[3.29, 3.39, 3.49, 3.59, 3.49],
        competitor_price=3.39
    ),
    Product(
        id=11,
        name="Tablet",
        current_price=449.99,
        inventory=75,
        sales_history=[419.99, 434.99, 449.99, 464.99, 449.99],
        competitor_price=429.99
    ),
    Product(
        id=12,
        name="Wireless Headphones",
        current_price=159.99,
        inventory=110,
        sales_history=[149.99, 154.99, 159.99, 164.99, 159.99],
        competitor_price=149.99
    )
]

@app.get("/")
async def root():
    return {"message": "AI PriceOptima API is running"}

@app.get("/api/products", response_model=List[Product])
async def get_products():
    return products

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Load the trained model
model = None
scaler = None

try:
    # Load the trained model
    model = joblib.load("model.pkl")
    print("Trained model loaded successfully")
    
    # Try to load scaler if it exists, otherwise create a simple one
    try:
        scaler = joblib.load("scaler.pkl")
        print("Scaler loaded successfully")
    except FileNotFoundError:
        # Create a simple scaler for basic normalization
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        # Fit with some sample data (this is just for initialization)
        sample_data = np.array([[100, 50, 0.5, 95], [200, 100, 0.7, 180], [50, 25, 0.3, 48]])
        scaler.fit(sample_data)
        print("Created default scaler")
        
except FileNotFoundError:
    print("Model file not found, using fallback optimization logic")
    model = None
    scaler = None

@app.post("/api/pricing/optimize", response_model=PricingResponse)
async def optimize_pricing(request: PricingRequest):
    print("=== PRICING REQUEST RECEIVED ===")
    print(f"Request data: {request}")
    print(f"Product ID: {request.product_id}")
    print(f"Custom Product: {request.custom_product}")
    print(f"Current Price: {request.current_price}")
    print(f"Inventory: {request.inventory}")
    print(f"Demand Factor: {request.demand_factor}")
    print(f"Competitor Price: {request.competitor_price}")
    print(f"Season: {request.season}")
    print(f"Weather: {request.weather}")
    print(f"Holiday: {request.holiday}")
    print(f"Discount: {request.discount}")
    print(f"Visitors: {request.visitors}")
    print("================================\n")
    
    # Validate that either product_id or custom_product is provided
    if not request.product_id and not request.custom_product:
        raise HTTPException(status_code=422, detail="Either product_id or custom_product must be provided")
    
    base_price = request.current_price
    
    if model:
        # Use trained model for prediction
        try:
            # Prepare features for the model based on your dataset structure
            if request.custom_product:
                print(f"Preparing features for custom product: {request.custom_product.name}")
            else:
                print(f"Preparing features for product_id: {request.product_id}")
            
            features = prepare_features(request, base_price)
            print(f"Features prepared: {len(features)} features")
            print("=== FEATURE DATA SENT TO MODEL ===")
            print(f"Raw features array: {features}")
            print(f"Features shape: {features.shape}")
            print(f"Features dtype: {features.dtype}")
            
            # Display features by category
            print("\n--- FEATURE BREAKDOWN ---")
            print(f"Core Business Metrics (7): {features[:7]}")
            print(f"Time Features (4): {features[7:11]}")
            print(f"Store Encodings (4): {features[11:15]}")
            print(f"Category Encodings (5): {features[15:20]}")
            print(f"Region Encodings (4): {features[20:24]}")
            print(f"Weather Encodings (4): {features[24:28]}")
            print(f"Season Encodings (4): {features[28:32]}")
            print(f"Holiday Flag (1): {features[32:33]}")
            print(f"Derived Ratios (3): {features[33:36]}")
            print("===============================\n")
            
            # Reshape for single prediction
            features = features.reshape(1, -1)
            print(f"Reshaped for prediction: {features.shape}")
            
            # Predict optimal price
            print("Making prediction with XGBoost model...")
            optimal_price = model.predict(features)[0]
            print(f"Model raw prediction: {optimal_price}")
            print(f"Model prediction type: {type(optimal_price)}")
            
            # Ensure price is reasonable and positive
            # First, ensure positive price
            if optimal_price <= 0:
                optimal_price = base_price * 0.9  # Default to 10% discount if negative
                print(f"Negative prediction detected, using fallback: {optimal_price}")
            
            # Then, ensure reasonable change limits
            max_change = 0.3  # Maximum 30% change
            if optimal_price > base_price * (1 + max_change):
                optimal_price = base_price * (1 + max_change)
                print(f"Price capped at maximum increase: {optimal_price}")
            elif optimal_price < base_price * (1 - max_change):
                optimal_price = base_price * (1 - max_change)
                print(f"Price capped at maximum decrease: {optimal_price}")
            
            # Dynamic confidence score based on prediction characteristics
            price_change = abs(optimal_price - base_price) / base_price
            
            # Higher confidence for smaller price changes, lower for dramatic changes
            if price_change < 0.05:  # Less than 5% change
                confidence_score = 0.95
            elif price_change < 0.10:  # Less than 10% change
                confidence_score = 0.90
            elif price_change < 0.20:  # Less than 20% change
                confidence_score = 0.80
            else:  # More than 20% change
                confidence_score = 0.70
            
            # Adjust confidence based on inventory levels
            if request.inventory < 10 or request.inventory > 200:
                confidence_score -= 0.05  # Lower confidence for extreme inventory
            
            # Adjust confidence based on demand factor
            if 0.3 <= request.demand_factor <= 0.7:  # Normal demand range
                confidence_score += 0.02
            elif request.demand_factor < 0.1 or request.demand_factor > 0.9:  # Extreme demand
                confidence_score -= 0.08
            
            # Ensure confidence stays within reasonable bounds
            confidence_score = max(0.50, min(0.98, confidence_score))
            
            reasoning = f"ML model prediction based on historical data patterns (price change: {price_change*100:.1f}%)"
            
        except Exception as e:
            print(f"Model prediction failed: {e}")
            # Fallback to simple logic
            optimal_price, confidence_score, reasoning = fallback_optimization(request)
    else:
        # Fallback optimization logic
        optimal_price, confidence_score, reasoning = fallback_optimization(request)
    
    price_change_percentage = ((optimal_price - base_price) / base_price) * 100
    
    return PricingResponse(
        optimal_price=round(optimal_price, 2),
        confidence_score=round(confidence_score, 2),
        price_change_percentage=round(price_change_percentage, 2),
        reasoning=reasoning
    )

def prepare_features(request: PricingRequest, base_price: float):
    """
    Prepare features for XGBoost model with clear, flexible logic for any product type.
    
    LOGIC BREAKDOWN:
    1. Core Business Metrics (7 features)
    2. Time Features (4 features) 
    3. Market Context (15 features - encodings)
    4. Derived Ratios (3 features)
    5. Buffer Features (7 features) - ensure 36 total
    """
    import datetime
    import math
    
    # Get current date/time for dynamic features
    now = datetime.datetime.now()
    
    # ===== CORE BUSINESS METRICS (7 features) =====
    core_features = [
        request.inventory,                    # 0: Current inventory level
        request.demand_factor * 100,        # 1: Demand forecast (0-100 scale)
        base_price,                         # 2: Current price
        request.discount or 10,               # 3: Discount percentage (from form)
        request.competitor_price or base_price,  # 4: Competitor price
        request.visitors or 50,               # 5: Estimated visitors (from form)
        base_price * 0.7,                  # 6: Estimated cost (70% of price)
    ]
    
    # ===== TIME FEATURES (4 features) =====
    time_features = [
        now.day,                             # 7: Day of month (1-31)
        now.month,                           # 8: Month (1-12)
        now.weekday(),                       # 9: Day of week (0=Monday, 6=Sunday)
        now.hour,                            # 10: Hour of day (0-23)
    ]
    
    # ===== MARKET CONTEXT - ENCODINGS (15 features) =====
    # Store encodings (4 features) - default to average store
    store_encodings = [0.25, 0.25, 0.25, 0.25]  # Equal weights for S001-S004
    
    # Category encodings (5 features) - based on actual category
    category_map = {
        'Groceries': [1,0,0,0,0], 
        'Toys': [0,1,0,0,0], 
        'Furniture': [0,0,1,0,0], 
        'Clothing': [0,0,0,1,0], 
        'Electronics': [0,0,0,0,1]
    }
    
    # Get category from custom product or use default
    if request.custom_product:
        category_encodings = category_map.get(request.custom_product.category, [0,0,0,0,1])
    else:
        category_encodings = category_map.get('Electronics', [0,0,0,0,1])  # Default to Electronics
    
    # Region encodings (4 features) - default to balanced regions
    region_encodings = [0.25, 0.25, 0.25, 0.25]  # Equal for North,South,East,West
    
    # Weather encodings (4 features) - based on actual weather selection
    weather_map = {'Sunny': [1,0,0,0], 'Cloudy': [0,1,0,0], 'Rainy': [0,0,1,0], 'Snowy': [0,0,0,1]}
    weather_encodings = weather_map.get(request.weather or 'Sunny', [1,0,0,0])
    
    # Season encodings (4 features) - based on actual season selection
    season_map = {'Spring': [1,0,0,0], 'Summer': [0,1,0,0], 'Autumn': [0,0,1,0], 'Winter': [0,0,0,1]}
    season_encodings = season_map.get(request.season or 'Summer', [0,1,0,0])
    
    # Holiday flag (1 feature) - based on actual holiday selection
    holiday_encoding = [1.0 if request.holiday else 0.0]
    
    # ===== DERIVED BUSINESS RATIOS (3 features) =====
    derived_features = [
        # 11: Inventory-to-Demand Ratio (how much inventory per unit demand)
        request.inventory / max(1, request.demand_factor * 100),
        
        # 12: Price Competitiveness (how our price compares to competitor)
        (request.competitor_price or base_price) / max(1, base_price),
        
        # 13: Inventory Value Density (price value per inventory unit)
        base_price / max(1, request.inventory),
    ]
    
    # ===== BUFFER FEATURES (7 features) =====
    # These ensure we have exactly 36 features and provide flexibility
    buffer_features = [
        1.0,    # 14: Scaling factor
        0.0,    # 15: Promotion flag (0=no, 1=yes)
        0.5,    # 16: Market volatility (0-1, default medium)
        1.0,    # 17: Quality factor (default premium)
        0.0,    # 18: Seasonal adjustment
        0.0,    # 19: Economic indicator
        0.0,    # 20: Future placeholder
    ]
    
    # ===== COMBINE ALL FEATURES =====
    all_features = (
        core_features + 
        time_features + 
        store_encodings + 
        category_encodings + 
        region_encodings + 
        weather_encodings + 
        season_encodings + 
        holiday_encoding + 
        derived_features + 
        buffer_features
    )
    
    # Ensure exactly 36 features (trim or pad as needed)
    if len(all_features) > 36:
        all_features = all_features[:36]
    elif len(all_features) < 36:
        all_features.extend([0.0] * (36 - len(all_features)))
    
    # Convert to numpy array with proper data types
    features_array = np.array(all_features, dtype=np.float32)
    
    return features_array

def fallback_optimization(request: PricingRequest):
    """Fallback optimization logic when model is not available"""
    base_price = request.current_price
    demand_multiplier = 1.0 + (request.demand_factor - 0.5) * 0.3
    
    # Inventory adjustment
    if request.inventory < 20:
        inventory_multiplier = 1.1  # Low inventory, increase price
    elif request.inventory > 100:
        inventory_multiplier = 0.95  # High inventory, decrease price
    else:
        inventory_multiplier = 1.0
    
    # Competitor price consideration
    if request.competitor_price:
        if request.competitor_price < base_price * 0.9:
            competitor_multiplier = 0.95
        elif request.competitor_price > base_price * 1.1:
            competitor_multiplier = 1.05
        else:
            competitor_multiplier = 1.0
    else:
        competitor_multiplier = 1.0
    
    # Calculate optimal price
    optimal_price = base_price * demand_multiplier * inventory_multiplier * competitor_multiplier
    
    # Confidence score based on data quality
    confidence_score = min(0.95, 0.7 + (len(products) * 0.05))
    
    # Reasoning
    reasoning_parts = []
    if demand_multiplier != 1.0:
        reasoning_parts.append(f"Demand factor: {demand_multiplier:.2f}x")
    if inventory_multiplier != 1.0:
        reasoning_parts.append(f"Inventory adjustment: {inventory_multiplier:.2f}x")
    if competitor_multiplier != 1.0:
        reasoning_parts.append(f"Competitor price consideration: {competitor_multiplier:.2f}x")
    
    reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No significant factors"
    
    return optimal_price, confidence_score, reasoning

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    # Calculate real metrics from products
    total_products = len(products)
    total_inventory = sum(p.inventory for p in products)
    average_price = sum(p.current_price for p in products) / len(products)
    
    # Calculate competitor price gap
    competitor_prices = [p.competitor_price for p in products if p.competitor_price]
    avg_competitor_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else average_price
    price_gap = ((average_price - avg_competitor_price) / avg_competitor_price) * 100
    
    # Simulate optimization based on current inventory levels
    # Low inventory = higher optimization potential
    avg_inventory = total_inventory / total_products
    optimization_savings = max(5, min(25, (100 - avg_inventory) / 4))
    
    # Revenue impact based on price optimization
    revenue_impact = optimization_savings * 0.65  # Conservative estimate
    
    return {
        "total_products": total_products,
        "total_inventory": total_inventory,
        "average_price": round(average_price, 2),
        "price_optimization_savings": round(optimization_savings, 1),
        "revenue_impact": round(revenue_impact, 1),
        "competitor_price_gap": round(abs(price_gap), 1),
        "average_discount_rate": 12.5,
        "store_performance": {
            "S001": 15.3,
            "S002": 8.7,
            "S003": 12.1,
            "S004": 6.9
        },
        "seasonal_trends": {
            "Spring": "High",
            "Summer": "Peak", 
            "Autumn": "Medium",
            "Winter": "Low"
        },
        "weather_impact": {
            "Sunny": 18,
            "Cloudy": 5,
            "Rainy": -8,
            "Snowy": -15
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
