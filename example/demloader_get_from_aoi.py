import math


def get_from_aoi(aoi, resolution):
    """
    This is a copy from 'demloader' project available at https://github.com/gaffinetB/demloader/tree/main.
    Function 'get_from_aoi()' from prefixes.py. From commit hash 'fcb3eb87ef324860c42a060bb21373c4d12e8450'.
    """
    resolution = str(int(resolution / 3))
    left, bottom, right, top = list(aoi)
    downloads = []

    if left * right < 0 and bottom * top > 0:
        northwards = 'N' if bottom > 0 else 'S'
        max_northing = math.floor(top) if northwards == 'N' else -math.floor(bottom)
        min_northing = math.floor(bottom) if northwards == 'N' else -math.floor(top)

        for northing in range(min_northing, max_northing + 1):
            eastwards = 'E'
            min_easting, max_easting = 0, math.floor(right)
            for easting in range(min_easting, max_easting + 1):
                downloads.append(
                    f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

            eastwards = 'W'
            min_easting, max_easting = 1, -math.floor(left)
            for easting in range(min_easting, max_easting + 1):
                downloads.append(
                    f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

    elif bottom * top < 0 and left * right > 0:
        eastwards = 'E' if left > 0 else 'W'
        max_easting = math.floor(right) if eastwards == 'E' else -math.floor(left)
        min_easting = math.floor(left) if eastwards == 'E' else -math.floor(right)

        for easting in range(min_easting, max_easting + 1):
            northwards = 'N'
            min_northing, max_northing = 0, math.floor(top)
            for northing in range(min_northing, max_northing + 1):
                downloads.append(
                    f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

            northwards = 'S'
            min_northing, max_northing = 1, -math.floor(bottom)
            for northing in range(min_northing, max_northing + 1):
                downloads.append(
                    f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

    elif bottom * top < 0 and left * right < 0:
        raise NotImplementedError(
            "Please choose AOI that does not contain both Prime Meridian and Equator simulataneously.")

    else:
        northwards = 'N' if bottom > 0 else 'S'
        max_northing = math.floor(top) if northwards == 'N' else -math.floor(bottom)
        min_northing = math.floor(bottom) if northwards == 'N' else -math.floor(top)

        eastwards = 'E' if left > 0 else 'W'
        max_easting = math.floor(right) if eastwards == 'E' else -math.floor(left)
        min_easting = math.floor(left) if eastwards == 'E' else -math.floor(right)

        for northing in range(min_northing, max_northing + 1):
            for easting in range(min_easting, max_easting + 1):
                downloads.append(
                    f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

    return downloads
