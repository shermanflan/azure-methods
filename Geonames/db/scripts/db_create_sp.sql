DROP PROCEDURE IF EXISTS MasterData.usp_UpsertGeography;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertStateTerritory;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertCountyProvince;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertGeoPlace;
DROP PROCEDURE IF EXISTS MasterData.usp_UpsertZipCode;
GO

CREATE PROCEDURE MasterData.usp_UpsertGeography
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        
        BEGIN TRANSACTION txnUpsertGeography;

        EXEC MasterData.usp_UpsertStateTerritory;
        EXEC MasterData.usp_UpsertCountyProvince;
        EXEC MasterData.usp_UpsertGeoPlace;
        EXEC MasterData.usp_UpsertZipCode;

        COMMIT TRANSACTION txnUpsertGeography;

    END TRY
    BEGIN CATCH

        IF @@TRANCOUNT > 0 AND XACT_STATE() != 0
        BEGIN
            ROLLBACK TRANSACTION;
        END

        DECLARE @messsage NVARCHAR(2048);

        SET @messsage = (
            SELECT CONCAT('usp_UpsertGeography ERROR: ', ERROR_MESSAGE())
        ); 

        THROW 50000, @messsage, 0;

    END CATCH

END
GO

CREATE PROCEDURE MasterData.usp_UpsertStateTerritory
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        
        INSERT INTO [MasterData].[StateTerritory] (
            [Region]
            ,[Division]
            ,[StateFIPS]
            ,[StateName]
            ,[StateCode]
            ,[RegionName]
            ,[DivisionName]
            ,[RecCreatedBy]
        )
        SELECT  s.[Region]
                , s.[Division]
                , s.[StateFIPS]
                , s.[StateName]
                , s.[USPS]
                , s.[RegionName]
                , s.[DivisionName]
                , s.[RecCreatedBy]
        FROM [Staging].[State] AS s
            LEFT JOIN [MasterData].[StateTerritory] AS t
                ON s.[StateFIPS] = t.[StateFIPS]
        WHERE   t.[Id] IS NULL;

    END TRY
    BEGIN CATCH

        DECLARE @messsage NVARCHAR(2048);

        SET @messsage = (
            SELECT CONCAT('usp_UpsertStateTerritory ERROR: ', ERROR_MESSAGE())
        ); 

        THROW 50000, @messsage, 0;

    END CATCH

END
GO

CREATE PROCEDURE MasterData.usp_UpsertCountyProvince
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        
        MERGE INTO [MasterData].[CountyProvince] AS t 
            USING [Staging].[County] AS s
                ON  s.[CountyFIPS] = t.[CountyFIPS]
                    AND s.[StateFIPS] = t.[StateFIPS]
        WHEN MATCHED AND t.[CountyNameOriginal] <> s.[NAME]
            THEN 
                UPDATE SET
                    [CountyNameOriginal] = s.[NAME]
                    , [CountyName] = s.[CountyPrefix]
                    , [CountyType] = s.[CountySuffix]
                    , [Latitude] = s.[INTPTLAT]
                    , [Longitude] = s.[INTPTLONG]
                    , [ModifiedDateTime] = GETDATE()
                    , [ModifiedBy] = USER_NAME()
        WHEN NOT MATCHED THEN
            INSERT (
                [StateCode]
                , [StateFIPS]
                , [CountyFIPS]
                , [ANSICode]
                , [CountyNameOriginal]
                , [CountyName]
                , [CountyType]
                , [Latitude]
                , [Longitude]
                , [RecCreatedBy]
            )
        VALUES (
            s.[USPS]
            , s.[StateFIPS]
            , s.[CountyFIPS]
            , s.[ANSICode]
            , s.[NAME]
            , s.[CountyPrefix]
            , s.[CountySuffix]
            , s.[INTPTLAT]
            , s.[INTPTLONG]
            , s.[RecCreatedBy]
        );

    END TRY
    BEGIN CATCH

        DECLARE @messsage NVARCHAR(2048);

        SET @messsage = (
            SELECT CONCAT('usp_UpsertCountyProvince ERROR: ', ERROR_MESSAGE())
        ); 

        THROW 50000, @messsage, 0;

    END CATCH

