"""
this GEE script extracts GPM and MODIS LST data for given sample locations
projection: geo lat/lon
"""
import ee


def expand_image_meta(img_meta):
    """
    Function to expand the metadata associated with an ee.Image object
    :param img_meta: Retrieved ee.Image metadata dictionary using getInfo() method
    :return: String
    """
    if type(img_meta) != dict:
        if type(img_meta).__name__ == 'Image':
            img_meta = img_meta.getInfo()
        else:
            raise RuntimeError('Unsupported EE object')

    out_str = ''
    for k, y in img_meta.items():
        if k == 'bands':
            for _y in y:
                out_str += 'Band: {} : {}\n'.format(_y['id'], str(_y))
        elif k == 'properties':
            for _k, _y in y.items():
                out_str += 'Property: {} : {}\n'.format(_k, str(_y))
        else:
            out_str += '{} : {}\n'.format(str(k), str(y))
    return out_str


def expand_feature_meta(feat_meta):
    """
    Function to expand the metadata associated with an ee.Feature object
    :param feat_meta: Retrieved ee.Feature metadata dictionary using getInfo() method
    :return: String
    """
    if type(feat_meta) != dict:
        if type(feat_meta).__name__ == 'Feature':
            feat_meta = feat_meta.getInfo()
        else:
            raise RuntimeError('Unsupported EE object')

    out_str = ''
    for k, y in feat_meta.items():
        if k == 'geometry':
            for _k, _y in y.items():
                out_str += '{}: {}\n'.format(str(_k), str(_y))

        elif k == 'properties':
            for _k, _y in y.items():
                out_str += 'Property: {} : {}\n'.format(_k, str(_y))
        else:
            out_str += '{} : {}\n'.format(str(k), str(y))
    return out_str


def expand_feature_coll_meta(feat_coll_meta):
    """
    Function to expand the metadata associated with an ee.FeatureCollection object
    :param feat_coll_meta: Retrieved ee.FeatureCollection metadata dictionary using getInfo() method
    :return: String
    """
    if type(feat_coll_meta) != dict:
        if type(feat_coll_meta).__name__ == 'FeatureCollection':
            feat_coll_meta = feat_coll_meta.getInfo()
        else:
            raise RuntimeError('Unsupported EE object')

    out_str = '---------------------\n'
    for k, y in feat_coll_meta.items():
        if k == 'features':
            for feat in y:
                out_str += expand_feature_meta(feat) + '---------------------\n'

        elif k == 'properties':
            for _k, _y in y.items():
                out_str += 'Property: {} : {}\n'.format(_k, str(_y))
        else:
            out_str += '{} : {}\n'.format(str(k), str(y))
    return out_str


def filter_coll(coll,
                year=None,
                startjulian=None,
                endjulian=None):
    """
    Method to filter an ee.ImageCollection object by date and AOI
    :param coll:
    :param year:
    :param startjulian:
    :param endjulian:
    :return: ee.ImageCollection
    """
    return ee.ImageCollection(coll).filterDate(ee.Date.fromYMD(year, 1, 1),
                                               ee.Date.fromYMD(year, 12, 31)) \
        .filter(ee.Filter.calendarRange(startjulian,
                                        endjulian))


def composite(coll,
              multiplier=1.0,
              reduce_type='average'):
    """
    Function to reduce a given collection
    :param coll:
    :param multiplier:
    :param reduce_type: options: average, total, rms, diag
    :return:
    """
    coll_ = ee.ImageCollection(coll).map(lambda x: x.multiply(ee.Image(multiplier)))

    if reduce_type == 'average':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.ImageCollection(coll__).reduce(ee.Reducer.mean())
    if reduce_type == 'median':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.ImageCollection(coll__).reduce(ee.Reducer.median())
    elif reduce_type == 'total':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.ImageCollection(coll__).reduce(ee.Reducer.sum())
    elif reduce_type == 'max':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.ImageCollection(coll__).reduce(ee.Reducer.max())
    elif reduce_type == 'min':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.ImageCollection(coll__).reduce(ee.Reducer.min())
    elif 'pctl' in reduce_type:
        pctl = int(reduce_type.replace('pctl_', ''))
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.ImageCollection(coll__).reduce(ee.Reducer.percentile([pctl]))
    elif reduce_type == 'rms':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.Image(coll__.reduce(ee.Reducer.mean())).sqrt()
    elif reduce_type == 'diag':
        coll__ = ee.ImageCollection(coll_).map(lambda x: ee.Image(x).multiply(ee.Image(x)))
        return ee.Image(coll__.reduce(ee.Reducer.sum())).sqrt()
    else:
        raise ValueError('Not Implemented')


def lst_band_properties_scale(lst_img,
                              band='LST_Day_1km'):
    """
    Scaling MODIS LST and adding system:time_start property
    :param lst_img:
    :param band:
    :return:
    """
    out_img = ee.Image(lst_img.select([band]).copyProperties(lst_img))
    return out_img


