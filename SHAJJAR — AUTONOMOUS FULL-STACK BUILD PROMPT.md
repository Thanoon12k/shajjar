# SHAJJAR — AUTONOMOUS FULL-STACK BUILD PROMPT
## Claude Code / Codex / Coding Agent Execution Specification

You are an autonomous Senior Software Architect, Senior Flutter Engineer, Senior Django Engineer, DevOps Engineer, QA Engineer, and Security Reviewer.

Your task is to build a complete, working, production-oriented MVP named:

# شجّر — Shajjar

This is an environmental operations platform for tree planting campaigns, environmental reporting, tree tracking, volunteers, planting sites, campaigns, and long-term tree follow-up.

You are not creating a mockup.

You are not creating only UI screens.

You are not creating a proof of concept.

You must create the actual working project.

---

# 0. CORE EXECUTION RULE

You have access to the local project directory and terminal.

Use them.

DO NOT merely explain what should be done.

Actually:

- create files
- edit files
- install dependencies
- create projects
- generate migrations
- run migrations
- run tests
- start services when appropriate
- inspect errors
- fix errors
- rerun tests
- update documentation
- maintain project status

Continue autonomously.

Do not stop after each phase asking for permission.

Do not ask questions unless progress is genuinely impossible without external credentials or an irreversible product decision.

When something is unspecified:

choose the simplest reliable production-oriented solution,

document the decision,

and continue.

---

# 1. PRIMARY OBJECTIVE

Build a complete repository containing:

```text
shajjar/
│
├── backend/
│
├── mobile/
│
├── docs/
│
├── scripts/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── PROJECT_STATUS.md
├── CHANGELOG.md
└── Makefile
```

The final application must include:

- Django backend
- Django REST Framework APIs
- PostgreSQL support
- JWT authentication
- Flutter mobile app
- Arabic RTL support
- OpenStreetMap
- planting locations
- tree requests
- tree tracking
- tree follow-up updates
- environmental reports
- campaigns
- volunteering
- notifications architecture
- administration
- analytics
- seed data
- automated tests
- Docker
- documentation
- production configuration
- Android release preparation

---

# 2. PRODUCT PHILOSOPHY

Shajjar is NOT primarily a social networking application.

It is an:

# Environmental Operations Platform

The central workflow is:

```text
طلب
 ↓
موافقة
 ↓
توزيع
 ↓
زراعة
 ↓
توثيق
 ↓
متابعة
 ↓
حماية
 ↓
قياس الأثر
```

Every major feature should support one or more of these objectives.

Avoid unnecessary social-media functionality.

---

# 3. TARGET USERS

Initially:

- Mosul
- Nineveh
- Iraq

Future architecture should allow use across all Iraqi governorates.

User types:

- guest
- citizen
- volunteer
- field supervisor
- admin
- super admin

---

# 4. TECHNOLOGY STACK

Use this stack unless a serious compatibility problem requires a change.

## Backend

Python 3.12+

Django

Django REST Framework

SimpleJWT

django-filter

drf-spectacular

Pillow

django-cors-headers

PostgreSQL

Gunicorn

pytest / pytest-django if appropriate

## Mobile

Flutter stable

Dart

Material 3

Riverpod

Dio

go_router

flutter_secure_storage

shared_preferences

flutter_map

latlong2

image_picker

image compression package

intl

freezed/json_serializable only if they simplify maintainability.

Do not introduce excessive code generation unless useful.

## Maps

OpenStreetMap

flutter_map

Avoid mandatory paid Google Maps dependencies.

## Notifications

Create Firebase Cloud Messaging integration architecture.

Application must continue functioning without Firebase credentials.

## Development Database

PostgreSQL through Docker.

SQLite may be temporarily useful for isolated tests but PostgreSQL must be the normal development target.

---

# 5. INITIAL TERMINAL PROCEDURE

Before coding:

1. Inspect current directory.

2. If the repository is empty, initialize project structure.

3. Initialize Git if not initialized.

4. Check installed versions:

```bash
python --version
pip --version
flutter --version
dart --version
docker --version
docker compose version
git --version
```

5. Record relevant environment information in:

```text
docs/DEVELOPMENT_ENVIRONMENT.md
```

Do not fail the entire build just because optional software such as Docker or Flutter is missing.

If something is unavailable:

document it,

continue with everything that can be completed,

and mark the unavailable verification clearly in PROJECT_STATUS.md.

---

# 6. CREATE PROJECT STATUS FIRST

Before implementing functionality create:

```text
PROJECT_STATUS.md
```

Use this structure:

```markdown
# Shajjar Project Status

## Overall Status

## Current Phase

## Completed

## In Progress

## Pending

## Tests

### Backend
### Flutter
### Integration

## Known Issues

## External Credentials Needed

## Last Verification
```

Update this file after every major phase.

Never allow PROJECT_STATUS.md to become stale.

---

# 7. CREATE IMPLEMENTATION PLAN

Create:

```text
docs/IMPLEMENTATION_PLAN.md
```

Divide implementation into:

Phase 0 — Environment & repository

Phase 1 — Backend foundation

Phase 2 — Database design

Phase 3 — Authentication & authorization

Phase 4 — Species and planting locations

Phase 5 — Tree request workflow

Phase 6 — Trees and follow-up

Phase 7 — Environmental reports

Phase 8 — Campaigns and volunteers

Phase 9 — Content and contribution information

Phase 10 — Notifications

Phase 11 — Analytics and administration

Phase 12 — Flutter foundation

Phase 13 — Flutter authentication

Phase 14 — Flutter core screens

Phase 15 — Flutter map

Phase 16 — Flutter requests

Phase 17 — Flutter trees

Phase 18 — Flutter reports

Phase 19 — Flutter campaigns

Phase 20 — Testing

Phase 21 — Security review

Phase 22 — Docker & deployment

Phase 23 — Android release preparation

Phase 24 — Final verification

---

