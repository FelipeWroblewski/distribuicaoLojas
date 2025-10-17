function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

document.addEventListener('DOMContentLoaded', function () {
const flaskDataUrl = '/dados_grafico';

const darkModeToggle = document.getElementById('dark-mode');

darkModeToggle.addEventListener('click', () => {
  const isDark = document.documentElement.classList.contains('dark');
    aplicarTemaHighcharts(isDark);
});

function aplicarTemaHighcharts(isDark) {
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

  // Re-renderiza o gráfico com o novo tema (sem refazer fetch)
  if (window.graficoAtual && window.graficoAtual.userOptions) {
    const chartOptions = window.graficoAtual.userOptions;
    window.graficoAtual.destroy(); // Remove o gráfico atual
    window.graficoAtual = Highcharts.chart('container', chartOptions); // Cria novamente
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
    let dadosTamanho = []; // Será a série de colunas
    let dadosTabela = [];  // Será a série de linha

    data.forEach(item => {
        const tamanhoEmBytes = item.tamanho_bytes;       
        const tamanhoFormatado = item.tamanho_formatado; 
        const quantidadeTabelas = item.quantidade_tabelas; 
        
        const valorNumericoTamanho = (typeof tamanhoEmBytes === 'number' && !isNaN(tamanhoEmBytes)) ? tamanhoEmBytes : 0;
        const valorNumericoTabelas = (typeof quantidadeTabelas === 'number' && !isNaN(quantidadeTabelas)) ? quantidadeTabelas : 0;
        
        const esquemaNome = item.esquema ? item.esquema : 'Esquema Desconhecido';

        categorias.push(esquemaNome);

        // Dados para a série de COLUNAS (Tamanho)
        dadosTamanho.push({
            y: valorNumericoTamanho,
            Tamanho_Formatado: tamanhoFormatado // Mantemos essa chave para o tooltip customizado
        });

        // Dados para a série de LINHA (Tabelas)
        dadosTabela.push(valorNumericoTabelas);
    });

    window.graficoAtual = Highcharts.chart('container', {
        colors: ['#b7a696', '#846c5b'],
        chart: { 
            zoomType: 'xy', // Use zoomType ao invés de zooming para compatibilidade e clareza
            // type: 'column' // Opcional: define um tipo padrão para o gráfico
        },

        title: { text: 'Tamanho e Quantidade de Tabelas por Esquema', align: 'left' },

        xAxis: [{
            categories: categorias,
            crosshair: true,
            labels: {
                // Rotaciona os rótulos do X para evitar sobreposição
                rotation: -45, 
                style: {
                    fontSize: '10px'
                }
            }
        }],

        yAxis: [
        {
            // Eixo Y 0 (Esquerdo): Para a série 'Tabela (Referência)' (a linha)
            title: { text: 'Quantidade de tabelas' }, 
            min: 0,
            lineWidth: 2,
            lineColor: '#846c5b' // Cor da linha do eixo para Tabelas
        },
        {
            // Eixo Y 1 (Direito): Para a série 'Tamanho em Memória' (as colunas)
            title: { text: 'Tamanho em Bytes' }, 
            opposite: true, // Coloca no lado direito do gráfico
            min: 0,
            lineWidth: 2,
            lineColor: '#b7a696', // Cor da linha do eixo para Tamanho
            labels: {
                // Formatador de rótulo para o eixo Y de Tamanho
                formatter: function () {
                    return formatBytes(this.value); 
                }
            }
        }],

    tooltip: { 
        shared: true, // Mostra o tooltip de todas as séries no mesmo ponto
        // Melhorar o tooltip para exibir o Tamanho_Formatado
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
        // Série de COLUNAS (Tamanho)
        name: 'Tamanho em Memória',
        type: 'column',
        yAxis: 1, // Aponta para o Eixo Y 1 (Direito)
        data: dadosTamanho,
        // Remover o pointFormatter do tooltip da série individual se usar um formatter global
        // tooltip: {
        //     pointFormatter: function () {
        //         return '<span style="color:' + this.color + '">\u25CF</span> ' +
        //         this.series.name + ': <b>' + this.Tamanho_Formatado + '</b>';
        //     }
        // }
    }, {
        // Série de LINHA (Tabelas)
        name: 'Tabela (Referência)',
        type: 'spline',
        yAxis: 0, // Aponta para o Eixo Y 0 (Esquerdo)
        data: dadosTabela,
        // Remover o valueSuffix aqui, pois o formatter do tooltip global vai cuidar
        // tooltip: { valueSuffix: '' }
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