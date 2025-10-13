document.addEventListener('DOMContentLoaded', function () {
const flaskDataUrl = '/dados_grafico';

fetch(flaskDataUrl)
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.erro || 'Erro HTTP: ' + response.statusText);
            });
        }
    return response.json();})
    .then(data => {
        if (data.erro) {
            throw new Error(data.erro);
        }

    let categorias = [];
    let dadosTamanho = [];
    let dadosTabela = [];

    data.forEach(item => {
        const tamanhoEmBytes = item.Tamanho_Bytes;
        const tamanhoFormatado = item.Tamanho_Formatado;

        const valorNumerico = (typeof tamanhoEmBytes === 'number' && !isNaN(tamanhoEmBytes)) ? tamanhoEmBytes : 0;

        const esquemaNome = item.Esquema ? item.Esquema : 'Esquema Desconhecido';

        categorias.push(esquemaNome);

        dadosTamanho.push({
            y: valorNumerico,
            Tamanho_Formatado: tamanhoFormatado 
        });

        dadosTabela.push(0);
    });

    Highcharts.chart('container', {
        colors: ['#b7a696', '#846c5b'],
        chart: { zooming: { type: 'xy' } },

        title: { text: 'Tamanho dos Esquemas do Banco de Dados', align: 'left' },

        xAxis: [{
            categories: categorias,
            crosshair: true
        }],

        yAxis: [{
            labels: { format: '' },
            title: { text: 'Tabelas' },
            lineColor: '#846c5b',
            lineWidth: 2
        },
        {
            title: { text: 'Tamanho em Memória' },
            labels: {

                pointFormatter: function () {
                    return '<span style="color:' + this.color + '">\u25CF</span> ' +
                    this.series.name + ': <b>' + this.Tamanho_Formatado + '</b>';
                }
            },
            lineColor: '#b7a696',
            lineWidth: 2,
            opposite: true
        }],

    tooltip: { shared: true },
    legend: { align: 'left', verticalAlign: 'top' },
    series: [{
    name: 'Tamanho em Memória',
    type: 'column',
    yAxis: 1,
    data: dadosTamanho,
    tooltip: {
         pointFormatter: function () {
            return '<span style="color:' + this.color + '">\u25CF</span> ' +
            this.series.name + ': <b>' + this.Tamanho_Formatado + '</b>';
        }
    }
    }, {
    name: 'Tabela (Referência)',
    type: 'spline',
    data: dadosTabela,
    tooltip: { valueSuffix: '' }
    }]
});
})
.catch(error => {
 console.error('Erro ao processar dados para o gráfico:', error);
document.getElementById('container').innerHTML =
'<p style="color: red; text-align: center;">Erro: Não foi possível carregar ou processar os dados.</p>' +
'<p style="text-align: center;">Detalhe: ' + error.message + '</p>';
 });
});