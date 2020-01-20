from modules import *


if __name__ == '__main__':

    infile = 'c:/temp/extracted_data_rtz20200119T061159.csv'
    outfile_ = Handler(infile).add_to_filename('_reformatted', False)

    list_dicts = Handler(infile).read_from_csv(return_dicts=True)

    site_ids = sorted(list(set(list(dict_['site_id'] for dict_ in list_dicts if dict_['site_id'] != 'site_id'))))
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    features1 = ['site_id', 'longitude', 'latitude']
    features2 = ['precipErrDiagMM', 'precipErrRMSMM', 'precipMM', 'lstC',]
    years = range(2000, 2020)

    header_str = ', '.join(features1)
    header_add_list = list()
    for year in years:
        for month in months:
            for feat in features2:
                header_add_list.append('{}__{}_{}'.format(feat,
                                                          year,
                                                          month))
    header_str += ','
    header_str += ','.join(header_add_list)

    site_list = [header_str]
    for site in site_ids:
        print(site)
        site_data = list(dicts_ for dicts_ in list_dicts if dicts_['site_id'] == site)
        site_str = ', '.join([str(site_data[0]['site_id']),
                              str(site_data[0]['longitude']),
                              str(site_data[0]['latitude'])]) + ','
        for year in years:
            site_data_year = list(dicts_ for dicts_ in site_data if dicts_['year'] == year)
            for month in months:
                site_data_month = list(dicts_ for dicts_ in site_data if dicts_['month'] == month)
                for feat in features2:
                    if feat == 'lstC':
                        try:
                            val = 0.02 * float(site_data_month[0][feat])
                        except:
                            val = site_data_month[0][feat]
                    else:
                        val = site_data_month[0][feat]

                    if len(site_data_month) > 0:
                        if str(val) in ('nan', 'None'):
                            site_str += str(0)
                        else:
                            site_str += str(val)
                    site_str += ','
        site_list.append(site_str)

    Handler(outfile_).write_list_to_file(site_list)


