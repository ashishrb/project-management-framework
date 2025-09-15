from fastapi import APIRouter, HTTPException, status, Response, Request
import json
import base64

router = APIRouter()

# Simple demo users - no password hashing for demo simplicity
DEMO_USERS = {
    "manager1": {"password": "password123", "role": "manager", "id": 1, "email": "manager1@demo.com"},
    "manager2": {"password": "password123", "role": "manager", "id": 2, "email": "manager2@demo.com"},
    "executive": {"password": "password123", "role": "executive", "id": 3, "email": "executive@demo.com"},
    "admin": {"password": "password123", "role": "admin", "id": 4, "email": "admin@demo.com"}
}

def encode_user_data(user_data):
    """Simple base64 encoding for demo"""
    return base64.b64encode(json.dumps(user_data).encode()).decode()

def decode_user_data(encoded_data):
    """Simple base64 decoding for demo"""
    try:
        return json.loads(base64.b64decode(encoded_data.encode()).decode())
    except:
        return None

@router.post("/login")
async def login(request: Request, response: Response):
    """Super simple login for demo - no database dependency"""
    try:
        # Get form data
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )
        
        # Check demo users
        if username in DEMO_USERS:
            user_data = DEMO_USERS[username]
            if user_data["password"] == password:
                # Create simple user info
                user_info = {
                    "id": user_data["id"],
                    "username": username,
                    "email": user_data["email"],
                    "role": user_data["role"]
                }
                
                # Set simple cookie
                encoded_user = encode_user_data(user_info)
                response.set_cookie(
                    key="user_session",
                    value=encoded_user,
                    httponly=True,
                    samesite="lax",
                    secure=False,  # Set to True in production with HTTPS
                    max_age=3600  # 1 hour
                )
                
                return {
                    "message": "Login successful",
                    "user": user_info
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.post("/logout")
async def logout(response: Response):
    """Simple logout - clear cookie"""
    try:
        response.delete_cookie(key="user_session")
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout error: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(request: Request):
    """Get current user info from cookie"""
    try:
        user_cookie = request.cookies.get("user_session")
        if user_cookie:
            user_data = decode_user_data(user_cookie)
            if user_data:
                return user_data
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user info: {str(e)}"
        )