from modules import *
from sys import argv
import multiprocessing as mp


def extract_from_ras(filename_,
                     prefix,
                     out_proj,
                     px,
                     wktlist):
    ras_ = Raster(filename_)
    ras_.initialize()

    temp_outfile = Handler(filename_).add_to_filename('_resamp', True)

    reproj_ds = ras_.reproject(outfile=temp_outfile,
                               out_proj4=out_proj,
                               verbose=True,
                               resampling='near',
                               output_res=(float(px), float(px)),
                               out_nodatavalue=0.0,
                               bigtiff='yes',
                               compress='lzw',
                               return_vrt=True)

    reproj_ = Raster('reproj')
    reproj_.datasource = reproj_ds
    reproj_.initialize()

    samp_output_ = reproj_.extract_geom(wktlist)

    bnames_ = list(elem_.replace(prefix, '') for elem_ in ras_.bnames)

    reproj_ds = None
    reproj_ = None
    Handler(temp_outfile).file_delete()

    return bnames_, samp_output_


def extract_from_precip_temp_ras(args):
    filename_temp, filename_precip, suffix_temp_str, suffix_precip_str, out_proj, px, wktlist, attrlist = args

    Opt.cprint('Processing : {},  {}'.format(filename_precip, filename_temp))

    if (Handler(filename_precip).file_exists()) and (Handler(filename_temp).file_exists()):

        prefix_temp = Handler(filename_temp).basename.replace(suffix_temp_str, '')
        bnames_temp, samp_output_temp = extract_from_ras(filename_temp,
                                                         prefix_temp,
                                                         out_proj,
                                                         px,
                                                         wktlist)
        strs_temp = prefix_temp.split('_')
        time_dict = {'year': int(strs_temp[0].replace('y', '')), 'month': strs_temp[1]}

        prefix_precip = Handler(filename_precip).basename.replace(suffix_precip_str, '')
        bnames_precip, samp_output_precip = extract_from_ras(filename_precip,
                                                             prefix_precip,
                                                             out_proj,
                                                             px,
                                                             wktlist)

        outlist_ = list()
        for i, attr_ in enumerate(attrlist):
            out_dict_ = dict()
            out_dict_.update(attr_)
            out_dict_.update(dict(zip(bnames_temp, samp_output_temp[i][1])))
            out_dict_.update(dict(zip(bnames_precip, samp_output_precip[i][1])))
            out_dict_.update(time_dict)
            outlist_.append(out_dict_)

        return outlist_
    else:
        return []


if __name__ == '__main__':

    script, pixel_size, n_procs = argv

    # -------------------------------------------------------------------
    list_precip_files = '/scratch/rm885/temp/ls.txt'
    precip_folder = '/scratch/rm885/gdrive/sync/decid/kyoko_files_tif/precip/'
    temp_folder = '/scratch/rm885/gdrive/sync/decid/kyoko_files_tif/temp/'
    data_folder = '/scratch/rm885/gdrive/sync/decid/kyoko_files_tif/data/'

    outfile = Handler(data_folder + 'extracted_data_rt.csv').add_to_filename(timestamp=True)

    files = Handler(list_precip_files).read_from_csv()

    precip_files = [precip_folder + filename for filename in [elem[0] for elem in files['feature']] + files['name']]
    temp_files = [elem.replace('precip', 'temp') for elem in precip_files]

    file_list = dict(zip(precip_files, temp_files))

    outdir = data_folder
    vecfilename = data_folder + "ClimateDataRequest_lat_lon.csv"
    pixel_size = float(pixel_size)
    n_procs = int(n_procs)
    pool = mp.Pool(processes=n_procs)
    # -------------------------------------------------------------------

    out_proj4 = '+proj=longlat +ellps=WGS84 +datum=WGS84'

    attr = {'site_id': 'str',
            'latitude': 'float',
            'longitude': 'float'}

    samp_data = Handler(vecfilename).read_from_csv(return_dicts=True)

    wkt_list = list()
    attr_list = list()

    count = 0
    for row in samp_data:
        elem = dict()
        for header in list(attr):
            elem[header] = row[header]

        wkt_list.append(Vector.wkt_from_coords([row['longitude'], row['latitude']]))

        attr_list.append(elem)

        count += 1

    args_list = list((rasfile_temp,
                      rasfile_precip,
                      'temp_data_img.tif',
                      'precip_data_img.tif',
                      out_proj4,
                      pixel_size,
                      wkt_list,
                      attr_list) for rasfile_precip, rasfile_temp in file_list.items())

    # outlist = list()
    file_handler = Handler(outfile)
    for file_outlist in pool.imap_unordered(extract_from_precip_temp_ras, args_list):
        Opt.cprint(len(file_outlist))
        if len(file_outlist) > 0:
            if file_handler.file_exists():
                file_handler.write_to_csv(file_outlist, outfile, append=True)
            else:
                file_handler.write_to_csv(file_outlist, outfile, append=False)

        # outlist += file_outlist

    # Handler.write_to_csv(outlist, outfile)
