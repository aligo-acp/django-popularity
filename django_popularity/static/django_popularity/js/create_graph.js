document.write('<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>');
document.write('<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>');

function create_chart(ele) {
    const data = {
        labels: [],
        datasets: [
            {
                    label: 'label',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: [],
                    tension: 0.6,
                    pointRadius: 0,
            },
            {
                    label: 'label',
                    backgroundColor: 'rgb(0, 0, 0)',
                    borderColor: 'rgb(0, 0, 0)',
                    data: [],
                    tension: 0.6,
                    pointRadius: 0,
            },
            {
                    label: 'label',
                    backgroundColor: 'rgb(128, 128, 128)',
                    borderColor: 'rgb(128, 128, 128)',
                    data: [],
                    tension: 0.6,
                    pointRadius: 0,
            },
        ]
    };
    const config = {
        type: 'line',
        data: data,
        options: {
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'n일 전'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: '검색량'
                    }
                }
            },
            plugins: {
                decimation: {
                    enabled: false,
                    algorithm: 'min-max',
                }
            },
            animation: false,
            //   parsing: false,
        }
    };
    const myChart = new Chart(
        ele,
        config
    );
    $.ajax({
        url: ele.dataset.request_url,
        method: "GET",
        dataType: 'json',
    }).done(function(res) {
        let labels = [];
        let data = [];
        res.graph_data.forEach((point) => {
            labels.push(point.days_ago);
            data.push(point.value);
        })
        myChart.data.labels = labels;
        myChart.data.datasets[0].data = data;
        myChart.data.datasets[0].label = res.title;
        
        labels = [];
        data = [];
        res.standard.graph_data.forEach((point) => {
            labels.push(point.days_ago);
            data.push(point.value);
        })
        myChart.data.labels = labels;
        myChart.data.datasets[1].data = data;
        myChart.data.datasets[1].label = res.standard.title;

        labels = [];
        data = [];
        res.standard2.graph_data.forEach((point) => {
            labels.push(point.days_ago);
            data.push(point.value);
        })
        myChart.data.labels = labels;
        myChart.data.datasets[2].data = data;
        myChart.data.datasets[2].label = res.standard2.title;

        myChart.update();
    }).fail(function(xhr, status, errorThrown) {

    });
}

$(document).ready(function() {
    words = window.location.href.split('/');
    create_chart(document.getElementById('visualization'));
});