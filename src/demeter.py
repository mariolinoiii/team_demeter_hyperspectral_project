"""Project Demeter - helper functions.

Self-contained: it needs only numpy, h5py, rasterio and requests (no course helper file).
Every function is short and commented so that each step can be explained.

Conventions
-----------
* Cubes are (bands, rows, cols), reflectance 0-1, NaN where invalid.
* Wavelengths are in nanometres.
* Confusion matrices are cm[reference, predicted].
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------------------
# 1. Tanager HDF5 access
# --------------------------------------------------------------------------------------
GRID = "HDFEOS/GRIDS/HYP"
FIELDS = GRID + "/Data Fields/"
REFLECTANCE = FIELDS + "surface_reflectance"
UNCERTAINTY = FIELDS + "surface_reflectance_uncertainty"


def download(url: str, dest: Path) -> Path:
    """Download `url` to `dest` once (resumable check by size); never partially trusted."""
    import h5py
    import requests

    dest = Path(dest)
    if dest.exists() and h5py.is_hdf5(dest):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(".part")
    with requests.get(url, stream=True, timeout=(30, 300)) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        got = 0
        with part.open("wb") as f:
            for chunk in r.iter_content(8 * 1024 * 1024):
                f.write(chunk)
                got += len(chunk)
    if total and got != total:
        raise IOError(f"Incomplete download: {got}/{total} bytes")
    part.replace(dest)
    return dest


def scene_grid(h5) -> dict:
    """Read the map grid (CRS, upper-left corner, pixel size) from the file's own metadata."""
    raw = h5["HDFEOS INFORMATION/StructMetadata.0"][()]
    text = raw.decode() if isinstance(raw, bytes) else str(raw)
    ul = re.search(r"UpperLeftPointMtrs=\(([-\d.]+),([-\d.]+)\)", text)
    lr = re.search(r"LowerRightMtrs=\(([-\d.]+),([-\d.]+)\)", text)
    xdim = int(re.search(r"XDim=(\d+)", text).group(1))
    ydim = int(re.search(r"YDim=(\d+)", text).group(1))
    x0, y0 = float(ul.group(1)), float(ul.group(2))
    x1, y1 = float(lr.group(1)), float(lr.group(2))
    px, py = (x1 - x0) / xdim, (y0 - y1) / ydim
    if abs(px - py) > 1e-6:
        raise ValueError("Non-square pixels: unexpected grid definition")
    return dict(epsg=int(h5[GRID].attrs["epsg_code"]), x0=x0, y0=y0, pixel=px, xdim=xdim, ydim=ydim)


def crop_window(grid: dict, size: int = 512):
    """Central square window (row0, row1, col0, col1)."""
    r0 = (grid["ydim"] - size) // 2
    c0 = (grid["xdim"] - size) // 2
    return r0, r0 + size, c0, c0 + size


def affine_for(grid: dict, window):
    """Affine transform (rasterio) of a window of the scene grid."""
    from rasterio.transform import Affine

    r0, _, c0, _ = window
    p = grid["pixel"]
    return Affine(p, 0.0, grid["x0"] + c0 * p, 0.0, -p, grid["y0"] - r0 * p)


def band_metadata(h5):
    """Wavelengths (nm), provider good-band flags and FWHM (nm)."""
    a = h5[REFLECTANCE].attrs
    return (np.asarray(a["wavelengths"], float), np.asarray(a["good_wavelengths"]).astype(bool),
            np.asarray(a["fwhm"], float))


def read_cube(h5, window, name: str = REFLECTANCE) -> np.ndarray:
    """Read a (bands, rows, cols) window as float32; the fill value -9999 becomes NaN."""
    r0, r1, c0, c1 = window
    cube = h5[name][:, r0:r1, c0:c1].astype("float32")
    cube[cube <= -9000] = np.nan
    return cube


def read_flag(h5, name: str, window) -> np.ndarray:
    """Read a binary mask (1 = flagged) as boolean. Fill value 255 counts as flagged."""
    r0, r1, c0, c1 = window
    m = h5[FIELDS + name][r0:r1, c0:c1]
    return (m == 1) | (m == 255)


