# CF Convention Mappings

This document provides the complete reference for CF standard name mappings to ontologies used in geo2dcat.

## Ontology Prefixes

- **SWEET**: Semantic Web for Earth and Environmental Terminology (`http://sweetontology.net/repr#`)
- **ENVO**: Environment Ontology (`http://purl.obolibrary.org/obo/ENVO_`)
- **INSPIRE**: EU INSPIRE Themes (`http://inspire.ec.europa.eu/theme/`)

## Complete CF Standard Name Mappings

### Atmospheric Variables

#### Temperature
| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `air_temperature` | `sweet:AirTemperature` | `theme:AtmosphericConditions` |
| `surface_temperature` | `sweet:SurfaceTemperature` | `theme:AtmosphericConditions` |
| `dew_point_temperature` | `sweet:DewPointTemperature` | `theme:AtmosphericConditions` |
| `air_potential_temperature` | `sweet:PotentialTemperature` | `theme:AtmosphericConditions` |
| `equivalent_potential_temperature` | `sweet:EquivalentPotentialTemperature` | `theme:AtmosphericConditions` |

#### Precipitation & Humidity
| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `precipitation_flux` | `sweet:Precipitation` | `theme:HydrologicalConditions` |
| `precipitation_amount` | `sweet:Precipitation` | `theme:HydrologicalConditions` |
| `lwe_precipitation_rate` | `sweet:Precipitation` | `theme:HydrologicalConditions` |
| `convective_precipitation_flux` | `sweet:ConvectivePrecipitation` | `theme:HydrologicalConditions` |
| `large_scale_precipitation_flux` | `sweet:LargeScalePrecipitation` | `theme:HydrologicalConditions` |
| `relative_humidity` | `sweet:RelativeHumidity` | `theme:AtmosphericConditions` |
| `specific_humidity` | `sweet:SpecificHumidity` | `theme:AtmosphericConditions` |

#### Wind
| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `eastward_wind` | `sweet:WindVelocity` | `theme:AtmosphericConditions` |
| `northward_wind` | `sweet:WindVelocity` | `theme:AtmosphericConditions` |
| `wind_speed` | `sweet:WindSpeed` | `theme:AtmosphericConditions` |
| `wind_speed_of_gust` | `sweet:WindGust` | `theme:AtmosphericConditions` |
| `wind_from_direction` | `sweet:WindDirection` | `theme:AtmosphericConditions` |

#### Pressure & Radiation
| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `air_pressure` | `sweet:AtmosphericPressure` | `theme:AtmosphericConditions` |
| `air_pressure_at_mean_sea_level` | `sweet:AtmosphericPressure` | `theme:AtmosphericConditions` |
| `surface_air_pressure` | `sweet:SurfacePressure` | `theme:AtmosphericConditions` |
| `surface_downwelling_shortwave_flux_in_air` | `sweet:SolarRadiation` | `theme:AtmosphericConditions` |
| `surface_downwelling_longwave_flux_in_air` | `sweet:LongwaveRadiation` | `theme:AtmosphericConditions` |
| `surface_upward_latent_heat_flux` | `sweet:LatentHeat` | `theme:AtmosphericConditions` |
| `surface_upward_sensible_heat_flux` | `sweet:SensibleHeat` | `theme:AtmosphericConditions` |

### Ocean Variables

| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `sea_water_temperature` | `sweet:SeaWaterTemperature` | `theme:OceanConditions` |
| `sea_surface_temperature` | `sweet:SeaSurfaceTemperature` | `theme:OceanConditions` |
| `sea_water_salinity` | `sweet:Salinity` | `theme:OceanConditions` |
| `sea_surface_salinity` | `sweet:SeaSurfaceSalinity` | `theme:OceanConditions` |
| `sea_surface_height_above_geoid` | `sweet:SeaSurfaceHeight` | `theme:OceanConditions` |
| `sea_water_velocity` | `sweet:OceanCurrent` | `theme:OceanConditions` |
| `eastward_sea_water_velocity` | `sweet:OceanCurrent` | `theme:OceanConditions` |
| `northward_sea_water_velocity` | `sweet:OceanCurrent` | `theme:OceanConditions` |
| `ocean_mixed_layer_thickness` | `sweet:MixedLayerDepth` | `theme:OceanConditions` |

### Cryosphere Variables

| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `sea_ice_area_fraction` | `sweet:SeaIce` | `theme:CryosphericConditions` |
| `sea_ice_thickness` | `sweet:SeaIceThickness` | `theme:CryosphericConditions` |
| `land_ice_thickness` | `sweet:IceThickness` | `theme:CryosphericConditions` |
| `snow_depth` | `sweet:SnowDepth` | `theme:CryosphericConditions` |
| `surface_snow_amount` | `sweet:SnowCover` | `theme:CryosphericConditions` |
| `snow_density` | `sweet:SnowDensity` | `theme:CryosphericConditions` |

### Land Surface Variables

| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `soil_moisture_content` | `sweet:SoilMoisture` | `theme:LandSurfaceConditions` |
| `volumetric_soil_water_layer` | `sweet:SoilMoisture` | `theme:LandSurfaceConditions` |
| `soil_temperature` | `sweet:SoilTemperature` | `theme:LandSurfaceConditions` |
| `surface_runoff_flux` | `sweet:Runoff` | `theme:HydrologicalConditions` |
| `subsurface_runoff_flux` | `sweet:SubsurfaceRunoff` | `theme:HydrologicalConditions` |
| `water_evaporation_flux` | `sweet:Evaporation` | `theme:HydrologicalConditions` |
| `canopy_water_amount` | `sweet:CanopyWater` | `theme:LandSurfaceConditions` |