# 8. BACKEND PROJECT CREATION

Create Python virtual environment if appropriate.

Example:

```bash
python -m venv .venv
```

Activate according to OS.

Install dependencies.

Create:

```text
backend/
```

Inside backend create Django project:

```text
config
```

Create logical Django applications:

```text
core
accounts
species
locations
trees
tree_requests
tree_updates
environmental_reports
campaigns
notifications
content
analytics
```

Do not create one giant Django app.

---

# 9. BACKEND DEPENDENCY MANAGEMENT

Create:

```text
backend/requirements/base.txt
backend/requirements/dev.txt
backend/requirements/prod.txt
```

Base includes runtime dependencies.

Development includes testing/linting tools.

Production includes Gunicorn and production-specific packages.

Also provide optionally:

```text
backend/requirements.txt
```

that references base requirements or contains the normal development set.

---

# 10. DJANGO SETTINGS

Split settings if maintainable:

```text
config/settings/base.py
config/settings/development.py
config/settings/production.py
```

Use environment variables.

Never hardcode:

- SECRET_KEY
- database credentials
- production hosts
- external credentials

Create backend:

```text
.env.example
```

with:

```text
DJANGO_SETTINGS_MODULE=
DEBUG=
SECRET_KEY=
ALLOWED_HOSTS=
DATABASE_URL=
CORS_ALLOWED_ORIGINS=
TIME_ZONE=Asia/Baghdad
MEDIA_ROOT=
MEDIA_URL=
FCM_ENABLED=
```

Database timestamps should use Django timezone awareness.

Display time should use:

```text
Asia/Baghdad
```

---

# 11. CUSTOM USER MODEL

Create the custom user model BEFORE initial migrations.

Fields:

```text
id
email
phone_number
full_name
profile_image
governorate
city
district
role
is_verified
is_active
is_staff
date_joined
updated_at
```

Roles:

```text
citizen
volunteer
supervisor
admin
super_admin
```

Use proper Django custom user architecture.

Use either email or phone as primary identifier.

Prefer email for MVP authentication if it reduces complexity.

Phone remains supported in profile architecture.

---

# 12. ROLE-BASED AUTHORIZATION

Create reusable DRF permissions:

```text
IsAdmin
IsSupervisor
IsAdminOrSupervisor
IsOwnerOrAdmin
IsVolunteer
```

Never rely exclusively on Flutter UI hiding buttons.

Every sensitive operation must be protected server-side.

---

# 13. DATABASE MODELS

Implement carefully normalized models.

---

# 13.1 TreeSpecies

Fields:

```text
id
arabic_name
english_name
scientific_name
description
image
heat_tolerance
water_requirement
growth_speed
shade_level
suitable_for_streets
suitable_for_gardens
suitable_for_farms
suitable_for_public_spaces
bird_friendly
notes
is_active
created_at
updated_at
```

---

# 13.2 PlantingSite

Fields:

```text
id
name
governorate
city
district
latitude
longitude
description
organization
planting_date
total_trees
alive_trees
damaged_trees
dead_trees
cover_image
status
created_by
created_at
updated_at
```

Statuses:

```text
active
needs_attention
completed
inactive
```

---

# 13.3 PlantingBatch

Fields:

```text
id
batch_code
planting_site
species
quantity
planting_date
responsible_entity
watering_entity
notes
created_at
updated_at
```

Automatically generate batch codes if missing.

Example:

```text
BAT-2026-000001
```

---

# 13.4 Tree

Fields:

```text
id
tree_code
batch
species
latitude
longitude
planting_date
owner
caretaker
height_cm
health_status
status
last_update_at
qr_identifier
created_at
updated_at
```

Health:

```text
excellent
good
needs_care
damaged
dead
```

Status:

```text
active
dead
replaced
removed
```

Generate identifier:

```text
SHJ-T-000001
```

or yearly equivalent.

---

# 13.5 TreeRequest

Fields:

```text
id
request_code
user
location_type
requested_tree_count
approved_tree_count
watering_commitment
latitude
longitude
address_description
governorate
city
district
notes
status
assigned_supervisor
distribution_date
internal_notes
created_at
updated_at
```

Statuses:

```text
submitted
under_review
approved
rejected
ready_for_distribution
distributed
planted
completed
```

Generate:

```text
REQ-2026-000001
```

---

# 13.6 TreeRequestImage

Multiple images per request.

Fields:

```text
tree_request
image
created_at
```

Maximum approximately 5 per request.

Validate server side.

---

# 13.7 TreeUpdate

Fields:

```text
id
tree
user
photo
height_cm
health_status
notes
latitude
longitude
verified
verified_by
created_at
```

---

# 13.8 EnvironmentalReport

Fields:

```text
id
report_code
reporter
category
title
description
latitude
longitude
address_description
status
priority
assigned_to
public_note
internal_notes
hide_reporter_identity
created_at
updated_at
```

Categories:

```text
tree_cutting
fire
green_area_destruction
illegal_hunting
waste
pollution
wildlife_harm
tree_damage
other
```

Statuses:

```text
submitted
under_review
verified
forwarded
in_progress
resolved
rejected
duplicate
```

Priority:

```text
low
normal
high
urgent
```

Generate:

```text
ENV-2026-000001
```

---

# 13.9 EnvironmentalReportMedia

Fields:

```text
report
file
media_type
created_at
```

Support image primarily.

Video support may be limited in MVP if complexity is significant.

---

# 13.10 Campaign

Fields:

```text
id
title
description
cover_image
location_name
latitude
longitude
start_date
end_date
registration_deadline
target_tree_count
volunteers_needed
organization
status
created_by
created_at
updated_at
```

Statuses:

```text
draft
published
registration_closed
active
completed
cancelled
```

---

# 13.11 CampaignParticipant

Fields:

```text
campaign
user
status
check_in_time
check_out_time
volunteer_hours
trees_planted
notes
registered_at
```

Statuses:

