from fastapi import FastAPI, Request
from app.api.analytics import analytics
from app.api.data_filtering import data_filtering
from app.api.visualization_data import visualization_data
from app.limiter import add_limiter_exception_handler, limiter


# Create FastAPI app instance
app = FastAPI()

# Add rate limiting exception handler
add_limiter_exception_handler(app)

# Include routers
app.include_router(data_filtering)
app.include_router(analytics)
app.include_router(visualization_data)


# Define root route
@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    """
    Root endpoint returning a simple message.
    """
    return {"message": "Hello World"}
