Highcharts.chart('container', {
    colors: [
        '#b7a696',  // Cor 1: Será usada para as suas barras (Azul)
        '#846c5b',  // Cor 2: Para a próxima série (se houver, ex: Linha)
        '#846c5b'   // Cor 3: Para a terceira série
    ],

    chart: {
        zooming: {
            type: 'xy'
        }
    },
    title: {
        text: 'Karasjok weather, 2023',
        align: 'left'
    },
    credits: {
        text: 'Source: ' +
            '<a href="https://www.yr.no/nb/historikk/graf/5-97251/Norge/Finnmark/Karasjok/Karasjok?q=2023"' +
            'target="_blank">YR</a>'
    },
    xAxis: [{
        categories: [
            'Api', 'Comercial', 'Estoque', 'Eventos', 'Live', 'Marft',
            'Ppcp', 'Rh', 'Rh_sci', 'Suprimentos', 'Sustentabilidade', 'Ti'
        ],
        crosshair: true
    }],
    yAxis: [{ // Primary yAxis
        labels: {
            format: '{value}°C'
        },
        title: {
            text: 'Tabelas'
        },
        lineColor: '846c5b',
        lineWidth: 2
    }, { // Secondary yAxis
        title: {
            text: 'Tamanho em Memória'
        },
        labels: {
            format: '{value} mm'
        },
        lineColor: '#b7a696', 
        lineWidth: 2,
        opposite: true
    }],
    tooltip: {
        shared: true
    },
    legend: {
        align: 'left',
        verticalAlign: 'top'
    },
    series: [{
        name: 'Tamanho em Memória',
        type: 'column',
        yAxis: 1,
        data: [
            45.7, 37.0, 28.9, 17.1, 39.2, 18.9, 90.2, 78.5, 74.6,
            18.7, 17.1, 16.0
        ],
        tooltip: {
            valueSuffix: ' mm'
        }

    }, {
        name: 'Tabela',
        type: 'spline',
        data: [
            -11.4, -9.5, -14.2, 0.2, 7.0, 12.1, 13.5, 13.6, 8.2,
            -2.8, -12.0, -15.5
        ],
        tooltip: {
            valueSuffix: '°C'
        }
    }]
});