```text
registered
approved
attended
absent
completed
cancelled
```

Unique constraint:

```text
campaign + user
```

---

# 13.12 Notification

Fields:

```text
user
title
body
type
related_object_type
related_object_id
is_read
created_at
```

---

# 13.13 ArticleCategory

Fields:

```text
name
slug
is_active
```

---

# 13.14 ContentArticle

Fields:

```text
title
slug
summary
body
cover_image
category
author
published_at
is_published
created_at
updated_at
```

Categories may include:

- tree planting
- tree care
- environmental awareness
- wildlife
- pollution
- environmental laws

---

# 13.15 ContributionMethod

Do not implement payments initially.

Fields:

```text
name
description
account_information
qr_image
instructions
is_active
sort_order
```

Never hardcode financial information in Flutter.

---

# 14. MODEL VALIDATION

Use model validation and serializer validation.

Examples:

Tree request:

```text
requested_tree_count > 0
```

Approved count cannot exceed sensible limits.

Latitude:

```text
-90 <= latitude <= 90
```

Longitude:

```text
-180 <= longitude <= 180
```

Tree update height:

must not be negative.

Campaign registration:

must occur before deadline.

Environmental report:

description must contain useful information.

---

# 15. DATABASE INDEXES

Add indexes to frequently searched fields:

```text
request_code
report_code
tree_code
batch_code
status
created_at
city
district
planting_date
```

Use database constraints when suitable.

---

# 16. MIGRATIONS

After creating models:

run:

```bash
python manage.py makemigrations
python manage.py migrate
```

If migration fails:

inspect the actual error,

fix the model/configuration,

rerun.

Never mark migration phase complete while errors remain.

---

# 17. DJANGO ADMIN

Configure useful Django Admin pages.

Add:

- list_display
- filters
- search
- autocomplete fields
- read-only identifiers
- bulk actions where safe

Admin must support:

Tree Requests

Trees

Updates

Reports

Campaigns

Users

Species

Planting Sites

Content

Notifications

Contribution Methods

Provide admin actions such as:

Approve request

Reject request

Mark distributed

Verify tree update

Mark report resolved

Publish campaign

Do not create dangerous bulk delete actions unnecessarily.

---

# 18. AUTHENTICATION API

Implement:

```text
POST /api/v1/auth/register/
POST /api/v1/auth/login/
POST /api/v1/auth/refresh/
POST /api/v1/auth/logout/
GET  /api/v1/auth/me/
PATCH /api/v1/auth/me/
POST /api/v1/auth/change-password/
```

If password reset requires external email infrastructure:

implement token/service architecture,

document required email configuration,

but do not block the rest of development.

---

# 19. API RESPONSE STANDARD

Prefer consistent format:

Success:

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

Errors:

```json
{
  "success": false,
  "message": "حدث خطأ",
  "errors": {}
}
```

Do not sacrifice normal DRF behavior if wrapping every response causes excessive complexity.

If choosing standard DRF response bodies instead:

document the choice clearly.

Consistency matters more than arbitrary wrapping.

---

# 20. REST API ENDPOINTS

Implement at least:

## Species

```text
GET /api/v1/species/
GET /api/v1/species/{id}/
```

## Planting Sites

```text
GET /api/v1/planting-sites/
GET /api/v1/planting-sites/{id}/
```

Support filtering:

```text
city
district
status
species
year
```

## Tree Requests

```text
POST /api/v1/tree-requests/
GET /api/v1/tree-requests/my/
GET /api/v1/tree-requests/{id}/
```

Admin endpoints may use protected ViewSets.

## Trees

```text
GET /api/v1/trees/my/
GET /api/v1/trees/{id}/
GET /api/v1/trees/public/{tree_code}/
POST /api/v1/trees/{id}/updates/
```

## Environmental Reports

```text
POST /api/v1/environmental-reports/
GET /api/v1/environmental-reports/my/
GET /api/v1/environmental-reports/{id}/
```

## Campaigns

```text
GET /api/v1/campaigns/
GET /api/v1/campaigns/{id}/
POST /api/v1/campaigns/{id}/join/
POST /api/v1/campaigns/{id}/leave/
```

## Notifications

```text
GET /api/v1/notifications/
POST /api/v1/notifications/{id}/read/
POST /api/v1/notifications/read-all/
```

## Content

```text
GET /api/v1/articles/
GET /api/v1/articles/{slug}/
```

## Contribution

```text
GET /api/v1/contribution-methods/
```

---

# 21. FILTERING & PAGINATION

Use pagination.

Default:

```text
20
```

Maximum:

```text
100
```

Provide useful:

- filtering
- search
- ordering

Avoid returning massive unrestricted datasets.

---

# 22. OPENAPI

Configure drf-spectacular.

Expose:

```text
/api/schema/
/api/docs/
```

Verify OpenAPI generation.

---

# 23. MEDIA SECURITY

For uploads:

Allow appropriate MIME types.

Validate:

- file size
- extension
- MIME type

Images:

```text
jpg
jpeg
png
webp
```

Set sensible size limits.

Do not trust user supplied filenames.

Use generated paths.

---

# 24. RATE LIMITING

Configure DRF throttling.

Environmental reports should have stronger protection.

Example:

authenticated ordinary API:

reasonable daily/minute limits.

Report creation:

protect from automated flooding.

Do not make legitimate citizen reporting frustrating.

---

# 25. AUDIT LOG

Create an AuditLog model or equivalent service.

Fields:

```text
actor
action
object_type
object_id
metadata
created_at
```

Record significant admin actions:

- request approval
- request rejection
- tree marked dead
- report status changed
- campaign change
- user blocking

Do not log passwords or JWT tokens.

---

# 26. ANALYTICS API

Create protected analytics endpoints.

At minimum calculate:

```text
total trees
healthy trees
damaged trees
dead trees
survival rate
total planting sites
pending requests
reports by status
campaign count
volunteer count
```

