import os 
import sys 
import alphashape
import argparse
import glob
import pandas as pd
import open3d as o3d
import numpy as np

# parsers ----------------------------------------------------------------------------------------------------------

def get_args():

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i',
                        '--indir',
                        help='Input directory containing pointclouds',
                        metavar='str',
                        type=str,
                        default='')
    
    parser.add_argument('-o',
                        '--outdir',
                        help='Output directory for .ply files',
                        metavar='str',
                        type=str,
                        default='')
    
    return parser.parse_args()

# functions ----------------------------------------------------------------------------------------------------------

def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos

def generate_pointcloud_ID(pcd_path):
    plant_id = os.path.basename(os.path.dirname(pcd_path))
    plant_id_split = plant_id.rsplit('_', 1) 
    plant_genotype = plant_id_split[0]
    plant_number = plant_id_split[1]
    date = generate_date(pcd_path)
    date_split = date.split('-')
    year = date_split[2]
    month = date_split[0]
    day = date_split[1]
    date_reordered = str(year + '-' + month + '-' + day)
    return [date_reordered, year, month, day, plant_genotype, plant_number, pcd_path]

def generate_date(path):
    file_name = os.path.basename(os.path.dirname(os.path.dirname(path)))
    date = file_name.split('_')[2]
    return date

def overlapped_shapes(shape_list):
    def iterable_overlap(list_):
        overlapping_list = []
        overlap_values = []
        for i in list_:
            for j in [x for x in list_ if x != i]:
                overlap = i[0].intersection(j[0]).area/min(i[0].area, j[0].area)
                overlap_values.append(overlap)
                if overlap < 0.5 or overlap in overlap_values: 
                    if i not in overlapping_list:
                        overlapping_list.append(i)
                    if j not in overlapping_list:
                        overlapping_list.append(j)
                else:
                    overlapping_list.append([i[0].union(j[0]),np.row_stack((i[1], j[1]))])
        return overlapping_list, len(overlapping_list)
    len_list = []
    while list(set(len_list)) == len_list:
        shape_list, new_len = iterable_overlap(shape_list)
        len_list.append(new_len)
    polygon_list = []
    array_list = []
    for i in shape_list:
        polygon_list.append(i[0])
        array_list.append(i[1])
    return array_list, polygon_list

def get_shapes(list_):
    shape_list = []
    for array in list_:
        xy_array = np.delete(array, [2,3], 1)
        alpha_shape = alphashape.alphashape(xy_array, alpha = 2)
        shape_list.append([alpha_shape, np.delete(array, 3, 1)]) 
    return shape_list

def get_largest_pointcloud(list_):
    len_list = []
    for i in range(0, len(list_)):
        len_list.append(len(list_[i]))
    for i in list_:
        if len(i) == max(len_list):
            largest_pointcloud = i
        else:
            continue
    return largest_pointcloud

def save_plant_array_to_ply(array, path_list, i):
    args = get_args()
    output_dir = args.outdir
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(array)
    directory = os.path.join(output_dir, path_list[i][0], path_list[i][4])
    if not os.path.isdir(directory):
        os.makedirs(directory)
    os.chdir(directory)
    o3d.io.write_point_cloud(path_list[i][4] + '_' + path_list[i][5] + '.ply', pcd)

# define main ----------------------------------------------------------------------------------------------------------

def main():
    """Make a jazz noise here"""

    args = get_args()
    input_dir = args.indir
    output_dir = args.outdir

    plant_pcd_filepaths = glob.glob(input_dir + '/*/combined_unregistered_plant.ply')

    path_list = [generate_pointcloud_ID(i) for i in plant_pcd_filepaths]

    m = 0
    for i in range(0, len(path_list)):
        plant_pcd = o3d.io.read_point_cloud(path_list[i][6])
        with o3d.utility.VerbosityContextManager(
                o3d.utility.VerbosityLevel.Debug) as cm:
            labels = np.array(
                plant_pcd.cluster_dbscan(eps=0.07, min_points=10, print_progress=True))
        
        labeled_pcd_array = np.column_stack((np.asarray(plant_pcd.points), np.array(labels)))
        
        dbscan_list = []
        for x in set(labeled_pcd_array[:,3]):
            dbscan_list.append(labeled_pcd_array[labeled_pcd_array[:,3] == x]) 
        
        if len(dbscan_list) == 1:
            array = np.delete(labeled_pcd_array, 3, 1)
            save_plant_array_to_ply(array, path_list, i)
            m += 1
            continue
            
        max_test_list = []
        max_len = len(get_largest_pointcloud(dbscan_list))
        for x in dbscan_list:
            if len(x) >= 0.05 * max_len:
                max_test_list.append(x)
        if len(max_test_list) == 1:
            array = np.delete(np.asarray(max_test_list[0]), 3, 1)
            save_plant_array_to_ply(array, path_list, i)
            m += 1
            continue
            
        shape_list = get_shapes(max_test_list)
        overlapped_array_list, overlapped_polygon_list = overlapped_shapes(shape_list)
        largest_sub_pcd = get_largest_pointcloud(overlapped_array_list)
        save_plant_array_to_ply(largest_sub_pcd, path_list, i)
        m += 1

# run main ----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