def retained_bands(wl, good, bad_ranges) -> np.ndarray:
    """Keep bands the provider marks good AND that lie outside our extra exclusion ranges."""
    keep = good.copy()
    for lo, hi in bad_ranges:
        keep &= ~((wl >= lo) & (wl <= hi))
    return keep


def nearest(wl, nm: float, tol: float = 15.0) -> int:
    """Index of the band closest to `nm`; refuse if none is within `tol` nm."""
    i = int(np.argmin(np.abs(wl - nm)))
    if abs(wl[i] - nm) > tol:
        raise ValueError(f"No retained band within {tol} nm of {nm} nm")
    return i


# --------------------------------------------------------------------------------------
# 2. Spectral features
# --------------------------------------------------------------------------------------
def norm_diff(a, b):
    """(a - b) / (a + b), NaN where either input is invalid or the sum is ~0."""
    out = np.full(np.shape(a), np.nan, dtype="float32")
    ok = np.isfinite(a) & np.isfinite(b) & (np.abs(a + b) > 1e-6)
    np.divide(a - b, a + b, out=out, where=ok)
    return out


def ndvi_sigma(red, nir, s_red, s_nir):
    """1-sigma NDVI uncertainty by first-order error propagation of the two bands.

    NDVI = (N - R) / (N + R);  dNDVI/dN = 2R/(N+R)^2;  dNDVI/dR = -2N/(N+R)^2.
    The two band errors are treated as independent (a simplification: they are probably
    positively correlated, which would make the true NDVI error smaller).
    """
    s = (nir + red) ** 2
    return np.sqrt((2 * red * s_nir / s) ** 2 + (2 * nir * s_red / s) ** 2).astype("float32")


def red_edge_position(cube, wl):
    """Red-edge position (nm) by four-point linear interpolation (Guyot, Baret & Major, 1988).

    Uses reflectance at ~670, 700, 740 and 780 nm. It needs narrow bands, which a broadband
    sensor does not have, so this is a hyperspectral-specific feature.
    """
    r670, r700, r740, r780 = (cube[nearest(wl, w)] for w in (670, 700, 740, 780))
    r_edge = 0.5 * (r670 + r780)
    out = np.full(r670.shape, np.nan, dtype="float32")
    den = r740 - r700
    ok = np.isfinite(den) & (np.abs(den) > 1e-4)
    out[ok] = 700 + 40 * (r_edge[ok] - r700[ok]) / den[ok]
    return np.clip(out, 680, 760)


# Sentinel-2 band centre and bandwidth (nm), from the ESA Sentinel-2 specification.
S2_BANDS = {"B2": (490, 65), "B3": (560, 35), "B4": (665, 30), "B5": (705, 15), "B6": (740, 15),
            "B7": (783, 20), "B8": (842, 115), "B8A": (865, 20), "B11": (1610, 90), "B12": (2190, 180)}


def simulate_bands(X, wl, bands=S2_BANDS):
    """Approximate a broadband sensor from narrow bands.

    X is (pixels, retained_bands). Each broad band is a Gaussian-weighted mean of the narrow
    bands around its centre (FWHM = bandwidth, cut at 1.5 x FWHM). Real Sentinel-2 response
    curves are flatter, so this is an approximation.
    """
    cols = []
    for centre, fwhm in bands.values():
        w = np.exp(-0.5 * ((wl - centre) / (fwhm / 2.3548)) ** 2)
        w[np.abs(wl - centre) > 1.5 * fwhm] = 0
        if w.sum() == 0:
            raise ValueError(f"No retained narrow bands near {centre} nm")
        cols.append((X @ w) / w.sum())
    return np.column_stack(cols).astype("float32")


