# Database Models Flowchart

This document shows the structure and relationships between all tables in the appointment system database.

## Entity Relationship Diagram

```mermaid
erDiagram
    %% Location Tables (Hierarchical)
    DIVISIONS {
        int id PK
        string name "unique"
    }

    DISTRICTS {
        int id PK
        string name
        int division_id FK
    }

    THANAS {
        int id PK
        string name
        int district_id FK
    }

    %% User Tables
    USERS {
        int id PK
        string full_name
        string email "unique"
        string mobile_number "unique"
        string hashed_password
        enum user_type "PATIENT/DOCTOR/ADMIN"
        int division_id FK
        int district_id FK
        int thana_id FK
        string profile_image_filename
        string profile_image_content_type
        datetime created_at
        datetime updated_at
    }

    DOCTOR_PROFILES {
        int id PK
        int user_id FK "unique"
        string license_number "unique"
        int experience_years
        float consultation_fee
    }

    DOCTOR_TIMESLOTS {
        int id PK
        int doctor_id FK
        string start_time
        string end_time
        boolean is_available
    }

    %% Appointment Table
    APPOINTMENTS {
        int id PK
        int patient_id FK
        int doctor_id FK
        date appointment_date
        time appointment_time
        text notes
        enum status "PENDING/CONFIRMED/CANCELLED/COMPLETED"
        datetime created_at
        datetime updated_at
    }

    %% Notification Table
    NOTIFICATIONS {
        int id PK
        int user_id FK
        boolean is_read
        datetime created_at
    }

    %% Token Management
    TOKEN_BLACKLIST {
        int id PK
        string token_jti "unique"
        int user_id FK
        datetime blacklisted_at
        datetime expires_at
    }

    %% Relationships
    DIVISIONS ||--o{ DISTRICTS : "has many"
    DISTRICTS ||--o{ THANAS : "has many"
    DISTRICTS }o--|| DIVISIONS : "belongs to"
    THANAS }o--|| DISTRICTS : "belongs to"

    USERS }o--|| DIVISIONS : "lives in"
    USERS }o--|| DISTRICTS : "lives in"
    USERS }o--|| THANAS : "lives in"

    USERS ||--o| DOCTOR_PROFILES : "may have"
    DOCTOR_PROFILES ||--o{ DOCTOR_TIMESLOTS : "has many"

    USERS ||--o{ APPOINTMENTS : "patient books"
    DOCTOR_PROFILES ||--o{ APPOINTMENTS : "doctor receives"

    USERS ||--o{ NOTIFICATIONS : "receives"
    USERS ||--o{ TOKEN_BLACKLIST : "has tokens"
```

## Table Communication Flow

### 1. Location Hierarchy
```mermaid
flowchart TD
    A[Divisions] --> B[Districts]
    B --> C[Thanas]

    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#fff3e0
```

### 2. User Management Flow
```mermaid
flowchart TD
    A[User Registration] --> B{User Type?}
    B -->|Patient| C[Regular User]
    B -->|Doctor| D[Doctor Profile Creation]
    B -->|Admin| E[Admin User]

    D --> F[Doctor Timeslots Setup]

    style A fill:#e3f2fd
    style D fill:#e8f5e8
    style F fill:#fff3e0
```

### 3. Appointment Booking Flow
```mermaid
flowchart TD
    A[Patient] --> B[Browse Available Doctors]
    B --> C[Check Doctor Timeslots]
    C --> D[Book Appointment]
    D --> E[Appointment Created]
    E --> F[Notification Sent]

    G[Doctor] --> H[View Appointments]
    H --> I{Confirm/Cancel?}
    I -->|Confirm| J[Update Status to CONFIRMED]
    I -->|Cancel| K[Update Status to CANCELLED]
    J --> L[Send Notification to Patient]
    K --> L

    style A fill:#e3f2fd
    style G fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fce4ec
```

### 4. Authentication & Security Flow
```mermaid
flowchart TD
    A[User Login] --> B[Generate JWT Token]
    B --> C[User Authenticated]
    C --> D[User Actions]
    D --> E{Logout?}
    E -->|Yes| F[Add Token to Blacklist]
    E -->|No| D

    style A fill:#e3f2fd
    style F fill:#ffebee
```

## Key Relationships Summary

