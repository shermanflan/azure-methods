CREATE UNIQUE INDEX IX_STATETERRITORY_FIPS 
	ON [MasterData].[StateTerritory]
(
	[StateFIPS]
)
INCLUDE ([StateName], [StateCode])
;

CREATE UNIQUE INDEX IX_STATETERRITORY_STATENAME
	ON [MasterData].[StateTerritory]
(
	[StateName]
)
INCLUDE ([StateFIPS], [StateCode])
;

CREATE UNIQUE INDEX IX_STATETERRITORY_STATECODE 
	ON [MasterData].[StateTerritory]
(
	[StateCode]
)
INCLUDE ([StateName], [StateFIPS])
;

CREATE UNIQUE INDEX IX_COUNTYPROVINCE_FIPS 
	ON [MasterData].[CountyProvince]
(
	[CountyFIPS], [StateFIPS]
)
INCLUDE ([CountyName])
;

CREATE UNIQUE INDEX IX_COUNTYPROVINCE_COUNTYNAME 
	ON [MasterData].[CountyProvince]
(
	[CountyName], [StateFIPS]
)
INCLUDE ([CountyFIPS])
;

CREATE UNIQUE INDEX IX_GEOPLACE_GEONAMEID 
	ON [MasterData].[GeoPlace]
(
	[GeoNameId], [PlaceName]
)
INCLUDE ([SourceModificationDate])
;

CREATE UNIQUE INDEX IX_ZIPCODE_ZIPCODE
	ON [MasterData].[ZipCode]
(
	[ZipCode]
)
INCLUDE ([PlaceName], [GeoNameId])
;