Formula:

```text
survival_rate =
alive / total * 100
```

Handle zero safely.

---

# 27. SEED DATA

Create:

```bash
python manage.py seed_demo
```

It must be safe for development environments.

Seed:

- admin
- citizen
- volunteer
- supervisor
- species
- planting sites
- batches
- trees
- requests
- reports
- campaigns
- notifications
- articles
- contribution methods

Use fictional Iraqi demo data.

Never use actual personal financial or phone information.

---

# 28. TEST BACKEND BEFORE FLUTTER

Create automated tests for:

Authentication

Permissions

Tree requests

Tree ownership

Tree updates

Environmental reports

Campaign joining

Admin-only operations

File validation where practical

Pagination/filtering

Run:

```bash
python manage.py test
```

or:

```bash
pytest
```

If failing:

fix errors.

Run again.

Do not continue to Flutter with major backend failures.

---

# 29. STATIC ANALYSIS BACKEND

Use practical tooling such as:

```text
ruff
```

Optionally:

```text
black
```

Avoid introducing an extremely strict configuration that slows the project unnecessarily.

Run formatter/linter.

Fix meaningful issues.

---

# 30. FLUTTER PROJECT CREATION

Create:

```text
mobile/
```

Run:

```bash
flutter create .
```

Set reasonable application identifier placeholder:

```text
com.shajjar.app
```

Configure application display name:

```text
شجّر
```

Do not add actual production signing keys.

---

# 31. FLUTTER DIRECTORY STRUCTURE

Use feature-oriented architecture.

Example:

```text
lib/
│
├── app/
│   ├── app.dart
│   ├── router.dart
│   └── bootstrap.dart
│
├── core/
│   ├── api/
│   ├── auth/
│   ├── constants/
│   ├── errors/
│   ├── localization/
│   ├── storage/
│   ├── theme/
│   ├── widgets/
│   └── utils/
│
├── features/
│   ├── auth/
│   ├── home/
│   ├── map/
│   ├── tree_requests/
│   ├── trees/
│   ├── environmental_reports/
│   ├── campaigns/
│   ├── notifications/
│   ├── species/
│   ├── content/
│   └── profile/
│
└── main.dart
```

Avoid one enormous screens folder.

---

# 32. FLUTTER ENVIRONMENT CONFIGURATION

Create a clean way to configure:

```text
API_BASE_URL
APP_ENV
```

For Android emulator backend:

document:

```text
10.0.2.2
```

when required.

For physical device:

document local LAN IP procedure.

Do not hardcode production endpoint deeply in source code.

---

# 33. LOCALIZATION

Primary language:

Arabic.

RTL must work properly.

Create localization structure using ARB.

Example:

```text
lib/l10n/app_ar.arb
lib/l10n/app_en.arb
```

English may initially contain basic translations.

No important UI labels should remain scattered as hardcoded strings.

---

# 34. APP THEME

Create central theme configuration.

Suggested visual identity:

Dark environmental green.

Secondary green.

Soft beige/off-white backgrounds.

Material 3.

Use Cairo or Tajawal.

Create:

```text
AppColors
AppSpacing
AppRadius
AppTypography
```

Do not specify colors separately in every screen.

---

# 35. CORE REUSABLE WIDGETS

Implement reusable:

```text
PrimaryButton
SecondaryButton
AppTextField
AppScaffold
StatusChip
StatisticCard
TreeCard
RequestCard
ReportCard
CampaignCard
LoadingView
ErrorView
EmptyState
ImagePickerField
LocationPicker
ConfirmDialog
```

---

# 36. NETWORKING

Use Dio.

Create:

```text
ApiClient
AuthInterceptor
TokenRefresh logic
ApiException mapping
```

Store tokens with:

```text
flutter_secure_storage
```

Do not store JWT in SharedPreferences.

Handle:

401

403

404

422/400

500

timeout

offline

---

# 37. TOKEN REFRESH

Implement safe access/refresh token behavior.

On expired access token:

refresh once.

Retry original request.

If refresh fails:

clear session.

redirect to login.

Avoid infinite interceptor loops.

Write tests where practical.

---

# 38. FLUTTER AUTHENTICATION FLOW

Implement screens:

Splash

Onboarding

Login

Register

Forgot Password placeholder/service-supported implementation

Startup behavior:

Check secure token.

Attempt profile load.

If valid:

Home.

If invalid:

Login.

---

# 39. HOME SCREEN

Arabic-first RTL.

Include:

Logo/header.

Greeting.

Statistics.

Quick actions:

```text
🌱 أريد شجرة
📸 شجرتي
🚨 بلّغ
🤝 تطوع
```

Latest campaigns.

Latest planting sites.

Tree transformations if available from API.

Latest awareness articles.

All numbers must come from API.

No fake counters.

---

# 40. BOTTOM NAVIGATION

Implement:

```text
الرئيسية
الخريطة
+
نشاطي
حسابي
```

Central + opens action sheet:

```text
طلب شجرة
تحديث شجرة
بلاغ بيئي
```

---

# 41. TREE REQUEST FLOW

Create a multi-step flow.

## Step 1

Location type:

```text
أمام البيت
أمام المحل
مدرسة
جامعة
مستشفى
مؤسسة
بستان
قرية
شارع
مكان عام
أخرى
```

## Step 2

Tree count.

## Step 3

Map location.

## Step 4

Watering commitment.

## Step 5

Photos.

## Step 6

Notes.

## Step 7

Review and submit.

After success:

display generated request code.

Example:

```text
REQ-2026-000123
```

---

# 42. MY REQUESTS

List user's requests.

Each card:

Request ID

Requested tree count

Location

Date

Status

Provide status timeline in details screen.

---

# 43. REQUEST TIMELINE

Display visually:

```text
تم إرسال الطلب
      ↓
قيد المراجعة
      ↓
تمت الموافقة
      ↓
جاهز للاستلام
      ↓
تم الاستلام
      ↓
تمت الزراعة
```

