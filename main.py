import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

# Use DATABASE_URL env var if provided (e.g. for PostgreSQL on Render),
# otherwise fall back to a local SQLite file.
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite:///./hope.db"
)

# check_same_thread is only valid for SQLite; omit it for other databases.
_connect_args = (
    {"check_same_thread": False}
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
    else {}
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hope Foundation API")

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return token

# --- Schemas ---
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

class StudentRequest(BaseModel):
    name: str
    grade: str
    age: int
    guardianName: str
    contactNumber: str
    email: Optional[str] = None
    address: Optional[str] = None
    status: str = "active"

class AnnouncementRequest(BaseModel):
    title: str
    content: str
    author: str
    date: str
    priority: str = "medium"
    category: str = "updates"
    isPinned: bool = False

class StockItemRequest(BaseModel):
    name: str
    category: str = "other"
    quantity: int
    minimumQuantity: int
    unit: str
    description: Optional[str] = None

class DonationRequest(BaseModel):
    donorName: str
    type: str = "monetary"
    amount: float
    itemDescription: Optional[str] = None
    status: str = "pending"
    date: str
    notes: Optional[str] = None

class AttendanceRecord(BaseModel):
    id: str
    status: str

class SaveAttendanceRequest(BaseModel):
    grade: str
    date: str
    attendance: List[AttendanceRecord]

# --- Routes: Auth ---
@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "name": user.name,
        "role": user.role,
        "token": f"mock_token_{user.role}"
    }

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "token": f"mock_token_{new_user.role}"
    }