END
GO

CREATE PROCEDURE MasterData.usp_UpsertGeoPlace
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        
        INSERT INTO [MasterData].[GeoPlace] (
            [GeoNameId]
            , [PlaceName]
            , [PlaceSynonyms]
            , [FeatureClass]
            , [FeatureCode]
            , [CountryCode]
            , [StateCode]       -- admin_code1
            , [StateFIPS]
            , [CountyFIPS]      -- admin_code2
            , [PlaceFIPS]       -- admin_code3
            , [Population]      
            , [Elevation]       
            , [DEM]
            , [TimeZone]        
            , [Latitude]       
            , [Longitude]
            , [SourceModificationDate]
            , [RecCreatedBy]
        )
        SELECT  p.[geonameid]     
                , p.[name]
                , p.[alternatenames]
                , p.[feature_class]
                , p.[feature_code]
                , p.[country_code]
                , p.[admin_code1]
                , s.[StateFIPS]
                , p.[admin_code2]
                , p.[admin_code3]    
                , p.[population]
                , p.[elevation]
                , p.[dem]
                , p.[timezone]
                , p.[latitude]
                , p.[longitude]
                , p.[modification_date]
                , p.[RecCreatedBy]     
        FROM    [Staging].[GeoPlace] AS p
            INNER JOIN [Staging].[State] AS s
                ON p.[admin_code1] = s.[USPS]
            LEFT JOIN [MasterData].[GeoPlace] AS t
                ON  p.[geonameid] = t.[GeoNameId]
                    AND p.[name] = t.[PlaceName]
        WHERE   t.[Id] IS NULL
        ;
        
        UPDATE [MasterData].[GeoPlace] 
            SET
                [PlaceSynonyms] = p.[alternatenames]
                , [FeatureClass] = p.[feature_class]
                , [FeatureCode] = p.[feature_code]
                , [CountryCode] = p.[country_code]
                , [StateCode] = p.[admin_code1]
                , [StateFIPS] = s.[StateFIPS]
                , [CountyFIPS] = p.[admin_code2]
                , [PlaceFIPS] = p.[admin_code3]
                , [Population] = p.[population]      
                , [Elevation] = p.[elevation]       
                , [DEM] = p.[dem]
                , [TimeZone] = p.[timezone]        
                , [Latitude] = p.[latitude]       
                , [Longitude] = p.[longitude]
                , [SourceModificationDate] = p.[modification_date]
                , [RecCreatedBy] = p.[RecCreatedBy]
                , [ModifiedDateTime] = GETDATE()
                , [ModifiedBy] = USER_NAME()
        FROM    [Staging].[GeoPlace] AS p
            INNER JOIN [Staging].[State] AS s
                ON p.[admin_code1] = s.[USPS]
            LEFT JOIN [MasterData].[GeoPlace] AS t
                ON  p.[geonameid] = t.[GeoNameId]
                    AND p.[name] = t.[PlaceName]
        WHERE   t.[Id] IS NOT NULL 
                AND t.[SourceModificationDate] <> p.[modification_date]
        ;

    END TRY
    BEGIN CATCH

        DECLARE @messsage NVARCHAR(2048);

        SET @messsage = (
            SELECT CONCAT('usp_UpsertGeoPlace ERROR: ', ERROR_MESSAGE())
        ); 

        THROW 50000, @messsage, 0;

    END CATCH
END
GO