Inactive future steps should appear visually distinct.

---

# 44. TREE SCREENS

Implement:

My Trees

Tree Details

Tree Update Form

Tree Timeline

Tree profile displays:

Tree ID

Species

Planting date

Age

Location

Health

Height

Last update

Timeline images

---

# 45. TREE UPDATE FLOW

Allow:

Photo

Height

Health

Notes

Optional current location

Statuses in Arabic:

```text
ممتازة
جيدة
تحتاج رعاية
متضررة
ميتة
```

Submit to API.

Display verification state.

---

# 46. MAP SCREEN

Use flutter_map + OpenStreetMap.

Display planting sites.

Marker states:

Green = healthy/active

Yellow = needs attention

Red = damaged

Use different icon/style for larger forest/planting areas.

Filter UI:

Species

Year

City

District

Status

Click marker:

show bottom sheet:

Site Name

Tree Count

Species summary

Planting Date

Status

Latest image

Details button

---

# 47. LOCATION PICKER

Create reusable location picker.

Functions:

- move map
- tap marker location
- optional device GPS if permission granted
- manual confirmation

Do not require GPS permission for all users.

The user must be able to manually choose location.

---

# 48. ENVIRONMENTAL REPORT FLOW

Screen title:

```text
بلّغ عن تجاوز
```

Categories:

```text
قطع أشجار
حريق
تجريف مساحة خضراء
صيد جائر
نفايات
تلوث
ضرر على الحيوانات البرية
ضرر على الأشجار
أخرى
```

Collect:

Category

Description

Location

Photos

Optional title

Privacy toggle:

```text
إخفاء هويتي عن العرض العام
```

Default:

true.

On success display:

```text
ENV-2026-000123
```

---

# 49. MY REPORTS

List:

Report ID

Category

Date

Status

Details page contains:

Public status history.

Public admin note.

Do NOT expose internal notes.

---

# 50. CAMPAIGNS

Campaign list screen.

Details screen shows:

Title

Cover

Description

Date

Time

Location

Target trees

Required volunteers

Registered count if API supports it

Button:

```text
شارك ويانا
```

If joined:

display participant status.

---

# 51. VOLUNTEER PROFILE

Display:

Campaign count

Volunteer hours

Trees planted

Achievements.

Avoid overly game-like design.

---

# 52. SPECIES LIBRARY

List tree species.

Search.

Details:

Arabic name

Scientific name

Image

Heat tolerance

Water requirement

Growth speed

Recommended locations

Notes

Everything from backend.

---

# 53. CONTENT / AWARENESS

Implement articles screen.

Categories.

Article details.

Legal section uses backend-managed articles.

Display disclaimer when category is legal/environmental regulation:

```text
المعلومات لأغراض التوعية العامة، ويجب الرجوع إلى النصوص الرسمية والجهات المختصة.
```

---

# 54. CONTRIBUTION SCREEN

Fetch available contribution methods from backend.

Do not add payment processing.

Do not hardcode bank/card/payment numbers.

---

# 55. NOTIFICATIONS UI

Implement:

Notifications list.

Read/unread state.

Mark individual read.

Mark all read.

Notification types may navigate to related resource.

Example:

Request approved → Request details.

Campaign reminder → Campaign details.

Tree follow-up → Tree update.

---

# 56. PUSH NOTIFICATION ARCHITECTURE

Create FCM service abstraction.

If Firebase credentials/configuration are absent:

do not crash.

Log that push notifications are disabled.

In-app notification data from backend must still function.

Document Firebase setup in:

```text
docs/FIREBASE_SETUP.md
```

---

# 57. IMAGE HANDLING

Before upload:

compress large images.

Show preview.

Allow delete before submission.

Display progress.

Handle upload failure gracefully.

Do not lose entire form if one image upload fails.

---

# 58. FORMS

Every form needs:

Validation

Loading state

Success state

Error state

Keyboard handling

RTL correctness

Confirmation where appropriate

Prevent double submission.

---

# 59. OFFLINE / NETWORK FAILURE

At minimum:

detect Dio network errors.

Display user-friendly Arabic message.

Do not display raw exceptions.

Persist draft forms where practical for:

Tree Request

Environmental Report

Tree Update

Basic caching can use lightweight local persistence.

Do not overbuild full offline synchronization in MVP.

---

# 60. PROFILE

Implement:

User details

Edit profile

My requests

My trees

My reports

My campaigns

Volunteer stats

Notifications

Settings

Logout

Account deletion request.

Account deletion must require confirmation.

---

# 61. ADMIN ANALYTICS

Use Django Admin first.

Optionally create API-ready dashboard statistics.

Do NOT spend disproportionate time creating a separate React admin dashboard unless core MVP is already complete and stable.

Django Admin is the required administrative interface for MVP.

---

# 62. DATA EXPORT

Create admin actions or protected endpoints to export:

Trees CSV

Requests CSV

Reports CSV

Campaign participants CSV

Volunteers CSV

CSV must use UTF-8.

---

# 63. QR CODE

Implement backend utility to generate QR code for Tree public identifier.

QR must not contain private user information.

It should point to public tree profile identifier or deep-link-ready identifier.

If external public base URL is unavailable:

generate identifier QR now.

Document how production URL will replace it.

---

# 64. TREE AGE

Calculate tree age from planting_date.

Do not store continuously changing age field unnecessarily.

Compute dynamically.

---

# 65. TREE STATISTICS CONSISTENCY

PlantingSite aggregate counts should not drift silently.

Either:

calculate from Tree records where feasible,

or maintain explicit synchronization service.

Document architectural choice.

Write tests.

---

# 66. NOTIFICATION CREATION EVENTS

Create backend notifications when:

Tree request status changes.

Environmental report status changes.

Campaign registration approved.

Tree follow-up due.

Important campaign announcement.

For scheduled follow-up notifications:

