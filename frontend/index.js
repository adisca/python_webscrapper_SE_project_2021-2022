function rand() {
    return Math.random() / 100000;
  }

    var time = new Date();

    var trace1 = {
        x: [],
        close: [],
        decreasing: {line: {color: '#7F7F7F'}},
        high: [],
        increasing: {line: {color: '#17BECF'}},
        line: {color: 'rgba(31,119,180,1)'},
        low: [],
        open: [],
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y',
        text: []
    };
  
    var data = [trace1];
  
    var layout = {
        dragmode: 'zoom',
        margin: {
            r: 10, 
            t: 25, 
            b: 40, 
            l: 60
        },
        showlegend: false,
    };

    Plotly.newPlot('myDiv', data, layout, {scrollZoom: true});

    var time = new Date();
    var minuteView = {
        xaxis: {
            type: 'date',
            range: [time, time.setMinutes(time.getMinutes() + 1)]
        },
        yaxis: {
            fixedrange: false
        }
    };

    var interval = setInterval(function() {
        var time = new Date();
        
        var update = {
            x:  [[time]],
            close: [[rand()]],
            high: [[rand()]],
            low: [[rand()]],
            open: [[rand()]],
            text: [[((rand() - rand()) * 100 / rand()) + "%"]]
        }

        if (ok == 0)
        {
            var yaixsrange = minuteView.xaxis.range;
            minuteView = {
                xaxis: {
                    type: 'date',
                    range: [yaixsrange[0], yaixsrange[1]]
                }
            };
        }
        else
        {
            var olderTime = time.setMinutes(time.getMinutes() - 1);
            var futureTime = time.setMinutes(time.getMinutes() + 2);
            time.setMinutes(time.getMinutes() - 1);
            minuteView = {
                xaxis: {
                    type: 'date',
                    range: [olderTime, futureTime]
                },
                yaxis: {
                    fixedrange: false
                }
            };
        }
    
        Plotly.relayout('myDiv', minuteView);
        Plotly.extendTraces('myDiv', update, [0])
    }, 1000);


