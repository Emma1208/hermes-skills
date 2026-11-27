# LinkedIn OpenID Connect — working integration notes (2026-07)

## App setup the USER must do (developer console at linkedin.com/developers)
1. Log in with the LinkedIn account to connect.
2. Create app -> needs a linked Company Page (mandatory, can be any page).
3. Auth tab -> copy Client ID and Client Secret.
4. Auth tab -> add redirect URI exactly: http://localhost:8080/
5. Products tab -> request "Sign In with LinkedIn using OpenID Connect".
   Without this, /authorization returns invalid_scope or refuses.

## Auth URL built by agent
https://www.linkedin.com/oauth/v2/authorization
  ?response_type=code
  &client_id=<id>
  &redirect_uri=http://localhost:8080/
  &scope=openid profile email
  &state=hermes_linkedin

## Token exchange (server-side, Python stdlib urllib)
POST to https://www.linkedin.com/oauth/v2/accessToken
content-type x-www-form-urlencoded, body:
grant_type=authorization_code&code=<code>&redirect_uri=http://localhost:8080/&client_id=<id>&client_secret=<secret>
Returns: {access_token, expires_in (~60 days/5184000s), scope, token_type, id_token}

## Profile read
GET https://api.linkedin.com/v2/userinfo with Authorization: Bearer <token>.
Returns OpenID standard claims:
{ "sub", "email_verified", "name", "locale":{country,language},
  "given_name", "family_name", "email", "picture" }
(For Dieudonne Kakesa: name, email kakesamudimba@gmail.com, FR/fr locale, picture URL.)

## HARD CAPABILITY LIMITS — LinkedIn API does NOT support
- Reading full profile (experience, education, skills, connections) -> needs partner
  validation, effectively unavailable to normal apps.
- Editing or arranging the profile -> NOT exposed by any API. Only browser UI.
- Job search -> NO job-search API exists at all.
=> When the user wants read everything / edit my profile / find jobs, tell them the
   API cannot do it; the real path is browser automation (agent drives their logged-in
   session) or guided manual. Do NOT promise API-based profile edits or job search.

## Security
- code is single-use, expires ~30s -> user must paste it immediately.
- access_token ~60 days; flag expiry to the user before it lapses.
- Keep client_secret out of any shared context; saved under ~/.agent/linkedin_app/config.json.