implement management command or scheduled-task-ready service.

Example:

```bash
python manage.py send_due_tree_reminders
```

Document cron/Celery future integration.

Do NOT introduce Celery unless genuinely useful for MVP.

---

# 67. SCHEDULING STRATEGY

For MVP use management commands that can be scheduled externally.

Examples:

```bash
python manage.py send_due_tree_reminders
python manage.py cleanup_expired_tokens
```

Document cron examples.

Future:

Celery + Redis.

Do not require Redis to run core MVP.

---

# 68. SECURITY REVIEW CHECKLIST

Before completion verify:

No secrets committed.

JWT stored securely.

No unrestricted admin endpoints.

No insecure direct object references.

User cannot modify another user's tree request.

User cannot modify another user's report.

User cannot verify own tree updates unless role permits.

Internal notes never exposed publicly.

Reporter private identity never appears on public API.

Uploads validated.

Rate limits configured.

CORS restricted in production.

DEBUG false in production.

Secure cookies/settings documented.

---

# 69. PRIVACY

Public map must NOT expose:

Phone

Email

Exact household owner name

Private notes

Internal report details.

Use approximate/public environmental information only.

---

# 70. BACKEND TESTING COMMANDS

Run appropriate commands:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

or pytest equivalent.

Run:

```bash
python manage.py spectacular --file schema.yml
```

if drf-spectacular supports configured command.

Fix warnings that indicate real API problems.

---

# 71. FLUTTER QUALITY COMMANDS

Run:

```bash
flutter pub get
dart format .
flutter analyze
flutter test
```

Fix analyzer errors.

Do not ignore widespread warnings.

---

# 72. INTEGRATION VERIFICATION

Run backend.

Example:

```bash
python manage.py runserver
```

Verify critical API endpoints manually using:

curl

or a simple integration script.

Create:

```text
scripts/api_smoke_test.py
```

It should test:

Register

Login

Profile

Create tree request

List own requests

Create environmental report

List campaigns

List species

Do not require destructive production behavior.

---

# 73. API SMOKE TEST

The script must:

Read base URL from environment.

Create uniquely named demo user.

Authenticate.

Exercise critical APIs.

Print clear pass/fail results.

Do not embed production passwords.

---

# 74. DOCKER

Create:

```text
docker-compose.yml
```

Services:

```text
db
backend
```

Optional:

nginx production example.

Use PostgreSQL.

Create Dockerfile for backend.

Add health checks where reasonable.

---

# 75. DOCKER COMMAND VERIFICATION

When Docker is available:

run:

```bash
docker compose config
```

Then:

```bash
docker compose build
```

Then:

```bash
docker compose up -d
```

Run migrations.

Run smoke test.

If Docker cannot run in current environment:

document exactly what remains unverified.

---

# 76. MAKEFILE

Create convenience commands where supported:

```text
make backend-install
make migrate
make seed
make backend-test
make backend-run
make flutter-get
make flutter-test
make flutter-run
make docker-up
make docker-down
```

On Windows compatibility, also document raw commands in README.

---

# 77. DOCUMENTATION FILES

Create:

```text
docs/
├── ARCHITECTURE.md
├── DATABASE.md
├── API.md
├── DEVELOPMENT.md
├── DEPLOYMENT.md
├── ADMIN_GUIDE.md
├── USER_FLOWS.md
├── SECURITY.md
├── BRANDING.md
├── FIREBASE_SETUP.md
├── ANDROID_RELEASE.md
├── BACKUP_RESTORE.md
└── FUTURE_ROADMAP.md
```

Documentation must reflect actual implementation.

Do not document hypothetical endpoints that do not exist.

---

# 78. README

README must include:

Project description

Architecture

Prerequisites

Quick Start

Backend setup

PostgreSQL setup

Docker setup

Seed data

Demo accounts

Flutter setup

Environment variables

Running tests

API documentation

Admin access

Deployment references

Known external credentials

---

# 79. DEMO ACCOUNTS

Seed development accounts such as:

```text
admin@example.test
citizen@example.test
volunteer@example.test
supervisor@example.test
```

Use clearly development-only password.

Example:

```text
DemoPass123!
```

Mention clearly:

Never use these credentials in production.

---

# 80. BRANDING

Create placeholder assets.

Provide exact replacement locations.

Do not generate random unofficial logos as if final.

Use temporary neutral environmental icon where needed.

Document:

App icon

Logo

Splash

Font

Colors

Android name

Package ID

---

# 81. ANDROID RELEASE PREPARATION

Configure project so that:

```bash
flutter build apk --release
```

can succeed once normal Flutter/Android environment is available.

Document:

Application ID

Version

Signing key configuration

App icon replacement

Firebase Android setup

API base URL

Release mode.

Do not generate or commit private keystore.

---

# 82. APK VERIFICATION

If Android SDK environment is available:

run:

```bash
flutter build apk --release
```

Record output path in:

```text
PROJECT_STATUS.md
```

If Android SDK unavailable:

run all available Flutter analysis/tests and clearly mark release build unverified.

---

# 83. OPTIONAL WEB DEVELOPMENT

Flutter web is NOT required.

Do not spend time optimizing for web before Android MVP is complete.

---

# 84. NO FAKE BUTTON RULE

Any visible primary MVP button must work.

If feature is not implemented:

do not show functional-looking button.

Never litter UI with:

```text
TODO
Coming Soon
Not Implemented
```

for core flows.

---

# 85. NO STATIC PRODUCTION DATA

Do not hardcode:

Tree totals

Volunteer totals

Campaign data

Legal articles

Contribution information

Tree species content

Reports

Requests

All must come from API/database.

Seed data is allowed for development.

---

# 86. UX STATES

Every network-driven screen must support:

Loading

Loaded

Empty

Error

Retry

Critical submit actions need disabled/loading states.

---

# 87. ARABIC UX

Arabic strings should be natural and short.

Examples:

```text
أريد شجرة

شجرتي

بلّغ عن تجاوز

شارك ويانا

طلباتـي

بلاغاتي

حملاتي

آخر تحديث

تحتاج رعاية

تمت الموافقة

قيد المراجعة
```

Use proper RTL alignment.

Avoid machine-like Arabic where possible.

---

# 88. CORE END-TO-END TEST SCENARIO

Verify this flow:

```text
User registration
        ↓
Login
        ↓
Request 3 trees
        ↓
Attach location
        ↓
Attach image
        ↓
Submit
        ↓
Admin sees request
        ↓
Admin approves
        ↓
User sees approved status
        ↓
Admin marks distributed
        ↓
Supervisor registers trees
        ↓
Trees appear under My Trees
        ↓
User adds follow-up photo
        ↓
Supervisor verifies update
        ↓
Tree timeline updates
```

Do not declare product complete unless this architecture works end-to-end.

---

# 89. ENVIRONMENTAL REPORT TEST SCENARIO

Verify:

```text
Citizen
 ↓
Creates tree-cutting report
 ↓
Uploads photo
 ↓
Selects location
 ↓
Receives ENV ID
 ↓
Admin opens report
 ↓
Admin changes status
 ↓
Citizen sees new status
```

---

# 90. CAMPAIGN TEST SCENARIO

Verify:

```text
Admin creates campaign
 ↓
Campaign published
 ↓
Volunteer sees campaign
 ↓
Volunteer joins
 ↓
Admin approves participation
 ↓
Volunteer status updates
 ↓
Admin records attendance
 ↓
Volunteer hours update
```

---

# 91. DATA OWNERSHIP TESTS

Explicitly test that:

Citizen A cannot access private request of Citizen B.

Citizen A cannot edit Citizen B's tree.

Citizen A cannot access internal report notes.

Volunteer cannot access admin analytics.

Supervisor permissions are limited to intended operations.

---

# 92. ERROR RESOLUTION RULE

Whenever any command fails:

Do not abandon the phase.

Do this:

1. Read full error.

2. Identify root cause.

3. Fix only the root cause.

4. Run the command again.

5. Confirm success.

6. Record important architectural corrections if needed.

Never solve errors by commenting out critical functionality.

Never disable tests simply because they fail.

---

# 93. DEPENDENCY FAILURE RULE

If a package has compatibility issues:

Prefer stable package.

Do not pin obscure abandoned packages.

If replacement is needed:

update documentation.

Continue.

---

# 94. FILE REVIEW RULE

After each large phase:

review files created during that phase.

Check:

Naming

Imports

Dead code

Duplicated logic

Security issues

Missing validation

Tests

Documentation.

---

# 95. GIT CHECKPOINTS

If Git repository is available and commits are permitted:

make logical local commits.

Example:

```text
chore: initialize shajjar repository

feat: add custom user authentication

feat: add tree request workflow

feat: add tree tracking models

feat: add environmental reports

feat: add campaigns

feat: initialize flutter app

feat: add tree request mobile flow

test: add backend integration coverage

docs: complete deployment documentation
```

Do not push anywhere unless explicitly authorized.

---

# 96. DO NOT DELETE USER WORK

If the repository already contains files:

inspect them first.

Never delete or overwrite existing user work unnecessarily.

Integrate carefully.

If destructive restructuring is required:

preserve original files under backup location or use Git.

---

# 97. PROGRESS BEHAVIOR

Work continuously.

After each major phase, provide a short terminal/session progress note such as:

```text
Phase 5 completed:
- TreeRequest model created
- API implemented
- permissions tested
- 14 tests passing
Next: Trees and follow-up
```

Do not ask for permission after every update.

Continue automatically.

---

# 98. WHEN YOU MAY ASK THE USER

Ask only when genuinely blocked by things such as:

Firebase credentials

Production domain

Actual legal text

Actual organization payment/contribution details

Final logo assets

Production server credentials

Apple Developer account.

Even when blocked on one of these:

implement placeholder integration,

document missing credential,

continue all unrelated work.

---

# 99. LEGAL INFORMATION RULE

Do NOT invent Iraqi legal regulations.

Use editable backend content placeholders only.

Populate demo legal articles as explicitly marked:

```text
DEMO — requires official verification
```

Do not present unverified legal text as authoritative.

---

# 100. FUTURE FEATURES — DOCUMENT ONLY

Do not implement these in MVP unless all core work is complete:

AI tree species recognition

Plant disease AI

Carbon calculations

Satellite GIS

Weather integration

IoT irrigation

Municipality portal

Online payments

Social feed

Advanced gamification

Create only:

```text
docs/FUTURE_ROADMAP.md
```

---

# 101. PERFORMANCE

Avoid obvious N+1 queries.

Use:

select_related

prefetch_related

where appropriate.

Paginate lists.

Compress images.

Avoid returning huge media payloads unnecessarily.

---

# 102. BACKUP & RESTORE

Document:

PostgreSQL pg_dump

PostgreSQL restore

Media directory backup

Environment backup guidance.

Never include actual secrets in backups checked into Git.

---

# 103. PRODUCTION SETTINGS

Production configuration must include guidance for:

DEBUG=False

HTTPS

secure proxy SSL header if behind nginx

allowed hosts

restricted CORS

PostgreSQL

Gunicorn

Nginx

static files

media storage

environment secrets

logging.

---

# 104. NGINX EXAMPLE

Create an example production Nginx configuration inside:

```text
docs/examples/nginx-shajjar.conf
```

Do not assume specific real domain.

Use placeholder:

```text
api.example.com
```

---

# 105. DEPLOYMENT OPTIONS

Document at least:

## Development

Docker Compose.

## Small production deployment

Ubuntu VPS

PostgreSQL

Gunicorn

Nginx

Let's Encrypt

## Hosted Python option

Generic Python hosting instructions where feasible.

Do not lock user into one vendor.

---

