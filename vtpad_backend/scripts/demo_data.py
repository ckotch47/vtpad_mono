import asyncio
import asyncpg
import uuid

SPACE_ID = '528f8a72-bc35-4237-b502-c3a51f6806b4'
DB_URL = 'postgres://cmsfast:cmsfast@192.168.3.15:5432/vtpad_back'


async def clear_space(conn):
    print("Clearing existing data...")
    await conn.execute(f"""
        DELETE FROM test_result WHERE run_id IN (
            SELECT id FROM test_run WHERE space_id = '{SPACE_ID}'
        )
    """)
    await conn.execute(f"DELETE FROM test_run WHERE space_id = '{SPACE_ID}'")
    await conn.execute(f"""
        DELETE FROM test_case_version WHERE testcase_id IN (
            SELECT id FROM test_case WHERE space_id = '{SPACE_ID}'
        )
    """)
    await conn.execute(f"DELETE FROM test_case WHERE space_id = '{SPACE_ID}'")
    await conn.execute(f"""
        DELETE FROM section WHERE suite_id IN (
            SELECT id FROM test_suite WHERE space_id = '{SPACE_ID}'
        )
    """)
    await conn.execute(f"DELETE FROM test_suite WHERE space_id = '{SPACE_ID}'")
    print("Cleared.")


