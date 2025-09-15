"""
Simple FastAPI application for demo - minimal middleware
"""
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.main_tables import Project, Backlog
import json
import base64

# Create FastAPI app
app = FastAPI(
    title="GenAI Project Management Demo",
    description="Simple demo application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Simple demo users
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

def get_user_from_cookie(request: Request):
    """Get current user from cookie"""
    user_cookie = request.cookies.get("user_session")
    if user_cookie:
        return decode_user_data(user_cookie)
    return None

# Simple routes
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page - landing page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/api/login")
async def login(request: Request, response: Response):
    """Super simple login"""
    try:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        
        if not username or not password:
            return {"error": "Username and password are required"}
        
        if username in DEMO_USERS:
            user_data = DEMO_USERS[username]
            if user_data["password"] == password:
                user_info = {
                    "id": user_data["id"],
                    "username": username,
                    "email": user_data["email"],
                    "role": user_data["role"]
                }
                
                # Set cookie
                encoded_user = encode_user_data(user_info)
                response.set_cookie(
                    key="user_session",
                    value=encoded_user,
                    httponly=True,
                    samesite="lax",
                    max_age=3600
                )
                
                return {"message": "Login successful", "user": user_info}
        
        return {"error": "Invalid username or password"}
    except Exception as e:
        return {"error": f"Login error: {str(e)}"}

@app.get("/api/me")
async def get_me(request: Request):
    """Get current user info"""
    try:
        user_cookie = request.cookies.get("user_session")
        if user_cookie:
            user_data = decode_user_data(user_cookie)
            if user_data:
                return user_data
        return {"error": "Not authenticated"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Test endpoint working", "timestamp": "2024-01-01"}

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - role-based dashboard"""
    try:
        user_cookie = request.cookies.get("user_session")
        if not user_cookie:
            return HTMLResponse("<h1>Please login first</h1><a href='/'>Login</a>")
        
        user_data = decode_user_data(user_cookie)
        if not user_data:
            return HTMLResponse("<h1>Invalid session</h1><a href='/'>Login</a>")
        
        role = user_data.get("role", "manager")
        
        if role == "admin":
            return templates.TemplateResponse("admin.html", {"request": request, "user": user_data})
        elif role == "executive":
            return templates.TemplateResponse("portfolio_dashboard.html", {"request": request, "user": user_data})
        else:  # manager
            return templates.TemplateResponse("manager_dashboard.html", {"request": request, "user": user_data})
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")

@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """Projects page"""
    try:
        user_cookie = request.cookies.get("user_session")
        if not user_cookie:
            return HTMLResponse("<h1>Please login first</h1><a href='/'>Login</a>")
        
        user_data = decode_user_data(user_cookie)
        if not user_data:
            return HTMLResponse("<h1>Invalid session</h1><a href='/'>Login</a>")
        
        return templates.TemplateResponse("projects.html", {"request": request, "user": user_data})
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")

@app.get("/comprehensive-dashboard", response_class=HTMLResponse)
async def comprehensive_dashboard_page(request: Request):
    """Comprehensive Dashboard page"""
    try:
        user_cookie = request.cookies.get("user_session")
        if not user_cookie:
            return HTMLResponse("<h1>Please login first</h1><a href='/'>Login</a>")
        
        user_data = decode_user_data(user_cookie)
        if not user_data:
            return HTMLResponse("<h1>Invalid session</h1><a href='/'>Login</a>")
        
        return templates.TemplateResponse("comprehensive_dashboard.html", {"request": request, "user": user_data})
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")

@app.get("/project/{project_id}", response_class=HTMLResponse)
async def project_detail_page(request: Request, project_id: int, mode: str = "readonly", db: Session = Depends(get_db)):
    """Project detail page"""
    try:
        user_cookie = request.cookies.get("user_session")
        if not user_cookie:
            return HTMLResponse("<h1>Please login first</h1><a href='/'>Login</a>")
        
        user_data = decode_user_data(user_cookie)
        if not user_data:
            return HTMLResponse("<h1>Invalid session</h1><a href='/'>Login</a>")
        
        # Get project details from database
        username = user_data.get("username")
        role = user_data.get("role")
        
        query = db.query(Project).filter(Project.id == project_id, Project.is_active == True)
        
        if role == "manager":
            query = query.filter(Project.project_manager == username)
        elif role not in ["executive", "admin"]:
            return HTMLResponse("<h1>Access denied</h1>")
        
        project = query.first()
        if not project:
            return HTMLResponse("<h1>Project not found</h1>")
        
        # Get related backlog items for this project
        backlog_items = []
        if role == "manager":
            # Get backlog items assigned to this manager's projects
            manager_projects = db.query(Project).filter(
                Project.project_manager == username,
                Project.is_active == True
            ).all()
            project_ids = [p.id for p in manager_projects]
            
            for project_id in project_ids:
                items = db.query(Backlog).filter(
                    Backlog.description.like(f"%Project {project_id} - {username.title()}%")
                ).all()
                backlog_items.extend(items)
        else:
            backlog_items = db.query(Backlog).limit(20).all()
        
        # Convert project to dict for template
        project_data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status_id": project.status_id,
            "priority_id": project.priority_id,
            "project_manager": project.project_manager,
            "percent_complete": float(project.percent_complete) if project.percent_complete else 0,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "due_date": project.due_date.isoformat() if project.due_date else None,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "budget_amount": float(project.budget_amount) if project.budget_amount else 0,
            "actual_cost": float(project.actual_cost) if project.actual_cost else 0
        }
        
        return templates.TemplateResponse("project_detail.html", {
            "request": request, 
            "user": user_data,
            "project": project_data,
            "mode": mode,
            "backlog_items": [
                {
                    "id": b.id,
                    "name": b.name,
                    "description": b.description,
                    "status_id": b.status_id,
                    "priority_id": b.priority_id,
                    "complexity": b.complexity,
                    "effort_estimate": float(b.effort_estimate) if b.effort_estimate else 0,
                    "target_quarter": b.target_quarter
                }
                for b in backlog_items
            ]
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")

@app.put("/api/v1/projects/{project_id}")
async def update_project(project_id: int, request: Request, db: Session = Depends(get_db)):
    """Update a project"""
    try:
        user = get_user_from_cookie(request)
        if not user:
            return {"error": "Not authenticated"}
        
        # Get request body
        body = await request.json()
        print(f"Updating project {project_id} with data:", body)
        
        # Get the project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found"}
        
        # Check if user has permission to edit this project
        username = user.get("username")
        role = user.get("role")
        
        if role == "manager" and project.project_manager != username:
            return {"error": "Access denied"}
        
        # Update project fields
        if "name" in body:
            project.name = body["name"]
        if "description" in body:
            project.description = body["description"]
        if "esa_id" in body:
            project.esa_id = body["esa_id"]
        if "status_id" in body:
            project.status_id = body["status_id"]
        if "priority_id" in body:
            project.priority_id = body["priority_id"]
        if "project_manager" in body:
            project.project_manager = body["project_manager"]
        if "percent_complete" in body:
            project.percent_complete = body["percent_complete"]
        if "start_date" in body:
            project.start_date = body["start_date"]
        if "due_date" in body:
            project.due_date = body["due_date"]
        if "budget_amount" in body:
            project.budget_amount = body["budget_amount"]
        if "actual_cost" in body:
            project.actual_cost = body["actual_cost"]
        if "business_owner" in body:
            project.business_owner = body["business_owner"]
        if "technology_portfolio_leader" in body:
            project.technology_portfolio_leader = body["technology_portfolio_leader"]
        
        # Commit changes
        db.commit()
        
        return {"message": "Project updated successfully", "project_id": project_id}
        
    except Exception as e:
        db.rollback()
        print(f"Error updating project: {e}")
        return {"error": f"Update failed: {str(e)}"}

@app.get("/api/v1/projects")
async def get_projects(request: Request, db: Session = Depends(get_db)):
    """Get projects based on user role"""
    try:
        user = get_user_from_cookie(request)
        print(f"DEBUG: get_user_from_cookie returned: {user}")
        if not user:
            return {"error": "Not authenticated"}
        
        username = user.get("username")
        role = user.get("role")
        
        print(f"Getting projects for user: {username}, role: {role}")
        
        query = db.query(Project).filter(Project.is_active == True)
        
        if role == "manager":
            query = query.filter(Project.project_manager == username)
        elif role not in ["executive", "admin"]:
            return {"projects": []}
        
        projects = query.all()
        print(f"Found {len(projects)} projects")
        
        return {
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "status_id": p.status_id,
                    "priority_id": p.priority_id,
                    "project_manager": p.project_manager,
                    "percent_complete": float(p.percent_complete) if p.percent_complete else 0,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "due_date": p.due_date.isoformat() if p.due_date else None,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None
                }
                for p in projects
            ]
        }
    except Exception as e:
        print(f"Error in get_projects: {e}")
        return {"error": str(e)}

@app.get("/api/v1/backlogs")
async def get_backlogs(request: Request, db: Session = Depends(get_db)):
    """Get backlog items based on user role"""
    user = get_user_from_cookie(request)
    if not user:
        return {"error": "Not authenticated"}
    
    username = user.get("username")
    role = user.get("role")
    
    # For demo, we'll get all backlog items and filter by description
    query = db.query(Backlog)
    
    if role == "manager":
        # Filter backlog items assigned to this manager's projects
        manager_projects = db.query(Project).filter(
            Project.project_manager == username,
            Project.is_active == True
        ).all()
        project_ids = [p.id for p in manager_projects]
        
        # Filter backlogs that mention this manager's projects
        backlog_items = []
        for project_id in project_ids:
            items = db.query(Backlog).filter(
                Backlog.description.like(f"%Project {project_id} - {username.title()}%")
            ).all()
            backlog_items.extend(items)
        
        # Remove duplicates
        seen_ids = set()
        unique_items = []
        for item in backlog_items:
            if item.id not in seen_ids:
                unique_items.append(item)
                seen_ids.add(item.id)
        
        backlogs = unique_items
    else:
        backlogs = query.limit(20).all()
    
    return {
        "backlogs": [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "status_id": b.status_id,
                "priority_id": b.priority_id,
                "complexity": b.complexity,
                "effort_estimate": float(b.effort_estimate) if b.effort_estimate else 0,
                "target_quarter": b.target_quarter,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "updated_at": b.updated_at.isoformat() if b.updated_at else None
            }
            for b in backlogs
        ]
    }

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    user = get_user_from_cookie(request)
    if not user:
        return {"error": "Not authenticated"}
    
    username = user.get("username")
    role = user.get("role")
    
    # Get user's projects
    if role == "manager":
        projects = db.query(Project).filter(
            Project.project_manager == username,
            Project.is_active == True
        ).all()
    else:
        projects = db.query(Project).filter(Project.is_active == True).all()
    
    # Calculate stats
    total_projects = len(projects)
    on_track_projects = len([p for p in projects if p.status_id == 1])  # Active
    at_risk_projects = len([p for p in projects if p.status_id == 3])  # At Risk
    completed_projects = len([p for p in projects if p.status_id == 2])  # Completed
    
    # Get backlog stats
    if role == "manager":
        manager_projects = db.query(Project).filter(
            Project.project_manager == username,
            Project.is_active == True
        ).all()
        project_ids = [p.id for p in manager_projects]
        
        total_backlog = 0
        high_priority = 0
        in_progress = 0
        completed_tasks = 0
        
        for project_id in project_ids:
            items = db.query(Backlog).filter(
                Backlog.description.like(f"%Project {project_id} - {username.title()}%")
            ).all()
            total_backlog += len(items)
            high_priority += len([i for i in items if i.priority_id >= 3])
            in_progress += len([i for i in items if i.status_id == 2])
            completed_tasks += len([i for i in items if i.status_id == 3])
    else:
        backlogs = db.query(Backlog).all()
        total_backlog = len(backlogs)
        high_priority = len([b for b in backlogs if b.priority_id >= 3])
        in_progress = len([b for b in backlogs if b.status_id == 2])
        completed_tasks = len([b for b in backlogs if b.status_id == 3])
    
    return {
        "projects": {
            "total": total_projects,
            "on_track": on_track_projects,
            "at_risk": at_risk_projects,
            "completed": completed_projects
        },
        "backlog": {
            "total": total_backlog,
            "high_priority": high_priority,
            "in_progress": in_progress,
            "completed": completed_tasks
        },
        "overdue_tasks": 0  # Placeholder for now
    }

@app.post("/api/v1/logs/frontend")
async def log_frontend(request: Request):
    """Frontend logging endpoint"""
    try:
        data = await request.json()
        print(f"Frontend log: {data}")
        return {"message": "Log received"}
    except Exception as e:
        print(f"Frontend log error: {e}")
        return {"message": "Log received"}

@app.get("/api/v1/lookup/portfolios")
async def get_portfolios(db: Session = Depends(get_db)):
    """Get portfolios for dropdowns"""
    try:
        from app.models.lookup_tables import Portfolio
        portfolios = db.query(Portfolio).filter(Portfolio.is_active == True).all()
        return {"portfolios": portfolios}
    except Exception as e:
        print(f"Error fetching portfolios: {e}")
        return {"portfolios": []}

@app.get("/api/v1/dashboard/comprehensive")
async def get_comprehensive_dashboard_data(db: Session = Depends(get_db), current_user: dict = Depends(get_user_from_cookie)):
    """Get comprehensive dashboard data for all charts"""
    try:
        from app.models.main_tables import Project, Backlog
        from app.models.lookup_tables import Status, Priority, Portfolio
        
        # Get all active projects
        projects = db.query(Project).filter(Project.is_active == True).all()
        
        # Get all active backlogs
        backlogs = db.query(Backlog).filter(Backlog.is_active == True).all()
        
        # Calculate summary statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status_id == 1])
        completed_projects = len([p for p in projects if p.status_id == 2])
        at_risk_projects = len([p for p in projects if p.status_id == 3])
        off_track_projects = len([p for p in projects if p.status_id == 4])
        
        # Calculate financial data
        total_budget = sum([float(p.budget_amount or 0) for p in projects])
        total_actual_cost = sum([float(p.actual_cost or 0) for p in projects])
        total_planned_benefits = sum([float(p.planned_benefits or 0) for p in projects])
        
        # Business Unit distribution
        business_units = {}
        for project in projects:
            unit = project.business_unit_id or "Unknown"
            business_units[unit] = business_units.get(unit, 0) + 1
        
        # Investment Type distribution
        investment_types = {}
        for project in projects:
            inv_type = project.investment_type_id or "Unknown"
            investment_types[inv_type] = investment_types.get(inv_type, 0) + 1
        
        # Priority distribution
        priorities = {}
        for project in projects:
            priority = project.priority_id or "Unknown"
            priorities[priority] = priorities.get(priority, 0) + 1
        
        # Status distribution
        statuses = {}
        for project in projects:
            status = project.status_id or "Unknown"
            statuses[status] = statuses.get(status, 0) + 1
        
        # Backlog statistics
        total_backlogs = len(backlogs)
        high_priority_backlogs = len([b for b in backlogs if b.priority_id == 4])
        in_progress_backlogs = len([b for b in backlogs if b.status_id == 2])
        completed_backlogs = len([b for b in backlogs if b.status_id == 3])
        
        return {
            "summary": {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "at_risk_projects": at_risk_projects,
                "off_track_projects": off_track_projects,
                "total_budget": total_budget,
                "total_actual_cost": total_actual_cost,
                "total_planned_benefits": total_planned_benefits,
                "budget_variance": total_budget - total_actual_cost if total_budget > 0 else 0
            },
            "distributions": {
                "business_units": business_units,
                "investment_types": investment_types,
                "priorities": priorities,
                "statuses": statuses
            },
            "backlog_stats": {
                "total": total_backlogs,
                "high_priority": high_priority_backlogs,
                "in_progress": in_progress_backlogs,
                "completed": completed_backlogs
            },
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status_id": p.status_id,
                    "priority_id": p.priority_id,
                    "business_unit_id": p.business_unit_id,
                    "investment_type_id": p.investment_type_id,
                    "budget_amount": float(p.budget_amount or 0),
                    "actual_cost": float(p.actual_cost or 0),
                    "planned_benefits": float(p.planned_benefits or 0),
                    "percent_complete": p.percent_complete or 0,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "due_date": p.due_date.isoformat() if p.due_date else None
                } for p in projects
            ]
        }
    except Exception as e:
        print(f"Error fetching comprehensive dashboard data: {e}")
        return {"error": str(e)}

@app.get("/api/v1/ai-insights/insights")
async def get_ai_insights(db: Session = Depends(get_db), current_user: dict = Depends(get_user_from_cookie)):
    """Get AI insights based on real project data"""
    try:
        from app.models.main_tables import Project, Backlog
        
        # Get project data for analysis
        projects = db.query(Project).filter(Project.is_active == True).all()
        backlogs = db.query(Backlog).filter(Backlog.is_active == True).all()
        
        insights = []
        
        # Analyze project health
        total_projects = len(projects)
        at_risk_count = len([p for p in projects if p.status_id == 3])
        off_track_count = len([p for p in projects if p.status_id == 4])
        
        if at_risk_count > 0:
            insights.append({
                "title": f"{at_risk_count} Projects At Risk",
                "description": f"Found {at_risk_count} projects marked as at-risk requiring immediate attention",
                "severity": "high" if at_risk_count > total_projects * 0.2 else "medium"
            })
        
        if off_track_count > 0:
            insights.append({
                "title": f"{off_track_count} Projects Off Track",
                "description": f"Found {off_track_count} projects that are off-track and need intervention",
                "severity": "high" if off_track_count > total_projects * 0.15 else "medium"
            })
        
        # Analyze budget performance
        total_budget = sum([float(p.budget_amount or 0) for p in projects])
        total_actual = sum([float(p.actual_cost or 0) for p in projects])
        
        if total_budget > 0:
            budget_variance = ((total_actual - total_budget) / total_budget) * 100
            if budget_variance > 10:
                insights.append({
                    "title": "Budget Overrun Alert",
                    "description": f"Projects are {budget_variance:.1f}% over budget on average",
                    "severity": "high" if budget_variance > 20 else "medium"
                })
            elif budget_variance < -10:
                insights.append({
                    "title": "Budget Underutilization",
                    "description": f"Projects are {abs(budget_variance):.1f}% under budget on average",
                    "severity": "medium"
                })
        
        # Analyze backlog health
        total_backlogs = len(backlogs)
        high_priority_backlogs = len([b for b in backlogs if b.priority_id == 4])
        
        if high_priority_backlogs > total_backlogs * 0.3:
            insights.append({
                "title": "High Priority Backlog Overload",
                "description": f"{high_priority_backlogs} high-priority items in backlog ({high_priority_backlogs/total_backlogs*100:.1f}%)",
                "severity": "medium"
            })
        
        # Analyze project completion rates
        completed_projects = len([p for p in projects if p.status_id == 2])
        if total_projects > 0:
            completion_rate = (completed_projects / total_projects) * 100
            if completion_rate > 80:
                insights.append({
                    "title": "Excellent Project Completion",
                    "description": f"{completion_rate:.1f}% of projects completed successfully",
                    "severity": "info"
                })
            elif completion_rate < 50:
                insights.append({
                    "title": "Low Project Completion Rate",
                    "description": f"Only {completion_rate:.1f}% of projects completed",
                    "severity": "medium"
                })
        
        # Default insight if no specific issues found
        if not insights:
            insights.append({
                "title": "Portfolio Health Good",
                "description": "All projects are performing within acceptable parameters",
                "severity": "info"
            })
        
        return {"insights": insights}
        
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return {"insights": [{"title": "Analysis Error", "description": "Unable to generate insights", "severity": "info"}]}

@app.get("/api/v1/ai-analysis/comprehensive")
async def get_comprehensive_ai_analysis(db: Session = Depends(get_db), current_user: dict = Depends(get_user_from_cookie)):
    """Get comprehensive AI analysis of project portfolio"""
    try:
        from app.models.main_tables import Project, Backlog
        
        # Get project data
        projects = db.query(Project).filter(Project.is_active == True).all()
        backlogs = db.query(Backlog).filter(Backlog.is_active == True).all()
        
        # Calculate key metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status_id == 1])
        completed_projects = len([p for p in projects if p.status_id == 2])
        at_risk_projects = len([p for p in projects if p.status_id == 3])
        off_track_projects = len([p for p in projects if p.status_id == 4])
        
        total_budget = sum([float(p.budget_amount or 0) for p in projects])
        total_actual = sum([float(p.actual_cost or 0) for p in projects])
        total_benefits = sum([float(p.planned_benefits or 0) for p in projects])
        
        # Calculate health score
        health_score = 100
        if total_projects > 0:
            risk_penalty = (at_risk_projects * 10) + (off_track_projects * 20)
            health_score = max(0, health_score - risk_penalty)
        
        # Generate analysis text
        analysis = f"""
        <div class="ai-analysis-content">
            <h5>Portfolio Health Analysis</h5>
            <p><strong>Health Score:</strong> {health_score:.1f}%</p>
            <p>Portfolio contains {total_projects} active projects with {active_projects} currently in progress, {completed_projects} completed, {at_risk_projects} at-risk, and {off_track_projects} off-track initiatives.</p>
            
            <h6>Financial Performance</h6>
            <p>Total budget allocation: ${total_budget:,.0f}</p>
            <p>Actual costs: ${total_actual:,.0f}</p>
            <p>Planned benefits: ${total_benefits:,.0f}</p>
            
            <h6>Risk Assessment</h6>
            <p>{"✅ Low risk portfolio" if at_risk_projects + off_track_projects < total_projects * 0.2 else "⚠️ Moderate risk portfolio" if at_risk_projects + off_track_projects < total_projects * 0.4 else "🚨 High risk portfolio"}</p>
            
            <h6>Recommendations</h6>
            <ul>
                {"<li>Focus on at-risk project recovery</li>" if at_risk_projects > 0 else ""}
                {"<li>Implement corrective actions for off-track projects</li>" if off_track_projects > 0 else ""}
                <li>Monitor budget performance closely</li>
                <li>Review project prioritization regularly</li>
            </ul>
        </div>
        """
        
        return {"analysis": analysis, "health_score": health_score}
        
    except Exception as e:
        print(f"Error generating comprehensive AI analysis: {e}")
        return {"analysis": "<p>Unable to generate analysis at this time.</p>", "health_score": 0}

@app.get("/api/v1/analytics/comparative-analysis")
async def get_comparative_analysis(db: Session = Depends(get_db), current_user: dict = Depends(get_user_from_cookie)):
    """Get comparative analysis data for portfolio dashboard"""
    try:
        from app.models.main_tables import Project
        
        # Get all active projects
        projects = db.query(Project).filter(Project.is_active == True).all()
        
        # Calculate comparative metrics
        total_budget = sum([float(p.budget_amount or 0) for p in projects])
        total_actual_cost = sum([float(p.actual_cost or 0) for p in projects])
        total_planned_benefits = sum([float(p.planned_benefits or 0) for p in projects])
        
        # Manager performance analysis
        managers = {}
        for project in projects:
            manager = project.project_manager or "Unassigned"
            if manager not in managers:
                managers[manager] = {
                    "project_count": 0,
                    "total_budget": 0,
                    "total_actual_cost": 0,
                    "health_score": 0
                }
            managers[manager]["project_count"] += 1
            managers[manager]["total_budget"] += float(project.budget_amount or 0)
            managers[manager]["total_actual_cost"] += float(project.actual_cost or 0)
            managers[manager]["health_score"] += 75 + float(project.percent_complete or 0) * 0.25
        
        # Calculate average health scores
        for manager in managers:
            if managers[manager]["project_count"] > 0:
                managers[manager]["health_score"] = round(managers[manager]["health_score"] / managers[manager]["project_count"])
        
        return {
            "portfolio_summary": {
                "total_projects": len(projects),
                "total_budget": total_budget,
                "total_actual_cost": total_actual_cost,
                "total_planned_benefits": total_planned_benefits,
                "budget_utilization": round((total_actual_cost / total_budget * 100) if total_budget > 0 else 0, 1)
            },
            "manager_performance": managers,
            "status_distribution": {
                "active": len([p for p in projects if p.status_id == 1]),
                "completed": len([p for p in projects if p.status_id == 2]),
                "planning": len([p for p in projects if p.status_id == 3]),
                "at_risk": len([p for p in projects if p.status_id == 4])
            }
        }
    except Exception as e:
        print(f"Error generating comparative analysis: {e}")
        return {"error": str(e)}

@app.get("/api/v1/dashboards/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db), current_user: dict = Depends(get_user_from_cookie)):
    """Get dashboard metrics for portfolio dashboard"""
    try:
        from app.models.main_tables import Project
        
        # Get all active projects
        projects = db.query(Project).filter(Project.is_active == True).all()
        
        # Calculate portfolio health metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status_id == 1])
        completed_projects = len([p for p in projects if p.status_id == 2])
        at_risk_projects = len([p for p in projects if p.status_id == 4])
        
        # Calculate financial metrics
        total_budget = sum([float(p.budget_amount or 0) for p in projects])
        total_actual_cost = sum([float(p.actual_cost or 0) for p in projects])
        total_planned_benefits = sum([float(p.planned_benefits or 0) for p in projects])
        
        # Calculate average portfolio health
        avg_health = 0
        if total_projects > 0:
            health_scores = []
            for project in projects:
                # Calculate health based on status and completion
                base_health = 75
                if project.status_id == 1:  # Active
                    base_health = 85
                elif project.status_id == 2:  # Completed
                    base_health = 95
                elif project.status_id == 4:  # At Risk
                    base_health = 45
                
                # Adjust based on completion percentage
                completion_factor = float(project.percent_complete or 0) * 0.2
                health_scores.append(min(100, base_health + completion_factor))
            
            avg_health = round(sum(health_scores) / len(health_scores))
        
        # Calculate budget utilization
        budget_utilization = round((total_actual_cost / total_budget * 100) if total_budget > 0 else 0, 1)
        
        return {
            "kpis": {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "at_risk_projects": at_risk_projects,
                "avg_portfolio_health": avg_health,
                "budget_utilization": budget_utilization,
                "total_budget": total_budget,
                "total_actual_cost": total_actual_cost,
                "total_planned_benefits": total_planned_benefits
            },
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status_id": p.status_id,
                    "project_manager": p.project_manager,
                    "budget_amount": float(p.budget_amount or 0),
                    "actual_cost": float(p.actual_cost or 0),
                    "planned_benefits": float(p.planned_benefits or 0),
                    "percent_complete": p.percent_complete or 0,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "due_date": p.due_date.isoformat() if p.due_date else None,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                } for p in projects
            ]
        }
    except Exception as e:
        print(f"Error generating dashboard metrics: {e}")
        return {"error": str(e)}

@app.post("/api/logout")
async def logout(response: Response):
    """Simple logout"""
    response.delete_cookie(key="user_session")
    return {"message": "Logout successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
