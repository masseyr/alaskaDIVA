from modules import *


if __name__ == '__main__':

    file1 = "C:/Users/Richard/Downloads/AK_interior_fire_decid_data_250m_2000_2019_new_1.csv"

    list_dicts = Handler(file1).read_from_csv(return_dicts=True)

    print('Number of dictionaries: {}'.format(str(len(list_dicts))))

    count = dict()

    for dict_ in list_dicts:
        fire_count = 0
        for k, v in dict_.items():
            if 'burn_year' in k:
                if 0 < int(v) < 2000:
                    fire_count += 1

        if fire_count in count:
            count[fire_count] += 1
        else:
            count[fire_count] = 1

    for k, v in count.items():
        print('{} burns : {} pixels'.format(str(k), str(v)))








