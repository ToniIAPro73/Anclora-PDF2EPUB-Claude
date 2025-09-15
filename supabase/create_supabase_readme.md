# Supabase Setup Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [What This Package Contains](#what-this-package-contains)
- [SQL Schema Summary](#sql-schema-summary)
- [Edge Function: create-admin-user](#edge-function-create-admin-user)
- [Deployment Instructions](#deployment-instructions)
- [Usage Examples](#usage-examples)
- [Testing and Validation](#testing-and-validation)
- [Best Practices](#best-practices)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Appendix](#appendix)

## Overview

This guide covers the setup of Supabase schema, Row Level Security (RLS) policies, and an Edge Function for creating admin users in the Anclora PDF2EPUB project.

## Prerequisites

- Supabase project set up
- Supabase CLI installed
- Access to Supabase Dashboard
- Environment variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

## What This Package Contains

- `create_supabase_tables_mejorado.sql`: Improved SQL script to create public.profiles, RLS policies, indexes, triggers, audit logging, and private.profile_audit.
- `supabase_setup.sql`: SQL script for setting up the conversions table and related functionality for PDF2EPUB processing.
- `create-admin-user.ts`: TypeScript Edge Function code for creating admin users.

All scripts are located at the root level of the project.

## SQL Schema Summary

### Tables

- `public.profiles`: Stores user profile data linked to `auth.users` via `user_id` UUID foreign key.
- `public.conversions`: Stores PDF2EPUB conversion tasks and metadata.
- `private.profile_audit`: Audit table in private schema for security.

### Security

- RLS enabled on `public.profiles` and `public.conversions` with policies restricting access to row owners.

### Performance

- Indexes on `user_id`, `task_id`, `status`, and audit table for efficient queries.

### Automation

- Triggers to update `updated_at` timestamps and log profile changes.
- Audit logging for profile modifications.

## Edge Function: create-admin-user

### Purpose

- Creates auth users using the Admin API with SUPABASE_SERVICE_ROLE_KEY.
- Inserts corresponding profile row.
- Includes validation and uniqueness checks.
- Rolls back user creation if profile insertion fails.

### Features

- Input validation for email, password, username.
- Duplicate prevention for username and email.
- Error handling with rollback mechanism.
- Secure key management.

## Deployment Instructions

1. Execute SQL scripts in Supabase SQL Editor or via psql:
   - `psql $SUPABASE_DB_URL -f create_supabase_tables_mejorado.sql`
   - `psql $SUPABASE_DB_URL -f supabase_setup.sql`

2. Deploy Edge Function:
   - Save `create-admin-user.ts` as `create-admin-user/index.ts` in Supabase functions folder.
   - Deploy with Supabase CLI: `supabase functions deploy create-admin-user`.

Environment variables are auto-available in Supabase environment.

## Usage Examples

### Creating an Admin User

```bash
curl -X POST "<PROJECT_FUNCTIONS_URL>/create-admin-user" \
  -H "Content-Type: application/json" \
  -H "apikey: <SERVICE_ROLE_KEY>" \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>" \
  -d '{"email":"antonio@anclora.com","password":"ancloraadm","username":"anclora_admin","full_name":"Antonio"}'
```

## Testing and Validation

1. Execute SQL scripts and verify tables/policies in Supabase Dashboard.
2. Test RLS as different users.
3. Test Edge Function with valid/invalid inputs.

## Best Practices

- Keep SUPABASE_SERVICE_ROLE_KEY secret.
- Use HTTPS for all requests.
- Test RLS policies thoroughly.
- Regularly audit access logs.
- Validate inputs on both client and server side.

## Performance Optimization

- Monitor query performance in Supabase Dashboard.
- Ensure indexes are used for common queries.
- Optimize RLS policies to avoid complex conditions.
- Use connection pooling for high-traffic scenarios.

## Troubleshooting

- **Deployment fails**: Check CLI version and permissions.
- **RLS not working**: Verify policies in Dashboard.
- **Edge Function errors**: Check logs in Supabase Dashboard.
- **User creation fails**: Ensure valid email and unique username.
- **SQL execution errors**: Check database permissions and syntax.

## Appendix

- Full Edge Function code: `create-admin-user.ts`
- SQL scripts: `create_supabase_tables_mejorado.sql`, `supabase_setup.sql`