# 106. API URL PRODUCTION DESIGN

Use versioning:

```text
/api/v1/
```

Never expose Flutter to Django internal implementation details.

---

# 107. LOGGING

Backend:

Use structured useful logs.

Do NOT log:

passwords

JWT tokens

financial information

private uploaded contents.

Flutter:

Debug logs only in development.

---

# 108. FINAL CODE SEARCH

Before completion search repository for:

```text
TODO
FIXME
password=
SECRET_KEY=
localhost
127.0.0.1
example token
Coming Soon
Not Implemented
```

Review every occurrence.

Some development references are acceptable if documented.

Remove accidental secrets or unfinished production code.

---

# 109. FINAL BACKEND VERIFICATION

Run:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

or equivalent pytest suite.

Generate OpenAPI.

Run API smoke tests.

Record exact result.

---

# 110. FINAL FLUTTER VERIFICATION

Run:

```bash
dart format .
flutter analyze
flutter test
```

Then if environment allows:

```bash
flutter build apk --release
```

Fix failures.

---

# 111. FINAL DOCKER VERIFICATION

Run if available:

```bash
docker compose config
docker compose build
docker compose up -d
```

Confirm backend health.

Run smoke test against Docker backend.

Then:

```bash
docker compose down
```

unless keeping it running is explicitly useful.

---

# 112. FINAL PROJECT STATUS

Update:

```text
PROJECT_STATUS.md
```

It must explicitly state:

Backend tests result.

Flutter analyze result.

Flutter tests result.

Docker result.

APK result.

OpenAPI result.

Known issues.

External credentials still needed.

Nothing should be described as verified unless actually verified.

---

# 113. FINAL DELIVERY REPORT

Create:

```text
docs/FINAL_BUILD_REPORT.md
```

Include:

Architecture summary.

Implemented features.

Database summary.

API count.

Flutter screens implemented.

Testing performed.

Security review.

Deployment readiness.

Missing external credentials.

Known limitations.

Suggested next steps.

---

# 114. DEFINITION OF DONE

The project is complete only when:

Django starts.

Database works.

Migrations pass.

Seed data works.

Authentication works.

Role permissions work.

Tree Requests work.

Planting Sites work.

Tree Batches work.

Individual Trees work.

Tree Updates work.

Environmental Reports work.

Campaigns work.

Volunteer participation works.

Notifications database works.

Articles work.

Contribution methods work.

Flutter authentication works.

Flutter API integration works.

Map displays backend data.

Tree Request submission works.

Tree Update submission works.

Environmental Report submission works.

Campaign registration works.

Arabic RTL works.

Backend tests pass.

Flutter tests pass.

Flutter analyze passes.

Documentation exists.

Docker configuration exists.

Production settings exist.

No critical security issue is known.

---

# 115. PRIORITY RULE

If limited by time or context:

prioritize in this exact order:

1. Working backend.

2. Database integrity.

3. Authentication & security.

4. Tree requests.

5. Trees & follow-up.

6. Environmental reports.

7. Campaigns.

8. Flutter core workflows.

9. Map.

10. Testing.

11. Admin.

12. Notifications.

13. Content.

14. Analytics.

15. Cosmetic improvements.

Never sacrifice working core functionality for decorative UI.

---

# 116. CONTEXT LIMIT / SESSION CONTINUATION PROTOCOL

If the coding environment is approaching context limits:

DO NOT abandon work.

Before ending the current session:

1. Update PROJECT_STATUS.md.

2. Update IMPLEMENTATION_PLAN.md.

3. Record exact last successful command.

4. Record next command/task.

5. Record unresolved errors.

6. Commit changes locally if appropriate.

Create:

```text
CONTINUE_HERE.md
```

with:

```markdown
# Continue Shajjar Development Here

## Last Completed Phase

## Current Repository State

## Last Successful Command

## Current Error

## Files Recently Modified

## Next Exact Task

## Verification Still Required
```

The next coding-agent session should read:

README.md

PROJECT_STATUS.md

CONTINUE_HERE.md

before doing anything else.

---

# 117. RESUMED SESSION RULE

If CONTINUE_HERE.md already exists:

do NOT restart the project.

First inspect:

```bash
git status
```

Then read:

```text
PROJECT_STATUS.md
CONTINUE_HERE.md
docs/IMPLEMENTATION_PLAN.md
```

Resume exactly where previous session stopped.

---

# 118. USER EXPERIENCE PRINCIPLE

The app should feel simple even though backend is sophisticated.

A citizen should understand the main application within seconds.

Primary home actions:

```text
أريد شجرة
شجرتي
بلّغ
تطوع
```

Avoid technical terminology in citizen UI.

---

# 119. PRODUCT SUCCESS EXAMPLE

The final product should allow a real workflow such as:

A citizen in Mosul requests three trees for the front of his house.

He selects his location.

Uploads a photo.

The organization approves his request.

The trees are distributed.

The trees are registered.

Six months later the citizen receives a reminder.

He photographs the trees.

The new photos enter their timeline.

Years later the system contains a documented history of the planting location.

At the same time another citizen can report environmental damage with a location and photo.

The organization can track the report.

Volunteers can register for planting campaigns.

Admins can see measurable environmental results.

That is the product.

---

# 120. START EXECUTION NOW

Begin immediately.

Do not return a large architectural essay.

Perform the work.

Your first actions should be:

```text
1. Inspect repository.
2. Check available development tools.
3. Initialize Git if appropriate.
4. Create PROJECT_STATUS.md.
5. Create docs/IMPLEMENTATION_PLAN.md.
6. Create repository folder structure.
7. Initialize backend.
8. Create custom user model before initial migration.
9. Configure PostgreSQL/Docker development environment.
10. Run the first successful Django check.
```

Then continue through the implementation phases automatically.

At every stage:

CODE → RUN → TEST → FIX → VERIFY → DOCUMENT → CONTINUE.

Do not stop at CODE.

Begin now.