async def create_demo_data(conn):
    print("Creating demo data...")

    # Suite 1: Authentication
    suite1 = await conn.fetchrow(
        """INSERT INTO test_suite (id, name, description, sort, status, space_id, created_at, updated_at)
           VALUES (gen_random_uuid(), 'Authentication & Authorization',
                   'Complete test coverage for login, registration and password reset flows',
                   10, 'active', $1, NOW(), NOW()) RETURNING id""",
        SPACE_ID
    )
    s1 = str(suite1['id'])

    # Sections for Suite 1
    sec_login = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'Login', 'All login-related scenarios', 10, $1, NOW(), NOW()) RETURNING id",
        s1
    )
    sec_reg = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'Registration', 'Sign-up and email verification', 20, $1, NOW(), NOW()) RETURNING id",
        s1
    )
    sec_reset = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'Password Reset', 'Forgot password flow', 30, $1, NOW(), NOW()) RETURNING id",
        s1
    )

    # Cases for Suite 1 - Login
    await create_case(conn, 'Successful login with valid credentials', 'manual', s1, str(sec_login['id']),
        '<p>Verify that a user can log in with valid email and password.</p>',
        '<p>1. User has a registered account<br>2. Account is active</p>',
        '<p>1. Navigate to /login<br>2. Enter valid email<br>3. Enter valid password<br>4. Click "Sign In"</p>',
        '<p>User is redirected to dashboard. Session token is created.</p>'
    )
    await create_case(conn, 'Login with invalid password', 'manual', s1, str(sec_login['id']),
        '<p>Verify error handling when password is incorrect.</p>',
        '<p>User account exists</p>',
        '<p>1. Navigate to /login<br>2. Enter valid email<br>3. Enter invalid password<br>4. Click "Sign In"</p>',
        '<p>Error message "Invalid credentials" is shown. Account is NOT locked after 1 attempt.</p>'
    )
    await create_case(conn, 'Login form validation', 'checklist', s1, str(sec_login['id']),
        '<p>Verify all validation rules on login form.</p>',
        '<p>Login page is accessible</p>',
        '<p>1. Submit empty form<br>2. Submit with invalid email format<br>3. Submit with password < 6 chars</p>',
        '<p>Appropriate validation messages displayed for each field.</p>'
    )

    # Cases for Suite 1 - Registration
    await create_case(conn, 'Register with valid email', 'manual', s1, str(sec_reg['id']),
        '<p>Verify successful registration with valid data.</p>',
        '<p>Email is not already registered</p>',
        '<p>1. Navigate to /register<br>2. Fill all required fields<br>3. Click "Create Account"</p>',
        '<p>Account created. Verification email sent. User redirected to confirmation page.</p>'
    )
    await create_case(conn, 'Register with existing email', 'manual', s1, str(sec_reg['id']),
        '<p>Verify duplicate email handling.</p>',
        '<p>Email already exists in database</p>',
        '<p>1. Navigate to /register<br>2. Use existing email<br>3. Submit form</p>',
        '<p>Error "Email already registered" shown. No new account created.</p>'
    )

    # Cases for Suite 1 - Password Reset
    await create_case(conn, 'Reset password with valid email', 'manual', s1, str(sec_reset['id']),
        '<p>Verify password reset flow.</p>',
        '<p>User has verified email</p>',
        '<p>1. Click "Forgot password"<br>2. Enter registered email<br>3. Click "Send reset link"</p>',
        '<p>Reset email sent. Token expires in 24 hours.</p>'
    )

    # Suite 2: API Endpoints
    suite2 = await conn.fetchrow(
        """INSERT INTO test_suite (id, name, description, sort, status, space_id, created_at, updated_at)
           VALUES (gen_random_uuid(), 'API Endpoints',
                   'REST API coverage for user and order management',
                   20, 'active', $1, NOW(), NOW()) RETURNING id""",
        SPACE_ID
    )
    s2 = str(suite2['id'])

    sec_users = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'User Management', 'CRUD operations on users', 10, $1, NOW(), NOW()) RETURNING id",
        s2
    )
    sec_orders = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'Order Management', 'Order lifecycle', 20, $1, NOW(), NOW()) RETURNING id",
        s2
    )

    await create_case(conn, 'GET /users returns paginated list', 'automated', s2, str(sec_users['id']),
        '<p>Verify user list endpoint with pagination.</p>',
        '<p>Database has >10 users</p>',
        '<p>1. Send GET /users?page=1&limit=10<br>2. Assert 200 OK<br>3. Assert response has items and total fields</p>',
        '<p>200 OK. JSON with items (max 10) and total count.</p>'
    )
    await create_case(conn, 'POST /users creates user', 'automated', s2, str(sec_users['id']),
        '<p>Verify user creation endpoint.</p>',
        '<p>Valid auth token</p>',
        '<p>1. Send POST /users with valid payload<br>2. Assert 201 Created<br>3. Send GET /users/{id}</p>',
        '<p>201 Created. New user retrievable by ID.</p>'
    )
    await create_case(conn, 'GET /orders with filters', 'automated', s2, str(sec_orders['id']),
        '<p>Verify order filtering by status and date.</p>',
        '<p>Orders with different statuses exist</p>',
        '<p>1. GET /orders?status=pending<br>2. GET /orders?date_from=2024-01-01</p>',
        '<p>Only matching orders returned. Pagination works with filters.</p>'
    )
    await create_case(conn, 'POST /order with invalid data', 'automated', s2, str(sec_orders['id']),
        '<p>Verify validation on order creation.</p>',
        '<p>Auth token present</p>',
        '<p>1. POST /order with missing required fields<br>2. POST /order with negative amount</p>',
        '<p>400 Bad Request with detailed validation errors.</p>'
    )

    # Suite 3: UI/UX
    suite3 = await conn.fetchrow(
        """INSERT INTO test_suite (id, name, description, sort, status, space_id, created_at, updated_at)
           VALUES (gen_random_uuid(), 'UI / UX',
                   'Visual regression and interaction tests',
                   30, 'active', $1, NOW(), NOW()) RETURNING id""",
        SPACE_ID
    )
    s3 = str(suite3['id'])

    sec_nav = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'Navigation', 'Menu, breadcrumbs, routing', 10, $1, NOW(), NOW()) RETURNING id",
        s3
    )
    sec_forms = await conn.fetchrow(
        "INSERT INTO section (id, name, description, sort, suite_id, created_at, updated_at)"
        " VALUES (gen_random_uuid(), 'Forms', 'Validation, auto-save, accessibility', 20, $1, NOW(), NOW()) RETURNING id",
        s3
    )

    await create_case(conn, 'Responsive menu on mobile', 'manual', s3, str(sec_nav['id']),
        '<p>Verify hamburger menu on viewports < 768px.</p>',
        '<p>Mobile device or Chrome DevTools</p>',
        '<p>1. Open site on 375px width<br>2. Tap hamburger icon<br>3. Tap menu item<br>4. Tap outside menu</p>',
        '<p>Menu opens/closes smoothly. Selected page loads. Backdrop blocks interaction.</p>'
    )
    await create_case(conn, 'Breadcrumb navigation', 'manual', s3, str(sec_nav['id']),
        '<p>Verify breadcrumb display and clickability.</p>',
        '<p>User is logged in, at least 2 levels deep</p>',
        '<p>1. Navigate to Space > Suite > Section<br>2. Click parent breadcrumb<br>3. Click root breadcrumb</p>',
        '<p>Breadcrumbs show correct path. Clicks navigate to correct pages.</p>'
    )
    await create_case(conn, 'Form validation messages', 'manual', s3, str(sec_forms['id']),
        '<p>Verify inline validation UX.</p>',
        '<p>Registration form is open</p>',
        '<p>1. Focus email field, blur without input<br>2. Type invalid email<br>3. Submit with empty required fields</p>',
        '<p>Red border + tooltip on blur. Real-time validation on typing. Submit blocked with summary.</p>'
    )
    await create_case(conn, 'Auto-save draft', 'manual', s3, str(sec_forms['id']),
        '<p>Verify draft auto-save on long forms.</p>',
        '<p>User is creating a test case</p>',
        '<p>1. Type title<br>2. Wait 5 seconds<br>3. Refresh page<br>4. Navigate back to form</p>',
        '<p>Draft restored. Toast "Draft saved" shown. No data loss.</p>'
    )

    print("Done! Created 3 suites, 7 sections, 15 test cases.")


async def create_case(conn, title, type_, suite_id, section_id, text, preconditions, steps, expected):
    case_id = await conn.fetchrow(
        """INSERT INTO test_case (
            id, title, text, steps, expected_results, preconditions,
            type, status, sort, space_id, suite_id, section_id, created_at, updated_at
        ) VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, 'active', 10, $7, $8, $9, NOW(), NOW())
        RETURNING id""",
        title, text, steps, expected, preconditions, type_, SPACE_ID, suite_id, section_id
    )
    # Create initial version snapshot
    await conn.execute(
        """INSERT INTO test_case_version (
            id, testcase_id, version_number, title, text, steps, expected_results, preconditions, created_at
        ) VALUES (gen_random_uuid(), $1, 1, $2, $3, $4, $5, $6, NOW())""",
        str(case_id['id']), title, text, steps, expected, preconditions
    )


async def main():
    conn = await asyncpg.connect(DB_URL)
    try:
        await clear_space(conn)
        await create_demo_data(conn)
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
