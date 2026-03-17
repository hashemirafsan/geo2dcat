from __future__ import annotations

import csv
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv()
    _write_netcdf()
    _write_hdf5()
    _write_geotiff()
    _write_vector()


def _write_csv() -> None:
    path = FIXTURES_DIR / "sample.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["station", "temp", "humidity"])
        writer.writeheader()
        writer.writerow({"station": "A", "temp": 290.1, "humidity": 55})
        writer.writerow({"station": "B", "temp": 291.0, "humidity": 58})


def _write_netcdf() -> None:
    try:
        import netCDF4
    except ImportError:
        return
    path = FIXTURES_DIR / "sample.nc"
    dataset = netCDF4.Dataset(path, "w")
    dataset.createDimension("time", 2)
    dataset.createDimension("lat", 2)
    dataset.createDimension("lon", 2)
    dataset.title = "Sample NetCDF"
    dataset.summary = "Fixture file for geo2dcat tests"
    dataset.institution = "Test Lab"
    dataset.Conventions = "CF-1.8"
    time = dataset.createVariable("time", "f8", ("time",))
    time.units = "hours since 2024-01-01 00:00:00"
    time[:] = [0, 24]
    lat = dataset.createVariable("lat", "f4", ("lat",))
    lat[:] = [10.0, 11.0]
    lon = dataset.createVariable("lon", "f4", ("lon",))
    lon[:] = [20.0, 21.0]
    t2m = dataset.createVariable("t2m", "f4", ("time", "lat", "lon"))
    t2m.long_name = "2 metre temperature"
    t2m.units = "K"
    dataset.close()


def _write_hdf5() -> None:
    try:
        import h5py
    except ImportError:
        return
    path = FIXTURES_DIR / "sample.h5"
    with h5py.File(path, "w") as handle:
        handle.attrs["title"] = "Sample HDF5"
        data = handle.create_dataset("sst", shape=(2, 2), dtype="f4")
        data.attrs["long_name"] = "sea surface temperature"
        data.attrs["units"] = "K"


def _write_geotiff() -> None:
    try:
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
    except ImportError:
        return
    path = FIXTURES_DIR / "sample.tif"
    transform = from_origin(20.0, 11.0, 0.5, 0.5)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=2,
        height=2,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dataset:
        dataset.write(np.array([[1.0, 2.0], [3.0, 4.0]], dtype="float32"), 1)
        dataset.set_band_description(1, "surface temperature")


def _write_vector() -> None:
    try:
        import geopandas as gpd
        from shapely.geometry import Point
    except ImportError:
        return
    path = FIXTURES_DIR / "sample.geojson"
    gdf = gpd.GeoDataFrame(
        {"name": ["A"], "value": [1]},
        geometry=[Point(20.0, 10.0)],
        crs="EPSG:4326",
    )
    gdf.to_file(path, driver="GeoJSON")


if __name__ == "__main__":
    main()
