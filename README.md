# API Authentication Learning Lab

A small Flask REST API for an API authentication assignment. It demonstrates password hashing, JSON Web Token (JWT) authentication, protected endpoints, role-based authorization, and security testing with Postman.

> **Educational demo:** users are kept in an in-memory Python dictionary, so registrations disappear when the server restarts. Do not deploy this demo as-is. A production system should use a database, HTTPS, rate limiting, monitoring, secret management, and a reviewed identity design.

## 1. Requirements

- Python 3.10 or newer
- pip
- Postman (optional but recommended)
- Git and a GitHub account for submission

## 2. Run on Windows PowerShell

Open PowerShell in this project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
python app.py
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000/`. Keep the terminal running while testing.

Demo credentials:
- Regular user: `student` / `Student@123`
- Administrator: `admin` / `Admin@123`

These are intentionally simple classroom credentials. Never reuse them outside this local demo.

## 3. Test with Postman

Import `postman/API-Authentication-Lab.postman_collection.json` into Postman. Set collection variable `baseUrl` to `http://127.0.0.1:5000`.

Recommended order:
1. **Health check** — expected `200`.
2. **Login - regular user** — expected `200`; copy `access_token` from response.
3. **Profile - without token** — expected `401`.
4. **Profile - with token** — set `access_token` collection variable to the token returned by login; expected `200`.
5. **Admin - regular user token** — expected `403`.
6. **Login - admin** — expected `200`; copy admin token into `admin_token`.
7. **Admin - with admin token** — expected `200`.
8. **Login - wrong password** — expected `401`.
9. **Register a new user** — expected `201` (change username if repeating).
10. **Profile - malformed token** — expected `401`.

For protected calls, use the header:
`Authorization: Bearer YOUR_ACCESS_TOKEN`

Do not paste tokens into public repositories, screenshots, or assignment reports.

## 4. API endpoint summary

| Method | Endpoint | Purpose | Expected result |
|---|---|---|---|
| GET | `/` | API overview | 200 |
| GET | `/health` | Health check | 200 |
| POST | `/register` | Register demo account | 201, or 400/409 |
| POST | `/login` | Verify credentials and issue JWT | 200, or 401 |
| GET | `/api/profile` | Protected profile resource | 200 with token; 401 without/invalid token |
| GET | `/api/admin` | Role-restricted resource | 200 for admin; 403 for regular user |

### Example login request

`POST http://127.0.0.1:5000/login`

```json
{
  "username": "student",
  "password": "Student@123"
}
```

Successful response includes an `access_token`. Send it in the `Authorization` header as `Bearer <token>` for the protected endpoint.

### Example registration request

`POST http://127.0.0.1:5000/register`

```json
{
  "username": "newstudent",
  "password": "StrongPass123!"
}
```

## 5. Assignment theory: API authentication

### What is API authentication, and why does it matter?

Authentication verifies the identity of a client or user making an API request. Authorization is a separate decision about what that authenticated identity is allowed to do. An API that exposes private records, account details, or administrative actions without appropriate checks can leak data or allow unauthorized changes. Authentication, authorization, transport security, input validation, and monitoring work together to reduce that risk.

### Common authentication approaches

**API keys:** A client sends a unique key, commonly in a request header. They are straightforward for identifying applications or server-to-server access, but a key alone often does not represent an end user, and leaked keys can be abused. Restrict scope, rotate keys, and never put secret keys in public frontend code.

**Basic authentication:** A client sends a username and password encoded with Base64. Base64 is not encryption, so Basic authentication must be protected by HTTPS and is generally less suitable than modern delegated flows for user-facing integrations.

**Session/cookie authentication:** After login, a server creates a session and sends a session identifier in a cookie. The server tracks the session. Secure cookie settings (`HttpOnly`, `Secure`, and appropriate `SameSite`) matter; cookie-based applications also need a CSRF strategy.

**Token-based authentication:** After valid credentials are supplied, the server issues a token. The client presents the token on later requests, commonly in `Authorization: Bearer <token>`. The server validates the token before allowing access. This project uses a signed JWT access token with an expiration time. A signed JWT is not encrypted by default, so do not place secrets in its payload.

**OAuth 2.0:** OAuth 2.0 is an authorization framework that lets a user authorize an application to access limited resources without sharing their password with that application. For example, a calendar application may obtain permission to read a user's calendar from a provider. The application receives access tokens with defined scopes. Use Authorization Code with PKCE for modern public clients such as browser/mobile apps; use an appropriate confidential-client flow for server-side applications. OAuth itself is primarily about delegated authorization. OpenID Connect (OIDC) adds an identity layer for sign-in.

