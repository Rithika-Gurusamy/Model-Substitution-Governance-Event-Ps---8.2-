-- Multi-Tenant SaaS Migration Script (v2_multitenant.sql)
-- Safe, additive migration: Creates organizations and user_profiles tables, adds organization_id foreign keys, and seeds default demo org.

-- 1. Create Organizations Table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'Compliance Officer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Add organization_id to agents table (Additive)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='agents' AND column_name='organization_id') THEN
        ALTER TABLE agents ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 4. Add organization_id to governance_events table (Additive)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='governance_events' AND column_name='organization_id') THEN
        ALTER TABLE governance_events ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 5. Seed default "Hackathon Demo Org" if not present and backfill existing unassigned records
INSERT INTO organizations (id, organization_name)
SELECT 'a0000000-0000-0000-0000-000000000001', 'Hackathon Demo Org'
WHERE NOT EXISTS (SELECT 1 FROM organizations WHERE id = 'a0000000-0000-0000-0000-000000000001');

-- Assign any unassigned agents to Hackathon Demo Org
UPDATE agents SET organization_id = 'a0000000-0000-0000-0000-000000000001' WHERE organization_id IS NULL;

-- Assign any unassigned governance events to Hackathon Demo Org
UPDATE governance_events SET organization_id = 'a0000000-0000-0000-0000-000000000001' WHERE organization_id IS NULL;
