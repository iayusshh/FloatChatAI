import xarray as xr
import numpy as np
import pandas as pd

def generate_dummy_nc():
    # dimensions
    taxis = pd.date_range("2023-01-01", periods=60, freq="D")
    xaxis = np.linspace(40, 130, 150)  # lon
    yaxis = np.linspace(-40, 40, 80)    # lat
    zax = np.array([10.0, 50.0, 100.0, 200.0, 500.0, 1000.0])

    # data
    shape = (len(taxis), len(zax), len(yaxis), len(xaxis))
    
    # Create realistic-looking data
    temp = 20.0 - (np.random.rand(*shape) * 5) - (np.arange(len(zax)).reshape(1, -1, 1, 1) * 2)
    sal = 35.0 + (np.random.randn(*shape) * 0.5)

    ds = xr.Dataset(
        {
            "TEMP": (["TAXIS", "ZAX", "YAXIS", "XAXIS"], temp),
            "SAL": (["TAXIS", "ZAX", "YAXIS", "XAXIS"], sal),
        },
        coords={
            "TAXIS": taxis,
            "ZAX": zax,
            "YAXIS": yaxis,
            "XAXIS": xaxis,
        },
    )

    ds.to_netcdf("tempsal.nc")
    print("Generated dummy tempsal.nc successfully.")

if __name__ == "__main__":
    generate_dummy_nc()
