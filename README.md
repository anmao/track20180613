功能：	将轨迹数据匹配到路网上并提出停留点，并将结果数据可视化。
	通过热力图显示每天的数据量，点击热力图可以显示该天的数据。

一.运行环境
	python3.x,需要的库：flask,scipy,json,datetime

二.运行
	进入项目根目录运行main.py,浏览器进入127.0.0.1:5000

三.更换离线地图
	打开./templates/map.html修改地图源：
	找到下面的代码：

	L.control.layers(
                 {
                    "百度地图": L.tileLayer.baidu({ layer: 'vec' }).addTo(map)
                    "百度卫星": L.tileLayer.baidu({ layer: 'img' }),
                },
                {
                     "实时交通信息": L.tileLayer.baidu({ layer: 'time' })
                 },
                 { position: "topright" }).addTo(map);

    删除上述代码

    修改为：new L.tileLayer('http://localhost:5000/static/tiles/{z}/{x}/{y}.png').addTo(map)
    
    将离线地图放在 项目所在路径/2018_6_13track/tiles 内即可
    注意：tiles文件夹内直接放各级瓦片图文件夹（文件夹名为9，10，11...18等）,并且检查瓦片图的格式是否为png，如果格式是jpg，需要将url内的文件格式换为jpg

四.更换轨迹文件
	原始轨迹文件的目录为./static/data.csv
	停留点文件目录为./static/n00001StayPoint.csv。停留点命名文件格式为 ‘车辆ID’+‘StayPoint.csv’,
    文件内每个停留区域的名称（如：xx小区）写在该停留区域所有轨迹点数据的前面，请根据真实名称按需修改
	目前匹配轨迹与原始轨迹文件相同	

	对应代码位于main.py中的169，113，96行
