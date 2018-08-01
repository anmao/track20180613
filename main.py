from flask import Flask, render_template, request, redirect, url_for
from scipy.spatial import ConvexHull
import json
import datetime
import sqlite3

app = Flask(__name__)


class Point:
    def __init__(self, date, lng, lat):
        self.date = date
        self.lng = lng
        self.lat = lat


class PointList:
    def __init__(self, list_id):
        self.list = []
        self.list_id = list_id

    def sort(self):
        self.list.sort(key=lambda p: p.date)

    def append(self, point):
        if len(self.list) == 0:
            self.start_date = point.date
            self.end_date = point.date
        else:
            if self.start_date > point.date:
                self.start_date = point.date
            if self.end_date < point.date:
                self.end_date = point.date
        self.list.append(point)


def point2dict(point):
    return {'year': point.date.year,
            'month': point.date.month,
            'day': point.date.day,
            'hour': point.date.hour,
            'minute': point.date.minute,
            'second': point.date.second,
            'lng': point.lng,
            'lat': point.lat}


def get_data(file_path):
    track_dict = {}
    with open(file_path, 'r') as data_file:  # 原始轨迹文件
        for line in data_file:
            point_id, date, time, lng, lat, _, _ = line.strip('\n').split(',')
            date = datetime.datetime.strptime(date + ',' + time, '%Y/%m/%d,%H:%M:%S')
            lng = float(lng)
            lat = float(lat)
            temp_point = Point(date, lng, lat)
            if not track_dict.get(point_id, False):
                track_dict[point_id] = PointList(point_id)
            track_dict[point_id].append(temp_point)
    return track_dict


def search_polygon_points(hull, cluster_points):
    polygon = []
    now_line = 0
    start = hull[0][0]
    end = 999
    if hull[now_line][0] != start:
        end = hull[now_line][0]
    if hull[now_line][1] != start:
        end = hull[now_line][1]
    polygon.append(cluster_points[start])

    while end != start:
        polygon.append(cluster_points[end])
        hull.pop(now_line)

        for idx, line in enumerate(hull):
            if line[0] == end:
                end = line[1]
                now_line = idx
                break
            if line[1] == end:
                end = line[0]
                now_line = idx
                break
    return polygon


@app.route('/', methods=['GET'])
def index():
    return render_template('map.html')


@app.route('/match_json/<search_param>', methods=['POST'])
def get_matching_data(search_param):
    data = get_data('./static/data.csv')
    search_result = data.get(search_param, False)
    track = list(map(point2dict, search_result.list))
    json_data = json.dumps(track)
    return json_data


@app.route('/stay_point_json/<stay_point_id>', methods=['get'])
def get_stay_point(stay_point_id):
    cluster_points = []
    cluster = []
    avg_points = []
    cluster_info = []
    mean_lng = 0
    mean_lat = 0
    point_count = 0

    file_path = './static/' + stay_point_id + 'StayPoint.csv'

    with open(file_path, 'r') as cluster_file:
        start_time = 0
        location = 0;
        for line in cluster_file:
            line_data = line.strip('\n').split(',')
            if line_data[0] != '':
                if line_data[1] != '':
                    if start_time == 0:
                        start_time = datetime.datetime.strptime(line_data[1] + ',' + line_data[2], '%Y/%m/%d,%H:%M:%S')
                    lng = float(line_data[3])
                    lat = float(line_data[4])
                    mean_lng += lng
                    mean_lat += lat
                    point_count += 1
                    cluster.append([lat, lng])
                    end_time = datetime.datetime.strptime(line_data[1] + ',' + line_data[2], '%Y/%m/%d,%H:%M:%S')
                else:
                    location = line_data[0];
            else:
                cluster_points.append(cluster)
                cluster = []
                mean_lat /= point_count
                mean_lng /= point_count
                avg_points.append([mean_lat, mean_lng])
                cluster_info.append([[start_time.day, start_time.hour, start_time.minute],
                                     [end_time.day, end_time.hour, end_time.minute], point_count, location])
                location = 0
                mean_lat = 0
                mean_lng = 0
                point_count = 0
                start_time = 0
        cluster_points.append(cluster)
        mean_lat /= point_count
        mean_lng /= point_count
        avg_points.append([mean_lat, mean_lng])
        cluster_info.append(
            [[start_time.day, start_time.hour, start_time.minute], [end_time.day, end_time.hour, end_time.minute],
             point_count, location])

    polygon_set = []

    hull_idx = 0
    for per_cluster in cluster_points:
        hull_idx += 1
        print(hull_idx)
        hull = list(ConvexHull(per_cluster).simplices)
        polygon_set.append(search_polygon_points(hull, per_cluster))

    for idx, polygon in enumerate(polygon_set):
        mean_lat = avg_points[idx][0]
        mean_lng = avg_points[idx][1]
        for latlng in polygon:
            latlng[0] = latlng[0] + 3 * (latlng[0] - mean_lat)
            latlng[1] = latlng[1] + 3 * (latlng[1] - mean_lng)

    return json.dumps([polygon_set, cluster_info])


@app.route('/origin_json/<search_param>', methods=['get'])
def get_origin_data(search_param):
    data = get_data('./static/data.csv')
    search_result = data.get(search_param, False)
    track = list(map(point2dict, search_result.list))
    json_data = json.dumps(track)
    return json_data


if __name__ == '__main__':
    app.run(debug=True)