### Vegetation Variables

| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `leaf_area_index` | `envo:LeafAreaIndex` | `theme:LandSurfaceConditions` |
| `normalized_difference_vegetation_index` | `envo:NDVI` | `theme:LandSurfaceConditions` |
| `gross_primary_productivity_of_biomass_expressed_as_carbon` | `envo:GrossPrimaryProductivity` | `theme:LandSurfaceConditions` |
| `net_primary_productivity_of_biomass_expressed_as_carbon` | `envo:NetPrimaryProductivity` | `theme:LandSurfaceConditions` |
| `vegetation_area_fraction` | `envo:VegetationCover` | `theme:LandSurfaceConditions` |

### Topography Variables

| CF Standard Name | Ontology URI | INSPIRE Theme |
|-----------------|--------------|---------------|
| `surface_altitude` | `sweet:Elevation` | `theme:ElevationConditions` |
| `bedrock_altitude` | `sweet:BedrockElevation` | `theme:ElevationConditions` |
| `geopotential_height` | `sweet:GeopotentialHeight` | `theme:ElevationConditions` |

## Common Variable Aliases

### ERA5 Aliases

| Short Name | CF Standard Name | Description |
|------------|-----------------|-------------|
| `t2m` | `air_temperature` | 2 metre temperature |
| `tp` | `precipitation_flux` | Total precipitation |
| `u10` | `eastward_wind` | 10 metre U wind component |
| `v10` | `northward_wind` | 10 metre V wind component |
| `sp` | `air_pressure` | Surface pressure |
| `msl` | `air_pressure_at_mean_sea_level` | Mean sea level pressure |
| `sst` | `sea_surface_temperature` | Sea surface temperature |
| `d2m` | `dew_point_temperature` | 2 metre dewpoint temperature |
| `si10` | `wind_speed` | 10 metre wind speed |
| `skt` | `surface_temperature` | Skin temperature |
| `stl1` | `soil_temperature` | Soil temperature level 1 |
| `swvl1` | `volumetric_soil_water_layer` | Soil water volume level 1 |
| `sd` | `snow_depth` | Snow depth |
| `e` | `water_evaporation_flux` | Evaporation |
| `ro` | `runoff_flux` | Runoff |

### CMIP6 Aliases

| Short Name | CF Standard Name | Description |
|------------|-----------------|-------------|
| `tas` | `air_temperature` | Near-surface air temperature |
| `pr` | `precipitation_flux` | Precipitation |
| `uas` | `eastward_wind` | Eastward near-surface wind |
| `vas` | `northward_wind` | Northward near-surface wind |
| `psl` | `air_pressure_at_mean_sea_level` | Sea level pressure |
| `tos` | `sea_surface_temperature` | Sea surface temperature |
| `hurs` | `relative_humidity` | Near-surface relative humidity |
| `huss` | `specific_humidity` | Near-surface specific humidity |
| `sfcWind` | `wind_speed` | Near-surface wind speed |
| `rsds` | `surface_downwelling_shortwave_flux_in_air` | Surface downwelling shortwave radiation |
| `rlds` | `surface_downwelling_longwave_flux_in_air` | Surface downwelling longwave radiation |
| `mrso` | `soil_moisture_content` | Total soil moisture content |
| `snd` | `snow_depth` | Snow depth |
| `snw` | `surface_snow_amount` | Surface snow amount |
| `siconc` | `sea_ice_area_fraction` | Sea ice area fraction |

### CORDEX Aliases

| Short Name | CF Standard Name | Description |
|------------|-----------------|-------------|
| `tas` | `air_temperature` | Air temperature |
| `tasmax` | `air_temperature` | Daily maximum air temperature |
| `tasmin` | `air_temperature` | Daily minimum air temperature |
| `pr` | `precipitation_flux` | Precipitation |
| `prsn` | `snowfall_flux` | Snowfall flux |
| `ps` | `surface_air_pressure` | Surface air pressure |
| `rsds` | `surface_downwelling_shortwave_flux_in_air` | Surface solar radiation downwards |
| `sfcWind` | `wind_speed` | Surface wind speed |
| `hurs` | `relative_humidity` | Surface relative humidity |

## Adding Custom Mappings

To add custom CF mappings in your code:

```python
from geo2dcat.mappings import CF_STANDARD_NAME_MAPPING, CF_SHORT_ALIASES, THEME_MAPPING

# Add a new CF standard name mapping
CF_STANDARD_NAME_MAPPING["my_custom_temperature"] = "sweet:CustomTemperature"

# Add a new short alias
CF_SHORT_ALIASES["cust_t"] = "my_custom_temperature"

# Add a new theme mapping
THEME_MAPPING["sweet:CustomTemperature"] = "theme:AtmosphericConditions"
```

## Notes

1. **Multiple mappings**: Some CF standard names may map to the same ontology concept (e.g., both `precipitation_flux` and `precipitation_amount` map to `sweet:Precipitation`)

2. **Missing mappings**: If a CF standard name is not in the mapping table, the `cf:ontologyURI` will be `null` in the output

3. **Case sensitivity**: All CF standard names are lowercase and use underscores

4. **Units preservation**: The ontology mapping does not change the units - they are preserved as-is from the source file

5. **Custom extensions**: Organizations can extend these mappings for domain-specific variables while maintaining compatibility with the base mappings