--/*
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

USE ScratchDB;
GO
--*/

DROP TABLE IF EXISTS Staging.State;
GO

DROP TABLE IF EXISTS Staging.County;
GO

DROP TABLE IF EXISTS Staging.GeoPlace;
GO

DROP TABLE IF EXISTS Staging.ZipCode;
GO

IF EXISTS(
    SELECT  * 
    FROM    sys.tables 
    WHERE   object_id = OBJECT_ID(N'MasterData.StateTerritory', 'U'))
BEGIN
    IF EXISTS(
        SELECT  * 
        FROM    sys.tables 
        WHERE   object_id = OBJECT_ID(N'MasterData.StateTerritory', 'U')
                AND temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE')
    BEGIN
        ALTER TABLE MasterData.StateTerritory SET (SYSTEM_VERSIONING = OFF);
        DROP TABLE MasterData.StateTerritoryHistory;
    END

    DROP TABLE MasterData.StateTerritory;
END
GO

IF EXISTS(
    SELECT  * 
    FROM    sys.tables 
    WHERE   object_id = OBJECT_ID(N'MasterData.CountyProvince', 'U'))
BEGIN
    IF EXISTS(
        SELECT  * 
        FROM    sys.tables 
        WHERE   object_id = OBJECT_ID(N'MasterData.CountyProvince', 'U')
                AND temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE')
    BEGIN
        ALTER TABLE MasterData.CountyProvince SET (SYSTEM_VERSIONING = OFF);
        DROP TABLE MasterData.CountyProvinceHistory;
    END

    DROP TABLE MasterData.CountyProvince;
END
GO

IF EXISTS(
    SELECT  * 
    FROM    sys.tables 
    WHERE   object_id = OBJECT_ID(N'MasterData.GeoPlace', 'U'))
BEGIN
    IF EXISTS(
        SELECT  * 
        FROM    sys.tables 
        WHERE   object_id = OBJECT_ID(N'MasterData.GeoPlace', 'U')
                AND temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE')
    BEGIN
        ALTER TABLE MasterData.GeoPlace SET (SYSTEM_VERSIONING = OFF);
        DROP TABLE MasterData.GeoPlaceHistory;
    END

    DROP TABLE MasterData.GeoPlace;
END
GO

IF EXISTS(
    SELECT  * 
    FROM    sys.tables 
    WHERE   object_id = OBJECT_ID(N'MasterData.ZipCode', 'U'))
BEGIN
    IF EXISTS(
        SELECT  * 
        FROM    sys.tables 
        WHERE   object_id = OBJECT_ID(N'MasterData.ZipCode', 'U')
                AND temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE')
    BEGIN
        ALTER TABLE MasterData.ZipCode SET (SYSTEM_VERSIONING = OFF);
        DROP TABLE MasterData.ZipCodeHistory;
    END

    DROP TABLE MasterData.ZipCode;
END
GO

DROP PROCEDURE IF EXISTS MasterData.usp_UpsertGeography;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertStateTerritory;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertCountyProvince;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertGeoPlace;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertZipCode;
GO
--/*
DROP SCHEMA IF EXISTS Staging;
GO

CREATE SCHEMA Staging;
GO

DROP SCHEMA IF EXISTS MasterData;
GO

CREATE SCHEMA MasterData;
GO
--*/
CREATE TABLE [Staging].[State] 
(
	[Id]                    INT             NULL 
	, [Region]              VARCHAR(max)    NULL 
	, [Division]            VARCHAR(max)    NULL 
	, [StateFIPS]           VARCHAR(max)    NULL 
	, [StateName]           VARCHAR(max)    NULL 
	, [RegionName]          VARCHAR(max)    NULL 
	, [DivisionName]        VARCHAR(max)    NULL 
	, [USPS]                VARCHAR(max)    NULL 
	, [CreatedDateTime]     DATETIME        NOT NULL
        DEFAULT GETDATE()
	, [RecCreatedBy]        VARCHAR(max)    NULL
);
GO

CREATE TABLE [Staging].[County] 
(
	[Id]                    INT             NULL 
	, [USPS]                VARCHAR(max)    NULL 
	, [GEOID]               VARCHAR(max)    NULL 
	, [ANSICODE]            VARCHAR(max)    NULL 
	, [NAME]                NVARCHAR(max)   NULL 
	, [ALAND]               BIGINT          NULL 
	, [AWATER]              BIGINT          NULL 
	, [ALAND_SQMI]          DECIMAL(12, 2)  NULL 
	, [AWATER_SQMI]         DECIMAL(12, 2)  NULL 
	, [INTPTLAT]            DECIMAL(9, 5)   NULL 
	, [INTPTLONG]           DECIMAL(9, 5)   NULL 
	, [StateFIPS]           VARCHAR(max)    NOT NULL 
	, [CountyFIPS]          VARCHAR(max)    NOT NULL 
	, [CountyPrefix]        NVARCHAR(max)   NULL 
	, [CountySuffix]        VARCHAR(max)    NULL 
	, [CreatedDateTime]     DATETIME        NOT NULL
        DEFAULT GETDATE()
	, [RecCreatedBy]        VARCHAR(max)    NULL
);
GO

CREATE TABLE [Staging].[GeoPlace]
(
	[Id]                    INT             NULL 
	, [geonameid]           BIGINT          NULL 
	, [name]                NVARCHAR(max)
        COLLATE Latin1_General_BIN2    NULL 
	, [alternatenames]      NVARCHAR(max)   NULL 
	, [latitude]            DECIMAL(9, 5)   NULL 
	, [longitude]           DECIMAL(9, 5)   NULL 
    -- See http://www.geonames.org/export/codes.html 
	, [feature_class]       VARCHAR(max)    NULL 
	, [feature_code]        VARCHAR(max)    NULL 
	, [country_code]        VARCHAR(max)    NULL 
	, [cc2]                 VARCHAR(max)    NULL 
	, [admin_code1]         VARCHAR(max)    NULL    -- state code
	, [admin_code2]         NVARCHAR(max)   NULL    -- county FIPS
	, [admin_code3]         VARCHAR(max)    NULL    -- place FIPS
	, [population]          BIGINT          NULL 
	, [elevation]           BIGINT          NULL 
	, [dem]                 BIGINT          NULL 
	, [timezone]            VARCHAR(max)    NULL 
	, [modification_date]   INT             NULL
	, [CreatedDateTime]     DATETIME        NOT NULL
        DEFAULT GETDATE()
	, [RecCreatedBy]        VARCHAR(max)    NULL
)

CREATE TABLE [Staging].[ZipCode] 
(
	[Id]                    INT             NULL 
	, [country_code]        VARCHAR(max)    NULL 
	, [postal_code]         VARCHAR(max)    NULL 
	, [place_name]          NVARCHAR(max)
        COLLATE Latin1_General_BIN2    NULL 
	, [admin_name1]         VARCHAR(max)    NULL 
	, [admin_code1]         VARCHAR(max)    NULL 
	, [admin_name2]         VARCHAR(max)    NULL 
	, [admin_code2]         NVARCHAR(max)   NULL 
	, [admin_name3]         VARCHAR(max)    NULL 
	, [admin_code3]         VARCHAR(max)    NULL 
	, [latitude]            DECIMAL(9, 5)   NULL 
	, [longitude]           DECIMAL(9, 5)   NULL 
	, [accuracy]            VARCHAR(max)    NULL
	, [CreatedDateTime]     DATETIME        NOT NULL
        DEFAULT GETDATE()
	, [RecCreatedBy]        VARCHAR(max)    NULL
);
GO

CREATE TABLE MasterData.StateTerritory
(
    [Id]                INT IDENTITY(1, 1)  NOT NULL
        PRIMARY KEY
    , [Region]               CHAR(1)         NOT NULL
    , [Division]             CHAR(1)         NOT NULL    
    , [StateFIPS]            CHAR(2)         NOT NULL
    , [StateName]            VARCHAR(128)    NOT NULL
    , [StateCode]            CHAR(2)         NOT NULL --from county lookup
    , [RegionName]           VARCHAR(128)    NOT NULL
    , [DivisionName]         VARCHAR(128)    NOT NULL
    , [CreatedDateTime]      DATETIME        NOT NULL
        DEFAULT GETDATE()
    , [RecCreatedBy]         VARCHAR(100)    NOT NULL
    , [ModifiedDateTime]     DATETIME        NULL
    , [ModifiedBy]           VARCHAR(100)    NULL
    , [ValidFrom]            DATETIME2(2)    GENERATED ALWAYS AS ROW START NOT NULL
    , [ValidTo]              DATETIME2(2)    GENERATED ALWAYS AS ROW END NOT NULL
    , PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = MasterData.StateTerritoryHistory));
GO

CREATE TABLE MasterData.CountyProvince
(
    [Id]                INT IDENTITY(1, 1)  NOT NULL
        PRIMARY KEY
    , [StateCode]            CHAR(2)         NOT NULL
    , [StateFIPS]            CHAR(2)         NOT NULL
    , [CountyFIPS]           CHAR(3)         NOT NULL
    , [ANSICode]             CHAR(8)         NOT NULL
    , [CountyNameOriginal]   NVARCHAR(128)   NOT NULL
    , [CountyName]           NVARCHAR(112)   NOT NULL
    , [CountyType]           VARCHAR(16)     NULL
    , [Latitude]             DECIMAL(9, 5)   NOT NULL
    , [Longitude]            DECIMAL(9, 5)   NOT NULL
    , [CreatedDateTime]      DATETIME        NOT NULL
        DEFAULT GETDATE()
    , [RecCreatedBy]         VARCHAR(100)    NOT NULL
    , [ModifiedDateTime]     DATETIME        NULL
    , [ModifiedBy]           VARCHAR(100)    NULL
    , [ValidFrom]            DATETIME2(2)    GENERATED ALWAYS AS ROW START NOT NULL
    , [ValidTo]              DATETIME2(2)    GENERATED ALWAYS AS ROW END NOT NULL
    , PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = MasterData.CountyProvinceHistory));
GO

CREATE TABLE MasterData.GeoPlace
(
    [Id]                    INT IDENTITY(1, 1)  NOT NULL
        PRIMARY KEY
	, [GeoNameId]               BIGINT          NULL
    -- See https://docs.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support#Binary-collations
	, [PlaceName]               NVARCHAR(200)   
        COLLATE Latin1_General_BIN2    NULL 
	, [PlaceSynonyms]           NVARCHAR(3400)  NULL 
    -- See http://www.geonames.org/export/codes.html 
	, [FeatureClass]            CHAR(1)         NULL 
	, [FeatureCode]             VARCHAR(10)     NULL 
	, [CountryCode]             CHAR(2)         NULL 
	, [StateCode]               CHAR(2)         NULL        -- admin_code1 
    , [StateFIPS]               CHAR(2)         NOT NULL
	, [CountyFIPS]              NVARCHAR(80)    NULL        -- admin_code2 
	, [PlaceFIPS]               VARCHAR(20)     NULL        -- admin_code3
	, [Population]              BIGINT          NULL 
	, [Elevation]               BIGINT          NULL 
	, [DEM]                     BIGINT          NULL 
	, [TimeZone]                VARCHAR(40)     NULL 
    , [Latitude]                DECIMAL(9, 5)   NOT NULL
    , [Longitude]               DECIMAL(9, 5)   NOT NULL
    , [SourceModificationDate]  INT             NULL
    , [CreatedDateTime]         DATETIME        NOT NULL
        DEFAULT GETDATE()
    , [RecCreatedBy]            VARCHAR(100)    NOT NULL
    , [ModifiedDateTime]        DATETIME        NULL
    , [ModifiedBy]              VARCHAR(100)    NULL
    , [ValidFrom]               DATETIME2(2)    GENERATED ALWAYS AS ROW START NOT NULL
    , [ValidTo]                 DATETIME2(2)    GENERATED ALWAYS AS ROW END NOT NULL
    , PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = MasterData.GeoPlaceHistory));
GO

CREATE TABLE MasterData.ZipCode
(
    [Id]                INT IDENTITY(1, 1)  NOT NULL
        PRIMARY KEY
    , [CountryCode]         CHAR(2)         NOT NULL
    , [ZipCode]             CHAR(5)         NOT NULL
    -- See https://docs.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support#Binary-collations
    , [PlaceName]           NVARCHAR(180)   
        COLLATE Latin1_General_BIN2    NOT NULL
    , [GeoNameId]           BIGINT          NULL        -- from GeoPlace lookup
    , [PlaceFIPS]           VARCHAR(20)     NULL        -- from GeoPlace lookup
    , [StateName]           VARCHAR(128)    NOT NULL    
    , [StateCode]           CHAR(2)         NOT NULL    
    , [StateFIPS]           CHAR(2)         NOT NULL    -- from state lookup
    , [CountyName]          NVARCHAR(128)   NOT NULL    
    , [CountyFIPS]          CHAR(3)         NOT NULL    
    , [Latitude]            DECIMAL(9, 5)   NOT NULL
    , [Longitude]           DECIMAL(9, 5)   NOT NULL
    , [Accuracy]            VARCHAR(32)     NULL
    , [CreatedDateTime]     DATETIME        NOT NULL
        DEFAULT GETDATE()
    , [RecCreatedBy]        VARCHAR(100)    NOT NULL
    , [ModifiedDateTime]    DATETIME        NULL
    , [ModifiedBy]          VARCHAR(100)    NULL
    , [ValidFrom]           DATETIME2(2)    GENERATED ALWAYS AS ROW START NOT NULL
    , [ValidTo]             DATETIME2(2)    GENERATED ALWAYS AS ROW END NOT NULL
    , PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = MasterData.ZipCodeHistory));
GO
