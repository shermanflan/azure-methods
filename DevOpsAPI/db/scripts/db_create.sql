/*
USE master;
GO
IF NOT EXISTS (
    SELECT  *
    FROM    sys.databases
    WHERE   name = N'ScratchDB')
BEGIN
    CREATE DATABASE ScratchDB;
END
GO
--*/

USE ScratchDB;
GO

DROP TABLE IF EXISTS [Staging].[AhaProject];
DROP TABLE IF EXISTS [Staging].[AhaIdea];
DROP TABLE IF EXISTS [Staging].[AhaUser];
DROP TABLE IF EXISTS [Staging].[AhaRelease];
DROP TABLE IF EXISTS [Staging].[AhaFeature];
DROP TABLE IF EXISTS [Staging].[AhaRequirement];
DROP TABLE IF EXISTS [Staging].[AhaIntegrationField];
DROP TABLE IF EXISTS [Staging].[AhaEpic];
DROP TABLE IF EXISTS [Staging].[AhaInitiative];
DROP TABLE IF EXISTS [Staging].[AhaEpoch];
GO

IF EXISTS (
    SELECT  *
    FROM    sys.schemas
    WHERE   name = 'Staging'
)
BEGIN
    DROP SCHEMA Staging;
END
GO

CREATE SCHEMA Staging;
GO

CREATE TABLE [Staging].[AhaProject]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_prefix                          NVARCHAR(64)            NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , last_release_num                          INT                     NULL
    , last_feature_num                          INT                     NULL
    , last_idea_num                             INT                     NULL
    , position                                  INT                     NULL
    , positioning_customer                      NVARCHAR(512)           NULL
    , positioning_problem                       NVARCHAR(512)           NULL
    , positioning_benefit1                      NVARCHAR(512)           NULL
    , positioning_benefit2                      NVARCHAR(512)           NULL
    , positioning_benefit3                      NVARCHAR(512)           NULL
    , product_line                              BIT                     NULL
    , product_line_type                         NVARCHAR(128)           NULL
    , capacity_planning_enabled                 BIT                     NULL
    , ideas_scoring_system_id                   VARCHAR(128)            NULL
    , ideas_default_user_id                     VARCHAR(128)            NULL
    , default_capacity_units                    INT                     NULL
    , default_feature_remaining_estimate        BIT                     NULL
    , last_page_num                             INT                     NULL
    , color                                     INT                     NULL
    , workflow_screen_enabled                   BIT                     NULL
    , competitor_scoring_system_id              VARCHAR(128)            NULL
    , initiative_workflow_id                    VARCHAR(128)            NULL
    , strategic_imperative_workflow_id          VARCHAR(128)            NULL
    , estimated_time_as_work_done               BIT                     NULL
    , last_epic_num                             INT                     NULL
    , configuration                             NVARCHAR(4000)          NULL
    , workspace_type                            NVARCHAR(128)           NOT NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , parent_id                                 VARCHAR(128)            NULL
    , scoring_system_id                         VARCHAR(128)            NULL
    , idea_workflow_id                          VARCHAR(128)            NOT NULL
    , feature_workflow_id                       VARCHAR(128)            NOT NULL
    , release_workflow_id                       VARCHAR(128)            NOT NULL
    -- , ideas_scoring_system_id                   VARCHAR(128)            NULL
);
GO