### Token-based authentication vs OAuth

Token-based authentication describes a broad pattern: a token is issued and later presented to access an API. OAuth 2.0 specifies a standardized delegated-authorization framework, including roles, grants, scopes, and token handling. An OAuth access token may be opaque or a JWT. A home-grown login endpoint that issues a JWT, as in this project, is a learning example; it is **not** a complete OAuth implementation.

### How this demo works

1. The client submits a username and password to `/login`.
2. The API compares the submitted password with a stored password hash.
3. On success, the API signs a JWT containing the subject, role, issued-at time, and expiry.
4. The client sends the JWT as a Bearer token on protected requests.
5. The API verifies the signature and expiration, then checks the role for admin-only resources.
6. Requests with missing/invalid tokens receive `401 Unauthorized`; a valid regular-user token for the admin endpoint receives `403 Forbidden`.

## 6. Security best practices

- Use HTTPS in deployed environments; do not send credentials or tokens over plain HTTP on public networks.
- Store secrets in environment variables or a secrets manager. Never commit `.env` or production secrets.
- Hash passwords with a modern password-hashing function; never store plaintext passwords.
- Validate input and return generic login errors to reduce username enumeration.
- Set short access-token lifetimes and design revocation/refresh behavior before production use.
- Verify token signatures, expiry, issuer/audience where applicable, and allow only expected algorithms.
- Apply authorization checks on every protected resource; authentication alone is not permission.
- Add rate limiting and monitoring for login attempts; consider MFA for sensitive accounts.
- Avoid logging passwords, API keys, Authorization headers, or complete tokens.
- Keep dependencies updated and run security tests.
- For cookie-based auth, use appropriate cookie flags and CSRF protection.
- Use OAuth/OIDC libraries and provider documentation rather than implementing the protocol from scratch.

## 7. Common implementation pitfalls

- Treating Base64 as encryption.
- Storing plaintext passwords or hard-coded production secrets.
- Accepting tokens without checking signature or expiration.
- Allowing a client to choose its own role during registration.
- Confusing `401` (authentication missing/invalid) with `403` (authenticated but not permitted).
- Placing tokens in URLs, where they can leak through logs and browser history.
- Putting private API secrets in frontend JavaScript or a public GitHub repository.
- Assuming a JWT is encrypted, revocable by default, or automatically safe because it is signed.
- Building a custom OAuth flow instead of using a vetted provider/library.
- Forgetting rate limits, account lockout/risk controls, logging hygiene, or dependency updates.

## 8. Suggested practical security test report

Record each test in your report with the request, expected result, actual result, and a screenshot from Postman.

| Test | Expected status | What it demonstrates |
|---|---:|---|
| Login with valid user | 200 | Valid credentials receive a token |
| Login with wrong password | 401 | Invalid credentials are rejected |
| Call profile without token | 401 | Protected route denies anonymous access |
| Call profile with malformed token | 401 | Invalid token is rejected |
| Call profile with valid token | 200 | Token enables access |
| Call admin endpoint with regular token | 403 | Role-based authorization works |
| Call admin endpoint with admin token | 200 | Authorized admin succeeds |
| Register username shorter than 3 chars | 400 | Input validation works |
| Register same username twice | 409 | Duplicate account is rejected |

## 9. GitHub submission steps

1. Create a new repository on GitHub, for example `api-authentication-assignment`.
2. Do not initialize it with a README if you already have this project README, or resolve the merge if you do.
3. Extract the ZIP and open the extracted folder in VS Code.
4. Open **Terminal → New Terminal** in VS Code.
5. Run the following commands, replacing the URL with your repository URL:

```bash
git init
git add .
git status
git commit -m "Add API authentication assignment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/api-authentication-assignment.git
git push -u origin main
```

6. Open the repository page on GitHub and confirm `app.py`, `README.md`, `requirements.txt`, and the `postman` folder are visible.
7. Copy the repository URL from the browser and submit that real URL to your instructor. The ZIP download itself is not a GitHub repository link.

Before pushing, check that `.env`, access tokens, passwords for real accounts, and other secrets are not included.

## References

- Flask quickstart: https://flask.palletsprojects.com/en/stable/quickstart/
- Flask-Security token authentication: https://flask-security.readthedocs.io/en/latest/features.html
- Flask-Security security patterns: https://flask-security.readthedocs.io/en/latest/patterns.html
- Python password hashing guidance: https://docs.python.org/3/library/hashlib.html
- OAuth 2.0 Security Best Current Practice (RFC 9700): https://www.rfc-editor.org/rfc/rfc9700.html
- JWT specification (RFC 7519): https://www.rfc-editor.org/rfc/rfc7519.html