# --------------------------------------------------------------------------------------
# 3. Independent reference labels (ESA WorldCover 2021 v200, CC-BY 4.0)
# --------------------------------------------------------------------------------------
CLASS_NAMES = ["Cropland", "Woody vegetation", "Grassland", "Built-up / bare", "Water"]
VEGETATION = [0, 1, 2]                                   # classes counted as "vegetation"
WC_TO_CLASS = {40: 0, 10: 1, 20: 1, 30: 2, 50: 3, 60: 3, 80: 4}   # WorldCover code -> class
WC_CODES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
WC_BASE = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"


def worldcover_url(lon: float, lat: float) -> str:
    """URL of the 3 x 3 degree WorldCover tile that contains (lon, lat)."""
    lat0, lon0 = int(np.floor(lat / 3) * 3), int(np.floor(lon / 3) * 3)
    tile = f"{'N' if lat0 >= 0 else 'S'}{abs(lat0):02d}{'E' if lon0 >= 0 else 'W'}{abs(lon0):03d}"
    return f"{WC_BASE}ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"


def worldcover_on_grid(transform, shape, epsg, factor: int = 3, cache: Path | None = None):
    """Resample WorldCover (10 m) onto the Tanager grid (30 m = factor x factor cells).

    Returns
      modal : (H, W) WorldCover code that occurs most often in the 3 x 3 cells
      pure  : (H, W) class index (0-4) only where all 9 cells agree and the class is used;
              otherwise -1. Using pure pixels keeps mixed edge pixels out of training/testing.
    """
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.warp import Resampling, reproject, transform_bounds
    from rasterio.windows import from_bounds

    if cache is not None and Path(cache).exists():
        z = np.load(cache)
        return z["modal"], z["pure"]
    h, w = shape
    px = transform.a
    x0, y_top = transform.c, transform.f
    left, bottom, right, top = x0, y_top - h * px, x0 + w * px, y_top
    west, south, east, north = transform_bounds(f"EPSG:{epsg}", "EPSG:4326", left, bottom, right, top, densify_pts=21)
    pad = 0.005
    with rasterio.open(worldcover_url((west + east) / 2, (south + north) / 2)) as ds:
        win = from_bounds(west - pad, south - pad, east + pad, north + pad, transform=ds.transform)
        win = win.round_offsets().round_lengths()
        src, src_tf = ds.read(1, window=win), ds.window_transform(win)
    fine = np.zeros((h * factor, w * factor), dtype="uint8")
    reproject(src, fine, src_transform=src_tf, src_crs="EPSG:4326",
              dst_transform=from_origin(x0, y_top, px / factor, px / factor), dst_crs=f"EPSG:{epsg}",
              resampling=Resampling.nearest)
    cells = fine.reshape(h, factor, w, factor).transpose(0, 2, 1, 3).reshape(h, w, factor * factor)
    counts = np.stack([(cells == c).sum(2) for c in WC_CODES])
    modal = np.array(WC_CODES, dtype="uint8")[counts.argmax(0)]
    pure = np.full((h, w), -1, dtype="int8")
    all_same = (cells == cells[:, :, :1]).all(2)
    for code, k in WC_TO_CLASS.items():
        pure[all_same & (cells[:, :, 0] == code)] = k
    if cache is not None:
        np.savez_compressed(cache, modal=modal, pure=pure)
    return modal, pure


# --------------------------------------------------------------------------------------
# 4. Spatially independent splits
# --------------------------------------------------------------------------------------
def block_ids(shape, block: int = 40) -> np.ndarray:
    """Integer id of the block x block square each pixel belongs to."""
    h, w = shape
    n_cols = int(np.ceil(w / block))
    r = np.arange(h)[:, None] // block
    c = np.arange(w)[None, :] // block
    return (r * n_cols + c).astype(np.int32)


