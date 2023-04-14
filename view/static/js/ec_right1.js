var ec_right1 = echarts.init(document.getElementById("r1"), "dark");

var option_right1 = {
    title: {
        text: '非湖北地区城市确诊TOP5',
        textStyle: {
            color: 'white'
        },
        left: 'left'
    },
    /*grid: {
        left: 50,
        top: 50,
        right: 0,
        width: '87%',
        height: 320,
    },*/
    color: ['#3398DB'],
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        }
    },
    //全局字体样式
    /*textStyle: {
        fontFamily: 'PingFangSC-Medium',
        fontSize: 14,
        color: '#858E96',
        lineHeight: 12
    },*/
    xAxis: {
        type: 'category',
        // scale:true,
        data: [],
        axisLabel: {
            interval: 0,
            formatter: function (value) {
                var str = "";
                var num = 2; //每行显示字数
                var valLength = value.length; //该项x轴字数
                var rowNum = Math.ceil(valLength / num); // 行数

                if (rowNum > 1) {
                    for (var i = 0; i < rowNum; i++) {
                        var temp = "";
                        var start = i * num;
                        var end = start + num;

                        temp = value.substring(start, end) + "\n";
                        str += temp;
                    }
                    return str;
                } else {
                    return value;
                }
            }
        }
    },
    yAxis: {
        type: 'value',
        //坐标轴刻度设置
    },
    series: [{
        type: 'bar',
        data: [],
        barMaxWidth: "50%"

    }]
};
ec_right1.setOption(option_right1);