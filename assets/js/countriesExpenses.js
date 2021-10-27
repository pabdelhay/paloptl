function PlotChart(category, data) {
    am4core.ready(function () {

        // Themes begin
        am4core.useTheme(am4themes_animated);
        // Themes end

        // Create chart instance
        var chart = am4core.create("chartdiv", am4charts.XYChart);
        chart.zoomOutButton.disabled = true;

        // Add data
        chart.data = data;

        // Create axes
        var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
        categoryAxis.dataFields.category = "country";
        categoryAxis.renderer.grid.template.location = 0;
        categoryAxis.renderer.grid.template.disabled = true;

        var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
        valueAxis.renderer.inside = true;
        valueAxis.renderer.labels.template.disabled = true;
        valueAxis.renderer.grid.template.disabled = true;
        valueAxis.min = 0;

        // Create series
        function createSeries(field, name) {

            // Set up series
            var series = chart.series.push(new am4charts.ColumnSeries());
            series.name = name;
            series.stacked = true;
            series.dataFields.valueY = field;
            series.dataFields.categoryX = "country";
            series.sequencedInterpolation = true;

            // Configure columns
            series.columns.template.width = am4core.percent(60);
            series.columns.template.tooltipText = "[bold]{name}[/]\n[font-size:14px]{categoryX}: {valueY.formatNumber('#.00')}%";

            // Add label
            var labelBullet = series.bullets.push(new am4charts.LabelBullet());
            //labelBullet.label.text = "{valueY}";
            labelBullet.label.text = "{valueY.formatNumber('#.00')}%";
            labelBullet.locationY = 0.5;
            labelBullet.label.hideOversized = true;

            return series;
        }

        var idx = 0;
        for (; idx < category.length; idx++) {
            createSeries(category[idx], category[idx]);
        }

        // Legend
        chart.legend = new am4charts.Legend();
        chart.legend.paddingTop = '40px';

    }); // end am4core.ready()
}


function GetPlotChart(year) {
    var url = "/api/budgets/expense_by_country/?year=" + year;
    $.get(url, function (result) {
        PlotChart(result.category, result.data);
        $('.historical-title .year').html(year);
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}

$(document).ready(function () {
    // Binds
    $(document).on('click', '.year-selector a', function (ev) {
        $('.year-selector a').removeClass('active');
        $(this).addClass('active');
        ev.preventDefault();
        var year = $(this).text();
        GetPlotChart(year)
    });
    $('.year-selector a:last').trigger('click');
});
