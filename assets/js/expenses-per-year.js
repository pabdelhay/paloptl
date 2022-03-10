let chart

function getExpenses(year, currency){
    url = '/api/angola-bernardo/total_expense/?year='+year+'&currency='+currency;
    $('.year-text').text(year)
    $('.currency-text').text(currency)
    $.get(url, function(data, status){
        if(status == 'success'){
            chart.data = data;
        }
    })
}

$(document).ready(function(){
    getExpenses($('#id_year').val(), $('#id_base_currency').val())

    $('#id_year').change(function(){
        year = $(this).val();
        currency = $('#id_base_currency').val();
        getExpenses(year, currency);
    })

    $('#id_base_currency').change(function(){
        year = $('#id_year').val();
        currency = $(this).val();
        getExpenses(year, currency);
    })
})

am4core.ready(function() {

// Themes begin
am4core.useTheme(am4themes_animated);
// Themes end



chart = am4core.create('chartdiv', am4charts.XYChart)
chart.colors.step = 2;

chart.legend = new am4charts.Legend()
chart.legend.position = 'top'
chart.legend.paddingBottom = 20
chart.legend.labels.template.maxWidth = 95
chart.numberFormatter.numberFormat = "#.a";
chart.numberFormatter.bigNumberPrefixes = [
            {"number": 1e+3, "suffix": "K"},
            {"number": 1e+6, "suffix": "Mi"},
            {"number": 1e+9, "suffix": "Bi"},
            {"number": 1e+12, "suffix": "Tri"},
            {"number": 1e+15, "suffix": "Qua"}
            /*{"number": 1e+18, "suffix": "E"},
            {"number": 1e+21, "suffix": "Z"},
            {"number": 1e+24, "suffix": "Y"}*/
        ]

var xAxis = chart.xAxes.push(new am4charts.CategoryAxis())
xAxis.dataFields.category = 'country'
xAxis.renderer.cellStartLocation = 0.1
xAxis.renderer.cellEndLocation = 0.9
xAxis.renderer.grid.template.location = 0;

var yAxis = chart.yAxes.push(new am4charts.ValueAxis());
yAxis.min = 0;

function createSeries(value, name) {
    var series = chart.series.push(new am4charts.ColumnSeries())
    series.dataFields.valueY = value
    series.dataFields.categoryX = 'country'
    series.name = name
    series.events.on("hidden", arrangeColumns);
    series.events.on("shown", arrangeColumns);

    if(value == 'expense'){
        series.columns.template.tooltipText = "{name}:\n Group: {expense_group}\n Value : {expense}"
    }else{
        series.columns.template.tooltipText = "{name}:\n Group: {revenue_group}\n Value : {revenue}"
    }

    var bullet = series.bullets.push(new am4charts.LabelBullet())
    bullet.interactionsEnabled = false
    bullet.dy = -10;
    bullet.label.text = '{valueY}'
    bullet.label.fill = am4core.color('#000')
    var bulletState = bullet.states.create("hover");
    bulletState.properties.fillOpacity = 1;
    bulletState.properties.strokeOpacity = 1;

    return series;
}




createSeries('expense', 'Expense');
createSeries('revenue', 'Revenue');


function arrangeColumns() {

    var series = chart.series.getIndex(0);

    var w = 1 - xAxis.renderer.cellStartLocation - (1 - xAxis.renderer.cellEndLocation);
    if (series.dataItems.length > 1) {
        var x0 = xAxis.getX(series.dataItems.getIndex(0), "categoryX");
        var x1 = xAxis.getX(series.dataItems.getIndex(1), "categoryX");
        var delta = ((x1 - x0) / chart.series.length) * w;
        if (am4core.isNumber(delta)) {
            var middle = chart.series.length / 2;

            var newIndex = 0;
            chart.series.each(function(series) {
                if (!series.isHidden && !series.isHiding) {
                    series.dummyData = newIndex;
                    newIndex++;
                }
                else {
                    series.dummyData = chart.series.indexOf(series);
                }
            })
            var visibleCount = newIndex;
            var newMiddle = visibleCount / 2;

            chart.series.each(function(series) {
                var trueIndex = chart.series.indexOf(series);
                var newIndex = series.dummyData;

                var dx = (newIndex - trueIndex + middle - newMiddle) * delta

                series.animate({ property: "dx", to: dx }, series.interpolationDuration, series.interpolationEasing);
                series.bulletsContainer.animate({ property: "dx", to: dx }, series.interpolationDuration, series.interpolationEasing);
            })
        }
    }
}

}); // end am4core.ready()