# Hello Miami Messaging App Project Specs

## Project Overview
The Hello Miami Messaging App is a comprehensive system for event check-ins, CRM, SMS and email blasting, and 1:1 conversation services. It includes a web app for user interactions and a Raspberry Pi-connected label printer for name tag printing.

## System Components
1. Frontend (Solid.js)
2. Backend API (FastAPI)
3. Database (Supabase)
4. SMS Service (Twilio)
5. Email Service (TBD)
6. Raspberry Pi Label Printer (hello-miami-pi)

## Features
1. Event Check-in
   - QR code scanning
   - Phone number verification
   - OTP via SMS
   - New user registration
   - Name tag printing
   - Check-in time recording
2. CRM functionality
   - Contact management
   - Interaction logging (notes, file uploads)
   - Contact segmentation
3. User Profiles
   - Bio
   - Self-uploaded avatar
   - LinkedIn and GitHub links
4. SMS and email blasting
5. 1:1 SMS conversations
6. Admin Dashboard
   - User management
   - Contact management
   - Message template editing

## Tech Stack
- Backend: FastAPI, Pydantic, Supabase
- Frontend: Solid.js
- SMS: Twilio
- Email: TBD
- Label Printing: CUPS on Raspberry Pi

## Solid.js Components
1. EventCheckIn
   - QRCodeScanner: For scanning QR codes
   - PhoneNumberInput: For entering phone numbers
   - OTPInput: For entering OTP codes
   - RegistrationForm: For new user registration
2. AdminDashboard
   - UserManagement: For managing admin users
   - ContactManagement: For managing contacts
   - MessageTemplateEditor: For editing message templates
3. CRM
   - ContactList: For displaying and filtering contacts
   - ContactDetails: For viewing and editing contact information
   - InteractionLog: For logging and displaying interactions
   - FileUpload: For uploading files to interactions
4. Messaging
   - MessageComposer: For composing SMS and email messages
   - BlastCreator: For creating and managing blast campaigns
   - ConversationView: For displaying 1:1 SMS conversations
5. UserProfile
   - ProfileEditor: For editing user profiles
   - AvatarUploader: For uploading profile avatars
6. Common
   - Navbar: For navigation
   - AuthenticationWrapper: For handling protected routes
   - NotificationSystem: For displaying system notifications

## Data Models
1. User (Admin users)
2. Contact (Event attendees)
3. Profile (Extended information for contacts)
4. Interaction (CRM-style notes and updates)
5. CheckIn (Event attendance records)
6. Message (SMS and Email messages)
7. Blast (Bulk messaging campaigns)

## New Endpoints
1. Event Check-in
   - POST /check-in: Handle check-in process
   - GET /check-in/{phone_number}: Get contact and profile info
   - POST /check-in/complete: Complete check-in and trigger name tag printing
2. User Management
   - POST /users: Create new admin user
   - GET /users: List admin users
   - PUT /users/{user_id}: Update admin user
   - DELETE /users/{user_id}: Delete admin user
3. Profile Management
   - POST /profiles: Create new profile
   - GET /profiles/{contact_id}: Get profile for a contact
   - PUT /profiles/{profile_id}: Update profile
4. Interactions
   - POST /interactions: Create new interaction
   - GET /interactions/{contact_id}: Get interactions for a contact
   - PUT /interactions/{interaction_id}: Update interaction
5. Webhooks
   - POST /webhooks/twilio: Handle Twilio webhook for real-time SMS responses and analytics

## Authentication and Authorization
- Implement JWT-based authentication for admin users
- Add middleware for protected routes
- Implement role-based access control (RBAC) for different admin levels


## Printer Setup
1. Connect the label printer to the Raspberry Pi
2. Install and configure CUPS on the Raspberry Pi
3. Set up the printer with the following specifications:
   - Media size: 2x4 inches (Custom.2x4in)
   - Orientation: Landscape
   - Print quality: Adjust based on printer capabilities

## Development Process
1. Update database models and create migrations
2. Implement new endpoints and modify existing ones
3. Create admin dashboard frontend
4. Implement event check-in flow in frontend
5. Set up webhook handling for Twilio
6. Implement authentication and authorization
7. Enhance contact segmentation features
8. Implement file upload functionality for interactions
9. Set up real-time updates using Supabase realtime features
10. Comprehensive testing of new features
11. Documentation update