# --- Routes: Dashboard ---
@app.get("/api/dashboard")
def get_dashboard(token: str = Depends(verify_token)):
    return {
        "totalStudents": {"title": "Total Students", "value": "1,234", "change": 12.0, "icon": "people"},
        "attendanceRate": {"title": "Attendance Rate", "value": "94.2%", "change": 2.3, "icon": "check_circle"},
        "stockItems": {"title": "Stock Items", "value": "456", "change": -5.0, "icon": "inventory"},
        "totalDonations": {"title": "Total Donations", "value": "$45,678", "change": 18.0, "icon": "volunteer"},
        "recentActivities": [
            {"title": "New student enrollment", "description": "Sarah Johnson enrolled in Grade 5", "time": "2 hours ago", "icon": "person_add"},
            {"title": "Donation received", "description": "$500 from Anonymous Donor", "time": "5 hours ago", "icon": "attach_money"},
            {"title": "Stock updated", "description": "50 notebooks added to inventory", "time": "1 day ago", "icon": "inventory"},
            {"title": "Attendance marked", "description": "Grade 6 attendance completed", "time": "1 day ago", "icon": "check_circle"}
        ],
        "upcomingEvents": [
            {"title": "Annual Sports Day", "date": "2026-03-15", "time": "9:00 AM", "icon": "sports"},
            {"title": "Parent-Teacher Meeting", "date": "2026-03-20", "time": "2:00 PM", "icon": "meeting"},
            {"title": "Charity Fundraiser", "date": "2026-03-25", "time": "10:00 AM", "icon": "fundraiser"}
        ],
        "impactItems": [
            {"title": "Quality Education", "icon": "education", "imageUrl": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=300&fit=crop"},
            {"title": "Community Support", "icon": "community", "imageUrl": "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?w=400&h=300&fit=crop"},
            {"title": "Generous Donors", "icon": "donors", "imageUrl": "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?w=400&h=300&fit=crop"},
            {"title": "Anything is possible", "icon": "possibility", "imageUrl": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&h=300&fit=crop"}
        ]
    }

# --- Routes: Students ---
@app.get("/api/students")
def get_students(token: str = Depends(verify_token)):
    return {
        "students": [
            {
                "id": "1", "name": "Sarah Johnson", "grade": "Grade 5", "age": 10,
                "guardianName": "Michael Johnson", "contactNumber": "+1 234-567-8901",
                "email": "sarah@example.com", "address": "123 Main St",
                "status": "active", "enrollmentDate": "2025-08-15"
            },
            {
                "id": "2", "name": "John Smith", "grade": "Grade 6", "age": 11,
                "guardianName": "Emily Smith", "contactNumber": "+1 234-567-8902",
                "email": "john@example.com", "address": "456 Oak Ave",
                "status": "active", "enrollmentDate": "2025-08-16"
            },
            {
                "id": "3", "name": "Maria Garcia", "grade": "Grade 4", "age": 9,
                "guardianName": "Carlos Garcia", "contactNumber": "+1 234-567-8903",
                "email": "maria@example.com", "address": "789 Pine St",
                "status": "active", "enrollmentDate": "2025-08-17"
            },
            {
                "id": "4", "name": "David Lee", "grade": "Grade 7", "age": 12,
                "guardianName": "Lisa Lee", "contactNumber": "+1 234-567-8904",
                "email": "david@example.com", "address": "321 Elm Blvd",
                "status": "active", "enrollmentDate": "2025-08-18"
            },
            {
                "id": "5", "name": "Emma Wilson", "grade": "Grade 5", "age": 10,
                "guardianName": "Robert Wilson", "contactNumber": "+1 234-567-8905",
                "email": "emma@example.com", "address": "654 Maple Dr",
                "status": "inactive", "enrollmentDate": "2025-08-19"
            },
            {
                "id": "6", "name": "James Brown", "grade": "Grade 8", "age": 13,
                "guardianName": "Patricia Brown", "contactNumber": "+1 234-567-8906",
                "email": "james@example.com", "address": "987 Cedar Ln",
                "status": "active", "enrollmentDate": "2025-08-20"
            }
        ]
    }

@app.post("/api/students", status_code=status.HTTP_201_CREATED)
def add_student(request: StudentRequest, token: str = Depends(verify_token)):
    return {"success": True, "student": request.model_dump()}

@app.get("/api/student/{student_id}")
def get_student_profile(student_id: str, token: str = Depends(verify_token)):
    return {
        "id": student_id, "name": "Sarah Johnson", "grade": "Grade 5", "age": 10,
        "guardianName": "Michael Johnson", "contactNumber": "+1 234-567-8901",
        "status": "active", "enrollmentDate": "2025-08-15"
    }

@app.put("/api/students/{student_id}")
def update_student(student_id: str, request: StudentRequest, token: str = Depends(verify_token)):
    return {"success": True, "student": request.model_dump()}

@app.delete("/api/students/{student_id}")
def delete_student(student_id: str, token: str = Depends(verify_token)):
    return {"success": True, "message": "Student deleted successfully"}

@app.get("/api/student/{student_id}/grades")
def get_student_grades(student_id: str, token: str = Depends(verify_token)):
    return {
        "overallGpa": 8.85,
        "performanceLevel": "Excellent",
        "subjects": [
            {"id": "1", "subject": "Mathematics", "grade": "A+", "percentage": 92, "credits": 4, "teacher": "Mrs. Smith", "remarks": "Excellent performance"},
            {"id": "2", "subject": "Science", "grade": "A", "percentage": 88, "credits": 4, "teacher": "Mr. Johnson", "remarks": "Good understanding"},
            {"id": "3", "subject": "English", "grade": "B+", "percentage": 85, "credits": 3, "teacher": "Ms. Davis", "remarks": "Needs improvement in writing"},
            {"id": "4", "subject": "Social Studies", "grade": "A", "percentage": 91, "credits": 3, "teacher": "Mr. Brown", "remarks": "Very good"},
            {"id": "5", "subject": "Computer Science", "grade": "A+", "percentage": 96, "credits": 4, "teacher": "Mrs. Wilson", "remarks": "Outstanding"}
        ],
        "terms": [
            {"term": "Term 1", "percentage": 88, "grade": "A+"},
            {"term": "Term 2", "percentage": 91, "grade": "A"},
            {"term": "Term 3", "percentage": 85, "grade": "B+"}
        ],
        "finalAverage": 88
    }

# --- Routes: Attendance ---
@app.get("/api/attendance")
def get_attendance(grade: str, date: str, token: str = Depends(verify_token)):
    return {
        "students": [
            {"id": "1", "name": "Sarah Johnson", "grade": grade, "age": 10, "status": "present"},
            {"id": "2", "name": "Emma Wilson", "grade": grade, "age": 10, "status": "present"},
            {"id": "3", "name": "Michael Chen", "grade": grade, "age": 11, "status": "late"},
            {"id": "4", "name": "Olivia Martinez", "grade": grade, "age": 10, "status": "present"},
            {"id": "5", "name": "Daniel Kim", "grade": grade, "age": 11, "status": "absent"},
            {"id": "6", "name": "Sophia Anderson", "grade": grade, "age": 10, "status": "present"},
            {"id": "7", "name": "James Taylor", "grade": grade, "age": 11, "status": "present"},
            {"id": "8", "name": "Isabella Brown", "grade": grade, "age": 10, "status": "present"}
        ],
        "summary": {"totalStudents": 8, "present": 6, "absent": 1, "late": 1}
    }

@app.post("/api/attendance/save")
def save_attendance(request: SaveAttendanceRequest, token: str = Depends(verify_token)):
    return {"success": True, "message": "Attendance saved successfully"}

# --- Routes: Announcements ---
@app.get("/api/announcements")
def get_announcements(token: str = Depends(verify_token)):
    return {
        "announcements": [
            {
                "id": "1", "title": "Annual Sports Day - March 15, 2026",
                "content": "We are excited to announce our Annual Sports Day on March 15th. All students are encouraged to participate in various sports activities.",
                "author": "Principal Smith", "date": "2026-03-08",
                "priority": "high", "category": "events", "isPinned": True
            },
            {
                "id": "2", "title": "Parent-Teacher Meeting Schedule",
                "content": "Parent-Teacher meetings will be held on March 20th from 2:00 PM to 5:00 PM.",
                "author": "Admin Office", "date": "2026-03-07",
                "priority": "high", "category": "academic", "isPinned": True
            }
        ]
    }

@app.post("/api/announcements", status_code=status.HTTP_201_CREATED)
def add_announcement(request: AnnouncementRequest, token: str = Depends(verify_token)):
    return {"success": True, "announcement": request.model_dump()}

@app.put("/api/announcements/{announcement_id}")
def update_announcement(announcement_id: str, request: AnnouncementRequest, token: str = Depends(verify_token)):
    return {"success": True, "announcement": request.model_dump()}

@app.delete("/api/announcements/{announcement_id}")
def delete_announcement(announcement_id: str, token: str = Depends(verify_token)):
    return {"success": True, "message": "Announcement deleted successfully"}

# --- Routes: Stock ---
@app.get("/api/stock")
def get_stock(token: str = Depends(verify_token)):
    return {
        "items": [
            {
                "id": "1", "name": "Notebooks", "category": "stationery",
                "quantity": 450, "minimumQuantity": 100, "unit": "pieces", "lastUpdated": "2026-03-05"
            },
            {
                "id": "2", "name": "Pens", "category": "stationery",
                "quantity": 49, "minimumQuantity": 50, "unit": "pieces", "lastUpdated": "2026-03-05"
            },
            {
                "id": "3", "name": "Textbooks", "category": "books",
                "quantity": 200, "minimumQuantity": 50, "unit": "pieces", "lastUpdated": "2026-03-04"
            },
            {
                "id": "4", "name": "Uniforms", "category": "uniforms",
                "quantity": 30, "minimumQuantity": 40, "unit": "sets", "lastUpdated": "2026-03-03"
            }
        ],
        "summary": {"totalItems": 7, "categories": 4, "lowStockItems": 3, "outOfStockItems": 0}
    }

@app.post("/api/stock", status_code=status.HTTP_201_CREATED)
def add_stock_item(request: StockItemRequest, token: str = Depends(verify_token)):
    return {"success": True, "item": request.model_dump()}

@app.put("/api/stock/{item_id}")
def update_stock_item(item_id: str, request: StockItemRequest, token: str = Depends(verify_token)):
    return {"success": True, "item": request.model_dump()}

@app.delete("/api/stock/{item_id}")
def delete_stock_item(item_id: str, token: str = Depends(verify_token)):
    return {"success": True, "message": "Stock item deleted successfully"}

# --- Routes: Donations ---
@app.get("/api/donations")
def get_donations(token: str = Depends(verify_token)):
    return {
        "donations": [
            {
                "id": "1", "donorName": "Anonymous Donor", "type": "monetary",
                "amount": 500.00, "status": "completed", "date": "2026-03-19"
            },
            {
                "id": "2", "donorName": "John Smith Foundation", "type": "monetary",
                "amount": 2500.00, "status": "completed", "date": "2026-03-15"
            },
            {
                "id": "3", "donorName": "Local Business Co.", "type": "goods",
                "amount": 50.0, "itemDescription": "50 School Bags", "status": "completed", "date": "2026-03-10"
            }
        ],
        "summary": {
            "totalDonations": 45780.00, "totalDonors": 128,
            "monthlyDonations": 8750.00, "percentageChange": 18.5
        }
    }

@app.post("/api/donations", status_code=status.HTTP_201_CREATED)
def add_donation(request: DonationRequest, token: str = Depends(verify_token)):
    return {"success": True, "donation": request.model_dump()}

@app.put("/api/donations/{donation_id}")
def update_donation(donation_id: str, request: DonationRequest, token: str = Depends(verify_token)):
    return {"success": True, "donation": request.model_dump()}

# --- Routes: Teacher ---
@app.get("/api/teacher/dashboard")
def get_teacher_dashboard(token: str = Depends(verify_token)):
    return {
        "students": [
            {"id": "1", "name": "Sarah Johnson", "grade": "Grade 5", "age": 10,
             "guardianName": "Michael Johnson", "contactNumber": "+1 234-567-8901",
             "status": "active", "enrollmentDate": "2025-08-15"}
        ],
        "announcements": [
            {"id": "1", "title": "Parent-Teacher Meeting",
             "content": "Parent-Teacher meetings will be held on March 20th from 2:00 PM to 5:00 PM.",
             "author": "Admin Office", "date": "2026-03-07",
             "priority": "high", "category": "academic", "isPinned": True}
        ]
    }

# --- Routes: Student Dashboard ---
@app.get("/api/student/{student_id}/dashboard")
def get_student_dashboard(student_id: str, token: str = Depends(verify_token)):
    return {
        "profile": {
            "id": student_id, "name": "Sarah Johnson", "grade": "Grade 5", "age": 10,
            "guardianName": "Michael Johnson", "contactNumber": "+1 234-567-8901",
            "status": "active", "enrollmentDate": "2025-08-15"
        },
        "announcements": [
            {"id": "1", "title": "Annual Sports Day",
             "content": "Annual Sports Day on March 15th. All students are encouraged to participate.",
             "author": "Principal Smith", "date": "2026-03-08",
             "priority": "high", "category": "events", "isPinned": True}
        ],
        "attendance": {
            "present": 28, "absent": 2, "late": 1,
            "totalDays": 31, "attendanceRate": 90.3
        }
    }

if __name__ == "__main__":
    # PORT is automatically provided by Render; default to 8080 for local dev.
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
