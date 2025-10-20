// ARQUIVO: homepage.js

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

const flaskDataUrl = '/dados_grafico';
const htmlElement = document.querySelector('html');
const isDarkInitial = localStorage.getItem('theme') === 'dark';
let graficoOptions = null;
const loadingSpinner = document.getElementById('loading-spinner');


function aplicarTemaHighcharts(isDark) {
    if (typeof Highcharts === 'undefined') {
        return; 
    }

    if (isDark) {
        Highcharts.setOptions({
            chart: {
                backgroundColor: '#22211D',
                style: { color: '#E3CFAA' }
            },
            title: { style: { color: '#E3CFAA' } },
            xAxis: {
                labels: { style: { color: '#E3CFAA' } },
                lineColor: '#CDB58C',
                tickColor: '#CDB58C'
            },
            yAxis: {
                labels: { style: { color: '#D6C0A4' } },
                title: { style: { color: '#C2A98B' } },
                gridLineColor: '#2A2926'
            },
            legend: { itemStyle: { color: '#D6C0A4' } },
            tooltip: { backgroundColor: '#2C2B28', style: { color: '#E3CFAA' } }
        });
    } else {
        Highcharts.setOptions({
            chart: { backgroundColor: '#FFFFFF' },
            title: { style: { color: '#000000' } },
            xAxis: {
                labels: { style: { color: '#000000' } },
                lineColor: '#846C5B',
                tickColor: '#846C5B'
            },
            yAxis: {
                labels: { style: { color: '#000000' } },
                title: { style: { color: '#000000' } },
                gridLineColor: '#e6e6e6'
            },
            legend: { itemStyle: { color: '#000000' } },
            tooltip: { backgroundColor: '#F9F9F9', style: { color: '#000000' } }
        });
    }

    if (window.graficoAtual && graficoOptions) {
        window.graficoAtual.destroy();
        window.graficoAtual = Highcharts.chart('container', graficoOptions); 
    }
}


if (isDarkInitial) {
    htmlElement.classList.add('dark');
} else {
    htmlElement.classList.remove('dark');
}


document.addEventListener('DOMContentLoaded', function () {
    aplicarTemaHighcharts(isDarkInitial);
});


function hideLoading() {
    if (loadingSpinner) {
        // Usa classes Tailwind para ocultar completamente
        loadingSpinner.classList.add('hidden');
        loadingSpinner.classList.remove('flex');
    }
}

function showLoading() {
    if (loadingSpinner) {
        // Usa classes Tailwind para exibir
        loadingSpinner.classList.remove('hidden');
        loadingSpinner.classList.add('flex');
    }
}


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
            const tamanhoEmBytes = item.tamanho_bytes;       
            const tamanhoFormatado = item.tamanho_formatado; 
            const quantidadeTabelas = item.quantidade_tabelas; 
            
            const valorNumericoTamanho = (typeof tamanhoEmBytes === 'number' && !isNaN(tamanhoEmBytes)) ? tamanhoEmBytes : 0;
            const valorNumericoTabelas = (typeof quantidadeTabelas === 'number' && !isNaN(quantidadeTabelas)) ? quantidadeTabelas : 0;
            
            const esquemaNome = item.esquema ? item.esquema : 'Esquema Desconhecido';

            categorias.push(esquemaNome);

            dadosTamanho.push({
                y: valorNumericoTamanho,
                Tamanho_Formatado: tamanhoFormatado 
            });

            dadosTabela.push(valorNumericoTabelas);
        });

        const chartOptions = {
            colors: ['#b7a696', '#846c5b'],
            chart: { zoomType: 'xy' },
            title: { text: 'Tamanho e Quantidade de Tabelas por Esquema', align: 'left' },
            xAxis: [{
                categories: categorias,
                crosshair: true,
                labels: { rotation: -45, style: { fontSize: '10px' } }
            }],
            yAxis: [
                {
                    title: { text: 'Quantidade de tabelas' }, 
                    min: 0,
                    lineWidth: 2,
                    lineColor: '#846c5b'
                },
                {
                    title: { text: 'Tamanho em Bytes' }, 
                    opposite: true,
                    min: 0,
                    lineWidth: 2,
                    lineColor: '#b7a696',
                    labels: { formatter: function () { return formatBytes(this.value); } }
                }
            ],
            tooltip: { 
                shared: true,
                formatter: function() {
                    let tooltipContent = '<b>' + this.x + '</b><br/>';
                    this.points.forEach(function(point) {
                        if (point.series.name === 'Tamanho em Memória') {
                            tooltipContent += '<span style="color:' + point.series.color + '">\u25CF</span> ' + 
                                            point.series.name + ': <b>' + point.point.Tamanho_Formatado + '</b><br/>';
                        } else {
                            tooltipContent += '<span style="color:' + point.series.color + '">\u25CF</span> ' + 
                                            point.series.name + ': <b>' + Highcharts.numberFormat(point.y, 0, ',', '.') + ' tabelas</b><br/>';
                        }
                    });
                    return tooltipContent;
                }
            },
            legend: { align: 'left', verticalAlign: 'top' },
            series: [{
                name: 'Tamanho em Memória', type: 'column', yAxis: 1, data: dadosTamanho,
            }, {
                name: 'Tabela (Referência)', type: 'spline', yAxis: 0, data: dadosTabela,
            }]
        };

        graficoOptions = chartOptions;
        aplicarTemaHighcharts(isDarkInitial);
        window.graficoAtual = Highcharts.chart('container', graficoOptions); 
        
        hideLoading(); // Esconde o spinner após o gráfico ser criado e estilizado
    })
    .catch(error => {
        console.error('Erro ao processar dados para o gráfico:', error);
        
        // Exibe a mensagem de erro no contêiner e esconde o spinner
        document.getElementById('container').innerHTML =
        '<p style="color: red; text-align: center;">Erro: Não foi possível carregar ou processar os dados.</p>' +
        '<p style="text-align: center;">Detalhe: ' + error.message + '</p>';
        
        hideLoading(); 
    });