### One-to-Many Relationships:
- **Division** → **Districts** (1:N)
- **District** → **Thanas** (1:N)
- **User** → **Appointments** as Patient (1:N)
- **DoctorProfile** → **Appointments** as Doctor (1:N)
- **DoctorProfile** → **DoctorTimeslots** (1:N)
- **User** → **Notifications** (1:N)
- **User** → **TokenBlacklist** (1:N)

### One-to-One Relationships:
- **User** → **DoctorProfile** (1:1, optional for doctors only)

### Many-to-One Relationships:
- **User** → **Division/District/Thana** (N:1 for address)

## Data Flow Scenarios

### 1. Doctor Registration:
1. User registers with type "DOCTOR"
2. DoctorProfile is created linked to User
3. Doctor sets up available timeslots
4. Doctor becomes available for appointments

### 2. Patient Booking:
1. Patient searches for doctors
2. Patient views available timeslots
3. Patient books appointment
4. Appointment record created
5. Notification sent to both doctor and patient

### 3. Location-based Search:
1. Filter users by Division → District → Thana
2. Find doctors in specific locations
3. Show relevant appointment options

This structure ensures data integrity and efficient querying while maintaining clear separation of concerns between different system components.


## Interactive System Flow Diagram

```mermaid
graph LR
    %% User Journey
    START([🚀 System Start]) --> REG{👤 User Registration}

    REG -->|Patient| PAT[🤒 Patient Dashboard]
    REG -->|Doctor| DOC[👨‍⚕️ Doctor Setup]
    REG -->|Admin| ADM[⚙️ Admin Panel]

    %% Doctor Flow
    DOC --> DOCPROF[📋 Create Doctor Profile]
    DOCPROF --> SCHEDULE[⏰ Set Time Slots]
    SCHEDULE --> DOCREADY[✅ Doctor Available]

    %% Patient Flow
    PAT --> SEARCH[🔍 Search Doctors]
    SEARCH --> FILTER[📍 Filter by Location]
    FILTER --> VIEWDOC[👁️ View Doctor Details]
    VIEWDOC --> CHECKTIME[⏰ Check Available Times]
    CHECKTIME --> BOOK[📅 Book Appointment]

    %% Appointment Flow
    BOOK --> CREATEAPPT[➕ Create Appointment]
    CREATEAPPT --> NOTIFY1[🔔 Notify Doctor]
    CREATEAPPT --> NOTIFY2[🔔 Notify Patient]

    DOCREADY --> VIEWAPPT[📋 View Appointments]
    VIEWAPPT --> CONFIRM{✅ Confirm?}
    CONFIRM -->|Yes| APPROVED[✅ Confirmed]
    CONFIRM -->|No| REJECTED[❌ Cancelled]

    APPROVED --> NOTIFYCONF[🔔 Notify Patient]
    REJECTED --> NOTIFYREJ[🔔 Notify Rejection]

    %% Admin Flow
    ADM --> MANAGE[👥 Manage Users]
    MANAGE --> REPORTS[📊 Generate Reports]

    %% Security Flow
    REG --> AUTH[🔐 Authentication]
    AUTH --> JWT[🎫 JWT Token]
    JWT --> ACTIONS[⚡ User Actions]
    ACTIONS --> LOGOUT{🚪 Logout?}
    LOGOUT -->|Yes| BLACKLIST[🚫 Blacklist Token]
    LOGOUT -->|No| ACTIONS

    %% Styling
    classDef startStyle fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:white
    classDef userStyle fill:#2196f3,stroke:#1565c0,stroke-width:2px,color:white
    classDef doctorStyle fill:#ff9800,stroke:#ef6c00,stroke-width:2px,color:white
    classDef appointmentStyle fill:#e91e63,stroke:#ad1457,stroke-width:2px,color:white
    classDef securityStyle fill:#9c27b0,stroke:#6a1b9a,stroke-width:2px,color:white

    class START startStyle
    class REG,PAT,SEARCH,FILTER,VIEWDOC userStyle
    class DOC,DOCPROF,SCHEDULE,DOCREADY,VIEWAPPT doctorStyle
    class BOOK,CREATEAPPT,CHECKTIME,APPROVED,REJECTED appointmentStyle
    class AUTH,JWT,BLACKLIST securityStyle
```