## Suggested Prompts for Development
1. "Update SQLAlchemy models for User, Contact, Profile, Interaction, and CheckIn"
2. "Implement JWT authentication and protected routes in FastAPI"
3. "Create event check-in endpoints and logic"
4. "Develop Solid.js components for event check-in flow"
5. "Implement file upload functionality for interactions"
6. "Set up Twilio webhook handling for real-time SMS responses"
7. "Create admin dashboard components in Solid.js"
8. "Implement contact segmentation features in backend and frontend"
9. "Set up real-time updates using Supabase for live interaction logging"
10. "Implement comprehensive unit and integration tests for new features"

## Deployment Considerations
1. Set up CI/CD pipeline for automated testing and deployment
2. Configure proper environment variables for production
3. Set up monitoring and logging for production environment
4. Implement rate limiting and other security measures
5. Ensure GDPR compliance for data handling

1. FastAPI: The main web framework used for building the API. It's used in the `main.py` file to define routes and handle HTTP requests.

2. Pydantic: Used for data validation and settings management. It's integrated with FastAPI for request/response models and is used in `schemas.py` to define data models.

3. SQLAlchemy: An ORM (Object-Relational Mapping) tool used to interact with the database. It's used in `models.py` to define database models and in various query files for database operations.

4. Alembic: A database migration tool used with SQLAlchemy. While not directly visible in the provided code snippets, it's listed in the `requirements.txt` file and is typically used for managing database schema changes.

5. Supabase: A Firebase alternative providing a Postgres database with real-time capabilities. The `supabase_client.py` file sets up the Supabase client for database operations.

6. Twilio: Used for SMS functionality. It's integrated in the `twilio_helpers.py` file (not shown in the snippets but referenced in `blasts.py`).

7. MailerSend: Likely used for email functionality, as referenced in `mailersend_helpers.py` (not shown in the snippets but referenced in `blasts.py`).

8. CORS Middleware: Implemented in `main.py` to handle Cross-Origin Resource Sharing.

9. Asyncio: Used for asynchronous programming, particularly in database operations and API endpoints.

10. pycups: Used for printing labels on the Raspberry Pi.

11. psycopg3: Used for interacting with the Supabase PostgreSQL database.

These tools interact in the following ways:
- FastAPI provides the web framework, using Pydantic for data validation.
- SQLAlchemy models (in `models.py`) define the database schema, which is used by FastAPI routes to interact with the database.
- The Supabase client is used as an alternative or complement to direct SQLAlchemy operations for certain database interactions.
- Alembic would be used to manage changes to the SQLAlchemy models over time.
- Twilio and MailerSend are used within the application logic to send SMS and emails, respectively.



This setup allows you to use SQLAlchemy's ORM features with Supabase's PostgreSQL database, while still maintaining the ability to use Supabase's client for other features like authentication and real-time subscriptions.

Note that when using SQLAlchemy with Supabase, you're bypassing some of Supabase's built-in features like row-level security. Make sure to implement appropriate security measures in your application logic.

For complex queries or operations that are more efficiently handled by Supabase's client, you can still use the Supabase client alongside SQLAlchemy in your application.

## SQLAlchemy Implementation with Supabase

The project uses SQLAlchemy's async features to interact with the Supabase PostgreSQL database. The `database.py` file sets up the async engine, session maker, and provides a `Database` class with methods for managing database connections and sessions.

Key points:
- Uses `create_async_engine` for asynchronous database operations
- Implements a `get_db` method as an async generator for dependency injection in FastAPI routes
- Provides a `test_connection` method to verify database connectivity
- Uses environment variables to securely store and access the database URL

To use the database in FastAPI routes:
1. Import the `db` instance from `database.py`
2. Use `Depends(db.get_db)` to inject a database session into your route functions
3. Use the session to execute database queries asynchronously

This setup allows for efficient, asynchronous database operations while working with Supabase, and maintains the ability to use SQLAlchemy's ORM features.
