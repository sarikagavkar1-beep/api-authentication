# Manual security test checklist

Use Postman and record actual results in your submission report.

- [ ] `GET /health` returns 200.
- [ ] Valid login returns 200 and an access token.
- [ ] Invalid password returns 401.
- [ ] Protected profile without token returns 401.
- [ ] Protected profile with a valid token returns 200.
- [ ] Malformed token returns 401.
- [ ] Regular user token on `/api/admin` returns 403.
- [ ] Admin token on `/api/admin` returns 200.
- [ ] Short username or password during registration returns 400.
- [ ] Duplicate username registration returns 409.