CREATE PROCEDURE MasterData.usp_UpsertZipCode
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        
        WITH zip
        AS
        (
            SELECT  z.[country_code]
                    , z.[postal_code]
                    , z.[place_name]
                    , p.[geonameid]
                    , p.[admin_code3]
                    , z.[admin_name1]
                    , z.[admin_code1]
                    , s.[StateFIPS]
                    , z.[admin_name2]
                    , z.[admin_code2]
                    , z.[latitude]
                    , z.[longitude]
                    -- accuracy of lat/lng
                    , CASE
                        WHEN z.[accuracy] = 1 THEN 'estimated'
                        WHEN z.[accuracy] = 4 THEN 'geonameid'
                        WHEN z.[accuracy] = 6 THEN 'centroid of addresses or shape'
                    END AS [accuracy]
                    , z.[RecCreatedBy]
                    , ROW_NUMBER() OVER (PARTITION BY z.[postal_code]
                                        ORDER BY CASE
                                                    WHEN p.[feature_class] = 'P' THEN 1 -- city, village
                                                    WHEN p.[feature_class] = 'A' THEN 2 -- country, state, region
                                                    WHEN p.[feature_class] = 'H' THEN 3 -- stream, lake
                                                    WHEN p.[feature_class] = 'L' THEN 4 -- parks, area
                                                    WHEN p.[feature_class] = 'R' THEN 5 -- road, railroad
                                                    WHEN p.[feature_class] = 'S' THEN 6 -- spot, building, farm
                                                    WHEN p.[feature_class] = 'T' THEN 7 -- mountain, hill, rock
                                                    WHEN p.[feature_class] = 'V' THEN 8 -- forest, heath
                                                    ELSE 10
                                                END
                                                , p.[feature_code], p.[name], p.[geonameid]
                                ) AS [PlaceRank]
            FROM [Staging].[ZipCode] AS z
                LEFT JOIN [Staging].[State] AS s
                    ON z.[admin_code1] = s.[USPS]
                LEFT JOIN [Staging].[GeoPlace] AS p
                    ON	z.[admin_code1] = p.[admin_code1] -- us states
						-- us counties
						AND (
							z.[admin_code2] IS NULL
							OR p.[admin_code2] IS NULL
							OR z.[admin_code2] = p.[admin_code2]
						)
                        AND z.[place_name] = p.[name]
            WHERE   z.[admin_name1] IS NOT NULL  -- us states only
        )
        MERGE INTO [MasterData].[ZipCode] AS t 
            USING (
                SELECT  *
                FROM    zip AS z
                WHERE   z.PlaceRank = 1
            ) as s
                ON s.[postal_code] = t.[ZipCode]
        WHEN MATCHED 
            AND (t.[PlaceName] <> s.[place_name]
                OR t.[GeoNameId] <> s.[geonameid])
            THEN
                UPDATE SET
                    [CountryCode] = s.[country_code]
                    , [PlaceName] = s.[place_name]
                    , [GeoNameId] = s.[geonameid]
                    , [PlaceFIPS] = s.[admin_code3]
                    , [StateName] = s.[admin_name1]
                    , [StateCode] = s.[admin_code1]
                    , [StateFIPS] = s.[StateFIPS]
                    , [CountyName] = s.[admin_name2]
                    , [CountyFIPS] = s.[admin_code2]
                    , [Latitude] = s.[latitude]
                    , [Longitude] = s.[longitude]
                    , [Accuracy] = s.[accuracy]
                    , [ModifiedDateTime] = GETDATE()
                    , [ModifiedBy] = USER_NAME()
        WHEN NOT MATCHED THEN
            INSERT (
                [CountryCode]
                ,[ZipCode]
                ,[PlaceName]
                ,[GeoNameId]
                ,[PlaceFIPS]
                ,[StateName]
                ,[StateCode]
                ,[StateFIPS]
                ,[CountyName]
                ,[CountyFIPS]
                ,[Latitude]
                ,[Longitude]
                ,[Accuracy]
                ,[RecCreatedBy]
            )
            VALUES (
                s.[country_code]
                , s.[postal_code]
                , s.[place_name]
                , s.[geonameid]
                , s.[admin_code3]
                , s.[admin_name1]
                , s.[admin_code1]
                , s.[StateFIPS]
                , s.[admin_name2]
                , s.[admin_code2]
                , s.[latitude]
                , s.[longitude]
                , s.[accuracy]
                , s.[RecCreatedBy]
            )
        ;

    END TRY
    BEGIN CATCH

        DECLARE @messsage NVARCHAR(2048);

        SET @messsage = (
            SELECT CONCAT('usp_UpsertZipCode ERROR: ', ERROR_MESSAGE())
        ); 

        THROW 50000, @messsage, 0;

    END CATCH

END
GO