CREATE TABLE [Staging].[AhaIdea]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_num                             NVARCHAR(64)            NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , score                                     INT                     NULL
    , visibility                                INT                     NULL
    , num_endorsements                          INT                     NULL
    , initial_votes                             INT                     NULL
    , contributorship_type                      NVARCHAR(128)           NULL
    , promotable_type                           NVARCHAR(128)           NULL
    , is_spam                                   BIT                     NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , project_id                                VARCHAR(128)            NOT NULL
    , promotable_id                             VARCHAR(128)            NULL
    , contributorship_id                        VARCHAR(128)            NOT NULL
    , workflow_status_id                        VARCHAR(128)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaUser]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , first_name                                NVARCHAR(128)           NOT NULL
    , last_name                                 NVARCHAR(128)           NOT NULL
    , email                                     NVARCHAR(128)           NOT NULL
    , timezone                                  VARCHAR(128)            NULL
    , locale                                    VARCHAR(128)            NULL
    , unsubscribe_lifecycle_emails              BIT                     NULL
    , unsubscribe_all_notifications             BIT                     NULL
    , email_verified                            BIT                     NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaRelease]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_num                             NVARCHAR(64)            NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , release_date                              DATE                    NULL
    , released_on                               DATE                    NULL
    , progress                                  FLOAT                   NOT NULL
    , progress_source                           NVARCHAR(128)           NULL
    , development_started_on                    DATE                    NULL
    , external_release_date                     DATE                    NULL
    , external_date_resolution                  INT                     NOT NULL
    , total_capacity                            FLOAT                   NULL
    , capacity_units                            INT                     NULL
    , parking_lot                               BIT                     NOT NULL
    , type                                      NVARCHAR(128)           NOT NULL
    , start_on                                  DATE                    NULL
    , created_by_user_id                        VARCHAR(128)            NOT NULL
    , duration_source                           NVARCHAR(128)           NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , project_id                                VARCHAR(128)            NOT NULL
    , workflow_status_id                        VARCHAR(128)            NOT NULL
    , owner_id                                  VARCHAR(128)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaFeature]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_num                             NVARCHAR(64)            NOT NULL
    , position                                  INT                     NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , score                                     INT                     NOT NULL
    , last_requirement_num                      INT                     NOT NULL
    , progress                                  FLOAT                   NULL
    , progress_source                           NVARCHAR(128)           NULL
    , show_feature_remaining_estimate           BIT                     NOT NULL
    , due_date                                  DATE                    NULL
    , start_date                                DATE                    NULL
    , duration_estimate                         FLOAT                   NULL
    , original_estimate                         FLOAT                   NULL
    , remaining_estimate                        FLOAT                   NULL
    , work_done                                 FLOAT                   NULL
    , status_changed_on                         DATE                    NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , epic_id                                   VARCHAR(128)            NULL
    , project_id                                VARCHAR(128)            NOT NULL
    , release_id                                VARCHAR(128)            NOT NULL
    , initiative_id                             VARCHAR(128)            NULL
    , assigned_to_user_id                       VARCHAR(128)            NULL
    , created_by_user_id                        VARCHAR(128)            NOT NULL
    , workflow_status_id                        VARCHAR(128)            NOT NULL
    , workflow_kind_id                          VARCHAR(128)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaRequirement]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_num                             NVARCHAR(64)            NOT NULL
    , created_by_user_id                        VARCHAR(128)            NOT NULL
    , position                                  INT                     NOT NULL
    , original_estimate                         FLOAT                   NULL
    , remaining_estimate                        FLOAT                   NULL
    , work_done                                 FLOAT                   NULL
    , name                                      NVARCHAR(512)           NOT NULL    
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , feature_id                                VARCHAR(128)            NOT NULL
    , project_id                                VARCHAR(128)            NOT NULL
    , workflow_status_id                        VARCHAR(128)            NOT NULL
    , assigned_to_user_id                       VARCHAR(128)            NULL
);
GO

CREATE TABLE [Staging].[AhaIntegrationField]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL    
    , value                                     NVARCHAR(512)           NOT NULL
    , integratable_type                         NVARCHAR(128)           NOT NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , account_id                                VARCHAR(128)            NOT NULL
    , integration_id                            VARCHAR(128)            NOT NULL
    , integratable_id                           VARCHAR(128)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaEpic]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_num                             NVARCHAR(64)            NOT NULL
    , position                                  INT                     NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , score                                     INT                     NULL
    , progress                                  FLOAT                   NULL
    , progress_source                           NVARCHAR(128)           NULL
    , show_feature_remaining_estimate           BIT                     NOT NULL
    , due_date                                  DATE                    NULL
    , start_date                                DATE                    NULL
    , duration_estimate                         FLOAT                   NULL
    , original_estimate                         FLOAT                   NULL
    , remaining_estimate                        FLOAT                   NULL
    , work_done                                 FLOAT                   NULL
    , status_changed_on                         DATE                    NULL
    , duration_source                           NVARCHAR(128)           NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , release_id                                VARCHAR(128)            NOT NULL
    , project_id                                VARCHAR(128)            NOT NULL
    , initiative_id                             VARCHAR(128)            NULL
    , created_by_user_id                        VARCHAR(128)            NOT NULL
    , workflow_status_id                        VARCHAR(128)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaInitiative]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , reference_num                             NVARCHAR(64)            NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , color                                     INT                     NULL
    , position                                  INT                     NOT NULL
    , value                                     INT                     NOT NULL
    , effort                                    INT                     NOT NULL
    , presented                                 BIT                     NOT NULL
    , start_date                                DATE                    NULL
    , end_date                                  DATE                    NULL
    , progress                                  FLOAT                   NULL
    , progress_source                           NVARCHAR(128)           NULL
    , duration_source                           NVARCHAR(128)           NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , project_id                                VARCHAR(128)            NOT NULL
    , epoch_id                                  VARCHAR(128)            NULL
    , workflow_status_id                        VARCHAR(128)            NOT NULL
);
GO

CREATE TABLE [Staging].[AhaEpoch]
(
    Id                                          INT IDENTITY(1, 1)      NOT NULL
        PRIMARY KEY
    , aha_id                                    VARCHAR(128)            NOT NULL
    , name                                      NVARCHAR(512)           NOT NULL
    , archived                                  BIT                     NOT NULL
    , created_at                                DATETIME2(2)            NOT NULL
    , updated_at                                DATETIME2(2)            NOT NULL
    , account_id                                VARCHAR(128)            NOT NULL
);
GO