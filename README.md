# Hope Foundation Backend API

This directory contains the FastAPI backend for the Hope Foundation application.

## 🚀 Setup & Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --reload --port 8080
   ```

The API will be available at `http://localhost:8080`.

---

# 📚 API Endpoints Reference

Below is a comprehensive list of API endpoints required for the Hope Foundation Application, including expected request bodies and response structures.

**Base URL:** `http://localhost:8080/api`

---

## 🔐 Authentication

### 1. Login
Authenticate a user and receive a JWT token.

**Request:**
```bash
curl -X POST http://localhost:8080/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
           "email": "admin@hopefoundation.com",
           "password": "yourpassword"
         }'
```

**Response (200 OK):**
```json
{
  "name": "Admin User",
  "role": "admin",
  "token": "mock_token_admin"
}
```

### 2. Register
Register a new user account.

**Request:**
```bash
curl -X POST http://localhost:8080/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Jane Doe",
           "email": "jane@example.com",
           "password": "yourpassword",
           "role": "teacher"
         }'
```

**Response (201 Created):**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "teacher",
  "token": "mock_token_teacher"
}
```

---

## 📊 Dashboard

### 1. Get Dashboard Summary
Retrieve high-level statistics and recent activities.

**Request:**
```bash
curl -X GET http://localhost:8080/api/dashboard \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "totalStudents": {
    "title": "Total Students",
    "value": "1,234",
    "change": 12.0,
    "icon": "people"
  },
  "attendanceRate": {
    "title": "Attendance Rate",
    "value": "94.2%",
    "change": 2.3,
    "icon": "check_circle"
  },
  "stockItems": {
    "title": "Stock Items",
    "value": "456",
    "change": -5.0,
    "icon": "inventory"
  },
  "totalDonations": {
    "title": "Total Donations",
    "value": "$45,678",
    "change": 18.0,
    "icon": "volunteer"
  },
  "recentActivities": [
    {
      "title": "New student enrollment",
      "description": "Sarah Johnson enrolled in Grade 5",
      "time": "2 hours ago",
      "icon": "person_add"
    }
  ],
  "upcomingEvents": [
    {
      "title": "Annual Sports Day",
      "date": "2026-03-15",
      "time": "9:00 AM",
      "icon": "sports"
    }
  ],
  "impactItems": [
    {
      "title": "Quality Education",
      "icon": "education",
      "imageUrl": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=300&fit=crop"
    }
  ]
}
```

---

## 🎓 Student Management

### 1. List All Students
Retrieve a list of all students.

**Request:**
```bash
curl -X GET http://localhost:8080/api/students \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "students": [
    {
      "id": "1",
      "name": "Sarah Johnson",
      "grade": "Grade 5",
      "age": 10,
      "guardianName": "Michael Johnson",
      "contactNumber": "+1 234-567-8901",
      "email": "sarah@example.com",
      "address": "123 Main St",
      "status": "active",
      "enrollmentDate": "2025-08-15"
    }
  ]
}
```

### 2. Get Student Profile
Retrieve details for a specific student.

**Request:**
```bash
curl -X GET http://localhost:8080/api/student/1 \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "id": "1",
  "name": "Sarah Johnson",
  "grade": "Grade 5",
  "age": 10,
  "guardianName": "Michael Johnson",
  "contactNumber": "+1 234-567-8901",
  "status": "active",
  "enrollmentDate": "2025-08-15"
}
```

### 3. Get Student Grades
Retrieve academic performance for a student.

**Request:**
```bash
curl -X GET http://localhost:8080/api/student/1/grades \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "overallGpa": 8.85,
  "performanceLevel": "Excellent",
  "subjects": [
    {
      "id": "1",
      "subject": "Mathematics",
      "grade": "A+",
      "percentage": 92,
      "credits": 4,
      "teacher": "Mrs. Smith",
      "remarks": "Excellent performance"
    }
  ],
  "terms": [
    { "term": "Term 1", "percentage": 88, "grade": "A+" }
  ],
  "finalAverage": 88
}
```

---

## 📅 Attendance

### 1. Get Attendance Record
Fetch attendance for a specific grade and date.

**Request:**
```bash
curl -X GET "http://localhost:8080/api/attendance?grade=Grade5&date=2026-03-24" \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "students": [
    {
      "id": "1",
      "name": "Sarah Johnson",
      "grade": "Grade 5",
      "age": 10,
      "status": "present"
    }
  ],
  "summary": {
    "totalStudents": 8,
    "present": 6,
    "absent": 1,
    "late": 1
  }
}
```

### 2. Save Attendance
Submit attendance data for a session.

**Request:**
```bash
curl -X POST http://localhost:8080/api/attendance/save \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
           "grade": "Grade 5",
           "date": "2026-03-24",
           "attendance": [
             {"id": "1", "status": "present"},
             {"id": "2", "status": "absent"}
           ]
         }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Attendance saved successfully"
}
```

---

## 📢 Announcements

### 1. List Announcements
Retrieve all school announcements.

**Request:**
```bash
curl -X GET http://localhost:8080/api/announcements \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "announcements": [
    {
      "id": "1",
      "title": "Annual Sports Day - March 15, 2026",
      "content": "Sports Day details...",
      "author": "Principal Smith",
      "date": "2026-03-08",
      "priority": "high",
      "category": "events",
      "isPinned": true
    }
  ]
}
```

---

## 📦 Stock Management

### 1. List Stock Items
Retrieve inventory details.

**Request:**
```bash
curl -X GET http://localhost:8080/api/stock \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "1",
      "name": "Notebooks",
      "category": "stationery",
      "quantity": 450,
      "minimumQuantity": 100,
      "unit": "pieces",
      "lastUpdated": "2026-03-05"
    }
  ],
  "summary": {
    "totalItems": 7,
    "categories": 4,
    "lowStockItems": 3,
    "outOfStockItems": 0
  }
}
```

---

## 💰 Donations

### 1. List Donations
Retrieve donation history and summaries.

**Request:**
```bash
curl -X GET http://localhost:8080/api/donations \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "donations": [
    {
      "id": "1",
      "donorName": "Anonymous Donor",
      "type": "monetary",
      "amount": 500.00,
      "status": "completed",
      "date": "2026-03-19"
    }
  ],
  "summary": {
    "totalDonations": 45780.00,
    "totalDonors": 128,
    "monthlyDonations": 8750.00,
    "percentageChange": 18.5
  }
}
```

---

## 👩‍🏫 Teacher Panel

### 1. Teacher Dashboard
Retrieve specific data for the teacher view.

**Request:**
```bash
curl -X GET http://localhost:8080/api/teacher/dashboard \
     -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "students": [
    {
      "id": "1",
      "name": "Sarah Johnson",
      "grade": "Grade 5",
      "status": "active"
    }
  ],
  "announcements": [
    {
      "id": "1",
      "title": "Parent-Teacher Meeting",
      "priority": "high"
    }
  ]
}
```