if __name__ == '__main__':

    ee.Initialize()

    samp = ee.FeatureCollection("users/masseyr44/shapefiles/DiVA_ALL_coordinates").getInfo()

    gpm = ee.ImageCollection("NASA/GPM_L3/IMERG_V06")
    lst = ee.ImageCollection("MODIS/006/MOD11A1")

    print(expand_image_meta(lst.first().getInfo()))

    drive_folder = 'kyoko_precip_temp_v3'

    aoi_coords = [[[-155.75502485485526, 68.4916626820707],
                  [-155.75502485485526, 61.4225492862472],
                  [-140.11049360485526, 61.4225492862472],
                  [-140.11049360485526, 68.4916626820707]]]

    aoi_geom = {'type': 'Polygon', 'coordinates': aoi_coords}

    aoi = ee.Geometry.Polygon(aoi_coords, None, False)

    julian_days = [['jan', (1, 31)],
                   ['feb', (32, 59)],
                   ['mar', (60, 90)],
                   ['apr', (91, 120)],
                   ['may', (121, 151)],
                   ['jun', (152, 181)],
                   ['jul', (182, 212)],
                   ['aug', (213, 243)],
                   ['sep', (244, 273)],
                   ['oct', (274, 304)],
                   ['nov', (305, 334)],
                   ['dec', (335, 365)]]

    years = list(range(2000, 2020))

    gpm_precip = gpm.select(['precipitationCal'])
    gpm_error = gpm.select(['randomError'])
    lst_daily = lst.map(lst_band_properties_scale)

    first_meta = gpm.first().getInfo()

    print(expand_image_meta(first_meta))

    print('\n\n')

    first_meta = lst_daily.first()

    print(expand_image_meta(first_meta))

    print(expand_feature_coll_meta(samp))

    print('\n----------****----------------\n')

    coll_list = []

    for year in years:

        for month, days in julian_days:

            print('Date: {}-{}-XX'.format(str(year), str(month).upper()))

            str_id = 'y{}_{}_'.format(str(year), str(month))

            gpm_precip_coll = filter_coll(gpm_precip, year, days[0], days[1])
            gpm_error_coll = filter_coll(gpm_error, year, days[0], days[1])
            lst_coll = filter_coll(lst_daily, year, days[0], days[1])

            n_gpm = gpm_precip_coll.size().getInfo()
            n_lst = lst_coll.size().getInfo()

            print('GPM images: {} | LST images: {}'.format(str(n_gpm), str(n_lst)))

            if n_gpm > 0 and n_lst > 0:

                data_img = ee.Image(composite(gpm_precip_coll, 0.5, 'total').select([0],
                                                                                    [str_id + 'precipMM'])
                                    .addBands(composite(gpm_error_coll,  0.5, 'diag').select([0],
                                                                                             [str_id + 'precipErrDiagMM']))
                                    .addBands(composite(gpm_error_coll,  0.5, 'rms').select([0],
                                                                                            [str_id + 'precipErrRMSMM']))
                                    ).clip(aoi)

                print(expand_image_meta(data_img.getInfo()))

                coll_list.append(data_img)

                task_config = {
                    'driveFileNamePrefix': str_id + 'precip_data_img',
                    'crs': 'EPSG:4326',
                    'scale': 11500,
                    'maxPixels': 1e13,
                    'fileFormat': 'GeoTIFF',
                    'region': aoi_coords,
                    'driveFolder': drive_folder
                }

                task1 = ee.batch.Export.image(data_img,
                                              str_id + 'precip_data_img',
                                              task_config)

                # task1.start()
                print(task1)

                data_img = ee.Image(composite(lst_coll,  0.02, 'average').select([0], [str_id + 'lstC_avg']))\
                                   .subtract(273.15).clip(aoi) \
                    .addBands(ee.Image(composite(lst_coll, 0.02, 'median').select([0], [str_id + 'lstC_median'])) \
                              .subtract(273.15).clip(aoi)) \
                    .addBands(ee.Image(composite(lst_coll,  0.02, 'max').select([0], [str_id + 'lstC_max']))\
                               .subtract(273.15).clip(aoi))\
                        .addBands(ee.Image(composite(lst_coll, 0.02, 'min').select([0], [str_id + 'lstC_min']))\
                                  .subtract(273.15).clip(aoi))

                print(expand_image_meta(data_img.getInfo()))

                coll_list.append(data_img)

                task_config = {
                    'driveFileNamePrefix': str_id + 'temp_data_img',
                    'crs': 'EPSG:4326',
                    'scale': 1000,
                    'maxPixels': 1e13,
                    'fileFormat': 'GeoTIFF',
                    'region': aoi_coords,
                    'driveFolder': drive_folder
                }

                task2 = ee.batch.Export.image(data_img,
                                              str_id + 'temp_data_img',
                                              task_config)

                task2.start()
                print(task2)

            print('\n----------****----------------\n')






