from modules import Vector, Handler


if __name__ == '__main__':

    csvfile = "D:/Shared/Dropbox/projects/NAU/landsat_diva/data2/gee_mack_data_extract_30_v2019_07_09T20_11_02_3_2000.csv"
    outfile = "D:/Shared/Dropbox/projects/NAU/landsat_diva/data2/gee_mack_data_extract_30_v2019_07_09T20_11_02_3_2000.shp"

    samp_data = Handler(csvfile).read_from_csv(return_dicts=True)

    headers = list(samp_data[0])

    spref_str = '+proj=longlat +datum=WGS84'

    wkt_list = list()
    attr_list = list()
    attribute_types = dict()

    for header in headers:
        attribute_types[header] = Handler.string_to_type(samp_data[0][header],
                                                         return_type=True)

    # attribute_types['DecidFracR'] = 'str'
    # attribute_types['TreeCovR'] = 'str'

    for k, v in attribute_types.items():
        print('{} - {}'.format(str(k), str(v)))

    for elem in samp_data:
        wkt_list.append(Vector.wkt_from_coords((elem['longitude'], elem['latitude']),
                                               geom_type='point'))

        attr_list.append(elem)

    vector = Vector.vector_from_string(wkt_list,
                                       spref_string=spref_str,
                                       spref_string_type='proj4',
                                       vector_type='point',
                                       attributes=attr_list,
                                       attribute_types=attribute_types)

    print(vector)

    vector.write_vector(outfile)