def assign_blocks(ref, usable, block=40, fractions=(0.5, 0.2, 0.3), min_pixels=(200, 60, 100), seed0=42):
    """Randomly give whole blocks to train / validation / test (0 / 1 / 2).

    Whole blocks, not single pixels, are assigned, so no test pixel has a training neighbour
    inside the same block. We redraw (different seed) until every class has at least
    `min_pixels` usable reference pixels in every split.
    Returns (split_image, seed_used).
    """
    ids = block_ids(ref.shape, block)
    n_blocks = ids.max() + 1
    k = len(CLASS_NAMES)
    per_block = np.zeros((n_blocks, k), dtype=np.int64)
    for c in range(k):
        per_block[:, c] = np.bincount(ids[usable & (ref == c)], minlength=n_blocks)
    n_train, n_val = int(round(fractions[0] * n_blocks)), int(round(fractions[1] * n_blocks))
    for attempt in range(2000):
        rng = np.random.default_rng(seed0 + attempt)
        order = rng.permutation(n_blocks)
        split_of_block = np.empty(n_blocks, dtype=np.int8)
        split_of_block[order[:n_train]] = 0
        split_of_block[order[n_train:n_train + n_val]] = 1
        split_of_block[order[n_train + n_val:]] = 2
        ok = all(per_block[split_of_block == s].sum(0).min() >= min_pixels[s] for s in range(3))
        if ok:
            return split_of_block[ids], seed0 + attempt
    raise RuntimeError("Could not find a split in which every class appears in every split")


# --------------------------------------------------------------------------------------
# 5. Metrics and block bootstrap (confusion matrices are cm[reference, predicted])
# --------------------------------------------------------------------------------------
def block_confusions(y, p, blocks, k):
    """One k x k confusion matrix per block -> array (n_blocks, k, k) plus the block ids."""
    uniq, inv = np.unique(blocks, return_inverse=True)
    flat = np.bincount(inv * k * k + y * k + p, minlength=len(uniq) * k * k)
    return flat.reshape(len(uniq), k, k), uniq


def metrics_from_cm(cm):
    """OA, per-class precision (user's acc.), recall (producer's acc.), F1, IoU, macro-F1.

    Works on one matrix (k, k) or a stack (B, k, k). Classes with no data give NaN.
    """
    cm = np.asarray(cm, dtype=float)
    tp = np.diagonal(cm, axis1=-2, axis2=-1)
    ref, pred = cm.sum(-1), cm.sum(-2)
    with np.errstate(divide="ignore", invalid="ignore"):
        precision, recall = tp / pred, tp / ref
        f1 = 2 * precision * recall / (precision + recall)
        iou = tp / (ref + pred - tp)
        oa = tp.sum(-1) / cm.sum((-2, -1))
    return dict(OA=oa, precision=precision, recall=recall, F1=f1, IoU=iou, macro_F1=np.nanmean(f1, axis=-1))


def bootstrap_draws(n_blocks, n_boot=1000, seed=42):
    """Indices of blocks drawn with replacement, shared by all models (so differences are paired)."""
    return np.random.default_rng(seed).integers(0, n_blocks, size=(n_boot, n_blocks))


def boot_cm(block_cm, draws):
    """Sum the confusion matrices of the resampled blocks -> (n_boot, k, k)."""
    return block_cm[draws].sum(axis=1)


def ci95(values):
    """2.5 and 97.5 percentiles (ignores NaN)."""
    return tuple(np.nanpercentile(values, [2.5, 97.5]))


def merge_classes(y, mapping):
    """Relabel an integer array with a lookup array (used to build vegetation / non-vegetation)."""
    return np.asarray(mapping)[y]


# --------------------------------------------------------------------------------------
# 6. GeoTIFF / COG output
# --------------------------------------------------------------------------------------
def save_cog(path, array, transform, epsg, nodata, description):
    """Write a single-band Cloud-Optimised GeoTIFF with CRS, transform and a band description."""
    import tempfile

    import rasterio
    from rasterio.shutil import copy as rio_copy

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_tif = Path(tmp) / "tmp.tif"
        with rasterio.open(tmp_tif, "w", driver="GTiff", height=array.shape[0], width=array.shape[1], count=1,
                           dtype=array.dtype, crs=f"EPSG:{epsg}", transform=transform, nodata=nodata) as dst:
            dst.write(array, 1)
            dst.set_band_description(1, description)
        rio_copy(str(tmp_tif), str(path), driver="COG", compress="DEFLATE")
    return path
