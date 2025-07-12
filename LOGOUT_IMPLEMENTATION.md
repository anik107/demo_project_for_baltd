# Logout Implementation Documentation

## Overview

The logout functionality has been implemented with a token blacklist approach to ensure proper session management and security.

## Features Implemented

### 1. Token Blacklisting
- Added `TokenBlacklist` model to track revoked tokens
- Tokens are blacklisted until their natural expiration time
- Automatic cleanup of expired blacklisted tokens

### 2. Enhanced JWT Tokens
- Added JWT ID (jti) claim to all tokens for unique identification
- Updated `create_access_token()` to include jti
- Enhanced token verification to check blacklist status

### 3. Logout Endpoint
- **Endpoint**: `POST /auth/logout`
- **Authentication**: Requires Bearer token in Authorization header
- **Response**: Returns success message and status

### 4. Security Dependencies
- Added `get_current_user()` dependency for protected routes
- Automatic token blacklist checking
- Proper error handling for invalid/expired tokens

## API Usage

### Logout Request
```http
POST /auth/logout
Authorization: Bearer <your_jwt_token>
```

### Logout Response
```json
{
  "message": "Successfully logged out",
  "success": true
}
```

### Error Responses
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Server-side logout failure

## Database Schema Changes

### New Table: `token_blacklist`
```sql
CREATE TABLE token_blacklist (
    id INTEGER PRIMARY KEY,
    token_jti VARCHAR UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Security Benefits

1. **Session Termination**: Tokens are immediately invalidated upon logout
2. **Replay Attack Prevention**: Blacklisted tokens cannot be reused
3. **Cleanup**: Expired tokens are automatically removed from blacklist
4. **Scalability**: Efficient blacklist checking with indexed jti field

## Usage in Client Applications

### JavaScript Example
```javascript
// Logout function
async function logout() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            // Remove token from client storage
            localStorage.removeItem('access_token');
            // Redirect to login page
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout failed:', error);
    }
}
```

### Python Client Example
```python
import requests

def logout(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('/auth/logout', headers=headers)
    return response.status_code == 200
```

## Testing

Use the provided test script to verify logout functionality:

```bash
python test_logout.py
```

## Maintenance

### Token Cleanup
The system includes a `cleanup_expired_blacklisted_tokens()` function that should be called periodically (e.g., via cron job) to keep the blacklist table clean:

```python
from auth_utils import cleanup_expired_blacklisted_tokens
from database import SessionLocal

def cleanup_task():
    db = SessionLocal()
    try:
        cleanup_expired_blacklisted_tokens(db)
    finally:
        db.close()
```

## Best Practices

1. **Client-Side**: Always remove tokens from client storage after logout
2. **Error Handling**: Handle 401 responses by redirecting to login
3. **Token Refresh**: Implement token refresh for better user experience
4. **Cleanup**: Run periodic cleanup to maintain performance
5. **Monitoring**: Log logout events for security auditing
