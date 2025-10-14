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

    Highcharts.chart('container', {
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